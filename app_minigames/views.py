from django.shortcuts import render

# Create your views here.
import os
from django.conf import settings
from django.http import FileResponse, Http404

def download_game(request):
    file_path = os.path.join(settings.BASE_DIR, 'RES', 'downloads', 'minigames', 'test_study_words_knight.py')

    if not os.path.exists(file_path):
        raise Http404("Файл не знайдено")
    # FileResponse автоматично ставить відповідні заголовки і стрімить файл
    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename='test_study_words_knight.py')