from datetime import datetime, timedelta
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Avg
from django.utils import timezone
from .utils import get_user_activity, get_user_data
from django.views.decorators.http import require_POST

from user_app.models import UserProfile, Trip as UserTrip, FavoriteTrip, Follow
from .models import (
    Notification, SupportTicket, TicketResponse, Traveler, TravelerNote,
    TravelerVerification, Trip, Itinerary, Category, POI, HighestUserActivity, FeatureClick
)
from .utils import get_user_activity

logger = logging.getLogger(__name__)

def logging_view(request):
    logger.warning("Warning from Django to Logstash")
    return HttpResponse("Log sent!")

# (SALMA)
def is_staff(user):
    """Check if the user has staff privileges."""
    return user.is_staff


# Analytics page render to put data in charts (ATHEEN)
@login_required
def analytics(request):
    # Staff check
    if not request.user.is_staff:
        return redirect('/')
    
    # Data for user activity linechart
    activity_dates, activity_counts = get_user_activity()

    # Data for gender distribution pie chart
    female_count = UserProfile.objects.filter(gender='F').count()
    male_count = UserProfile.objects.filter(gender='M').count()

    # Donut chart data for the engagement type
    follow_count = Follow.objects.count()
    like_count = FavoriteTrip.objects.count()

    # Data for the bar graph of feature usage
    feature_names = [feature.feature_name for feature in FeatureClick.objects.all()]
    feature_clicks = [feature.click_count for feature in FeatureClick.objects.all()]

    # Data for other general insights
    highest_activity = HighestUserActivity.objects.get(pk=1).count
    total_accounts = User.objects.count()
    most_used_feature = FeatureClick.objects.order_by('-click_count').first().feature_name
    total_trips = UserTrip.objects.count()
    avg_trips_per_user = round(total_trips / total_accounts, 2)
    avg_journey_duration = UserTrip.objects.aggregate(avg_duration=Avg('duration'))['avg_duration'] or 0

    # Organize data in a dictionary
    data = {
        'activity_dates': [date.strftime('%Y-%m-%d') for date in activity_dates],
        'activity_counts': activity_counts,
        'female_count': female_count,
        'male_count': male_count,
        'follow_count': follow_count,
        'like_count': like_count,
        'feature_names': feature_names,
        'feature_clicks': feature_clicks,
        'highest_activity': highest_activity,
        'total_accounts': total_accounts,
        'most_used_feature': most_used_feature,
        'total_trips': total_trips,
        'avg_trips_per_user': avg_trips_per_user,
        'avg_journey_duration': int(avg_journey_duration),
    }
    return render(request, 'analytics.html', data)

# Monitor page to administer all users (ATHEEN)
@login_required
def monitor(request):
    if not request.user.is_staff:
        return redirect('/')
    # User details AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        username = request.GET.get('username')
        action   = request.GET.get('action')
        
        # perform an action if specified
        if action == 'delete_trip':
            trip_id = request.GET.get('trip_id')
            # you could wrap this in try/except for safety
            UserTrip.objects.filter(id=trip_id, user__username=username).delete()
        elif action == 'delete_like':
            like_id = request.GET.get('like_id')
            FavoriteTrip.objects.filter(id=like_id, user__username=username).delete()
        elif action == 'delete_follower':
            follower_id = request.GET.get('follower_id')
            Follow.objects.filter(id=follower_id, follow__username=username).delete()
        elif action == 'delete_following':
            following_id = request.GET.get('following_id')
            Follow.objects.filter(id=following_id, user__username=username).delete()
            
        
        # whether or not you deleted, re-fetch fresh data
        user_data = get_user_data(username)
        return JsonResponse(user_data)
    
    # Regular page render
    users = User.objects.all().values('username', 'email', 'is_staff')
    return render(request, 'monitor.html', {'users': users})

#(SALMA)
@login_required
def dashboard(request):
    """
    Render the user dashboard page.

    Displays user-specific information such as trip counts,
    upcoming trips, countries visited, and recent trips.
    """
    user = request.user
    traveler, created = Traveler.objects.get_or_create(user=user)

    context = {
        'user': user,
        'total_trips': Trip.objects.filter(traveler=traveler).count(),
        'upcoming_trips': Trip.objects.filter(
            traveler=traveler,
            start_date__gte=timezone.now().date()
        ).count(),
        'countries_visited': Itinerary.objects.filter(
            trip__traveler=traveler
        ).values('location').distinct().count(),
        'recent_trips': Trip.objects.filter(traveler=traveler).order_by('-start_date')[:5]
    }
    return render(request, 'templates/accounts/dashboard.html', context)


