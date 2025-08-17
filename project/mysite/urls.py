from django.urls import path
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView

from . import views

# class CustomLogoutView(LogoutView):
#     http_method_names = ['get', 'post']  # дозволяємо GET

urlpatterns = [
    #basic
    path('login/', views.login_and_register, name='login_register'),
    # path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login_register'), name='logout'),
    
    path("", views.index_page, name = "index"),
    #profile
    path('profile/', views.profile_page, name = 'profile'),
    path('get-user-info/', views.get_user_info, name='user_info'),
    #vocabulary
    path('vocabulary/', views.vocabulary_page, name = 'vocabulary'),
    path('create-list/', views.create_study_list, name ='create_list'),
    path('get-statistics-basic/', views.get_statistics_basic, name='get_statistics_basic'),
    path('get-box-word/', views.get_box_word, name='get_box_word'),
    path('test-word/', views.test_word, name='test_word'),
    #armory
    path('armory/', views.armory_page, name = 'armory'),
    #arena
    path('arena/', views.arena_page, name = 'arena'),    
    
    #pygame
    path("api/word/", views.get_word, name="get_word")    
]

