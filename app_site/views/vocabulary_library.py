import json
from django.shortcuts import render
from app_site.models import UserCustomWord, Word, WordDeutch, UserWordsProgress, UserWordsDeutchProgress, User, UserSettings, WordCategory, WordSubcategory, PlayerProfile, Battle, BossProfile, Skill, PlayerSkill, BossSkill

from django.http import JsonResponse

from django.utils.timezone import now

from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from ..models import UserSettings, get_default_category, get_default_subcategory
from django.db.models import F

from datetime import timedelta

from .utils import *

# FOR EXPORT USER WORDS IN FILE
from ..resources import UserCustomWordResource
from django.http import HttpResponse
from import_export.formats import base_formats

#=========================================================================================== VOCABULARY PAGE ========================================================================================================================
def serialize_custom_word(word): # utilit
    return {
        'id': word.id,
        'status': word.status, 
        'article': word.article,
        'word': word.word,
        'language': word.language,
        'transcription': word.transcription,
        'translation_options': word.translation_options,
        'translation': word.translation,
        'synonims': word.synonims,
        'word_type': word.word_type,
        'word_level': word.word_level,
        'word_category': word.category.id,
        'word_subcategory': word.sub_category.id,
        'word_link': word.link,
        'comment': word.comment}

@login_required
def vocabulary_page(request):
    return render(request, 'app_site/vocabulary.html', context = {
        'app_name': 'app_site',
        'page_name': 'vocabulary',
                                                         'user_info': get_all_info(request.user),
                                                        #  'custom_categories_all': get_custom_categories(request.user),
                                                         })

@login_required
def get_custom_words(request):
    filters = {}
    
    word_level = request.GET.get('word_level')
    word_type = request.GET.get('word_type')
    word = request.GET.get('word')
    language = request.GET.get('language')
    translation = request.GET.get('translation')
    category = request.GET.get('category')
    sub_category = request.GET.get("sub_category", "")

    if word_level:
        filters['word_level'] = word_level
    if word_type:
        filters['word_type'] = word_type
    if word:
        filters['word'] = word  # пошук по слову частково
    if language:
        filters['language'] = language
    if translation:
        filters['translation'] = translation
    if not(category in (None, '', 'RANDOM')):
        filters['category'] = int(category)
    if not(sub_category in (None, '', 'RANDOM')):
        filters['sub_category'] = int(sub_category)


    # тільки для поточного користувача
    searched_words = UserCustomWord.objects.filter(user=request.user, **filters)

    words_list = [serialize_custom_word(word) for word in searched_words]
    
    if len(words_list) == 0 :
        return JsonResponse({"status": "error", "message": "Співпадінь не знайдено"})

    return JsonResponse({'status': 'ok', 'words': words_list})

@require_POST
@login_required
def add_custom_word(request):
    try:
        data = json.loads(request.body)  # <-- тут зчитуємо JSON
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Некоректний формат JSON"}, status=400)

    user = request.user
    language = data.get("language")
    if not language:
        return JsonResponse({"status": "error", "message": "Поле 'language' обов'язкове"}, status=400)
    word = data.get("word")
    if not word:
        return JsonResponse({"status": "error", "message": "Поле 'word' обов'язкове"}, status=400)
    word_level = data.get("word_level", "")
    word_type = data.get("word_type", "")
    article = data.get("article", "")
    transcription = data.get("transcription", "")
    translation = data.get("translation", "")
    translation_options = data.get("translation_options", "")
    synonims = data.get("synonims", "NO SYNONIM FOR THIS WORD")
    comment = data.get("comment", "")
    
    category = data.get("category", "")
    if category in (None, '', 'RANDOM'):
        category = get_default_category()
    sub_category = data.get("sub_category", "")
    if sub_category in (None, '', 'RANDOM'):
        sub_category = get_default_subcategory()
    
    

    exists = UserCustomWord.objects.filter(user=user, language=language, word=word, word_type = word_type).exists()
    if exists:
        return JsonResponse({"status": "error", "message": "Слово вже існує"}, status=400)

    UserCustomWord.objects.create(
        user=user,
        language=language,
        word_level=word_level,
        word_type=word_type,
        article=article,
        word=word,
        transcription=transcription,
        translation=translation,
        translation_options=translation_options,
        category=WordCategory.objects.get(id=int(category)),
        sub_category=WordSubcategory.objects.get(id=int(sub_category)),
        synonims=synonims,
        comment=comment,
        status="NEW",
        status_changed_date=now()
    )

    return JsonResponse({"status": "success", "message": "Слово додано"})