@login_required
def my_trips_view(request):
    """
    Render the page displaying all trips for the logged-in traveler.
    """
    user = request.user
    traveler = Traveler.objects.get(user=user)
    trips = Trip.objects.filter(traveler=traveler).order_by('-start_date')

    context = {
        'user': user,
        'trips': trips,
    }
    return render(request, 'templates/accounts/my_trips.html', context)


@require_POST
@login_required
def create_trip(request):
    """
    Create a new trip using POST data and return a JSON response.
    """
    try:
        user = request.user
        traveler = Traveler.objects.get(user=user)
        trip = Trip.objects.create(
            name=request.POST.get('name'),
            traveler=traveler,
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date'),
            category=request.POST.get('category'),
            description=request.POST.get('description'),
            location=request.POST.get('location'),
            latitude=float(request.POST.get('latitude')),
            longitude=float(request.POST.get('longitude'))
        )
        response_data = {
            'success': True,
            'trip': {
                'id': trip.id,
                'name': trip.name,
                'start_date': trip.start_date,
                'end_date': trip.end_date,
                'category': trip.category,
                'location': trip.location
            }
        }
        return JsonResponse(response_data)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def map_view(request):
    """
    Render a map view displaying the trips of the logged-in traveler.
    """
    user = request.user
    traveler = Traveler.objects.get(user=user)
    trips = Trip.objects.filter(traveler=traveler)
    context = {
        'user': user,
        'trips': trips,
    }
    return render(request, 'templates/accounts/map.html', context)


@login_required
def category_list(request):
    """
    Render a list of all categories.
    """
    categories = Category.objects.all()
    return render(request, 'templates/accounts/category_list.html', {'categories': categories})

@login_required
def poi_delete(request, pk):
    """
    Delete a specific point of interest (POI) identified by its primary key.
    """
    poi_obj = get_object_or_404(POI, pk=pk)

    if request.method == 'POST':
        try:
            # Save POI name for success message
            poi_name = poi_obj.name

            # Delete the POI
            poi_obj.delete()

            # Add success message
            messages.success(request, f'Point of Interest "{poi_name}" has been successfully deleted.')

            # Redirect to POI list
            return redirect('poi_list')
        except Exception as e:
            # In case of error during deletion
            messages.error(request, f'Error occurred while deleting POI: {str(e)}')
            return redirect('poi_list')

    # If request is not POST, redirect to list page (since we're using JavaScript confirmation)
    return redirect('poi_list')

@login_required
def category_create(request):
    """
    Handle the creation of a new category.

    On POST, creates a new category with an optional icon.
    """
    if request.method == 'POST':
        try:
            category_obj = Category.objects.create(
                name=request.POST['name'],
                description=request.POST['description']
            )
            if 'icon' in request.FILES:
                category_obj.icon = request.FILES['icon']
            category_obj.save()
            messages.success(request, 'Category created successfully.')
            return redirect('category_list')
        except Exception as e:
            messages.error(request, f'Error occurred: {str(e)}')
    return render(request, 'templates/accounts/category_form.html')


@login_required
def category_edit(request, pk):
    """
    Edit an existing category identified by its primary key.
    """
    category_obj = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        try:
            category_obj.name = request.POST['name']
            category_obj.description = request.POST['description']
            if 'icon' in request.FILES:
                category_obj.icon = request.FILES['icon']
            category_obj.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('category_list')
        except Exception as e:
            messages.error(request, f'Error occurred: {str(e)}')
    return render(request, 'templates/accounts/category_form.html', {'category': category_obj})


@login_required
def poi_list(request):
    """
    Render a list of all points of interest (POI).
    """
    pois = POI.objects.all()
    return render(request, 'poi/list.html', {'pois': pois})


