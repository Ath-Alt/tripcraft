from django.contrib import admin
from .models import UserActivity, HighestUserActivity, FeatureClick, FeatureUsage, GenderDistribution, EngagementMetrics, DashboardInsights

# (ATHEEN)
admin.site.register(UserActivity)
admin.site.register(HighestUserActivity)
admin.site.register(FeatureClick)

# (SALMA)
admin.site.register(FeatureUsage)
admin.site.register(GenderDistribution)
admin.site.register(EngagementMetrics)
admin.site.register(DashboardInsights)

