from django.db import models
from django.contrib.auth.models import User


DEFAULT_BOX_1_LIMIT = 90
DEFAULT_BOX_2_LIMIT = 150
DEFAULT_BOX_3_LIMIT = 150
DEFAULT_TEST_DAYS_LIMIT = 1
DEFAULT_REPS_NUMBER = 15
DEFAULT_NEW_NUMBER = 5
DEFAULT_MIN_NUMBER = DEFAULT_NEW_NUMBER + DEFAULT_REPS_NUMBER #20

class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    rep_words_number = models.PositiveIntegerField(default = DEFAULT_REPS_NUMBER)
    new_words_number = models.PositiveIntegerField(default = DEFAULT_NEW_NUMBER)
    min_words_number = models.PositiveIntegerField(default = DEFAULT_MIN_NUMBER) # min number of words creating study list
    box_1_limit = models.PositiveIntegerField(default = DEFAULT_BOX_1_LIMIT)
    box_2_limit = models.PositiveIntegerField(default = DEFAULT_BOX_2_LIMIT)
    box_3_limit = models.PositiveIntegerField(default = DEFAULT_BOX_3_LIMIT)
    testing_days_limit = models.PositiveIntegerField(default = DEFAULT_TEST_DAYS_LIMIT)
    
    class Meta:
        verbose_name = 'Налаштування користувача'
        verbose_name_plural = "Налаштування користувача"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    level = models.IntegerField(default=0)
    current_exp = models.IntegerField(default=0)
    currency = models.IntegerField(default=0)  # ігрова валюта


class Word(models.Model):
    id = models.AutoField(primary_key=True)
    word_level = models.CharField(max_length = 2, default = '')
    word_type = models.CharField(max_length=20, default = '')
    article = models.CharField(max_length=4, default='')
    eng = models.CharField(max_length=30)
    transcription = models.CharField(max_length=30, default='')
    ukr = models.CharField(max_length=30, default='')
    translation_options = models.TextField(default='')
    synonims = models.TextField(default='NO SYNONIM FOR THIS WORD')
    comment = models.TextField(default='')
    category = models.CharField(max_length=20, default='')
    sub_category = models.CharField(max_length=20, default='')
    is_irregular_verb = models.BooleanField(default = True)
    is_modal_verb = models.BooleanField(default = False)
    
    class Meta:
        verbose_name = 'Слово'
        verbose_name_plural = "Слова"

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
        verbose_name = 'Статус слова'
        verbose_name_plural = "Статуси слів"
        