@require_POST
@login_required
def modify_custom_word(request):
    user = request.user
    try:
        data = json.loads(request.body)  # <-- тут зчитуємо JSON
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Некоректний формат JSON"}, status=400)
    word_ID = data.get('word_ID')
    language = data.get("language")
    word = data.get("word")
    word_level = data.get("word_level", "")
    word_type = data.get("word_type", "")
    article = data.get("article", "")
    transcription = data.get("transcription", "")
    translation = data.get("translation", "")
    translation_options = data.get("translation_options", "")
    category = data.get("category", "")
    sub_category = data.get("sub_category", "")
    synonims = data.get("synonims", "NO SYNONIM FOR THIS WORD")
    comment = data.get("comment", "")

    if not language:
        return JsonResponse({"status": "error", "message": "Поле 'language' обов'язкове"}, status=400)
    if not word:
        return JsonResponse({"status": "error", "message": "Поле 'word' обов'язкове"}, status=400)
    
    if category in (None, '', 'RANDOM'):
        category = WordCategory.objects.get(id=get_default_category())

    if sub_category in (None, '', 'RANDOM'):
        sub_category = WordSubcategory.objects.get(id=get_default_subcategory())
    
    UserCustomWord.objects.filter(user=user, id=word_ID).update(
        language=language,
        word_level=word_level,
        word_type=word_type,
        article=article,
        word=word,
        transcription=transcription,
        translation=translation,
        translation_options=translation_options,
        category=category,
        sub_category=sub_category,
        synonims=synonims,
        comment=comment,
        status_changed_date=now()
    )

    return JsonResponse({"status": "success", "message": "Слово оновлено!!!"})

# --------------------------------------------------------------------- EXPORT USER WORDS

@login_required
def export_user_words(request):
    from datetime import datetime

    resource = UserCustomWordResource()
    instance_language = request.GET.get('instance_language')
    queryset = UserCustomWord.objects.filter(user=request.user)

    if instance_language:
        queryset = queryset.filter(language = instance_language)

    dataset = resource.export(queryset)

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    file_name = f"my_words_{instance_language}_{timestamp}.xlsx"

    response = HttpResponse(
        dataset.xlsx,
        content_type=base_formats.XLSX.CONTENT_TYPE
    )
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response

#=========================================================================================== LIBRARY PAGE ========================================================================================================================
@login_required
def library_page(request):
    return render(request, 'app_site/library.html', context = {
        'app_name': 'app_site',
        'page_name': 'library',
                                                         'user_info': get_all_info(request.user),
                                                         })
@login_required
def get_categories(request):
       
    return JsonResponse(get_categories_info())




# TESTING FOR PYGAME ==============================================================================================
import random

WORDS = [
    {"eng": "apple", "translation": "яблуко"},
    {"eng": "car", "translation": "автомобіль"},
    {"eng": "house", "translation": "будинок"},
]

def minigame_get_word(request):
    word = random.choice(WORDS)
    return JsonResponse(word)
#================================================================================================ COMMON ===================================================================================================

@require_POST
@login_required
def create_study_list(request):
     
    user = request.user
    data = json.loads(request.body)
    instance_type = data['instance_type']
        
    if instance_type not in INSTANCES_MAP:
        return JsonResponse({'error': 'Invalid instance_type'}, status=400)
    
    instance_language = data['instance_language']
    if instance_language not in INSTANCES_MAP[instance_type]:
        return JsonResponse({'error': 'Invalid instance_language'}, status=400)

    print(f'-------------CREATING STUDY LIST. instance = {instance_type}, language = {instance_language}', data)
    
    words_list = []
    server_answer = ''

    # GETIING current study list query
    if instance_type == 'custom':
        current_words_list_query = get_current_study_list_custom(user, instance_language)
    elif instance_type == 'basic':
        current_words_list_query = get_current_study_list_basic(user, instance_type, instance_language)

    if len(current_words_list_query) > 0:
            for word in current_words_list_query:
                words_list.append(serialize_word(word))

    # ADDING new words to current study list
    if instance_type == 'custom':
        new_words_list = create_custom_study_list(user, data)        
                
    elif instance_type == 'basic':
        new_words_list = create_basic_study_list(user, data)

    if len( new_words_list) > 0:
        words_list.extend(new_words_list)            
        server_answer = f'There were found {len(new_words_list)} words by your filter conditions!'
    else:
        server_answer = 'No words found for you filter!'        

    if len(words_list) > 0:
        return JsonResponse({'words': words_list,
                             'message': server_answer
                            })
    else:
        return JsonResponse({'error':'There are no more words to create study list.',
                             'code': 'NO_MORE_WORDS'}, status = 404)

