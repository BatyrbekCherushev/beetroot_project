from django.contrib import admin
from .models import Word, WordDeutch, UserSettings, UserWordsProgress,UserWordsDeutchProgress, UserCustomWord, models
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

from import_export.admin import ImportExportModelAdmin
from import_export.results import RowResult
from import_export import resources

from django.db import connection
from django.contrib import messages
# Register your models here.

from import_export import fields
from import_export.widgets import ForeignKeyWidget
from .models import WordSubcategory, WordCategory
from django.forms import TextInput, Textarea

# GAME IMPORTS
from .models import PlayerProfile, BossProfile, Skill, PlayerSkill, BossSkill, Battle, BattleTurn


#============================================================================================= USER SETTINGS ADMIN ========================================================================================================
@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in UserSettings._meta.fields]
#============================================================================================= GAME MODELS ADMIN ========================================================================================================
#------------------------------------------------------------------------- PLAYER PROFILE

@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PlayerProfile._meta.fields]
    list_filter = ('user', 'level', 'currency')

#------------------------------------------------------------------------- BOSS PROFILE
class BossProfileResource(resources.ModelResource):
    class Meta:
        model = BossProfile
        fields = [field.name for field in BossProfile._meta.fields]

        export_order = fields

        import_id_fields = ("id",)  
        """означає, що під час імпорту система буде шукати існуючі записи у базі за полем id.
            Якщо запис з таким id існує → він оновлюється. 
            Якщо запису з таким id немає → створюється новий запис."""
        

@admin.register(BossProfile)
class BossProfileAdmin(ImportExportModelAdmin):
    resource_class = BossProfileResource
    list_display = [field.name for field in BossProfile._meta.fields ]

    list_editable = [field.name for field in BossProfile._meta.fields if field.name != 'id']

    list_filter = [field.name for field in BossProfile._meta.fields ]
    search_fields = ('name',)


#----------------------------------------------------------------------- SKILLS
class SkillResource(resources.ModelResource):
    class Meta:
        model = Skill
        fields = (
            'id',
        'type', 'name', 'description',
        'endurance_cost','damage_physical', 
        'mana_cost', 'damage_fire', 'damage_water', 'damage_earth', 'damage_wind',
        )

        export_order = fields

        import_id_fields = ("id",)  
        """означає, що під час імпорту система буде шукати існуючі записи у базі за полем id.
            Якщо запис з таким id існує → він оновлюється. 
            Якщо запису з таким id немає → створюється новий запис."""

@admin.register(Skill)
class SkillAdmin(ImportExportModelAdmin):
    resource_class = SkillResource

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'style': 'width: 50px;'})},
        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':20})},
    }

    list_display = (
        'id',
        'type', 'name', 'description',
        'endurance_cost','damage_physical', 
        'mana_cost', 'damage_fire', 'damage_water', 'damage_earth', 'damage_wind',  )
    list_editable = ( 'type', 'name', 'description',
        'endurance_cost','damage_physical', 
        'mana_cost', 'damage_fire', 'damage_water', 'damage_earth', 'damage_wind',)

@admin.register(PlayerSkill)
class PlayerSkillAdmin(admin.ModelAdmin):
    list_display = ('id',
        'profile', 'skill')
    list_editable = ('skill',)

#--------------------------------------------------------------------- BATTLES
@admin.register(Battle)
class BattleAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'style': 'width: 100px;'})},
        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},
    }

    list_display = [field.name for field in Battle._meta.fields]
    # list_display=('id', 'battle_type', 'player_1_name', 'player_1_hitpoints', 'boss_name', 'boss_hitpoints')

@admin.register(BattleTurn)
class BattleTurnAdmin(admin.ModelAdmin):
    list_display = [field.name for field in BattleTurn._meta.fields]
    # list_display = (
    #     'id', 'player_profile', 'battle', 'round', 'skill', 'created_at', 'processed'
    # )
# ============================================================================================== VOCABULARIES MODELS ADMINS =====================================================================================================================
#============================================================================================= CATEGORIES ADMIN
class WordCategoryResource(resources.ModelResource):
    class Meta:
        model = WordCategory
        fields = ('id', 'name')
        import_id_fields = ('id',)

class WordSubcategoryResource(resources.ModelResource):
    category = fields.Field(
        column_name='category_name',
        attribute='category',
        widget=ForeignKeyWidget(WordCategory, 'name')  # шукає категорію по name
    )

    class Meta:
        model = WordSubcategory
        fields = ('id', 'name', 'category')
        import_id_fields = ('id',)

class WordSubcategoryInline(admin.TabularInline):  # або StackedInline
    model = WordSubcategory
    extra = 1  # кількість порожніх рядків для додавання нових

@admin.register(WordCategory)
class WordCategoryAdmin(ImportExportModelAdmin):
    resource_class = WordCategoryResource

    list_display = ("id", "name")
    search_fields = ('name',)
    list_editable = ('name',)

    inlines = [WordSubcategoryInline]  # додаємо inline


@admin.register(WordSubcategory)
class WordSubcategoryAdmin(ImportExportModelAdmin):
    resource_class = WordSubcategoryResource

    list_display = ("id", "name", "category")
    search_fields = ('name',)
    list_editable = ('name',)
    list_filter = ("category",)


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



admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)