@login_required
def poi_create(request):
    """
    Handle creation of a new point of interest (POI).
    """
    categories = Category.objects.all()
    if request.method == 'POST':
        try:
            poi_obj = POI.objects.create(
                name=request.POST['name'],
                category_id=request.POST['category'],
                description=request.POST['description'],
                location=request.POST['location'],
                latitude=float(request.POST['latitude']),
                longitude=float(request.POST['longitude'])
            )
            if 'image' in request.FILES:
                poi_obj.image = request.FILES['image']
                poi_obj.save()
            messages.success(request, 'POI created successfully.')
            return redirect('poi_list')
        except Exception as e:
            messages.error(request, f'Error occurred: {str(e)}')
    return render(request, 'poi/create.html', {'categories': categories})


@login_required
def poi_edit(request, pk):
    """
    Edit an existing point of interest (POI) identified by its primary key.
    """
    poi_obj = get_object_or_404(POI, pk=pk)
    categories = Category.objects.all()
    if request.method == 'POST':
        try:
            poi_obj.name = request.POST['name']
            poi_obj.category_id = request.POST['category']
            poi_obj.description = request.POST['description']
            poi_obj.location = request.POST['location']
            poi_obj.latitude = float(request.POST['latitude'])
            poi_obj.longitude = float(request.POST['longitude'])
            if 'image' in request.FILES:
                poi_obj.image = request.FILES['image']
            poi_obj.save()
            messages.success(request, 'POI updated successfully.')
            return redirect('poi_list')
        except Exception as e:
            messages.error(request, f'Error occurred: {str(e)}')
    return render(request, 'poi/create.html', {'poi': poi_obj, 'categories': categories})


@login_required
def traveler_list(request):
    """
    Render a list of travelers along with related user and verification information.
    """
    travelers = Traveler.objects.select_related('user', 'verification').all()
    return render(request, 'templates/accounts/traveler_list.html', {'travelers': travelers})


@login_required
def traveler_detail(request, pk):
    """
    Display details of a specific traveler along with support tickets and admin notes.

    Allows adding new notes or verifying the traveler.
    """
    traveler_obj = get_object_or_404(Traveler.objects.select_related('user', 'verification'), pk=pk)
    support_tickets = traveler_obj.support_tickets.all()
    notes = traveler_obj.admin_notes.all().order_by('-created_at')

    if request.method == 'POST':
        if 'add_note' in request.POST:
            TravelerNote.objects.create(
                traveler=traveler_obj,
                author=request.user,
                note=request.POST['note']
            )
        elif 'verify_traveler' in request.POST:
            verification, created = TravelerVerification.objects.get_or_create(traveler=traveler_obj)
            verification.status = 'verified'
            verification.verified_at = timezone.now()
            verification.verified_by = request.user
            verification.save()
        return redirect('traveler_detail', pk=pk)

    return render(request, 'templates/accounts/traveler_detail.html', {
        'traveler': traveler_obj,
        'support_tickets': support_tickets,
        'notes': notes
    })


@login_required
def support_ticket_list(request):
    """
    Render a list of support tickets along with summary counts.
    """
    tickets = SupportTicket.objects.select_related('traveler__user', 'assigned_to').all()
    context = {
        'tickets': tickets,
        'new_tickets_count': tickets.filter(status='new').count(),
        'in_progress_tickets_count': tickets.filter(status='in_progress').count(),
        'resolved_tickets_count': tickets.filter(status='resolved').count(),
        'urgent_tickets_count': tickets.filter(priority='urgent').count(),
    }
    return render(request, 'templates/accounts/support_ticket_list.html', context)


@login_required
def support_ticket_detail(request, pk):
    """
    Render detailed view of a support ticket.

    Allows staff to add responses, update status, or assign the ticket.
    """
    ticket = get_object_or_404(SupportTicket.objects.select_related('traveler__user'), pk=pk)
    responses = ticket.responses.all().order_by('created_at')

    if request.method == 'POST':
        if 'add_response' in request.POST:
            TicketResponse.objects.create(
                ticket=ticket,
                responder=request.user,
                message=request.POST['message'],
                is_staff_response=True
            )
        elif 'update_status' in request.POST:
            ticket.status = request.POST['status']
            ticket.save()
        elif 'assign_ticket' in request.POST:
            ticket.assigned_to = request.user
            ticket.save()
        return redirect('support_ticket_detail', pk=pk)

    staff_users = User.objects.filter(is_staff=True)
    return render(request, 'templates/accounts/support_ticket_detail.html', {
        'ticket': ticket,
        'responses': responses,
        'staff_users': staff_users
    })


