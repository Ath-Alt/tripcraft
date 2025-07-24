from pyexpat.errors import messages
from datetime import date, datetime, timedelta
from dateutil import parser
import pytz 
import json
from django.utils import timezone
from django.forms import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import MainArea, Category, Trip, DailyPlanner, UserProfile, Follow, Notification
from .forms import catForm, tripForm, UserProfileForm, FollowForm
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib import messages
from admin_app.utils import feature_click
from django.shortcuts import render, get_object_or_404
from .models import Trip, FavoriteTrip
from itertools import groupby
from operator import attrgetter
from django.contrib.auth import login


#====================================
# [Az]myTrips
# [Az] myTrip displays trips and categorys and update dynamicly 
@login_required
def myTrips(request):
    # (ATHEEN) redirect to main page if user is staff
    if request.user.is_staff:
        return redirect('/')
    # (ATHEEN) log feature click for admin analytics
    feature_click("Trips")
    cat_form = catForm()
    trip_form = tripForm()
    categories = Category.objects.filter(user=request.user)

    selected_category = None
    selected_trips = None
    # [Az]Initialize the main_area variable
    main_area = None  
    # [Az] Try to get the user's main area (if it exists)
    try:
        main_area = MainArea.objects.get(user=request.user)
    except MainArea.DoesNotExist:
        main_area = None  # [Az] If the user doesn't have a main area, set it to None
    cat_id = request.GET.get("cat_id")
    if cat_id:
        try:
            selected_category = Category.objects.get(id=cat_id, user=request.user)
            selected_trips = Trip.objects.filter(category=selected_category, user=request.user)
        except Category.DoesNotExist:
            selected_category = None
            selected_trips = None
    else:
        selected_trips = Trip.objects.filter(main_area__isnull=False, category__isnull=True, main_area__user=request.user)
    context = {
        'cat_form': cat_form,
        'trip_form': trip_form,
        'categories': categories,
        'selected_category': selected_category,
        'uncategorized_trips': selected_trips,
        'main_area': main_area, 
    }
    # [Az]🔥 If HTMX request, only return the partials (db1 + db2)
    if request.headers.get('Hx-Request') == 'true':
        db1_html = render_to_string("partials/db1.html", context, request)
        db2_html = render_to_string("partials/db2.html", context, request)
        return HttpResponse(db1_html + db2_html)
    # [Az]Normal full page load
    return render(request, 'myTrips.html', context)

# [Az] categorys
# [Az] to link the category db with the form to add, edit and delete
@login_required
def add_category(request):
    print('a new day')
    if request.method == 'POST':
        form = catForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            print("Category saved:", category)  # Debugging line
            # [Az]Return updated list or close modal
            return HttpResponse('<script>window.location.reload()</script>')
        else:
            print("form not correct")
            print("Form is invalid:", form.errors)  # Debugging line
            return render(request, 'partials/category_form.html', {'cat_form': form})
    else:
        form = catForm()
        return render(request, 'partials/category_form.html', {'cat_form': form})
    
# [Az] edit category
@login_required
def edit_category(request, cat_id):
    category = get_object_or_404(Category, id=cat_id, user=request.user)
    if request.method == 'POST':
        form = catForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return HttpResponse('<script>window.location.reload()</script>')
        else:
            return render(request, 'partials/category_form.html', {
                'cat_form': form,
                'category': category 
            })
    else:
        form = catForm(instance=category)
        return render(request, 'partials/category_form.html', {
            'cat_form': form,
            'category': category  
            
        })
    

@login_required
def confirm_delete(request, cat_id):
    category = get_object_or_404(Category, id=cat_id)
    return render(request, 'partials/del_cat.html', {'category': category})


# [Az] delete category
@login_required
def delete_category(request, cat_id):
    if request.method == 'POST':
        category = get_object_or_404(Category, id=cat_id, user=request.user)
        category.delete()
        return HttpResponse('<script>window.location.reload()</script>')  # reload to reflect deletion
    return HttpResponseNotAllowed(['POST'])

