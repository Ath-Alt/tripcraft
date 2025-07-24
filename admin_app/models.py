import random, string
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta

# Models for analytics data (Atheen)
# Create a record whenever a user logs in to keep track of activity
class UserActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    
    # Auto delete activity older than 7 days to avoid DB overload
    def save(self, *args, **kwargs):
        old = timezone.now() - timezone.timedelta(days=7)
        UserActivity.objects.filter(date__lt=old).delete()
        super().save(*args, **kwargs)

        # Count active users today
        today = timezone.now().date()
        count_today = UserActivity.objects.filter(date__date=today).values('user').distinct().count()

        # Compare today's activity to highest record and reassign if need be
        highestActivity, created = HighestUserActivity.objects.get_or_create(pk=1)  # Only one row
        if count_today > highestActivity.count:
            highestActivity.count = count_today
            highestActivity.save()

# Store all-time highest number of active users
class HighestUserActivity(models.Model):
    count = models.PositiveIntegerField(default=0)

# Track how many times each feature is used
class FeatureClick(models.Model):
    feature_name = models.CharField(max_length=100, unique=True)
    click_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.feature_name}: {self.click_count} clicks"

# (SALMA)
class FeatureUsage(models.Model):
    """
    Track the number of clicks for a given feature.
    """
    feature_name = models.CharField(max_length=100, unique=True)
    click_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.feature_name}: {self.click_count} clicks"



class GenderDistribution(models.Model):
    """
    Maintain a singleton record for gender counts.

    This model stores counts for female and male users, updated automatically.
    """
    female_count = models.PositiveIntegerField(default=0)
    male_count = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Gender Distribution (F: {self.female_count}, M: {self.male_count})"

    @classmethod
    def update_counts(cls):
        """
        Update gender counts based on data from UserProfile.
        """
        from user_app.models import UserProfile

        female_count = UserProfile.objects.filter(gender='F').count()
        male_count = UserProfile.objects.filter(gender='M').count()

        obj, created = cls.objects.get_or_create(pk=1)
        obj.female_count = female_count
        obj.male_count = male_count
        obj.save()
        return obj


class EngagementMetrics(models.Model):
    """
    Store engagement metrics as a singleton record.

    Tracks the number of follows, comments, and likes.
    """
    follow_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Engagement Metrics (updated: {self.last_updated.strftime('%Y-%m-%d')})"


class DashboardInsights(models.Model):
    """
    Store dashboard insights as a singleton record.

    Includes highest daily active users, total accounts, most used feature,
    itinerary statistics, and average journey duration.
    """
    highest_active_users = models.PositiveIntegerField(default=0)
    total_accounts = models.PositiveIntegerField(default=0)
    most_used_feature = models.CharField(max_length=100, blank=True)
    total_itineraries = models.PositiveIntegerField(default=0)
    avg_itineraries_per_user = models.FloatField(default=0.0)
    avg_journey_duration = models.PositiveIntegerField(default=0)  # Duration in days
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dashboard Insights (updated: {self.last_updated.strftime('%Y-%m-%d')})"

    @classmethod
    def update_insights(cls):
        """
        Recalculate and update all dashboard insights.
        """
        total_accounts = User.objects.count()
        most_used = FeatureUsage.objects.order_by('-click_count').first()
        most_used_feature = most_used.feature_name if most_used else ""

        # Calculate the highest number of active users in one day.
        from django.db.models import Count
        user_counts = UserActivity.objects.values('date__date').annotate(
            user_count=Count('user', distinct=True)
        ).order_by('-user_count')
        highest_active = user_counts.first()
        highest_active_users = highest_active['user_count'] if highest_active else 0

        # Placeholder values for itineraries and journey duration.
        total_itineraries = 0
        avg_itineraries_per_user = 0.0
        avg_journey_duration = 0

        obj, created = cls.objects.get_or_create(pk=1)
        obj.total_accounts = total_accounts
        obj.most_used_feature = most_used_feature
        obj.highest_active_users = highest_active_users
        obj.total_itineraries = total_itineraries
        obj.avg_itineraries_per_user = avg_itineraries_per_user
        obj.avg_journey_duration = avg_journey_duration
        obj.save()
        return obj