def get_current_study_list_basic(user, instance_type, instance_language):
    statuses_model = INSTANCES_MAP[instance_type][instance_language]['statuses']
    words_model = INSTANCES_MAP[instance_type][instance_language]['words']
    in_process_word_ids = list(statuses_model.objects.filter(
        user=user,
        status__in=[
            
            'PROCESS',
        ]
    ).values_list('word__id', flat=True))
    
    words = words_model.objects.filter(id__in=in_process_word_ids)
    return words

def get_current_study_list_custom(user, instance_language):
    custom_words = UserCustomWord.objects.filter(
            user=user,
            language=instance_language,
            status='PROCESS'
        )
    return custom_words

@login_required
def get_study_list(request):
    user = request.user
    instance_type = request.GET.get('instance_type')
    instance_language = request.GET.get('instance_language')
    
    words_list = []
    if (instance_type == 'basic'):
        
        
        for word in get_current_study_list_basic(user, instance_type, instance_language):
            words_list.append(serialize_word(word))

        list_create_date = INSTANCES_MAP[instance_type][instance_language]['statuses'].objects.filter(user=user, status='PROCESS').values_list('status_changed_date', flat=True).first()
    else:
        custom_words = get_current_study_list_custom(user, instance_language)

        words_list = [serialize_word(word) for word in custom_words]

        list_create_date = (custom_words.first().status_changed_date   if custom_words.exists()    else None)
    
    return JsonResponse({'words': words_list,
                         'create_date': list_create_date
                         })

@require_POST
@login_required
def clear_study_list(request):
    user = request.user
    data = json.loads(request.body)

    instance_type = data['instance_type']
    if instance_type not in INSTANCES_MAP:
        return JsonResponse({'error': 'Invalid instance_type'}, status=400)
    
    instance_language = data['instance_language']
    if instance_language not in INSTANCES_MAP[instance_type]:
        return JsonResponse({'error': 'Invalid instance_language'}, status=400)

    print(f'-------------> CLEARING STUDY LIST. instance = {instance_type}, language = {instance_language}', data)
    instance_statistics = get_statistics_info(user)[instance_type][instance_language] 
    print(instance_statistics)
    box_1_words = instance_statistics['BOX_1']
    box_1_max = instance_statistics['BOX_1_LIMIT']
    free_places = max(box_1_max - box_1_words, 0)
    print(instance_type, instance_language, free_places)

    if free_places <= 0:
        return JsonResponse({'error': 'No free places in BOX_1'}, status=400)

    if instance_type == 'custom':
        qs = UserCustomWord.objects.filter(user=user, language=instance_language, status='PROCESS')[:free_places]
        ids = qs.values_list('id', flat=True)
        UserCustomWord.objects.filter(id__in=ids).update(status='BOX_1')
    elif instance_type == 'basic':
        # MODELS
        statuses_model = INSTANCES_MAP[instance_type][instance_language]['statuses']
        
        # Оновити статус PROCESS → BOX_1
        qs = statuses_model.objects.filter(user=user, status='PROCESS')[:free_places]
        ids = qs.values_list('id', flat=True)
        statuses_model.objects.filter(id__in=ids).update(status='BOX_1')

    words_list = []
    if (instance_type == 'basic'):
        for word in get_current_study_list_basic(user, instance_type, instance_language):
            words_list.append(serialize_word(word))

        list_create_date = INSTANCES_MAP[instance_type][instance_language]['statuses'].objects.filter(user=user, status='PROCESS').values_list('status_changed_date', flat=True).first()
    else:
        custom_words = get_current_study_list_custom(user, instance_language)

        words_list = [serialize_word(word) for word in custom_words]

        list_create_date = (custom_words.first().status_changed_date   if custom_words.exists()    else None)

    if len(words_list) > 0:
        return JsonResponse({'status': 'ok',
                                'words': words_list,
                                'is_clear': False,
                                'message': f'There was not enogh place in BOX_1, so {len(words_list)} worrds have left in study_list'})
    
    
    return JsonResponse({'status': 'ok',
                         'is_clear': True})

# ------------------------------------------------------------------------------------- VOCABULARY / LIBRARY STUDY LIST WORDS TESTING

