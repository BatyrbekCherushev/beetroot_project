from django.contrib import admin
from .models import Word, WordDeutch, UserSettings, UserWordsProgress,UserWordsDeutchProgress, UserCustomWord, UserProfile, models
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

from import_export.admin import ImportExportModelAdmin
from import_export.results import RowResult
from import_export import resources

from django.db import connection
from django.contrib import messages
# Register your models here.
from .models import WordCategory, WordSubcategory
from django.forms import TextInput, Textarea

#============================================================================================= CATEGORIES ADMIN
class WordSubcategoryInline(admin.TabularInline):  # або StackedInline
    model = WordSubcategory
    extra = 1  # кількість порожніх рядків для додавання нових


@admin.register(WordCategory)
class WordCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ('name',)
    list_editable = ('name',)
    inlines = [WordSubcategoryInline]  # щоб додавати підкатегорії прямо в категорії


@admin.register(WordSubcategory)
class WordSubcategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category")
    search_fields = ('name',)
    list_editable = ('name',)
    list_filter = ("category",)

#=====================================================================================================================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'level', 'current_exp', 'currency')
    list_filter = ('user', 'level', 'currency')

#============================================================================================= CUSTOM WORDS ADMIN
@admin.register(UserCustomWord)
class UserCustomWordAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'id',
        'language',
        'word_level',
        'word_type',
        'article',
        'status',
        'status_changed_date',
        'word',
        'transcription',
        'translation',
        'translation_options',
        'synonims',
        'comment',
        'category',
        'sub_category',
        'link'
    )


#============================================================================================= ENGLISH BASIC WORDS ADMIN
class WordResource(resources.ModelResource):
    class Meta:
        model = Word
        # НЕ включаємо "id" у fields
        fields = (
            'id',
            "word_level", "word_type", "article", "word",
            "transcription", "translation", "translation_options", "synonims",
            "comment", "category", "sub_category", "is_irregular_verb",
            "is_modal_verb", "link"
        )
        import_id_fields = ("id",)  # або будь-яке унікальне поле для оновлення        


@admin.register(Word)
class WordAdmin(ImportExportModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'style': 'width: 100px;'})},
        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},
    }

    resource_class = WordResource
    list_display = (
        'id', 'word_level', 'word_type', 'article', 'word',
        'transcription', 'translation', 'translation_options',
        'synonims', 'comment', 'category', 'sub_category',"link",
        'is_irregular_verb', 'is_modal_verb'
    )
    list_editable = (
        "word_level", "word_type", "article", "word", "transcription",
        "translation", "translation_options", "synonims", "comment",
        "category", "sub_category", "link", "is_irregular_verb", "is_modal_verb"
    )
    # readonly_fields = ('id',)
    actions = ["delete_all_and_reset_id_and_progress"]
    
    def delete_all_and_reset_id_and_progress(self, request, queryset):
        # 1. Видаляємо всі записи з Word
        Word.objects.all().delete()

        # 2. Обнуляємо лічильник id (AUTOINCREMENT)
        table_name = Word._meta.db_table
        with connection.cursor() as cursor:
            if 'sqlite' in connection.settings_dict['ENGINE']:
                cursor.execute(f'DELETE FROM sqlite_sequence WHERE name="{table_name}";')
            elif 'postgresql' in connection.settings_dict['ENGINE']:
                cursor.execute(f'ALTER SEQUENCE {table_name}_id_seq RESTART WITH 1;')
            elif 'mysql' in connection.settings_dict['ENGINE']:
                cursor.execute(f'ALTER TABLE {table_name} AUTO_INCREMENT = 1;')

        # 3. Очищаємо всі статуси користувачів
        UserWordsProgress.objects.all().delete()

        self.message_user(request, "Всі слова та прогрес користувачів видалено, ID обнулено!", level=messages.WARNING)

    delete_all_and_reset_id_and_progress.short_description = "Видалити всі слова та скинути прогрес користувачів"


@admin.register(UserWordsProgress)
class UserWordsProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'word', 'status', 'repetition_count', 'status_changed_date', 'was_learnt_once')
    list_filter = ('status', 'status_changed_date', 'user')

#============================================================================================= DEUTCH BASIC WORDS AND STATUSES ADMIN
class WordDeutchResource(resources.ModelResource):
    class Meta:
        model = WordDeutch
        # НЕ включаємо "id" у fields
        fields = (
            'id',
            "word_level", "word_type", "article", "word",
            "transcription", "translation", "translation_options", "synonims",
            "comment", "category", "sub_category", "link",
            "is_modal_verb", "is_trennbar_verb", "is_vokalwechsel_verb"
        )
        import_id_fields = ("id",)  # або будь-яке унікальне поле для оновлення        

@admin.register(WordDeutch)
class WordDeutchAdmin(ImportExportModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'style': 'width: 100px;'})},
        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},
    }

    resource_class = WordDeutchResource
    list_display = (
        'id',
        "word_level",
        "word_type",
        "article",
        "word",
    "transcription",
    "translation",
    "translation_options",
    "synonims",
    "comment",
    "category",
    "sub_category",
    "link",
    "is_modal_verb")
    list_editable = (
        
        "word_level",
        "word_type",
    "article",
    "word",
    "transcription",
    "translation",
    "translation_options",
    "synonims",
    "comment",
    "category",
    "sub_category",
    "link",
    "is_modal_verb")
    # readonly_fields = ('id',)

    actions = ["delete_all_and_reset_id_and_progress"]
    
    def delete_all_and_reset_id_and_progress(self, request, queryset):
        # 1. Видаляємо всі записи з Word
        WordDeutch.objects.all().delete()

        # 2. Обнуляємо лічильник id 
        table_name = WordDeutch._meta.db_table
        with connection.cursor() as cursor:
            if 'sqlite' in connection.settings_dict['ENGINE']:
                cursor.execute(f'DELETE FROM sqlite_sequence WHERE name="{table_name}";')
            elif 'postgresql' in connection.settings_dict['ENGINE']:
                cursor.execute(f'ALTER SEQUENCE {table_name}_id_seq RESTART WITH 1;')
            elif 'mysql' in connection.settings_dict['ENGINE']:
                cursor.execute(f'ALTER TABLE {table_name} AUTO_INCREMENT = 1;')

        # 3. Очищаємо всі статуси користувачів
        UserWordsDeutchProgress.objects.all().delete()

        self.message_user(request, "Всі слова та прогрес користувачів видалено, ID обнулено!", level=messages.WARNING)

    delete_all_and_reset_id_and_progress.short_description = "Видалити всі слова та скинути прогрес користувачів"

@admin.register(UserWordsDeutchProgress)
class UserWordsDeutchProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'word', 'status', 'repetition_count', 'status_changed_date', 'was_learnt_once')
    list_filter = ('status', 'status_changed_date', 'user')

#============================================================================================================================================

class CustomUserAdmin(DefaultUserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff')

# @admin.register(UserSettings)
# class UserSettingsAdmin(admin.ModelAdmin):
#     list_display = ('id',
#                     'user',
#                     'basic_EN_repeat_words_number',
#                     'basic_EN_study_list_length',
#                     'basic_EN_box_1_limit',
#                     'basic_EN_box_2_limit',
#                     'basic_EN_box_3_limit',
#                     'basic_EN_testing_days_limit')
#     list_editable = ('basic_EN_repeat_words_number', 'basic_EN_study_list_length', 'basic_EN_box_1_limit', 'basic_EN_box_2_limit', 'basic_EN_box_3_limit', 'basic_EN_testing_days_limit')
#     list_filter = ('user',)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)