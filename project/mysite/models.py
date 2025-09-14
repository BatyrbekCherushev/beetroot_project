from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

DEFAULT_BOX_LIMIT_MIN = 60
DEFAULT_BOX_LIMIT_MAX = 150

DEFAULT_BOX_1_LIMIT = 90
DEFAULT_BOX_2_LIMIT = 150
DEFAULT_BOX_3_LIMIT = 150

DEFAULT_REPS_NUMBER = 10
# DEFAULT_NEW_NUMBER = 5
DEFAULT_STUDY_LIST_LENGTH = 20 #20

DEFAULT_TEST_DAYS_LIMIT = 5

LANGUAGES = ["EN", "DE", "FR"]  # можна розширювати
INSTANCE_TYPES = ["basic", 'custom']      # потім додаси "custom" і т.д.

def set_default_dictionaries_settings():
    default_settings = {}
    for instance_type in INSTANCE_TYPES:
        for language in LANGUAGES:
            default_settings[f'{instance_type}_{language}'] = {
                'repeat_words_number': DEFAULT_REPS_NUMBER,
                'study_list_length': DEFAULT_STUDY_LIST_LENGTH,
                'box_limit_min': DEFAULT_BOX_LIMIT_MIN,
                'box_limit_max': DEFAULT_BOX_LIMIT_MAX,
                'box_1_limit': DEFAULT_BOX_1_LIMIT,
                'box_1_limit_rec': DEFAULT_BOX_1_LIMIT,
                'box_2_limit': DEFAULT_BOX_2_LIMIT,
                'box_2_limit_rec': DEFAULT_BOX_2_LIMIT,
                'box_3_limit': DEFAULT_BOX_3_LIMIT,
                'box_3_limit_rec': DEFAULT_BOX_3_LIMIT,
                'testing_days_limit': DEFAULT_TEST_DAYS_LIMIT,
            }    
    return default_settings



class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    dictionaries = models.JSONField(default=set_default_dictionaries_settings)
    
    class Meta:
        verbose_name = 'Налаштування користувача'
        verbose_name_plural = "Налаштування користувача"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    level = models.IntegerField(default=0)
    current_exp = models.IntegerField(default=0)
    currency = models.IntegerField(default=0)  # ігрова валюта

#------------------------------------------------------------------------------------- КАТЕГОРІЇ СЛІВ
class WordCategory(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True,
        default='БЕЗ КАТЕГОРІЇ',
        verbose_name="Категорія"
        )
    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"

    def __str__(self):
        return self.name

class WordSubcategory(models.Model):
    category = models.ForeignKey(
        WordCategory,
        on_delete=models.CASCADE,
        related_name='subcategories')
    name = models.CharField(max_length=255, verbose_name="Підкатегорія")

    class Meta:
        verbose_name = "Підкатегорія"
        verbose_name_plural = "Підкатегорії"

    def __str__(self):
        return self.name
    
def get_default_category():
    default_category, _ = WordCategory.objects.get_or_create(name="БЕЗ КАТЕГОРІЇ")
    return default_category.id

def get_default_subcategory():
    # Беремо дефолтну категорію
    default_category, _ = WordCategory.objects.get_or_create(name="БЕЗ КАТЕГОРІЇ")
    
    # Беремо дефолтну підкатегорію, яка належить до дефолтної категорії
    default_subcategory, _ = WordSubcategory.objects.get_or_create(
        name="БЕЗ ПІДКАТЕГОРІЇ",
        category=default_category
    )
    
    return default_subcategory.id  # повертаємо id для ForeignKey

#--------------------------------------------------------------------------------------------------- МОДЕЛЬ СЛІВ КАСТОМНОГО СЛОВНИКА
class UserCustomWord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="custom_words")
    language = models.CharField(max_length=10) # EN, DE, ES, FR
    word_level = models.CharField(max_length = 2, default = '')
    word_type = models.CharField(max_length=20, default = '')
    article = models.CharField(max_length=4, default='')
    word = models.CharField(max_length=30)
    transcription = models.CharField(max_length=30, default='')
    translation = models.CharField(max_length=30, default='')
    translation_options = models.TextField(default='')
    synonims = models.TextField(default='NO SYNONIM FOR THIS WORD')
    comment = models.TextField(default='')
    is_irregular_verb = models.BooleanField(default = True)
    is_modal_verb = models.BooleanField(default = False)

    category = models.ForeignKey(
        WordCategory,
        null=False,
        on_delete=models.SET_DEFAULT,
        default=get_default_category
    )
    
    sub_category = models.ForeignKey(
        WordSubcategory,
        on_delete=models.SET_DEFAULT,
        null=False,
        default=get_default_subcategory,
        verbose_name="Підкатегорія"
    )

    # прогрес в цій же таблиці
    status = models.CharField(
        max_length=20,
        choices=[
            ("NEW", "New"),
            ("REPEAT", "Repeat"),
            ("BOX_1", 'Box 1'),
            ("BOX_2", "Box 2"),
            ("BOX_3", "Box 3"),
            ("LEARNED", "Learned")            
        ],
        default="NEW"
    )
    status_changed_date = models.DateTimeField(auto_now=True)
    repetition_count = models.IntegerField(default=0)

