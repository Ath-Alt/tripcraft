from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

# app_name = "admin_app"

urlpatterns = [

    # Category management routes
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/create/form', views.category_create_form, name='category_create_form'),
    path('categories/<int:pk>/', views.category_detail, name='category_detail'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),

    # Point of Interest (POI) routes
    path('poi/', views.poi_list, name='poi_list'),
    path('poi/create/', views.poi_create, name='poi_create'),
    path('poi/<int:pk>/', views.poi_detail, name='poi_detail'),
    path('poi/<int:pk>/edit/', views.poi_edit, name='poi_edit'),

    # Dashboard and analytics routes
    path('dashboard/', views.category_list, name='dashboard'),
    path('dashboard/', views.category_list, name='admin_dashboard'),
    path('analytics/', views.analytics, name='analytics'),


    path('poi/<int:pk>/delete/', views.poi_delete, name='poi_delete'),

    # User monitoring and management routes
    path('monitor/', views.monitor, name='monitor'),
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),

    # Traveler management routes
    path('travelers/', views.traveler_list, name='traveler_list'),
    path('travelers/<int:pk>/', views.traveler_detail, name='traveler_detail'),

    # Support ticket routes
    path('support/', views.support_ticket_list, name='support_ticket_list'),
    path('support/<int:pk>/', views.support_ticket_detail, name='support_ticket_detail'),

    # Notification routes for admin and users
    path('user/notifications/', views.notification_list, name='notification_list'),
    path('user/notifications/create/', views.notification_create, name='notification_create'),
    path('user/notifications/<int:pk>/delete/', views.notification_delete, name='notification_delete'),
    path('notifications/', views.user_notifications, name='user_notifications'),
    path('notifications/<int:pk>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('api/notifications/unread-count/', views.unread_notifications_count, name='unread_notifications_count'),

    # path('admin_app/', include('admin_app.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
