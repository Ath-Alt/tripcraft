from django.contrib import admin
from .models import UserProfile, MainArea, Category, Trip, DailyPlanner

# admin.site.register(UserProfile)

admin.site.register(UserProfile)
admin.site.register(MainArea)
admin.site.register(Category)
admin.site.register(Trip)
admin.site.register(DailyPlanner)