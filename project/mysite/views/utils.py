
from mysite.models import UserCustomWord, Word, WordDeutch, UserWordsProgress, UserWordsDeutchProgress, User, UserSettings, WordCategory, WordSubcategory, PlayerProfile, Battle, BossProfile, Skill, PlayerSkill, BossSkill
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
    player_profile = user.player_profile
    return {
            'user_name': user.username, 
            'level': player_profile.level,
            'current_exp': player_profile.current_exp,
            'currency': player_profile.currency,
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

            limit_date_30 = today - timedelta(days=30)
            limit_datetime_30 = datetime.combine(limit_date_30, time.max)

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

                Status_Model.objects.filter(
                    user=user,
                    status='LEARNT',
                    status_changed_date__lte=limit_datetime_30
                ).update(is_freezed=True)
                count_learnt_freezed = max(Status_Model.objects.filter(user=user, status='LEARNT', is_freezed=True).count(), 0)

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
                    status='BOX_3', status_changed_date__lte=limit_datetime).count()
                
                count_learnt_words = Custom_Words_Model.filter(status='LEARNT').count()
                count_learnt_usable = Custom_Words_Model.filter(
                    status='LEARNT', status_changed_date__lte=limit_datetime
                ).count()

                # CHECKING if word does not have to become freezed
                Custom_Words_Model.filter(
                    status='LEARNT', status_changed_date__lte=limit_datetime_30
                ).update(is_freezed=True)
                count_learnt_freezed = max(Custom_Words_Model.filter(
                    status='LEARNT', is_freezed=True
                ).count(), 0)

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
                'LEARNT_freezed': count_learnt_freezed,
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

#-------------------------------------------------- VOCABULARY, LIBRARY - CREATE STUDY LIST
def serialize_word(word): # utilit
    return {
        'article': word.article,
        'id': word.id,
        'word': word.word,
        'translation': word.translation,
        'translation_options': word.translation_options,
        'comment': word.comment,
        'synonims': word.synonims,
        'word_type': word.word_type,
        'word_level': word.word_level,
        'category': word.category.name,
        'subcategory': word.sub_category.name,
        "link":word.link
        
        
   }


def create_custom_study_list(user, data):
    instance_language = data['instance_language']
    study_list_length = int(data['study_list_length'])
    repeat_words_number = int(data['repeat_words_number'])

    filters = {}
    if data.get('words_type') not in (None, '', 'RANDOM'):
        filters['word_type'] = data['new_words_type']
    if data.get('words_level') not in (None, '', 'RANDOM'):
        filters['word_level'] = data['new_words_level']
    if data.get('words_category') not in (None, '', 'RANDOM'):
        filters['category'] = int(data['new_words_category'])
    if data.get('words_subcategory') not in (None, '', 'RANDOM'):
        filters['sub_category'] = int(data['new_words_subcategory'])

    words_qs = UserCustomWord.objects.filter(user=user, language=instance_language)

    words_list = []

    #--------------------- REPEAT WORTS with FILTERS and without them
    if repeat_words_number > 0:

        # Беремо слова для повторення (REPEAT) WITH FILTERS
        rep_words_ids = list(
            words_qs.filter(**filters, status='REPEAT')
            .order_by('?')
            .values_list('id', flat=True)[:repeat_words_number]
        )
        words_qs.filter(id__in=rep_words_ids).update(status='PROCESS')

        rep_words = words_qs.filter(id__in=rep_words_ids)
        words_list.extend([serialize_word(w) for w in rep_words])

    #--------------------- NEW WORDS WITH FILTERS
    if len(words_list) < study_list_length:
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

        # Добираємо нові слова згідно з фільтрами
        new_words_number = study_list_length - len(words_list)
        
        new_words = list(
            words_qs.filter(**filters)
            .exclude(id__in=in_process_word_ids)
            .order_by('?')[:new_words_number]
        )

        if new_words:
            words_qs.filter(id__in=[w.id for w in new_words]).update(status='PROCESS')
            words_list.extend([serialize_word(w) for w in new_words])
        
    return words_list

def create_basic_study_list(user, data):
    instance_type = data['instance_type']
    instance_language = data['instance_language']
    study_list_length = int(data['study_list_length'])
    repeat_words_number = int(data['repeat_words_number'])
    

    filters = {}
    words_type = data['words_type'] if data['words_type'] and data['words_type'] != 'RANDOM' else ''
    words_level = data['words_level'] if data['words_level'] and data['words_level'] != 'RANDOM' else ''
    if words_type:
        filters['word_type'] = words_type
    if words_level:
        filters['word_level'] = words_level
    
    words_category = int(data['words_category']) if data['words_category'] and data['words_category'] != 'RANDOM' else None
    words_subcategory = int(data['words_subcategory']) if data['words_subcategory'] and data['words_subcategory'] != 'RANDOM' else None
    if words_category is not None:
        filters['category'] = words_category
    if words_subcategory is not None:
        filters['sub_category'] = words_subcategory
    
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
        
    words_list = []

    if repeat_words_number > 0:       

        rep_words = words_model.objects.filter(
            **filters,
            id__in=statuses_model.objects.filter(user=user, status='REPEAT').values_list('word__id', flat=True))[:repeat_words_number]
        
        statuses_model.objects.filter(user=user,  word__in=rep_words).update(status="PROCESS")

        for word in rep_words:
            words_list.append(serialize_word(word))
        print(f'------------------repeat_words_number={repeat_words_number}, words_list len = {len(words_list)}')
       
    #---------------------------------------------------
    if study_list_length > repeat_words_number:

        new_words_number = study_list_length - len(words_list)

        # CHOOSE 'NEW' words
        # ДОДАВАННЯ нових слів до навчального списку з урахуванням обраних користувачем фільтрів
        
        new_words = words_model.objects.filter(**filters).exclude(id__in=in_process_word_ids)[:new_words_number ]

        if new_words.count() > 0:
            for word in new_words:
                statuses_model.objects.create(
                    user=user,
                    word=word,
                    status='PROCESS'
                )
                words_list.append(serialize_word(word))   
    
    return words_list