from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl.registries import registry
from django.contrib.auth import get_user_model
from .models import UserProfile, Category, Trip, Follow, FavoriteTrip
from admin_app.models import UserActivity, HighestUserActivity, FeatureClick

User = get_user_model()

# Indices for each model
profile_index = Index('profiles')
category_index = Index('categories')
trip_index = Index('trips')
follow_index = Index('follows')
like_index = Index('likes')
activity_index = Index('useractivity')
peak_index = Index('peakusage')
feature_index = Index('features')

# Index settings
for index in [profile_index, category_index, trip_index, follow_index, like_index, activity_index, peak_index, feature_index]:
    index.settings(number_of_shards=1, number_of_replicas=0)

@registry.register_document
class ProfileDocument(Document):
    class Django:
        model = UserProfile
        fields = ['gender', 'bio', 'account_active', 'likes_notifications', 'followers_notification',]
    
    user = fields.ObjectField(properties= {
        'username': fields.TextField(),
    })

@registry.register_document
class CategoryDocument(Document):
    class Django:
        model = Category
        fields = ['name', 'color']
    
    user = fields.ObjectField(properties= {
        'username': fields.TextField(),
    })

@registry.register_document
class TripDocument(Document):
    class Django:
        model = Trip
        fields = ['name', 'destination', 'duration', 'date', 'color']

    user = fields.ObjectField(properties= {
        'username': fields.TextField(),
    })

    category = fields.ObjectField(properties={
        'name': fields.TextField(),
    })

@registry.register_document
class FollowDocument(Document):
    class Django:
        model = Follow
        fields = ['created_at']

    user = fields.ObjectField(properties= {
        'username': fields.TextField(),
    })

    follow = fields.ObjectField(properties={
        'username': fields.TextField(),
    })

@registry.register_document
class LikeDocument(Document):
    class Django:
        model = FavoriteTrip
        fields = ['created_at']

    user = fields.ObjectField(properties= {
        'username': fields.TextField(),
    })

    trip = fields.ObjectField(properties={
        'name': fields.TextField(),
    })

@registry.register_document
class UserActivityDocument(Document):
    class Django:
        model = UserActivity
        fields = ['date']

    user = fields.ObjectField(properties= {
        'username': fields.TextField(),
    })

@registry.register_document
class PeakUsageDocument(Document):
    class Django:
        model = HighestUserActivity
        fields = ['count']

@registry.register_document
class FeatureDocument(Document):
    class Django:
        model = FeatureClick
        fields = ['feature_name', 'click_count']