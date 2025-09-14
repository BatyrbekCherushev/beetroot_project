import json
from django.shortcuts import render
from mysite.models import UserCustomWord, Word, WordDeutch, UserWordsProgress, UserWordsDeutchProgress, User, UserSettings, WordCategory, WordSubcategory

from django.http import JsonResponse

from django.utils.timezone import now

from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from .models import UserSettings, get_default_category, get_default_subcategory

from datetime import timedelta


# Create your views here.
INSTANCES_MAP = {
    'basic':{
        'EN': {
            'words': Word,
            'statuses': UserWordsProgress
        },
        'DE': {
            'words': WordDeutch,
            'statuses': UserWordsDeutchProgress
        },
        # 'FR': {
        #     # 'words': WordFrench,
        #     # 'statuses': UserWordsFrenchProgress
        # },
        # 'ES': {
        #     # 'words': WordSpanish,
        #     # 'statuses': UserWordsSpanishProgress
        # }
    },
    'custom': [
        'EN', 'DE', 
        # 'FR', 'ES'
    ]}

#======================================================================================================= UTILS ============================================================================
def get_settings_info(user):
    user_settings = user.settings.dictionaries
    langs = ['EN', 'DE']
    types = ['basic', 'custom']

    settings_info = {}

    for t in types:
        for lang in langs:
            key = f"{t}_{lang}"
            settings_info[f'{t}_{lang}'] = user_settings.get(key, {})

    return settings_info


def get_player_info(user):
    user_profile = user.profile
    return {
            'user_name': user.username, 
            'level': user_profile.level,
            'current_exp': user_profile.current_exp,
            'currency': user_profile.currency,
        }

def get_statistics_info(user):
    """Counts statistics for basic and custom vocabulary for every category of word."""
    from datetime import datetime, time, timedelta
    from django.utils.timezone import now

    instance_types = ['basic', 'custom']
    instance_languages = ['EN', 'DE']

    today = now().date()
    result_statistics = {}

    for instance in instance_types:
        result_statistics[instance] = {}
        for language in instance_languages:
            result_statistics[instance][language] = {}

            current_instance_settings = user.settings.dictionaries.get(f'{instance}_{language}', {})
            limit_date = today - timedelta(days=current_instance_settings.get('testing_days_limit', 5))
            limit_datetime = datetime.combine(limit_date, time.max)

            if instance == 'basic':
                Word_Model = INSTANCES_MAP['basic'][language]['words']
                Status_Model = INSTANCES_MAP['basic'][language]['statuses']

                count_total_words = Word_Model.objects.count()
                count_repeat_words = Status_Model.objects.filter(user=user, status='REPEAT').count()
                count_process_words = Status_Model.objects.filter(user=user, status='PROCESS').count()
                count_box_1_words = Status_Model.objects.filter(user=user, status='BOX_1').count()
                count_box_1_usable = Status_Model.objects.filter(
                    user=user, status='BOX_1', status_changed_date__lte=limit_datetime
                ).count()
                count_box_2_words = Status_Model.objects.filter(user=user, status='BOX_2').count()
                count_box_2_usable = Status_Model.objects.filter(
                    user=user, status='BOX_2', status_changed_date__lte=limit_datetime
                ).count()
                count_box_3_words = Status_Model.objects.filter(user=user, status='BOX_3').count()
                count_box_3_usable = Status_Model.objects.filter(
                    user=user, status='BOX_3', status_changed_date__lte=limit_datetime
                ).count()
                count_learnt_words = Status_Model.objects.filter(user=user, status='LEARNT').count()
                count_learnt_usable = Status_Model.objects.filter(
                    user=user, status='LEARNT', status_changed_date__lte=limit_datetime
                ).count()
                count_new_words = count_total_words - count_repeat_words - count_process_words - \
                                  count_box_1_words - count_box_2_words - count_box_3_words - count_learnt_words
            else:
                Custom_Words_Model = UserCustomWord.objects.filter(user=user, language=language)
                count_total_words = Custom_Words_Model.count()
                count_repeat_words = Custom_Words_Model.filter(status='REPEAT').count()
                count_process_words = Custom_Words_Model.filter(status='PROCESS').count()
                count_box_1_words = Custom_Words_Model.filter(status='BOX_1').count()
                count_box_1_usable = Custom_Words_Model.filter(
                    status='BOX_1', status_changed_date__lte=limit_datetime
                ).count()
                count_box_2_words = Custom_Words_Model.filter(status='BOX_2').count()
                count_box_2_usable = Custom_Words_Model.filter(
                    status='BOX_2', status_changed_date__lte=limit_datetime
                ).count()
                count_box_3_words = Custom_Words_Model.filter(status='BOX_3').count()
                count_box_3_usable = Custom_Words_Model.filter(
                    status='BOX_3', status_changed_date__lte=limit_datetime
                ).count()
                count_learnt_words = Custom_Words_Model.filter(status='LEARNT').count()
                count_learnt_usable = Custom_Words_Model.filter(
                    status='LEARNT', status_changed_date__lte=limit_datetime
                ).count()
                count_new_words = Custom_Words_Model.filter(status='NEW').count()

            result_statistics[instance][language] = {
                'TOTAL': count_total_words,
                'NEW': count_new_words,
                'REPEAT': count_repeat_words,
                'PROCESS': count_process_words,
                'BOX_1': count_box_1_words,
                'BOX_1_usable': count_box_1_usable,
                'BOX_2': count_box_2_words,
                'BOX_2_usable': count_box_2_usable,
                'BOX_3': count_box_3_words,
                'BOX_3_usable': count_box_3_usable,
                'LEARNT': count_learnt_words,
                'LEARNT_usable': count_learnt_usable,
                'BOX_1_LIMIT': current_instance_settings.get('box_1_limit', 90),
                'BOX_2_LIMIT': current_instance_settings.get('box_2_limit', 150),
                'BOX_3_LIMIT': current_instance_settings.get('box_3_limit', 150),
            }

    return result_statistics