def get_test_case_custom_instance(request):
    instance_language = request.GET.get('instance_language')

    already_tested_ids_cookie = request.COOKIES.get(f'custom_{instance_language}_tested_ids')

    if already_tested_ids_cookie:
        try:
            already_tested_ids = json.loads(already_tested_ids_cookie)
        except json.JSONDecodeError:
            already_tested_ids = []
    else:
        already_tested_ids = []
    print(already_tested_ids)

    words_in_process_qs = UserCustomWord.objects.filter(
        user=request.user,
        language=instance_language,
        status='PROCESS'
    ).exclude(id__in=already_tested_ids)

    # IF THERE ARE NO WORDS
    if not words_in_process_qs.exists():
        response = JsonResponse({'error': 'Не лишилось непротестованих слів. Натисніть повторно, щоб почати знову.'}, status=404)
        response.delete_cookie(f'custom_{instance_language}_tested_ids')
        return response
    
    random_word_object_in_process = random.choice(list(words_in_process_qs))

    already_tested_ids.append(random_word_object_in_process.id)


    #choose randomly 4 answer options
    correct_answer = random_word_object_in_process.translation  # або будь-яке поле
    all_words = list(UserCustomWord.objects.filter(
        user=request.user, 
        language=instance_language).exclude(id=random_word_object_in_process.id))

    wrong_answers = random.sample(all_words, min(3, len(all_words)))
    wrong_answers = [w.translation for w in wrong_answers]

    # змішуємо всі варіанти
    answer_options = wrong_answers + [correct_answer]
    random.shuffle(answer_options)
    
    response = JsonResponse({
        'word': random_word_object_in_process.article + ' ' + random_word_object_in_process.word,
        'correct_answer': correct_answer,
        'answer_options': answer_options
    })

    response.set_cookie(
        key=f'custom_{instance_language}_tested_ids',
        value=json.dumps(already_tested_ids),
        max_age=3600,       # час життя (секунди) — тут 1 година
        samesite='Lax',
        httponly=False      # False, бо ми можемо читати cookie з JS, якщо потрібно
    )
    return response

    

def get_test_case_basic_instance(request):
    
    instance_language = request.GET.get('instance_language')
    print('Instance language: ', instance_language)
    
    already_tested_ids_cookie = request.COOKIES.get(f'basic_{instance_language}_tested_ids')

    if already_tested_ids_cookie:
        try:
            already_tested_ids = json.loads(already_tested_ids_cookie)
        except json.JSONDecodeError:
            already_tested_ids = []
    else:
        already_tested_ids = []
    
    print(already_tested_ids)

    if instance_language == 'EN':
        words_in_process_qs =  UserWordsProgress.objects.filter(
            user=request.user,
            status='PROCESS'
        ).exclude(word__id__in=already_tested_ids).select_related('word')
    elif instance_language == 'DE':
        words_in_process_qs = UserWordsDeutchProgress.objects.filter(
            user=request.user,
            status='PROCESS'
        ).exclude(word__id__in=already_tested_ids).select_related('word')

    
    
    if not words_in_process_qs.exists():
        response = JsonResponse({'error': 'Не лишилось непротестованих слів. Натисніть повторно, щоб почати знову.'}, status=404)
        response.delete_cookie(f'basic_{instance_language}_tested_ids')
        return response
    
    random_word_object_in_process = random.choice(list(words_in_process_qs)).word

    already_tested_ids.append(random_word_object_in_process.id)


    #choose randomly 4 answer options
    correct_answer = random_word_object_in_process.translation  # або будь-яке поле

    if instance_language == 'EN':
        all_words = list(Word.objects.exclude(id=random_word_object_in_process.id))
    elif instance_language == 'DE':
        all_words = list(WordDeutch.objects.exclude(id=random_word_object_in_process.id))

    wrong_answers = random.sample(all_words, min(3, len(all_words)))
    wrong_answers = [w.translation for w in wrong_answers]

    # змішуємо всі варіанти
    answer_options = wrong_answers + [correct_answer]
    random.shuffle(answer_options)
    
    response = JsonResponse({
        'word': random_word_object_in_process.article + ' ' +random_word_object_in_process.word,
        'correct_answer': correct_answer,
        'answer_options': answer_options
    })

    response.set_cookie(
        key=f'basic_{instance_language}_tested_ids',
        value=json.dumps(already_tested_ids),
        max_age=3600,       # час життя (секунди) — тут 1 година
        samesite='Lax',
        httponly=False      # False, бо ми можемо читати cookie з JS, якщо потрібно
    )
    return response

def get_study_test_case(request):
    instance_type = request.GET.get('instance_type')
    print(instance_type)
    
    if instance_type == 'basic':
        return get_test_case_basic_instance(request)
    elif instance_type == 'custom':
        return get_test_case_custom_instance(request)

   
    return JsonResponse({'error': 'Unknown instance type'}, status=400)

