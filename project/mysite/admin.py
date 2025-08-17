from django.contrib import admin
from .models import Word, UserSettings, UserWordsProgress, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
# Register your models here.


@admin.register(UserWordsProgress)
class UserWordsProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'word', 'status', 'repetition_count', 'status_changed_date', 'was_learnt_once')
    list_filter = ('status', 'status_changed_date', 'user')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'level', 'current_exp', 'currency')
    list_filter = ('user', 'level', 'currency')

@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('id', 'eng', 'ukr', 'word_level', 'word_type', 'article', 'synonims')
    readonly_fields = ('id',)

class CustomUserAdmin(DefaultUserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff')

@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'rep_words_number', 'new_words_number', 'min_words_number', 'box_1_limit', 'box_2_limit', 'box_3_limit', 'testing_days_limit')
    list_editable = ('rep_words_number', 'new_words_number', 'min_words_number', 'box_1_limit', 'box_2_limit', 'box_3_limit', 'testing_days_limit')
    list_filter = ('user',)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)