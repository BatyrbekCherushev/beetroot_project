from django.urls import path
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView

from . import views

# class CustomLogoutView(LogoutView):
#     http_method_names = ['get', 'post']  # дозволяємо GET

urlpatterns = [
    #basic authentification
    path('login/', views.login_user, name='login'),
    path('register/', views.register_user, name='register'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    
    #index
    path("", views.index_page, name = "index"),

    #profile
    path('profile/', views.profile_page, name = 'profile'),
    path('get-user-info/', views.get_user_info, name='user_info'),

    #vocabulary
    path('vocabulary/', views.vocabulary_page, name = 'vocabulary'),
    path('create-list/', views.create_study_list, name ='create_list'),
    # path('get-statistics-basic/', views.get_statistics_basic, name='get_statistics_basic'),
    path('get-box-word/', views.get_box_word, name='get_box_word'),
    path('test-word/', views.test_word, name='test_word'),
    
    #armory
    path('armory/', views.armory_page, name = 'armory'),
    
    #arena
    path('arena/', views.arena_page, name = 'arena'),    
    
    #pygame
    path("api/word/", views.get_word, name="get_word")    
]

