# app_authentification/urls.py

from django.urls import path
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView

from . import views
from django.urls import path, include

# class CustomLogoutView(LogoutView):
#     http_method_names = ['get', 'post']  # дозволяємо GET

app_name = 'app_authentification'

urlpatterns = [
    path('register/', views.register_user, name='register'),
    
    
    path('login/', views.custom_login_view, name='login'),
]



    