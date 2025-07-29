# urls.py
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from . import views
from .views import password_reset, verify_reset_code, set_new_password

# Add page paths here (Atheen)
urlpatterns = [
    path('admin/', admin.site.urls),
    path ('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    # path('admin_app/', include('admin_app.urls')),
    path('admin_app/', include(('admin_app.urls','admin_app')),name='admin_app'),

    path('user_app/', include('user_app.urls')),
    #path('', include('user_app.urls', namespace='user_root')),
    path('password_reset/', password_reset, name='password_reset'),
    path('verify_reset_code/', verify_reset_code, name='verify_reset_code'),
    path('set_new_password/', set_new_password, name='set_new_password'),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # [Az] to handle media