# [Az] Trips
# [Az] to link the trip db to the form and the logic behind main area
@login_required
def add_trip_main(request, main_id):
    print('Main testing')
    main_area = get_object_or_404(MainArea, id=main_id, user=request.user)

    if request.method == 'GET':
        print('Main testing 1')
        form = tripForm()
        return render(request, 'partials/trip_form.html', {
            'trip_form': form, 
            'main_area_id': main_id,
            'hx_post_url': reverse('user_app:add_trip_main', args=[main_id])
            })

    elif request.method == 'POST':
        print('Main testing 2')
        form = tripForm(request.POST, request.FILES)
        # [Az] Assign main_area and user **before** validation 
        form.instance.user = request.user
        form.instance.main_area = main_area

        if form.is_valid():
            print('Main testing 3')
            form.save()
            print('Main testing 4')
            return HttpResponse('<script>window.location.reload()</script>')

        else:
            print('Form is not valid:', form.errors)
            # [Az] If the form is invalid, return only the form portion to re-render in modal
            return render(request, 'partials/trip_form.html', {
                'trip_form': form,
                'hx_post_url': request.path,
                'main_area_id': request.POST.get('main_area'),
            })
    else:

        return render(request, 'partials/trip_form.html', {
            'trip_form': form,
            'main_area_id': main_id
        })
# [Az] to add trip in a category
@login_required
def add_trip_cat(request, cat_id):
    print('Category trip view hit')
    category = get_object_or_404(Category, id=cat_id, user=request.user)

    if request.method == 'GET':
        form = tripForm()
        return render(request, 'partials/trip_form.html', {
            'trip_form': form,
            'cat_id': cat_id,
            'hx_post_url': reverse('user_app:add_trip_cat', args=[cat_id])
        })

    elif request.method == 'POST':
        print('Category form POST')
        form = tripForm(request.POST, request.FILES)
        
        # [Az]🔥 Set category and user **before validation** 
        form.instance.user = request.user
        form.instance.category = category

        if form.is_valid():
            print('Category trip form valid')
            form.save()
            return HttpResponse('<script>window.location.reload()</script>')
        else:
            print('Form errors:', form.errors)
            # [Az] If the form is invalid, return only the form portion to re-render in modal
            return render(request, 'partials/trip_form.html', {
                'trip_form': form,
                'hx_post_url': request.path,
                'category_id': request.POST.get('category'),
            })
    else:
        return render(request, 'partials/trip_form.html', {
            'trip_form': form,
            'cat_id': cat_id
        })
    
# [Az] edit a trip 
@login_required
def edit_trip(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)

    if request.method == 'GET':
        form = tripForm(instance=trip)
        return render(request, 'partials/trip_form.html', {
            'trip_form': form,
            'trip_id': trip_id,
            'hx_post_url': reverse('user_app:edit_trip', args=[trip_id])
        })
    elif request.method == 'POST':
        form = tripForm(request.POST, request.FILES, instance=trip)

        if form.is_valid():
            form.save()
            return HttpResponse('<script>window.location.reload()</script>')
        else:
            # If the form is invalid, return only the form portion to re-render in modal
            return render(request, 'partials/trip_form.html', {
                'trip_form': form,
                'hx_post_url': request.path,
                'main_area_id': request.POST.get('main_area'),
                'category_id': request.POST.get('category'),
            })
    else:
        return render(request, 'partials/trip_form.html', {
            'trip_form': form,
            'trip_id': trip_id
        })