def get_categories_info():
    from collections import defaultdict         

    categories = [{'id':category['id'],'name': category['name']} for category in WordCategory.objects.values('id', 'name')]
    subcategories = {}
    for category in categories:
        subcategories[category['id']] = list(WordSubcategory.objects.filter(category=category['id']).values('id', 'name'))
    
    return {'categories': categories,
            'subcategories': subcategories}

def get_all_info(user):
    return {
        'player_profile': get_player_info(user),
        'settings': get_settings_info(user), 
        'statistics': get_statistics_info(user),
        'categories': get_categories_info(),
        }

#========================================================================================= COMMON CONTROLLERS ====================================================================================
@login_required
def get_user_info(request):
    user = request.user
    
    return JsonResponse(get_all_info(user))

@login_required
def get_statistics(request): 
    return JsonResponse(get_statistics_info(request.user))

@login_required
def get_settings(request):
    return JsonResponse(get_settings_info(request.user))

#-------------------------------------------------- VOCABULARY, LIBRARY - CREATE STUDY LIST
def serialize_word(word): # utilit
    return {
        'article': word.article,
        'id': word.id,
        'word': word.word,
        'translation': word.translation,
        'synonims': word.synonims,
        'word_type': word.word_type,
        'word_level': word.word_level,
        'word_category': word.category.name,
        'word_subcategory': word.sub_category.name
   }


