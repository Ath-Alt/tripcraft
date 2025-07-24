from django.contrib.auth import authenticate
from user_app   .models import UserProfile
from django.contrib.auth import login, logout
from admin_app.models import UserActivity, PasswordResetCode
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.template.loader import render_to_string

# define page renders here
def home(request):
    return render(request, 'tripcraft.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

# Handle user registration (Atheen)
def user_register(request):
    if request.method == "POST":
        # Retreive data from register form
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        gender = request.POST.get("gender")
        terms = request.POST.get("agree")

        # Validation Checks
        # Empty fields?
        if not all ([username, email, password, gender]):
            messages.error(request, "Please fill out all fields")
        # Agreed to terms?
        elif not terms:
            messages.error(request, "You must agree to the terms of service to make an account")
        # Email/Username already taken?
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username taken")
        # If all pass
        else:
            # Create user instance
            user = User.objects.create_user(username=username, email=email, password=password)
            # Create profile
            UserProfile.objects.create(user=user, gender=gender)
            # Log in new user
            login(request, user)
            UserActivity.objects.create(user=request.user)

            # return HttpResponse("User logged in")
            return redirect('user_app:myTrips') 
    return render(request, 'register.html')

# Handle user login (Atheen)
def user_login(request):
    if request.method == "POST":
        # Retrieve identifier (email/username) and password from login form
        identifier = request.POST.get("identifier")
        password = request.POST.get("password")

        # Validation checks
        # Empty fields?
        if not all([identifier, password]):
            messages.error(request, "Please fill out all fields")
        # Incorrect identifier or password?
        else:
            user = User.objects.filter(email=identifier).first() or User.objects.filter(username=identifier).first()
            
            # If information is correct, log in
            if user and (user := authenticate(request, username=user.username, password=password)):
                login(request, user)
                UserActivity.objects.create(user=request.user)

                # Admin login
                if user.is_staff:
                    # return HttpResponse("Admin logged in") 
                    return redirect('admin_app:analytics') 
                # User login
                else:
                    # return HttpResponse("User logged in")
                    return redirect('user_app:myTrips') 
                
            # If incorrect, show an error message
            else:
                messages.error(request, "Information incorrect")
                
    return render(request, 'login.html')

# Handle user logout (Atheen)
def user_logout(request):
    if request.method == "POST":
        logout(request)
    # Redirect to home page
    return redirect('/')






def password_reset(request):
    """
    Display the password reset request page and send the verification code.
    """
    email_sent = False
    email = request.GET.get('email', '')
    resend = request.GET.get('resend', False)

    # Handle resending the verification code if requested
    if email and resend:
        try:
            user = User.objects.get(email=email)
            # Generate a new verification code
            reset_code = PasswordResetCode.generate_code(user)

            # Send the verification code by email
            send_verification_email(user, reset_code.code)

            messages.success(request, 'The verification code has been resent to your email.')
            return render(request, 'forget_password.html', {'code_sent': True, 'email': email})

        except User.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
            return render(request, 'forget_password.html')

    # Handle sending verification code when submitting the form
    if request.method == 'POST' and request.POST.get('step') == 'email':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)
            # Generate a new verification code
            reset_code = PasswordResetCode.generate_code(user)

            # Send the verification code by email
            send_verification_email(user, reset_code.code)

            email_sent = True
            messages.success(request, 'The verification code has been sent to your email.')

        except User.DoesNotExist:
            messages.error(request, 'No account found with this email address.')

    return render(request, 'forget_password.html', {'code_sent': email_sent, 'email': email})


def verify_reset_code(request):
    """
    Verify the validity of the submitted verification code.
    """
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

            # Collect the 6 digits of the verification code
            code_digits = [
                request.POST.get('code1', ''),
                request.POST.get('code2', ''),
                request.POST.get('code3', ''),
                request.POST.get('code4', ''),
                request.POST.get('code5', ''),
                request.POST.get('code6', '')
            ]
            verification_code = ''.join(code_digits)

            # Check the code in the database
            try:
                reset_code = PasswordResetCode.objects.get(
                    user=user,
                    code=verification_code,
                    is_used=False
                )

                # Validate the code's expiration
                if reset_code.is_valid():
                    return render(request, 'reset_password.html', {'user_id': user.id})
                else:
                    messages.error(request, 'The verification code has expired. Please request a new code.')
                    return render(request, 'forget_password.html')

            except PasswordResetCode.DoesNotExist:
                messages.error(request, 'Invalid verification code. Please try again.')
                return render(request, 'forget_password.html', {'code_sent': True, 'email': email})

        except User.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
            return render(request, 'forget_password.html')

    return redirect('password_reset')


def set_new_password(request):
    """
    Set a new password after successful verification.
    """
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        try:
            user = User.objects.get(id=user_id)

            # Ensure both passwords match
            if new_password1 != new_password2:
                messages.error(request, 'Passwords do not match. Please try again.')
                return render(request, 'reset_password.html', {'user_id': user_id})

            # Check password strength
            if len(new_password1) < 8:
                messages.error(request, 'Password is too short. It must be at least 8 characters long.')
                return render(request, 'reset_password.html', {'user_id': user_id})

            # Set the new password
            user.set_password(new_password1)
            user.save()

            # Mark all reset codes as used
            PasswordResetCode.objects.filter(user=user, is_used=False).update(is_used=True)

            messages.success(request,
                             'Your password has been reset successfully. You can now log in with your new password.')
            return redirect('login')

        except User.DoesNotExist:
            messages.error(request, 'An error occurred. Please try again.')
            return redirect('password_reset')

    return redirect('password_reset')




def send_verification_email(user, verification_code):
    """
    Sends an email containing a verification code using direct SMTP communication.
    """
    context = {
        'user': user,
        'verification_code': verification_code,
        'current_year': datetime.now().year
    }

    # Prepare the email content
    html_content = render_to_string('verification_code_email.html', context)
    plain_content = f'Please use the following verification code: {verification_code}'

    # Set up the email message (without using 'alternative')
    msg = MIMEMultipart()
    msg['Subject'] = 'Verification Code for Password Reset - TripCraft'
    msg['From'] = 'a34372842@gmail.com'  # Ideally, use an official email address as the sender
    msg['To'] = user.email

    # Attach plain text first
    msg.attach(MIMEText(plain_content, 'plain', 'utf-8'))

    # Then attach the HTML content
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))

    # Email server settings
    smtp_host = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'a34372842@gmail.com'
    smtp_password = 'oxqf esxb mwov vonh'

    # Connect to SMTP server and send the email
    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.ehlo()  # Initial greeting to the server
        server.starttls()  # Start TLS encryption
        server.ehlo()  # Greet the server again after TLS starts
        server.login(smtp_username, smtp_password)

        # Send the email
        text = msg.as_string()
        server.sendmail(smtp_username, user.email, text)

        server.quit()
        return True
    except Exception as e:
        # Log the error instead of raising it
        print(f"Error sending email: {e}")
        return False