@login_required
def user_list(request):
    """
    Render a list of all users with statistics on active, staff, and new users.
    """
    users = User.objects.all().order_by('-date_joined')
    context = {
        'users': users,
        'active_users_count': users.filter(is_active=True).count(),
        'staff_users_count': users.filter(is_staff=True).count(),
        'new_users_count': users.filter(date_joined__gte=timezone.now() - timedelta(days=30)).count(),
    }
    return render(request, 'templates/accounts/user_list.html', context)


@login_required
def user_detail(request, pk):
    """
    Render the detail page for a specific user.

    Allows toggling active/staff status and resetting the password.
    """
    user_obj = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        if 'toggle_active' in request.POST:
            user_obj.is_active = not user_obj.is_active
            user_obj.save()
            messages.success(request, f'User {"activated" if user_obj.is_active else "deactivated"} successfully.')
        elif 'toggle_staff' in request.POST:
            user_obj.is_staff = not user_obj.is_staff
            user_obj.save()
            messages.success(request, f'Admin privileges {"granted" if user_obj.is_staff else "revoked"}.')
        elif 'reset_password' in request.POST:
            new_password = User.objects.make_random_password()
            user_obj.set_password(new_password)
            user_obj.save()
            messages.success(request, f'New password set: {new_password}')
        return redirect('user_detail', pk=pk)

    context = {
        'user_detail': user_obj,
        'last_login': user_obj.last_login,
        'date_joined': user_obj.date_joined,
        'is_active': user_obj.is_active,
        'is_staff': user_obj.is_staff,
    }

    try:
        traveler = user_obj.traveler
        context.update({
            'is_traveler': True,
            'trips_count': traveler.trips.count(),
            'verification_status': traveler.verification.status if hasattr(traveler, 'verification') else None,
        })
    except Traveler.DoesNotExist:
        context['is_traveler'] = False

    return render(request, 'templates/accounts/user_detail.html', context)


@login_required
def user_create(request):
    """
    Create a new user (and traveler account if requested) via POST data.
    """
    if request.method == 'POST':
        try:
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            is_staff_flag = request.POST.get('is_staff', False)
            user_obj = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            user_obj.is_staff = is_staff_flag
            user_obj.save()
            if request.POST.get('create_traveler', False):
                Traveler.objects.create(user=user_obj)
            messages.success(request, 'User created successfully.')
            return redirect('admin:user_list')
        except Exception as e:
            messages.error(request, f'Error occurred: {str(e)}')
    return render(request, 'templates/accounts/user_form.html')


@staff_member_required
def notification_list(request):
    """
    Render a list of notifications with counts by type.
    """
    notifications = Notification.objects.all().order_by('-notification_date')
    context = {
        'notifications': notifications,
        'unread_count': notifications.filter(is_read=False).count(),
        'system_count': notifications.filter(notification_type='system').count(),
        'trip_count': notifications.filter(notification_type='trip').count()
    }
    return render(request, 'templates/accounts/notification_list.html', context)