#-------------------------------------------------------------------------------------- VOCABULARY, LIBRARY -> words TESTING
def get_box_word(request):
    """
    Повертає одне слово для тестування в залежності від переданого бокса.
    Очікує GET-параметр 'box' з назвою бокса, наприклад: BOX_1, BOX_2, BOX_3, LEARNT
    """
    user = request.user
    box = request.GET.get('box')
    instance_type = request.GET.get('instance_type')
    instance_language = request.GET.get('instance_language')
    user_settings = user.settings.dictionaries.get(f'{instance_type}_{instance_language}', {}) 

    today = now().date()


    if not box:
        return JsonResponse({'error': 'Box not specified'}, status=400)
    
    if (instance_type == 'basic'):
        statuses = INSTANCES_MAP[instance_type][instance_language]['statuses']
        # Беремо випадкове слово з цього бокса
        # word_progress = UserWordsProgress.objects.filter(user=user, status=box).exclude(status_changed_date__date=today).order_by('?').first() #стара версія де перевірялось що статус слова помінявся не сьогодні
        #тепер бере слово якщо дата зміни статусу не менше ніж закладено в налаштування користувача
        word_progress = statuses.objects.filter(user=user, status=box, status_changed_date__date__lte=today - timedelta(days=user_settings.get('testing_days_limit',5))).order_by('-is_freezed', '?').first()

        if not word_progress:
            return JsonResponse({'word': None})  # Слова закінчилися
        word = word_progress.word
    
    elif instance_type == 'custom':
        word = UserCustomWord.objects.filter(
            user = user,
            status = box,
            language = instance_language,
            status_changed_date__date__lte=today - timedelta(days=user_settings.get('testing_days_limit', 5))
        ).order_by('-is_freezed', '?').first()
        
    if not word:
        return JsonResponse({'word': None})
    
    return JsonResponse({'word': serialize_word(word)})

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
    instance_type = data.get('instance_type')
    instance_language = data.get('instance_language')

    if not word_id or not answer:
        return JsonResponse({'error': 'Missing data'}, status=400)

    if instance_type == 'basic':
        Status_Model = INSTANCES_MAP['basic'][instance_language]['statuses']
        # Шукаємо слово в базі
        try:
            progress = Status_Model.objects.get(user=user, word_id=word_id)
        except Status_Model.DoesNotExist:
            return JsonResponse({'error': 'Word not found'}, status=404)
        correct_answer = progress.word.translation.strip().lower()
        alternative_answers = [alt.strip() for alt in progress.word.translation_options.strip().lower().split('*')]
    elif instance_type == 'custom':
        try:
            progress = UserCustomWord.objects.get(
                user = user,
                language = instance_language,
                id=word_id           
            )
        except UserCustomWord.DoesNotExist:
            return JsonResponse({'error': 'Word not found'}, status=404)
        correct_answer = progress.translation.strip().lower()
        alternative_answers = [alt.strip() for alt in progress.translation_options.strip().lower().split('*')]
    
    user_answer = answer.strip().lower()

    all_correct_answers = {correct_answer, *alternative_answers}
    is_correct = user_answer in all_correct_answers

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
        if progress.status =='LEARNT':
            progress.is_freezed = False
            if instance_type== 'basic' and not progress.was_learnt_once:
                progress.was_learnt_once = True
                PlayerProfile.objects.filter(user = user).update(currency=F('currency') + 20)

    else:
        if progress.status =='LEARNT':
            progress.is_freezed = False
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

#------------------------------------------------------------------------------------- VOCABULARY, LIBRARY -> CLEAN BOX of words 
@require_POST
@login_required
def clean_box(request):
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    user = request.user
    
    instance_type = data.get('instance_type')
    if instance_type not in INSTANCES_MAP:
        return JsonResponse({'error': 'Invalid instance_type'}, status=400)
    
    instance_language = data.get('instance_language')
    if instance_language not in INSTANCES_MAP[instance_type]:
        return JsonResponse({'error': 'Invalid instance_language'}, status=400)
    
    box_for_clean = data.get('current_box')
    words_number = int(data.get('words_number'))
    
    if (instance_type == 'basic'):

        words_for_clean = INSTANCES_MAP['basic'][f'{instance_language}']['statuses'].objects.filter(
            user = user,
            status = box_for_clean)[:words_number]
        
        
    else:
        words_for_clean = UserCustomWord.objects.filter(
            user = user,
            language = instance_language, 
            status = box_for_clean
        )[:words_number]
    
    for word in words_for_clean:
            word.status_changed_date = now().date()
            word.status = 'REPEAT'
            word.save()
    

    return JsonResponse({'status': 'ok', 'received': data})