class Traveler(models.Model):
    """
    Extend the default User model with traveler-specific information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    settings = models.JSONField(default=dict)  # Stores preferences such as notifications

    def __str__(self):
        return self.user.username


class Category(models.Model):
    """
    Represent a category to classify trips or POIs.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to='category_icons/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class POI(models.Model):
    """
    Represent a Point of Interest.

    Linked to a Category, includes geolocation and an optional image.
    """
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='points_of_interest')
    description = models.TextField()
    location = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    image = models.ImageField(upload_to='poi_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Point of Interest"
        verbose_name_plural = "Points of Interest"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class Trip(models.Model):
    """
    Represent a travel trip organized by a traveler.

    Contains details such as trip dates, category, collaborators, and points of interest.
    """
    name = models.CharField(max_length=200)
    traveler = models.ForeignKey(Traveler, on_delete=models.CASCADE, related_name='trips')
    start_date = models.DateField()
    end_date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='trips')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    collaborators = models.ManyToManyField(Traveler, related_name='collaborated_trips')
    points_of_interest = models.ManyToManyField(POI, related_name='trips', blank=True)
    location = models.CharField(max_length=200, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} by {self.traveler.user.username}"


class Itinerary(models.Model):
    """
    Represent an itinerary entry for a trip.

    Contains location details and the start/end times for the itinerary segment.
    """
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='itineraries')
    location = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.trip.name} - {self.location}"


class Notification(models.Model):
    """
    Represent a notification for a traveler.

    Can be a system notification or a trip reminder.
    """
    NOTIFICATION_TYPES = [
        ('system', 'System Notification'),
        ('trip', 'Trip Reminder')
    ]

    traveler = models.ForeignKey(Traveler, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    notification_date = models.DateTimeField()
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.traveler.user.username}"


class CalendarSync(models.Model):
    """
    Represent a calendar synchronization record for a traveler.

    Stores sync status, device ID, and calendar data.
    """
    traveler = models.ForeignKey(Traveler, on_delete=models.CASCADE, related_name='calendar_syncs')
    device_id = models.CharField(max_length=200)
    calendar_data = models.JSONField()
    sync_date = models.DateTimeField()
    sync_status = models.CharField(max_length=50)  # e.g., success, failed

    def __str__(self):
        return f"Calendar sync for {self.traveler.user.username}"


class SupportTicket(models.Model):
    """
    Represent a support ticket submitted by a traveler.

    Contains ticket details, status, priority, and an optional assignment to a staff user.
    """
    STATUS_CHOICES = [
        ('new', 'جديد'),
        ('in_progress', 'قيد المعالجة'),
        ('resolved', 'تم الحل'),
        ('closed', 'مغلق')
    ]
    PRIORITY_CHOICES = [
        ('low', 'منخفضة'),
        ('medium', 'متوسطة'),
        ('high', 'عالية'),
        ('urgent', 'عاجلة')
    ]

    traveler = models.ForeignKey(Traveler, on_delete=models.CASCADE, related_name='support_tickets')
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='assigned_tickets')

    def __str__(self):
        return f"Ticket #{self.id} - {self.subject}"


class TicketResponse(models.Model):
    """
    Represent a response to a support ticket.
    """
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='responses')
    responder = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_staff_response = models.BooleanField(default=False)

    def __str__(self):
        return f"Response to ticket #{self.ticket.id}"


class TravelerNote(models.Model):
    """
    Represent an administrative note for a traveler.
    """
    traveler = models.ForeignKey(Traveler, on_delete=models.CASCADE, related_name='admin_notes')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note for {self.traveler.user.username}"


class TravelerVerification(models.Model):
    """
    Represent the verification details for a traveler.

    Includes document uploads and phone verification status.
    """
    VERIFICATION_STATUS = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected')
    ]

    traveler = models.OneToOneField(Traveler, on_delete=models.CASCADE, related_name='verification')
    id_document = models.FileField(upload_to='verification_docs/', null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    is_phone_verified = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Verification for {self.traveler.user.username}"

class PasswordResetCode(models.Model):
    """Model to store password reset verification codes."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"Reset code for {self.user.username} ({self.code})"

    @classmethod
    def generate_code(cls, user):
        """Generate a new verification code for a user."""
        # Delete any previous unused codes
        cls.objects.filter(user=user, is_used=False).delete()

        # Generate a new 6-digit numeric code
        verification_code = ''.join(random.choice(string.digits) for _ in range(6))

        # Save the new code to the database
        reset_code = cls.objects.create(
            user=user,
            code=verification_code
        )

        return reset_code

    def is_valid(self):
        """Check if the code is still valid (not used and not expired)."""
        # Check if the code has already been used
        if self.is_used:
            return False

        # Check if the code has expired (valid for 30 minutes)
        expiration_time = self.created_at + timedelta(minutes=30)
        if timezone.now() > expiration_time:
            return False

        return True
