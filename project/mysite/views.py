from django.shortcuts import render
from mysite.models import Word, User, UserWordsProgress
from django.http import JsonResponse

from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

# Create your views here.


# ============================================> DEFINE FUNCTIONS <=====================================================
def index_page(request):
    return render(request, 'index.html', context = {'page_name': 'INDEX'})

def room_page(request):
    return render(request, 'room.html', context = {'page_name': 'ROOM',})

def vocabulary_page(request):
    return render(request, 'vocabulary.html', context = {'page_name': 'VOCABULARY',})


def armory_page(request):
    return render(request, 'armory.html', context = {'page_name': 'ARMORY'})

def arena_page(request):
    return render(request, 'arena.html', context = {'page_name': 'ARENA',})

@require_POST
@login_required
def create_study_list(request):
    user = request.user

    # Отримати всі id слів, які вже в процесі вивчення
    in_process_word_ids = list(UserWordsProgress.objects.filter(
        user=user,
        status__in=[
            'PROCESS',
            'BOX_1',
            'BOX_2',
            'BOX_3',
            'LEARNT'
        ]
    ).values_list('word__id', flat=True))

    # print(in_process_word_ids)

    # Оновити статус PROCESS → BOX_1
    UserWordsProgress.objects.filter(
        user=user,
        word__id__in = in_process_word_ids,
        status='PROCESS'
    ).update(status='BOX_1')

    # Вибрати до 20 нових слів, яких ще немає в in_process_word_ids
    study_list = Word.objects.exclude(id__in=in_process_word_ids)[:20]

    words_list = []
    for word in study_list:
        UserWordsProgress.objects.create(
            user=user,
            word=word,
            status='PROCESS'
        )
        words_list.append({
            'article': word.article,
            'eng': word.eng,
            'ukr': word.ukr,
        })

    return JsonResponse({'words': words_list})






# for item in create_study_list():
#     print(item)
