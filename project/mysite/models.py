from django.db import models
from django.contrib.auth.models import User


class Word(models.Model):
    id = models.AutoField(primary_key=True)
    word_level = models.CharField(max_length = 2, default = '')
    word_type = models.CharField(max_length=20, default = '')
    article = models.CharField(max_length=4, default='')
    eng = models.CharField(max_length=30)
    transcription = models.CharField(max_length=30, default='')
    forms = models.CharField(max_length=40, default='')
    ukr = models.CharField(max_length=30, default='')
    commentary = models.TextField(default='')
    synonims = models.TextField(default='')
    category = models.CharField(max_length=20, default='')
    sub_category = models.CharField(max_length=20, default='')
    is_oxford = models.BooleanField(default = True)
    is_important = models.BooleanField(default = False)
    
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

    class Meta:
        verbose_name = 'Статус слова'
        verbose_name_plural = "Статуси слів"
        





