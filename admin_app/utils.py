from datetime import timedelta
from .models import UserActivity
from django.utils import timezone
from django.db.models import Count
from django.contrib.auth.models import User
from user_app.models import UserProfile, Trip, FavoriteTrip, Follow
from .models import FeatureClick
from django.db.models import F

# Retrieve user activity over the past 7 days (Atheen)
def get_user_activity():
    today = timezone.now().date()
    dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
    activity = {date: 0 for date in dates}

    # Query DB for user activity
    user_activity = (
        UserActivity.objects
        .filter(date__date__gte=dates[0])
        .values('date__date')
        .annotate(count=Count('user', distinct=True))
    )
    # Return a list of dates and another of counts
    for entry in user_activity:
        activity[entry['date__date']] = entry['count']
    return list(activity.keys()), list(activity.values())

# Get data about a specific user using the username (ATHEEN)
def get_user_data(username):
    user = User.objects.get(username=username)
    profile = UserProfile.objects.filter(user=user).first()
    trips = Trip.objects.filter(user=user).values("id", "name", "destination", "date")
    likes = FavoriteTrip.objects.filter(user=user).select_related("trip")
    followers = Follow.objects.filter(follow=user).select_related("user")
    following = Follow.objects.filter(user=user).select_related("follow")

    # Create a dictionary of user info
    user_data = {
        "username": user.username,
        "email": user.email,
        "is_staff": user.is_staff,
        "account_status": profile.account_active if profile else "Unknown",
        "creation_date": user.date_joined.strftime("%Y-%m-%d"),
        "last_active_date": user.last_login.strftime("%Y-%m-%d"),
        "trip_amount": trips.count(),
        "trips": list(trips),
        "likes": [{"id": like.id, "trip_name": like.trip.name, "creator": like.trip.user.username} for like in likes],
        "likes_amount": FavoriteTrip.objects.filter(trip__user=user).count(),
        "followers": [{"id": f.id, "follower": f.user.username} for f in followers],
        "followers_amount": followers.count(),
        "following": [{"id": f.id, "following": f.follow.username} for f in following],
        "following_amount": following.count(),
        "pfp": profile.avatar.name if profile and profile.avatar else None,
    }
    return user_data

# Track how many times a feature is used (ATHEEN)
def feature_click(feature_name):
    feature, created = FeatureClick.objects.get_or_create(feature_name=feature_name)
    feature.click_count = F('click_count') + 1
    feature.save()
    feature.refresh_from_db()