def create_custom_study_list(user, data):
    instance_language = data['instance_language']
    study_list_length = int(data['study_list_length'])
    repeat_words_number = int(data['repeat_words_number'])

    words_qs = UserCustomWord.objects.filter(user=user, language=instance_language)

    # GET IDs of all words, that have some status excluding 'NEW' status
    in_process_word_ids = list(words_qs.filter(
        status__in=[
            'REPEAT',
            'PROCESS',
            'BOX_1',
            'BOX_2',
            'BOX_3',
            'LEARNT'
        ]
    ).values_list('id', flat=True))

    # 1️⃣ Переводимо PROCESS → BOX_1
    words_qs.filter(status='PROCESS').update(status='BOX_1')

    words_list = []

    # 2️⃣ Беремо слова для повторення (REPEAT)
    rep_words_ids = list(
        words_qs.filter(status='REPEAT')
        .order_by('?')
        .values_list('id', flat=True)[:repeat_words_number]
    )
    words_qs.filter(id__in=rep_words_ids).update(status='PROCESS')

    rep_words = words_qs.filter(id__in=rep_words_ids)
    words_list.extend([serialize_word(w) for w in rep_words])

    # 3️⃣ Добираємо нові слова згідно з фільтрами
    new_words_number = study_list_length - len(words_list)

    filters = {}
    if data.get('new_words_type') not in (None, '', 'RANDOM'):
        filters['word_type'] = data['new_words_type']
    if data.get('new_words_level') not in (None, '', 'RANDOM'):
        filters['word_level'] = data['new_words_level']
    if data.get('new_words_category') not in (None, '', 'RANDOM'):
        filters['category'] = int(data['new_words_category'])
    if data.get('new_words_subcategory') not in (None, '', 'RANDOM'):
        filters['sub_category'] = int(data['new_words_subcategory'])

    new_words = list(
        words_qs.filter(**filters)
        .exclude(id__in=in_process_word_ids)
        .order_by('?')[:new_words_number]
    )

    if new_words:
        words_qs.filter(id__in=[w.id for w in new_words]).update(status='PROCESS')
        words_list.extend([serialize_word(w) for w in new_words])

    # 4️⃣ Fallback: якщо ще не вистачає — добираємо будь-які NEW
    if len(words_list) < study_list_length:
        rest_words_number = max(study_list_length - len(words_list),0)

        rest_words = list(
            words_qs.filter(status='NEW')
            .exclude(id__in=[w['id'] for w in words_list])  # уникаємо повторів
            .order_by('?')[:rest_words_number]
        )

        if rest_words:
            words_qs.filter(id__in=[w.id for w in rest_words]).update(status='PROCESS')
            words_list.extend([serialize_word(w) for w in rest_words])

    return words_list

