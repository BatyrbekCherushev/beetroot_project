from django.contrib import admin
from .models import Word
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import UserWordsProgress
# Register your models here.


@admin.register(UserWordsProgress)
class UserWordsProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'word', 'status', 'repetition_count', 'status_changed_date')
    list_filter = ('status', 'status_changed_date', 'user')

@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('id', 'eng', 'ukr', 'word_level', 'word_type', 'article', 'synonims')
    readonly_fields = ('id',)

class CustomUserAdmin(DefaultUserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff')

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)