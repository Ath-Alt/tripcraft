
from django.urls import path
from . import views

app_name = 'user_app'

urlpatterns = [
    # path('', views.user),
# [Az] urls for myTrips display
    #[Az] path for myTrips
    path('myTrips/', views.myTrips, name='myTrips' ),
    # [Az] Path for adding a category
    path('add-category/', views.add_category, name="add_category"),
    # cat edit and delete
    path('edit-category/<int:cat_id>/', views.edit_category, name='edit_category'),
    # path('edit-category/<int:cat_id>/', views.edit_category, name='edit_category'),
    path('confirm-delete/<int:cat_id>/', views.confirm_delete, name='confirm_delete'),
    path('delete-category/<int:cat_id>/', views.delete_category, name='delete_category'),
    # [Az] Path for adding a trip
    path('add_trip_main/<int:main_id>/', views.add_trip_main, name='add_trip_main'),
    path('add_trip_cat/<int:cat_id>/', views.add_trip_cat, name='add_trip_cat'),
    # [Az] edit and delete a trip 
    path('edit_trip/<int:trip_id>/', views.edit_trip, name='edit_trip'),
    path('confirm_del_trip/<int:trip_id>/', views.confirm_del_trip, name='confirm_del_trip'),
    path('delete_trip/<int:trip_id>/', views.delete_trip, name='delete_trip'),
    # [Az] path for monthly view
    path('get_trips_for_calendar/', views.get_trips_for_calendar, name='get_trips_for_calendar'),
    # [Az] path for Daily view
    path('trip/<int:trip_id>/', views.trip_detail_view, name='trip_detail_view'),
    # [Az] path for fetcing the planner data using json
    path('api/daily-events/<int:trip_id>/', views.daily_events_json, name='daily_events_json'),
    # [Az] pth for createing events 
    path('api/create-event/<int:trip_id>/', views.create_event, name='create_event'),
    # [Az] path for updating time, editing event and deleteing event 
    path('api/update-event-time/<int:event_id>/', views.update_event_time, name='update_event_time'),
    path('api/edit-event/<int:event_id>/', views.edit_event, name='edit_event'),
    path('api/delete-event/<int:event_id>/', views.delete_event, name='delete_event'),
# myTrips urls end 

#[Lyan]
# [Lyan] Profile page (root URL for displaying trip cards, avatar, username, bio, following, and notifications)
    path('profile/', views.profile, name='profile'),
    # [Lyan] Settings page for updating avatar, username, and bio
    path('settings/', views.settings, name='settings'),
    # [Lyan] Favorites page for displaying favorite trips
    path('favorites/', views.favorites, name='favorites'),
    # [Lyan] Toggle favorite status for a trip
    path('toggle_favorite/<int:trip_id>/', views.toggle_favorite, name='toggle_favorite'),
    # [Lyan] Add a follow
    path('add_follow/', views.add_follow, name='add_follow'),
    # [Lyan] Delete a follow
    path('delete_follow/<int:follow_id>/', views.delete_follow, name='delete_follow'),
    # [Lyan] Mark a notification as read
    path('mark_notification_as_read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
# End of profile & favoret
    path('favorites/', views.favorites, name='favorites'),



    # wafa
    # URLs for Explore pages
    path('explore/', views.explore_view, name='explore'),
    path('following-explore/', views.following_explore_view, name='following_explore'),
    path('explore-card/<int:trip_id>/', views.explore_card_view, name='explore_card'),
    path('toggle-favorite/', views.toggle_favorite_ajax, name='toggle_favorite_ajax'),
    path('toggle-follow/', views.toggle_follow_ajax, name='toggle_follow_ajax'),

    path('settings/', views.settings, name='settings'),
    path('api/delete-account', views.delete_account, name='delete_account'),
]