def create_basic_study_list(user, data):
    instance_type = data['instance_type']
    instance_language = data['instance_language']
    study_list_length = int(data['study_list_length'])
    repeat_words_number = int(data['repeat_words_number'])

    # MODELS
    statuses_model = INSTANCES_MAP[instance_type][instance_language]['statuses']
    words_model = INSTANCES_MAP[instance_type][instance_language]['words']

    # GET IDs of all words, that have some status excluding 'NEW' status
    in_process_word_ids = list(statuses_model.objects.filter(
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


    # Оновити статус PROCESS → BOX_1
    statuses_model.objects.filter(
        user=user,
        word__id__in = in_process_word_ids,
        status='PROCESS'
    ).update(status='BOX_1')
    
        
    words_list = []
    # CHOOSE 'REPEAT" words
    rep_words_ids = list(
        statuses_model.objects.filter(user=user, status='REPEAT')
        .order_by('?')
        .values_list('id', flat=True)[:repeat_words_number]
        )
    # Масове оновлення статусу на PROCESS
    statuses_model.objects.filter(id__in=rep_words_ids).update(status='PROCESS')
    
    # Отримуємо відповідні слова
    rep_words = words_model.objects.filter(
        id__in=statuses_model.objects.filter(id__in=rep_words_ids)
        .values_list('word__id', flat=True)
        )

    for word in rep_words:
        words_list.append(serialize_word(word))

    
    new_words_number = study_list_length - len(words_list)

    # CHOOSE 'NEW' words
    # ДОДАВАННЯ нових слів до навчального списку з урахуванням обраних користувачем фільтрів
    
    new_words_type = data['new_words_type'] if data['new_words_type'] and data['new_words_type'] != 'RANDOM' else ''
    new_words_level = data['new_words_level'] if data['new_words_level'] and data['new_words_level'] != 'RANDOM' else ''
    # new_words_category = int(data['new_words_category'] if data['new_words_category'] and data['new_words_category'] != 'RANDOM' else '')
    # new_words_subcategory = int(data['new_words_subcategory'] if data['new_words_subcategory'] and data['new_words_subcategory'] != 'RANDOM' else '')
    new_words_category = int(data['new_words_category']) if data['new_words_category'] and data['new_words_category'] != 'RANDOM' else None
    new_words_subcategory = int(data['new_words_subcategory']) if data['new_words_subcategory'] and data['new_words_subcategory'] != 'RANDOM' else None
    
    filters = {}


    if new_words_type:
        filters['word_type'] = new_words_type
    if new_words_level:
        filters['word_level'] = new_words_level
    if new_words_category is not None:
        filters['category'] = new_words_category
    if new_words_subcategory is not None:
        filters['sub_category'] = new_words_subcategory
    
    new_words = words_model.objects.filter(**filters).exclude(id__in=in_process_word_ids)[:new_words_number ]

    if new_words.count() > 0:
        for word in new_words:
            statuses_model.objects.create(
                user=user,
                word=word,
                status='PROCESS'
            )
            words_list.append(serialize_word(word))   
    

    # ДОДАВАННЯ нових слів до навчального списку без урахування фільтрів користувача, якщо наприклад слів за фільтром більше не було
    if len(words_list) < study_list_length:
        rest_words_number = study_list_length -  len(words_list) 

        # CHOOSE 'REPEAT" words
        rep_words_ids = list(
            statuses_model.objects.filter(user=user, status='REPEAT')
            .order_by('?')
            .values_list('id', flat=True)[:repeat_words_number]
            )

        rest_words = rep_words = words_model.objects.filter(id__in=statuses_model.objects.filter(id__in=rep_words_ids).values_list('word__id', flat=True))[:rest_words_number]

        for word in rest_words:
            statuses_model.objects.update_or_create(
            user=user,
            word=word,
            defaults={'status': 'PROCESS'})

            words_list.append(serialize_word(word))
    
    return words_list

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

    if instance_type == 'custom':
        words_list = create_custom_study_list(user, data)
    elif instance_type == 'basic':
        words_list = create_basic_study_list(user, data)

    if len(words_list) > 0:
        return JsonResponse({'words': words_list,
                            })
    else:
        return JsonResponse({'error':'There are no more words to create study list.',
                             'code': 'NO_MORE_WORDS'}, status = 404)

@login_required
def get_study_list(request):
    user = request.user
    instance_type = request.GET.get('instance_type')
    instance_language = request.GET.get('instance_language')
    
    words_list = []
    if (instance_type == 'basic'):
        statuses_model = INSTANCES_MAP[instance_type][instance_language]['statuses']
        words_model = INSTANCES_MAP[instance_type][instance_language]['words']
        in_process_word_ids = list(statuses_model.objects.filter(
            user=user,
            status__in=[
                
                'PROCESS',
            ]
        ).values_list('word__id', flat=True))
       
        words = words_model.objects.filter(id__in=in_process_word_ids)
        
        for word in words:
            words_list.append(serialize_word(word))

        list_create_date = statuses_model.objects.filter(user=user, status='PROCESS').values_list('status_changed_date', flat=True).first()
    else:
        custom_words = UserCustomWord.objects.filter(
            user=user,
            language=instance_language,
            status='PROCESS'
        )

        words_list = [serialize_word(word) for word in custom_words]

        list_create_date = (custom_words.first().status_changed_date   if custom_words.exists()    else None)
    
    return JsonResponse({'words': words_list,
                         'create_date': list_create_date
                         })

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
        word_progress = statuses.objects.filter(user=user, status=box, status_changed_date__date__lte=today - timedelta(days=user_settings.get('testing_days_limit',5))).order_by('?').first()

        if not word_progress:
            return JsonResponse({'word': None})  # Слова закінчилися
        word = word_progress.word
    
    elif instance_type == 'custom':
        word = UserCustomWord.objects.filter(
            user = user,
            status = box,
            language = instance_language,
            status_changed_date__date__lte=today - timedelta(days=user_settings.get('testing_days_limit', 5))
        ).order_by('?').first()
        
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
    elif instance_type == 'custom':
        try:
            progress = UserCustomWord.objects.get(
                user = user,
                language = instance_language,
                word_id=word_id           
            )
        except UserCustomWord.DoesNotExist:
            return JsonResponse({'error': 'Word not found'}, status=404)
    
    correct_answer = progress.word.translation.strip().lower()
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
        if progress.status =='LEARNT' and instance_type== 'basic' and not progress.was_learnt_once:
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

#---------------------------------------- VOCABULARY, LIBRARY -> CLEAN BOX of words 
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
        words_for_clean = UserCustomWord.object.filter(
            user = user,
            language = instance_language, 
            status = box_for_clean
        )[:words_number]
    
    for word in words_for_clean:
            word.status_changed_date = now().date()
            word.status = 'REPEAT'
            word.save()
    

    return JsonResponse({'status': 'ok', 'received': data})


#========================================================================================= LOGIN PAGE =====================================================================================
def login_user(request):
    login_form = AuthenticationForm()
    

    if request.method == 'POST':
        # Якщо форма логіну була надіслана
        if 'login_submit' in request.POST:
            login_form = AuthenticationForm(data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                return redirect('index')

    context = {
        'login_form': login_form,
    }
    return render(request, 'login.html', context)
#========================================================================================= REGISTER PAGE =====================================================================================
def register_user(request):
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
    context = {
        'register_form': register_form
    }
    return render(request, 'register.html', context)

#========================================================================================= INDEX PAGE =====================================================================================
@login_required
def index_page(request):
    return render(request, 'index.html', context = {'page_name': 'index',
                                                    'user_name': request.user.username})

#======================================================================================= ARMORY PAGE =======================================================================================
@login_required
def armory_page(request):
    return render(request, 'armory.html', context = {'page_name': 'armory',

                                                     'user_info': get_all_info(request.user),})

#==================================================================================== ARENA PAGE ==========================================================================================
@login_required
def arena_page(request):
    return render(request, 'arena.html', context = {'page_name': 'arena',
                                                    'user_info': get_all_info(request.user),})



#================================================================================= PROFILE PAGE ===================================================================================================================
@login_required
@login_required
def profile_page(request):
    return render(request, 'profile.html', context = {'page_name': 'profile',
                                                      'user_info': get_all_info(request.user),
                                                    })


#--------------------------------------------------------------------------- PROFILE PAGE - CHANGE SETTINGS
@require_POST
@login_required
def change_settings(request):
    user = request.user
    instance_type = request.POST.get('instance_type')
    print(f'------ SETTINGS CHANGING ---> instance type = {instance_type}')
    instance_language = request.POST.get('instance_language')
    print(f'------ SETTINGS CHANGING ---> instance language = {instance_language}')

    dict_key = f"{instance_type}_{instance_language}"
    settings = user.settings.dictionaries.get(dict_key, {})

    def to_int(value, default=None):
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    new_settings = {
        'study_list_length': to_int(request.POST.get('study_list_length'), 20),
        'repeat_words_number': to_int(request.POST.get('repeat_words_number'), 10),
        'box_1_limit': to_int(request.POST.get('BOX_1_limit'), 90),
        'box_2_limit': to_int(request.POST.get('BOX_2_limit'), 150),
        'box_3_limit': to_int(request.POST.get('BOX_3_limit'), 150),
        'testing_days_limit': to_int(request.POST.get('testing_days_limit'), 5),
    }

    settings.update(new_settings)
    user.settings.dictionaries[dict_key] = settings  # <-- зберігаємо назад
    user.settings.save()

    return redirect('/profile/')

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
        'word_subcategory': word.sub_category.id}



@login_required
def vocabulary_page(request):
    return render(request, 'vocabulary.html', context = {'page_name': 'vocabulary',
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


#=========================================================================================== LIBRARY PAGE ========================================================================================================================
@login_required
def library_page(request):
    return render(request, 'library.html', context = {'page_name': 'library',
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








