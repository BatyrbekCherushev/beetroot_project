from django.urls import path

from . import views

urlpatterns = [
    path("", views.index_page, name = "index"),
    path('room/', views.room_page, name = 'room'),
    path('vocabulary/', views.vocabulary_page, name = 'vocabulary'),
    path('armory/', views.armory_page, name = 'armory'),
    path('arena/', views.arena_page, name = 'arena'),
    path('create-list/', views.create_study_list, name ='create_list')
    
]

