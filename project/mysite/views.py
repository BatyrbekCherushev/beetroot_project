import json
from django.shortcuts import render
from mysite.models import Word, User, UserWordsProgress, UserSettings
from django.http import JsonResponse

from django.utils.timezone import now

from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from .models import UserSettings

from datetime import timedelta


# Create your views here.

# ============================================> DEFINE FUNCTIONS <=====================================================
def login_and_register(request):
    login_form = AuthenticationForm()
    register_form = UserCreationForm()

    if request.method == 'POST':
        # Якщо форма реєстрації була надіслана
        if 'register_submit' in request.POST:
            register_form = UserCreationForm(request.POST)
            if register_form.is_valid():
                user = register_form.save()
                # UserSettings створюється автоматично через сигнал post_save
                login(request, user)
                return redirect('index')  # редірект на головну сторінку

        # Якщо форма логіну була надіслана
        elif 'login_submit' in request.POST:
            login_form = AuthenticationForm(data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                return redirect('index')

    context = {
        'login_form': login_form,
        'register_form': register_form
    }
    return render(request, 'login_register.html', context)

@login_required
def index_page(request):
    return render(request, 'index.html', context = {'page_name': 'index'})
@login_required
def profile_page(request):
    return render(request, 'profile.html', context = {'page_name': 'profile',})
@login_required
def vocabulary_page(request):
    return render(request, 'vocabulary.html', context = {'page_name': 'vocabulary',})

@login_required
def armory_page(request):
    return render(request, 'armory.html', context = {'page_name': 'armory'})
@login_required
def arena_page(request):
    return render(request, 'arena.html', context = {'page_name': 'arena',})

@require_POST
@login_required
def create_study_list(request):
     
    user = request.user
    user_settings = UserSettings.objects.get(user=request.user)

    # print("RAW BODY:", request.body)
    # print("HEADERS:", request.headers)
    data = json.loads(request.body)
    

    # GET IDs of all words, that have some status excluding 'NEW' status
    in_process_word_ids = list(UserWordsProgress.objects.filter(
        user=user,
        status__in=[
            'REPEAT',
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
    
    reps_number = data['rep_number']
    reps_number = reps_number if reps_number > 0 else user_settings.rep_words_number
    
    new_number = data['new_number']
    
    if reps_number + new_number < user_settings.min_words_number: 
        new_number = user_settings.min_words_number - reps_number
        
    words_list = []
    # CHOOSE 'REPEAT" words
    rep_words_ids = list(
        UserWordsProgress.objects.filter(user=user, status='REPEAT')
        .order_by('?')
        .values_list('id', flat=True)[:reps_number]
        )
    # Масове оновлення статусу на PROCESS
    UserWordsProgress.objects.filter(id__in=rep_words_ids).update(status='PROCESS')
    # Отримуємо відповідні слова
    rep_words = Word.objects.filter(
        id__in=UserWordsProgress.objects.filter(id__in=rep_words_ids)
        .values_list('word__id', flat=True)
        )

    for word in rep_words:
        words_list.append({
            'article': word.article,
            'eng': word.eng,
            'ukr': word.ukr,
            'synonims': word.synonims, 
        })

    if len(words_list) == 0:
        new_number += reps_number

    # CHOOSE 'NEW' words
    new_words = Word.objects.exclude(id__in=in_process_word_ids)[:new_number ]
    
    
    for word in new_words:
        UserWordsProgress.objects.create(
            user=user,
            word=word,
            status='PROCESS'
        )
        words_list.append({
            'article': word.article,
            'eng': word.eng,
            'ukr': word.ukr,
            'synonims': word.synonims, 
        })

    if len(words_list) > 0:
        return JsonResponse({'words': words_list,
                            })
    else:
        return JsonResponse({'error':'There are no more words to create study list.',
                             'code': 'NO_MORE_WORDS'}, status = 404)


@login_required
def get_box_word(request):
    """
    Повертає одне слово для тестування в залежності від переданого бокса.
    Очікує GET-параметр 'box' з назвою бокса, наприклад: BOX_1, BOX_2, BOX_3, LEARNT
    """
    user = request.user
    box = request.GET.get('box')
    user_settings = user.settings 

    today = now().date()


    if not box:
        return JsonResponse({'error': 'Box not specified'}, status=400)

    # Беремо випадкове слово з цього бокса
    # word_progress = UserWordsProgress.objects.filter(user=user, status=box).exclude(status_changed_date__date=today).order_by('?').first() #стара версія де перевірялось що статус слова помінявся не сьогодні
    #тепер бере слово якщо дата зміни статусу не менше ніж закладено в налаштування користувача
    word_progress = UserWordsProgress.objects.filter(user=user, status=box, status_changed_date__date__lte=today - timedelta(days=user_settings.testing_days_limit)).order_by('?').first()

    

    if not word_progress:
        return JsonResponse({'word': None})  # Слова закінчилися

    word = word_progress.word
    return JsonResponse({
        'word': {
            'id': word.id,
            'eng': word.eng,
            'article': word.article,   # виправлено назву поля
            'synonims': word.synonims,
        }
    })

@require_POST
@login_required
def test_word(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    user = request.user
    # box = request.GET.get('box')
    word_id = data.get('word_id')
    answer = data.get('answer')

    if not word_id or not answer:
        return JsonResponse({'error': 'Missing data'}, status=400)


    # Шукаємо слово в базі
    try:
        progress = UserWordsProgress.objects.get(user=user, word_id=word_id)
    except UserWordsProgress.DoesNotExist:
        return JsonResponse({'error': 'Word not found'}, status=404)
    
    correct_answer = progress.word.ukr.strip().lower()
    user_answer = answer.strip().lower()

    is_correct = user_answer == correct_answer

    # ===== ЛОГІКА ОНОВЛЕННЯ СТАТУСУ =====
    if is_correct:
        progress.repetition_count += 1

        next_status_map = {
            'NEW': 'BOX_1',
            'BOX_1': 'BOX_2',
            'BOX_2': 'BOX_3',
            'BOX_3': 'LEARNT',
            'REPEAT': 'BOX_1',
            'LEARNT': 'LEARNT'
        }

        progress.status = next_status_map.get(progress.status, progress.status)
        if progress.status =='LEARNT' and not progress.was_learnt_once:
            progress.was_learnt_once = True
    else:
        # Скидаємо прогрес, якщо помилка
        progress.status = 'REPEAT'
        progress.repetition_count = 0
    
    progress.status_changed_date = now().date()
    progress.save()

    return JsonResponse({
        'correct': is_correct,
        'correct_answer': correct_answer,
        'new_status': progress.status,
        'repetition_count': progress.repetition_count
    })

@login_required
def get_statistics_basic(request):
    """Counts statistics for basic vocabulary, for every category of word"""
    # from datetime import timedelta

    user = request.user
    user_settings = request.user.settings
    today = now().date()

    count_total_words = Word.objects.count()
    count_repeat_words = UserWordsProgress.objects.filter(user=user, status='REPEAT').count()
    count_process_words = UserWordsProgress.objects.filter(user=user, status='PROCESS').count()
    count_box_1_words = UserWordsProgress.objects.filter(user=user, status='BOX_1').count()
    count_box_2_words = UserWordsProgress.objects.filter(user=user, status='BOX_2').count()
    count_box_3_words = UserWordsProgress.objects.filter(user=user, status='BOX_3').count()
    count_learnt_words = UserWordsProgress.objects.filter(user=user, status='LEARNT').count()
    count_new_words = count_total_words -count_repeat_words - count_process_words - count_box_1_words -count_box_2_words - count_box_3_words - count_learnt_words

    # TEST response
    return JsonResponse({
        'TOTAL': count_total_words,
        'NEW': count_new_words,
        'REPEAT': count_repeat_words,
        'PROCESS': count_process_words,
        'BOX_1': count_box_1_words,
        'BOX_1_usable': UserWordsProgress.objects.filter(user=user, status='BOX_1', status_changed_date__date__lte=today - timedelta(days=user_settings.testing_days_limit)).count(),
        'BOX_2_usable': UserWordsProgress.objects.filter(user=user, status='BOX_2', status_changed_date__date__lte=today - timedelta(days=user_settings.testing_days_limit)).count(),
        'BOX_3_usable': UserWordsProgress.objects.filter(user=user, status='BOX_3', status_changed_date__date__lte=today - timedelta(days=user_settings.testing_days_limit)).count(),
        # 'BOX_2': 200,
        'BOX_2': count_box_2_words,
        'BOX_3': count_box_3_words,
        'LEARNT': count_learnt_words,
        'BOX_1_LIMIT': user_settings.box_1_limit,
        'BOX_2_LIMIT': user_settings.box_2_limit,
        'BOX_3_LIMIT': user_settings.box_3_limit})

# PROFILE =============================================================================================
@login_required
def get_user_info(request):

    user_settings = request.user.settings
    user_profile = request.user.profile
    return JsonResponse({
        'profile':{
            'level': user_profile.level,
            'current_exp': user_profile.current_exp,
            'currency': user_profile.currency,
        },
        'settings':{
                    'user_name': request.user.username, 
                    'new_words_number': user_settings.new_words_number,
                    'rep_words_number': user_settings.rep_words_number,
                    'min_words_number': user_settings.min_words_number, 
                    'BOX_1_limit': user_settings.box_1_limit,
                    'BOX_2_limit':user_settings.box_2_limit,
                    'BOX_3_limit': user_settings.box_3_limit},

            
        
    })
# TESTING ==============================================================================================
import random

WORDS = [
    {"eng": "apple", "ukr": "яблуко"},
    {"eng": "car", "ukr": "автомобіль"},
    {"eng": "house", "ukr": "будинок"},
]

def get_word(request):
    word = random.choice(WORDS)
    return JsonResponse(word)
    









