from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')])
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    account_active = models.BooleanField(default=True)
    likes_notifications = models.BooleanField(default=True)  # Whether the user wants likes notifications
    followers_notifications = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

#==============================
# [Az] Category Model
# Main area
class MainArea(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='main_area')

    def __str__(self):
        return f"{self.user.username}'s Main Area"
# Categorys
class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=25)
    img = models.ImageField(upload_to='images/uplodes/cat', null=True, blank=True)
    color = models.CharField(max_length=7)
    def __str__(self):
        return f"{self.user.username}'s {self.name}"

# [Az] Trip Model
class Trip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_trips', default=1)  # Creator

    name = models.CharField(max_length=25)
    destination = models.CharField(max_length=15)
    duration = models.IntegerField(default=1) # [Az] Day number 
    date = models.DateField(null=True, blank=True)
    color = models.CharField(max_length=7)
    img = models.ImageField(upload_to='images/uplodes/trip', null=True, blank=True)
    
    main_area = models.ForeignKey(MainArea, on_delete=models.CASCADE, null=True, blank=True, related_name='trips')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True, related_name='trips')

    # collaborators = models.ManyToManyField(User, related_name='collaborated_trips', blank=True)
    # [Az] to make sure no conflect between users and where they save there trips.
    def clean(self):
        if not self.main_area and not self.category:
            raise ValidationError("Trip must belong to either a main area or a category.")
        if self.main_area and self.category:
            raise ValidationError("Trip cannot belong to both a main area and a category.")
        if self.main_area and self.main_area.user != self.user:
            raise ValidationError("Trip user must match the user of the linked MainArea.")
        if self.category and self.category.user != self.user:
            raise ValidationError("Trip user must match the user of the linked Category.")

    def __str__(self):
        return self.name

# [Az] Daily Planner Model
class DailyPlanner(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='daily_plans')
    name = models.CharField(max_length=255)
    day_number = models.IntegerField()  # [Az] Day number (e.g., 1 for Day 1, etc.)
    location = models.CharField(max_length=255, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    description = models.TextField(null=True, blank=True)
    def __str__(self):
        return f"{self.name} for {self.trip.name} ({self.start_time} - {self.end_time})"
#==============================
#[Lyan]
# [Layan] Following Model
class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    follow = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'follow')  # Cannot duplicate the same relationship

    def __str__(self):
        return f"{self.user.username} -> {self.follow.username}"

# [Layan] Notifications Model
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=10, choices=[('like', 'Like'), ('follow', 'Follow')])
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"
    
class FavoriteTrip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
# wafa's explore
likes_count = models.IntegerField(default=0)  # To store the number of likes for each trip
class Meta:
        unique_together = ('user', 'trip')  # منع التكرار في المفضلات

def _str_(self):
        return f"{self.user.username} - {self.trip.name}"
#==============================