@staff_member_required
def notification_create(request):
    """
    Create a new notification. Can be targeted to:
    - A single traveler or all travelers
    - A single user or all users
    """
    travelers = Traveler.objects.all()
    users = User.objects.all()

    if request.method == 'POST':
        try:
            notification_type = request.POST.get('notification_type')
            message_text = request.POST.get('message')

            # Get notification date or use current time
            notification_date_str = request.POST.get('notification_date')
            if notification_date_str:
                notification_date = datetime.strptime(notification_date_str, "%Y-%m-%dT%H:%M")
            else:
                notification_date = timezone.now()

            recipient_category = request.POST.get('recipient_category')

            # Process notifications for travelers
            if recipient_category == 'traveler':
                traveler_recipient_type = request.POST.get('traveler_recipient_type')

                if traveler_recipient_type == 'single':
                    # Send to a single traveler
                    traveler_id = request.POST.get('traveler_id')
                    if not traveler_id:
                        messages.error(request, 'Please select a traveler.')
                        return render(request, 'templates/accounts/notification_form.html',
                                      {'travelers': travelers, 'users': users})

                    traveler = get_object_or_404(Traveler, id=traveler_id)
                    Notification.objects.create(
                        traveler=traveler,
                        message=message_text,
                        notification_type=notification_type,
                        notification_date=notification_date,
                        is_read=False
                    )
                    messages.success(request, f'Notification created for traveler {traveler.user.username}.')
                else:
                    # Send to all travelers
                    for traveler in travelers:
                        Notification.objects.create(
                            traveler=traveler,
                            message=message_text,
                            notification_type=notification_type,
                            notification_date=notification_date,
                            is_read=False
                        )
                    messages.success(request, f'Notification sent to all {travelers.count()} travelers.')

            # Process notifications for users
            elif recipient_category == 'user':
                user_recipient_type = request.POST.get('user_recipient_type')

                if user_recipient_type == 'single':
                    # Send to a single user
                    user_id = request.POST.get('user_id')
                    if not user_id:
                        messages.error(request, 'Please select a user.')
                        return render(request, 'templates/accounts/notification_form.html',
                                      {'travelers': travelers, 'users': users})

                    user = get_object_or_404(User, id=user_id)
                    Notification.objects.create(
                        user=user,
                        traveler=None,
                        message=message_text,
                        notification_type=notification_type,
                        notification_date=notification_date,
                        is_read=False
                    )
                    messages.success(request, f'Notification created for user {user.username}.')
                else:
                    # Send to all users
                    for user in users:
                        Notification.objects.create(
                            user=user,
                            traveler=None,
                            message=message_text,
                            notification_type=notification_type,
                            notification_date=notification_date,
                            is_read=False
                        )
                    messages.success(request, f'Notification sent to all {users.count()} users.')

            return redirect('admin_app:notification_list')

        except Exception as e:
            messages.error(request, f'Error occurred: {str(e)}')

    context = {
        'travelers': travelers,
        'users': users,
    }
    return render(request, 'templates/accounts/notification_form.html', context)

@staff_member_required
def notification_delete(request, pk):
    """
    Delete a specific notification.
    """
    notification_obj = get_object_or_404(Notification, pk=pk)
    if request.method == 'POST':
        notification_obj.delete()
        messages.success(request, 'Notification deleted successfully.')
        return redirect('notification_list')
    return redirect('notification_list')


@login_required
def user_notifications(request):
    """
    Render notifications for the logged-in user.
    """
    user = request.user
    traveler, created = Traveler.objects.get_or_create(user=user)
    notifications = Notification.objects.filter(traveler=traveler).order_by('-notification_date')
    context = {
        'notifications': notifications,
        'unread_count': notifications.filter(is_read=False).count()
    }
    return render(request, 'templates/accounts/user_notifications.html', context)


@login_required
def mark_notification_read(request, pk):
    """
    Mark a specific notification as read if it belongs to the current user.
    """
    notification_obj = get_object_or_404(Notification, pk=pk)
    traveler, created = Traveler.objects.get_or_create(user=request.user)
    if notification_obj.traveler != traveler:
        messages.error(request, 'Access denied for this notification.')
        return redirect('user_notifications')
    notification_obj.is_read = True
    notification_obj.save()
    return redirect('user_notifications')


@login_required
def unread_notifications_count(request):
    """
    Return the count of unread notifications for the current user as JSON.
    """
    user = request.user
    traveler = get_object_or_404(Traveler, user=user)
    count = Notification.objects.filter(traveler=traveler, is_read=False).count()
    return JsonResponse({'count': count})


@require_POST
def ajax_logout(request):
    """
    Log out the current user via an AJAX POST request.
    """
    logout(request)
    return JsonResponse({'success': True})


# Category and POI additional endpoints

def category_detail(request, pk):
    """
    Render the details of a specific category.
    """
    category_obj = get_object_or_404(Category, pk=pk)
    return render(request, 'categories/detail.html', {'category': category_obj})


def category_edit_view(request, pk):
    """
    Render the edit form for a category.

    Note: This function assumes the template handles fetching the category.
    """
    category_obj = get_object_or_404(Category, pk=pk)
    return render(request, 'categories/edit.html', {'category': category_obj})


def category_create_form(request):
    """
    Render the creation form for a new category.
    """
    return render(request, 'categories/create.html')


def poi_detail(request, pk):
    """
    Render the details of a specific point of interest (POI).
    """
    poi_obj = get_object_or_404(POI, pk=pk)
    return render(request, 'poi/detail.html', {'poi': poi_obj})