# [Az] delete a trip     
@login_required
def confirm_del_trip(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    return render(request, 'partials/del_trip.html', {'trip': trip})
@login_required
@require_POST
def delete_trip(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    trip.delete()
    return HttpResponse('<script>window.location.reload()</script>')

# [Az] Monthly view
# View to fetch trips with dates (for monthly calendar)
@login_required  
def get_trips_for_calendar(request):
    trips = Trip.objects.filter(user=request.user, date__isnull=False)
    
    events = []
    for trip in trips:
        start_date = trip.date
        end_date = start_date + timedelta(days=trip.duration - 1)  # [Az] Adjust to account for the entire duration, including start date

        # [Az] Check if the trip color is light or dark
        background_color = trip.color
        text_color = "black" if is_light(background_color) else "white"

        events.append({
            'title': trip.name,
            'start': start_date.isoformat(),
            'end': (end_date + timedelta(days=1)).isoformat(),  # [Az] The end date should be inclusive, so one more day is added to mark the last day
            'color': background_color,
            'textColor': text_color,
        })
    return JsonResponse(events, safe=False)
# [Az] for redablety resons so the text color chang based on the backgroud color used in the calender 
def is_light(color):
    """
    [Az] Determines if the color is light or dark.
    Returns True if light, False if dark.
    """
    # [Az] Convert hex to RGB
    color = color.lstrip('#')
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    # [Az] Using the luminance formula for light/dark detection
    luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
    return luminance > 0.5

# [Az] a detaled view of the trip with the daily planner 
# daily view
@login_required
def trip_detail_view(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    days = range(1, trip.duration + 1)
    daily_plans = DailyPlanner.objects.filter(trip=trip).order_by('day_number', 'start_time')

    context = {
        'trip': trip,
        'days': days,
        'daily_plans': daily_plans
    }
    return render(request, 'myTripsDailyview.html', context)
# [Az] for reding the data form the database using json
@login_required
@csrf_exempt
def daily_events_json(request, trip_id):
    trip = Trip.objects.get(id=trip_id)
    planners = DailyPlanner.objects.filter(trip=trip)

    #[Az] Use real trip.date if available, otherwise fallback to a static base since date are optional 
    base_date = trip.date if trip.date else date(2025, 1, 1)  # Pick a consistent fallback date

    events = []
    for planner in planners:
        event_date = base_date + timedelta(days=planner.day_number - 1)

        start = datetime.combine(event_date, planner.start_time).isoformat()
        end = datetime.combine(event_date, planner.end_time).isoformat()

        # [Az] Determine text color based on trip color
        text_color = "black" if is_light(trip.color) else "white"

        events.append({
            "title": planner.name,
            "start": start,
            "end": end,
            "id": planner.id,
            "color": trip.color, 
            "textColor": text_color,  #[Az] Dynamically set the text color based on the background color
            "location": planner.location,
            "description": planner.description,
        })
    return JsonResponse(events, safe=False)

# [Az] creat an event using the form 
@login_required
@csrf_exempt
def create_event(request, trip_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            trip = Trip.objects.get(id=trip_id)
            name = data.get('name')
            location = data.get('location', '')
            description = data.get('description', '')
            day_number = data.get('day_number')
            start_time = datetime.strptime(data.get('start_time'), '%H:%M').time()
            end_time = datetime.strptime(data.get('end_time'), '%H:%M').time()

            planner = DailyPlanner.objects.create(
                trip=trip,
                name=name,
                location=location,
                description=description,
                day_number=day_number,
                start_time=start_time,
                end_time=end_time
            )

            return JsonResponse({"status": "success", "id": planner.id})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})


# [Az] to enable update time using drag and drop or resize the event
@login_required
@csrf_exempt
@require_POST
def update_event_time(request, event_id):
    try:
        data = json.loads(request.body)
        start = parser.isoparse(data.get('start'))  # ISO time with Z
        end = parser.isoparse(data.get('end'))

        # [Az] Convert to local timezone (+03:00)
        local_tz = pytz.timezone('Asia/Riyadh')  # local zone
        start = start.astimezone(local_tz)
        end = end.astimezone(local_tz)

        print("Start local:", start)
        print("End local:", end)

        event = DailyPlanner.objects.get(id=event_id)
        event.start_time = start
        event.end_time = end
        event.save()

        return JsonResponse({"status": "success"})

    except Exception as e:
        print("Error updating event time:", str(e))
        return JsonResponse({"error": str(e)}, status=400)
# [Az] edit the entier event 
@login_required
@csrf_exempt
@require_POST
def edit_event(request, event_id):
    try:
        data = json.loads(request.body)
        event = DailyPlanner.objects.get(id=event_id)

        event.name = data.get('name')
        event.location = data.get('location', '')
        event.description = data.get('description', '')
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if start_time:
            event.start_time = datetime.strptime(start_time, '%H:%M').time()
        if end_time:
            event.end_time = datetime.strptime(end_time, '%H:%M').time()

        event.save()
        return JsonResponse({"status": "success"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})

# [Az] delete event
@login_required
@csrf_exempt
def delete_event(request, event_id):
    if request.method == "POST": 
        try:
            event = get_object_or_404(DailyPlanner, id=event_id)
            event.delete()
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
#====================================

#====================================

#[Lyan]
# [Lyan] Profile view to display trip cards, avatar, username, bio, following, and notifications
@login_required
def profile(request):
    # (ATHEEN) redirect to main page if user is staff
    if request.user.is_staff:
        return redirect('/')
    # (ATHEEN) log feature click for admin analytics
    feature_click("Profile")
    """
    Render the profile page with trip cards, avatar, username, bio, following, and notifications.
    """
    if request.user.is_staff:
        return redirect('/')

    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    # Number of following
    following_count = Follow.objects.filter(user=request.user).count()
    # List of following
    following = Follow.objects.filter(user=request.user).select_related('follow')
    # Trips
    trips = Trip.objects.filter(user=request.user)
    # Unread notifications
    notifications = Notification.objects.filter(user=request.user, is_read=False)

    # [Layan] Initialize FollowForm for adding following
    follow_form = FollowForm()

    context = {
        'user_profile': user_profile,
        'username': request.user.username,
        'trips': trips,
        'following_count': following_count,
        'following': following,
        'notifications': notifications,
        'follow_form': follow_form,  # [Layan] Added follow_form to context
    }
    if request.headers.get('Hx-Request') == 'true':
        return render(request, 'partials/trip_cards.html', context)
    return render(request, 'Profile.html', context)

# [Lyan] Add a follow using a form
# [Lyan] Add a follow using a form
@login_required
def add_follow(request):
    """
    Follow and send a notification to the followed user.
    """
    if request.method == 'POST':
        form = FollowForm(request.POST)
        if form.is_valid():
            follow = form.cleaned_data['follow_username']

            if follow == request.user:
                messages.error(request, "You cannot follow yourself!")
                return redirect('user_app:profile')

            Follow.objects.get_or_create(user=request.user, follow=follow)

            profile, created = UserProfile.objects.get_or_create(user=follow)

            if profile.followers_notifications:
                Notification.objects.create(
                    user=follow,
                    message=f"{request.user.username} followed you!",
                    notification_type='follow'
                )

            messages.success(request, f"You have followed {follow.username}!")
            return redirect('user_app:profile')
    else:
        form = FollowForm()

    # [Lyan] Pass the form to the template if GET request
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    following = Follow.objects.filter(user=request.user).select_related('follow')
    following_count = following.count()
    trips = Trip.objects.filter(user=request.user)
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False)

    context = {
        'user_profile': user_profile,
        'username': request.user.username,
        'trips': trips,
        'following_count': following_count,
        'following': following,
        'notifications': unread_notifications,
        'follow_form': form,
    }

    return render(request, 'Profile.html', context)

# [Lyan] Delete a follow
@login_required
def delete_follow(request, follow_id):
    """
    Remove a follow from the user's follow list.
    """
    follow = get_object_or_404(User, id=follow_id)
    followage = Follow.objects.filter(user=request.user, follow=follow).first()
    if followage:
        followage.delete()
        messages.success(request, f"You have unfollowed {follow.username}.")
    return redirect('user_app:profile')

@login_required
def card_view(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    context = {
        'trip': trip,
    }
    return render(request, 'user_app/card.html', context)

# [Lyan] Mark a notification as read
@login_required
def mark_notification_as_read(request, notification_id):
    """
    Mark a notification as read.
    """
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('user_app:profile')

# [Lyan] Settings view to update avatar, username, and bio
@login_required
def settings(request):
    """
    Handle updates to avatar, username, and bio.
    """
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)

        # Update avatar, username, and bio
        if form.is_valid():
            form.save()

            # Take in AJAX request
            if request.headers.get('Hx-Request') == 'true':
                # Prepare context for update
                context = {
                    'user_profile': user_profile,
                    'username': request.user.username,
                    'trips': Trip.objects.filter(user=request.user),
                }
                profile_html = render_to_string('partials/profile_header.html', context, request)
                return JsonResponse({'status': 'success', 'profile_html': profile_html})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    else:
        form = UserProfileForm(instance=user_profile, initial={'username': request.user.username})
    
    context = {'form': form}
    return render(request, 'settings.html', context)

# [Lyan] Favorites view to display favorite trips
@login_required
def favorites(request):
    # (ATHEEN) redirect to main page if user is staff
    if request.user.is_staff:
        return redirect('/')
    # (ATHEEN) log feature click for admin analytics
    feature_click("Favorites")
    favorite_trips = Trip.objects.filter(favoritetrip__user=request.user)
    context = {
        'trips': favorite_trips,
    }
    return render(request, 'favorites.html', context)

# [Lyan] Toggle favorite status for a trip
@login_required
@require_POST
def toggle_favorite(request, trip_id):
    """
    Toggle the favorite status of a trip and update the favorites page dynamically.
    """
    trip = get_object_or_404(Trip, id=trip_id, user=request.user)
    trip.is_favorite = not trip.is_favorite
    trip.save()
    favorite_trips = Trip.objects.filter(user=request.user, is_favorite=True)
    context = {
        'favorite_trips': favorite_trips,
    }
    return render(request, 'partials/fav_scroll.html', context)
#====================================
# wafa's explore
# Views for Explore pages
@login_required
def explore_view(request):
        # (ATHEEN) redirect to main page if user is staff
    if request.user.is_staff:
        return redirect('/')
    # (ATHEEN) log feature click for admin analytics
    feature_click("Explore")
    if request.method == "POST" and 'settings' in request.POST:
        return settings(request)
    """
    Render the explore page with all trips and search functionality.
    """
    query = request.GET.get('q', '')
    if query:
        trips = Trip.objects.filter(destination__icontains=query)
    else:
        trips = Trip.objects.all()

    context = {
        'trips': trips,
        'query': query,
    }
    return render(request, 'explore.html', context)
@login_required
def following_explore_view(request):
    """
    Render the following explore page with trips from following only.
    """
    query = request.GET.get('q', '')
    following = Follow.objects.filter(user=request.user).values_list('follow', flat=True)
    if query:
        trips = Trip.objects.filter(user__in=following, destination__icontains=query)
    else:
        trips = Trip.objects.filter(user__in=following)
    
    context = {
        'trips': trips,
        'query': query,
    }
    return render(request, 'following-explore.html', context)


@login_required
def explore_card_view(request, trip_id):
    trip = Trip.objects.get(id=trip_id)
    # استخدمت related_name الصحيح daily_plans
    daily_plans = trip.daily_plans.all().order_by('day_number', 'start_time')
    
    # تحقق من trip.date قبل الحساب
    end_date = None
    if trip.date:
        end_date = trip.date + timedelta(days=trip.duration)
    
    # جمع الأنشطة حسب اليوم
    plans_by_day = {}
    for plan in daily_plans:
        day = plan.day_number
        if day not in plans_by_day:
            plans_by_day[day] = []
        plans_by_day[day].append(plan)
    
    grouped_plans = [
        {'day_number': day, 'plans': plans}
        for day, plans in sorted(plans_by_day.items())
    ]


    context = {
        'trip': trip,
        'grouped_plans': grouped_plans,
        'end_date': end_date,
    }
    return render(request, 'explore-card.html', context)
#@login_required
#@require_POST
#@csrf_exempt
#def toggle_favorite_ajax(request):
    """
    Toggle favorite status for a trip via AJAX.
    """
    # try:
        #  data = json.loads(request.body)
        # trip_id = data.get('trip_id')
        # trip = get_object_or_404(Trip, id=trip_id)
        # favorite, created = FavoriteTrip.objects.get_or_create(user=request.user, trip=trip)
        #if not created:
            # favorite.delete()
            # trip.likes_count -= 1
            # action = 'unliked'
            #else:
            #  trip.likes_count += 1
            # action = 'liked'
        # trip.save()
        #return JsonResponse({
            #'status': 'success',
            #'action': action,
            #'likes_count': trip.likes_count
        # })
    #except Exception as e:
        #  return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
@login_required
@require_POST
@csrf_exempt
def toggle_favorite_ajax(request):
    """
    Toggle favorite status for a trip via AJAX, updating likes_count in FavoriteTrip.
    """
    try:
        data = json.loads(request.body)
        trip_id = data.get('trip_id')
        trip = get_object_or_404(Trip, id=trip_id)
        favorite, created = FavoriteTrip.objects.get_or_create(user=request.user, trip=trip)
        
        if not created:
            # If favorite exists, remove it and decrement likes_count
            favorite.delete()
            # Calculate total likes for the trip
            likes_count = FavoriteTrip.objects.filter(trip=trip).count()
            action = 'unliked'

            profile = UserProfile.objects.filter(user=trip.user).first()

            if profile and profile.likes_notifications:
                Notification.objects.create(
                    user=trip.user,
                    message=f"{request.user.username} unliked your trip.",
                    notification_type='like'
                )
        else:
            # If favorite is created, increment likes_count
            favorite.likes_count = FavoriteTrip.objects.filter(trip=trip).count()
            favorite.save()
            likes_count = favorite.likes_count
            action = 'liked'
            profile = UserProfile.objects.filter(user=trip.user).first()

            if profile and profile.likes_notifications:
                Notification.objects.create(
                    user=trip.user,
                    message=f"{request.user.username} liked your trip!",
                    notification_type='like'
                )
        
        return JsonResponse({
            'status': 'success',
            'action': action,
            'likes_count': likes_count
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
@login_required
@require_POST
@csrf_exempt
def toggle_follow_ajax(request):
    """
    Toggle follow status for a user via AJAX.
    """
    try:
        data = json.loads(request.body)
        follow_id = data.get('follow_id')
        follow = get_object_or_404(User, id=follow_id)
        if follow == request.user:
            return JsonResponse({'status': 'error', 'message': 'You cannot follow yourself'}, status=400)
        
        followage, follow_created = Follow.objects.get_or_create(user=request.user, follow=follow)
        profile, created = UserProfile.objects.get_or_create(user=follow)  # Corrected line

        if not follow_created:
            followage.delete()
            action = 'unfollowed'

            if profile.followers_notifications:
                Notification.objects.create(
                    user=follow,
                    message=f"{request.user.username} unfollowed you.",
                    notification_type='follow'
                )
        else:
            action = 'followed'
            if profile.followers_notifications:
                Notification.objects.create(
                    user=follow,
                    message=f"{request.user.username} followed you!",
                    notification_type='follow'
                )
        return JsonResponse({
            'status': 'success',
            'action': action
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)



@csrf_exempt
def settings(request):
    if request.method == "POST":
        name = request.POST.get('name')

        if name == 'notification_setting':
            setting = request.POST.get('setting')  # 'likes_notifications' or 'followers_notifications'
            value = request.POST.get('value') == 'true'  # Because checkbox value will come as string
            # Save the setting (in user profile or wherever you want)
            user = request.user
            
            # Get the user profile
            profile, created = UserProfile.objects.get_or_create(user=user)

            # Based on the setting, update the corresponding notification preference
            if setting == 'likes_notifications':
                profile.likes_notifications = value
            elif setting == 'followers_notifications':
                profile.followers_notifications = value
            
            profile.save()  # Save the updated profile

            return JsonResponse({'status': 'success'})
        else:
            # Get data sent via POST
            avatar = request.FILES.get('avatar')
            username = request.POST.get('username')
            email = request.POST.get('email')
            bio = request.POST.get('bio')
            password = request.POST.get('password')

            user = request.user

            if username:
                user.username = username
            if email:
                user.email = email
            if password:
                user.set_password(password)
            user.save()

            profile, created = UserProfile.objects.get_or_create(user=user)

            if bio:
                profile.bio = bio
            if avatar:
                profile.avatar = avatar
            profile.save()
            login(request, user)


        # Prepare the response data including updated username and avatar
        response_data = {
            'status': 'success',
            'message': 'Your settings have been updated successfully!',
            'new_username': user.username,
            'new_avatar_url': profile.avatar.url if profile.avatar else None,
        }

        return JsonResponse(response_data)

    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    
@csrf_exempt
@login_required
def delete_account(request):
    if request.method == 'DELETE':
        try:
            # Delete the user account
            user = request.user
            user.delete()
            return JsonResponse({'message': 'Account deleted successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)