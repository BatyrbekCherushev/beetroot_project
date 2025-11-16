from django.urls import path
from .views import download_game

app_name = 'app_minigames'

urlpatterns = [
    path('download-game/', download_game, name='download_game'),
]