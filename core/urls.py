from django.contrib import admin
from django.urls import path, include
from auth_app.api import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/registration/', auth_views.register_view, name='registration'),
    path('api/login/', auth_views.login_view, name='login'),
    path('api/email-check/', auth_views.check_email_view, name='email-check'),

    
    path('', include('boards_app.api.urls')),
]