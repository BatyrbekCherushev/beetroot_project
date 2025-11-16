from django.urls import path
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView

from . import views

# class CustomLogoutView(LogoutView):
#     http_method_names = ['get', 'post']  # дозволяємо GET

app_name = 'app_site'

urlpatterns = [
    # common
    path('get-statistics/', views.get_statistics, name='get_statistics'),
    path('get-settings/', views.get_settings, name='get_settings'),
    path('get-study-list/', views.get_study_list, name='get_study_list'),
    path('get-categories/', views.get_categories, name = 'get_categories'),
    path('create-study-list/', views.create_study_list, name ='create_list'),
    path('clear-study-list/', views.clear_study_list, name = 'clear_study_list'),
    path('get-box-word/', views.get_box_word, name='get_box_word'),
    path('test-word/', views.test_word, name='test_word'),
    path('clean-box/', views.clean_box, name="clean_box"),
    path('get-study-test-case/', views.get_study_test_case, name="get_study_test_case"),

    # #basic authentification
    # path('login/', views.login_user, name='login'),
    # path('logout/', LogoutView.as_view(next_page='app_site:login'), name='logout'),
    
    #index
    path("", views.profile_page, name = 'profile'),

    #vocabulary
    path('vocabulary/', views.vocabulary_page, name = 'vocabulary'),
    path('get-custom-words/', views.get_custom_words, name="get_custom_words"),
    path('add-word/', views.add_custom_word, name="add_custom_word"),
    path('modify-word/', views.modify_custom_word, name="modify_custom_word"),
    path('export-words/', views.export_user_words, name='export_words'),

    #library
    path('library/', views.library_page, name = 'library'),
    
    #profile
    path('profile/', views.profile_page, name = 'profile'),
    path('get-user-info/', views.get_user_info, name='user_info'),
    path('profile/change-settings/', views.change_settings, name='change-settings'),

    #armory
    path('armory/', views.armory_page, name = 'armory'),
    
    #arena
    path('arena/', views.arena_page, name = 'arena'),   
    path('find-pvp-battle/', views.find_pvp_battle, name='find_battle'),
    path('close-battles/', views.close_battles, name='close_battles'),
    path('fight-pvp/', views.fight_pvp, name='fight_action'),
    
    #pygame
    path("api/word/", views.minigame_get_word, name="get_word")    
]