#------------------------------------------------------------------------------------------------- ENGLISH BASIC VOCABULARY WORDS MODEL
class Word(models.Model):
    # id = models.AutoField(primary_key=True)
    word_level = models.CharField(max_length = 2, default = '')
    word_type = models.CharField(max_length=20, default = '')
    article = models.CharField(max_length=4, default='')
    word = models.CharField(max_length=100)
    transcription = models.CharField(max_length=100, default='')
    translation = models.CharField(max_length=100, default='')
    translation_options = models.TextField(max_length=200, default='')
    synonims = models.TextField(max_length=200, default='NO SYNONIM FOR THIS WORD')
    comment = models.TextField(max_length=200, default='')
    
    is_irregular_verb = models.BooleanField(default = True)
    is_modal_verb = models.BooleanField(default = False)

    category = models.ForeignKey(
        WordCategory,
        null=False,
        on_delete=models.SET_DEFAULT,
        default=get_default_category
    )
    
    sub_category = models.ForeignKey(
        WordSubcategory,
        on_delete=models.SET_DEFAULT,
        null=False,
        default=get_default_subcategory,
        verbose_name="Підкатегорія"
    )
    
    class Meta:
        verbose_name = 'ENGLISH: Слово'
        verbose_name_plural = "ENGLISH: Слова"

#------------------------------------------------------------------------------------- ENGLISH BASIC VOCABULARY WORDS STATUSES
class UserWordsProgress(models.Model):
    STATUS_CHOICES = [
    ('NEW', 'New'),
    ('PROCESS', 'In Process'),
    ('BOX_1', 'Box 1'),
    ('BOX_2', 'Box 2'),
    ('BOX_3', 'Box 3'),
    ('LEARNT', 'Learnt'),
    ('REPEAT', 'Repeat'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    word = models.ForeignKey(Word, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=10, choices = STATUS_CHOICES, default='NEW')
    repetition_count = models.IntegerField(default=0)
    status_changed_date = models.DateTimeField(auto_now=True)
    was_learnt_once = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'ENGLISH: Статус слова'
        verbose_name_plural = "ENGLISH: Статуси слів"

#------------------------------------------------------------------------------------- DEUTCH BASIC VOCABULARY WORDS MODEL
class WordDeutch(models.Model):
    id = models.AutoField(primary_key=True)
    word_level = models.CharField(max_length = 2, default = '')
    word_type = models.CharField(max_length=20, default = '')
    article = models.CharField(max_length=4, default='')
    word = models.CharField(max_length=30)
    transcription = models.CharField(max_length=30, default='')
    translation = models.CharField(max_length=30, default='')
    translation_options = models.TextField(default='')
    synonims = models.TextField(default='NO SYNONIM FOR THIS WORD')
    comment = models.TextField(default='')
    
    is_irregular_verb = models.BooleanField(default = True)
    is_modal_verb = models.BooleanField(default = False)

    category = models.ForeignKey(
        WordCategory,
        null=False,
        on_delete=models.SET_DEFAULT,
        default=get_default_category
    )
    
    sub_category = models.ForeignKey(
        WordSubcategory,
        on_delete=models.SET_DEFAULT,
        null=False,
        default=get_default_subcategory,
        verbose_name="Підкатегорія"
    )
    
    class Meta:
        verbose_name = 'DEUTCH: Слово'
        verbose_name_plural = "DEUTCH: Слова"

#------------------------------------------------------------------------------------- DEUTCH BASIC VOCABULARY WORDS STATUSES
class UserWordsDeutchProgress(models.Model):
    STATUS_CHOICES = [
    ('NEW', 'New'),
    ('PROCESS', 'In Process'),
    ('BOX_1', 'Box 1'),
    ('BOX_2', 'Box 2'),
    ('BOX_3', 'Box 3'),
    ('LEARNT', 'Learnt'),
    ('REPEAT', 'Repeat'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    word = models.ForeignKey(WordDeutch, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=10, choices = STATUS_CHOICES, default='NEW')
    repetition_count = models.IntegerField(default=0)
    status_changed_date = models.DateTimeField(auto_now=True)
    was_learnt_once = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'DEUTCH: Статус слова'
        verbose_name_plural = "DEUTCH: Статуси слів"

# 
        





