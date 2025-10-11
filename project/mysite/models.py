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

DEFAULT_TEST_DAYS_LIMIT = 0

DEFAULT_PLAYER_MAX_LEVEL = 100

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


#****************************************************************************************** GAME MODELS *************************************************************************************************************

#------------------------------------------------------------------------------------------- PLAYER PROFILE
class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='player_profile')
    name = models.CharField(max_length=200, blank=True, default='STRANGER')
    level = models.IntegerField(default=0)
    max_level = models.IntegerField(default = DEFAULT_PLAYER_MAX_LEVEL)
    current_exp = models.IntegerField(default=0)
    next_level_exp =models.IntegerField(default=100)
    currency = models.IntegerField(default=0)  # ігрова валюта

    # #abilities
    strength = models.IntegerField(default=1)
    dexterity = models.IntegerField(default=1)
    intelligence = models.IntegerField(default=1)
    
    # #characteristics
    damage_physical = models.IntegerField(default=10) # strength
    max_hitpoints = models.IntegerField(default=100) # strength
    hitpoints = models.IntegerField(default=100) # strength
    max_endurance = models.IntegerField(default=100) # strength
    endurance = models.IntegerField(default=100) # strength

    damage_magical = models.IntegerField(default=10) # intelligence
    max_mana = models.IntegerField(default=100) # intelligence
    mana = models.IntegerField(default=100) # intelligence

    dodge = models.FloatField(default=0) #dexterity
    accuracy = models.IntegerField(null=True, blank=True)
    critical_chance = models.FloatField(default=0) #dexterity
    
    armor = models.IntegerField(default=0)
    fire_defence = models.IntegerField(default=0)
    earth_defence = models.IntegerField(default=0)
    water_defence = models.IntegerField(default=0)
    earth_defence = models.IntegerField(default=0)

    # INVENTORY
    # slot_head
    #slot_body
    #slot_legs
    #slot_right_hand
    #slot_left_hand
    #slot_belt_1
    #slot_belt_2
    #slot_belt_3

    def __str__(self):
        return self.name


#------------------------------------------------------------------------------------------- BOSS PROFILE
class BossProfile(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200, blank=True)
    level = models.IntegerField(default=0)

    # # #abilities
    # strength = models.IntegerField(default=1)
    # dexterity = models.IntegerField(default=1)
    # intelligence = models.IntegerField(default=1)

    # #characteristics
    damage_physical = models.IntegerField(default=10) # strength
    hitpoints = models.IntegerField(default=100) # strength
    endurance = models.IntegerField(default=100)

    damage_magical = models.IntegerField(default=10) # intelligence
    mana = models.IntegerField(default=10) # intelligence

    dodge = models.FloatField(default=0) #dexterity
    accuracy = models.IntegerField(null=True, blank=True)
    critical_chance = models.FloatField(default=0) #dexterity

    #defence
    armor = models.IntegerField(default=0)
    defence_fire = models.IntegerField(default=0)
    defence_water = models.IntegerField(default=0)
    defence_earth = models.IntegerField(default=0)
    defence_wind = models.IntegerField(default=0)


#------------------------------------------------------------------------------------------- SKILLS
class Skill(models.Model):
    SKILL_TYPES = [
        ("PHYSICAL_DAMAGE", "Physical damage"),
        ("PHYSICAL_DEFENCE", "Physical defence"),
        ("MAGICAL_DAMAGE", 'Magical damage'),
        ("MAGICAL_DEFENCE", "Magical defence"),
        ('BUFF', 'Buff'),
        ('HEALING', 'Healing')         
    ]
    id = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=20, choices=SKILL_TYPES)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # cost
    mana_cost = models.IntegerField(default=0)
    endurance_cost = models.IntegerField(default=0)

    #damage
    damage_physical = models.IntegerField(default=0)
    damage_fire = models.IntegerField(default=0)
    damage_water = models.IntegerField(default=0)
    damage_earth = models.IntegerField(default=0)
    damage_wind = models.IntegerField(default=0)
    # buffs

    def __str__(self):
        return self.name


class PlayerSkill(models.Model):
    profile = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name="skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    skill_level = models.IntegerField(default=1)
    unlocked = models.BooleanField(default=True)


class BossSkill(models.Model):
    boss = models.ForeignKey(BossProfile, on_delete=models.CASCADE, related_name="skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    difficulty_level = models.IntegerField(default=1)  # наприклад, скільки шкоди наносить бос

#------------------------------------------------------------------------------------------- EQUIPMENT
class Items(models.Model):
    ITEM_TYPES = [
        ("ARMOR", "Armor"),
        ("WEAPON", "Weapon"),
        ("USABLE", 'Usable'),
        ("SHIELD", "Shield"),            
    ]

    name = models.CharField(max_length=100)
    item_type = models.CharField(max_length=10, choices=ITEM_TYPES)
    price = models.IntegerField(default=0)

    # характеристики для броні
    armor = models.IntegerField(null=True, blank=True)
    defence_fire = models.IntegerField(null=True, blank=True)
    defence_earth = models.IntegerField(null=True, blank=True)

    # характеристики для зброї
    damage = models.IntegerField(null=True, blank=True)
    is_damage_physical = models.BooleanField(default=False)
    is_damage_magical = models.BooleanField(default=False)
    is_damage_ice = models.BooleanField(default=False)
    is_damage_earth = models.BooleanField(default=False)
    
    accuracy = models.IntegerField(null=True, blank=True)

#------------------------------------------------------------------------------------------------------ BATTLES
class Battle(models.Model):
    BATTLE_TYPES = [
        ('PVE', 'Player vs Environment'),
        ('PVP', 'Player vs Player')
    ]
    #battle_info
    battle_type = models.CharField(max_length=3, choices=BATTLE_TYPES)
    player_1 = models.ForeignKey(PlayerProfile, null=True, blank=True, on_delete=models.CASCADE, related_name='battles_as_player1')
    
    player_2 = models.ForeignKey(PlayerProfile, null=True, blank=True, on_delete=models.CASCADE, related_name='battles_as_player2')
    
    boss = models.ForeignKey(BossProfile, null=True, blank=True, on_delete=models.CASCADE)
    
    battle_status = models.IntegerField(default=0)

    # battle statuses
    is_active = models.BooleanField(default=True)
    
    # ROUND
    round_status = models.IntegerField(default=0)
    round_number = models.IntegerField(default=1)
    player_1_finished_round = models.BooleanField(default=False)
    player_2_finished_round = models.BooleanField(default=False)
    notified_player = models.ForeignKey(PlayerProfile, null=True, blank=True, on_delete=models.CASCADE)
    winner = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='winner', null=True)
    
  
class BattleTurn(models.Model):
    player_profile = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name='battle_turn')
    battle = models.ForeignKey(Battle, on_delete=models.CASCADE, related_name='battle_turn')
    round_number = models.IntegerField(default=1)

    # player_choice
    player_attack = models.IntegerField(default=0)
    enemy_attack = models.IntegerField(default=0)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)


class BattleRound(models.Model):
    battle = models.ForeignKey(Battle, on_delete=models.CASCADE, related_name='rounds')
    number = models.PositiveIntegerField()
    status = models.IntegerField(choices=[
        (0, "NEW"),
        (1, "STARTED"),
        (2, "INFO_COUNTED"),
        (3, "INFO_SENT"),
    ], default=0)
    player_1_got_update = models.BooleanField(default=False)
    player_2_got_update = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


# ********************************************************************************************** WORDS MODELS ********************************************************************************************

#------------------------------------------------------------------------------------- КАТЕГОРІЇ СЛІВ
class WordCategory(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(
        max_length=255,
        unique=True,
        # default='БЕЗ КАТЕГОРІЇ',
        verbose_name="Категорія"
        )
    class Meta:
        verbose_name = "Категорія слова"
        verbose_name_plural = "Категорії слів"

    def __str__(self):
        return self.name

class WordSubcategory(models.Model):
    id = models.IntegerField(primary_key=True)
    category = models.ForeignKey(
        WordCategory,
        on_delete=models.CASCADE,
        related_name='subcategories')
    name = models.CharField(max_length=255, verbose_name="Підкатегорія")

    class Meta:
        verbose_name = "Підкатегорія слова"
        verbose_name_plural = "Підкатегорії слів"

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
    link = models.CharField(default='')

    category = models.ForeignKey(
        WordCategory,
        null=False,
        on_delete=models.SET_DEFAULT,
        default='БЕЗ КАТЕГОРІЇ'
    )
    
    sub_category = models.ForeignKey(
        WordSubcategory,
        on_delete=models.SET_DEFAULT,
        null=False,
        default='БЕЗ ПІДКАТЕГОРІЇ',
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
            ("LEARNT", "Learnt"),            
        ],
        default="NEW"
    )
    is_freezed = models.BooleanField(default=False)
    status_changed_date = models.DateTimeField(auto_now=True)
    repetition_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'КОРИСТУВАЦЬКЕ СЛОВО'
        verbose_name_plural = "КОРИСТУВАЦЬКІ СЛОВА"

#------------------------------------------------------------------------------------------------- ENGLISH BASIC VOCABULARY WORDS MODEL
class Word(models.Model):
    id = models.IntegerField(primary_key=True)
    word_level = models.CharField(max_length = 2, default = '')
    word_type = models.CharField(max_length=20, default = '')
    article = models.CharField(max_length=4, default='')
    word = models.CharField(max_length=100)
    transcription = models.CharField(max_length=100, default='')
    translation = models.CharField(max_length=100, default='')
    translation_options = models.TextField(default='')
    synonims = models.TextField(max_length=200, default='NO SYNONIMS')
    comment = models.TextField(max_length=200, default='NO COMMENTS')
    link = models.CharField(default='https://www.oxfordlearnersdictionaries.com/wordlists/oxford3000-5000')
    
    # specific verb forms
    is_irregular_verb = models.BooleanField(default = False)
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
    link = models.CharField(default='https://www.verbformen.net/')
    
    # specific verb forms
    is_trennbar_verb = models.BooleanField(default = False)
    is_vokalwechsel_verb = models.BooleanField(default=False)
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

#------------------------------------------------------------------------------------- WORDS STATUSES
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
    status = models.CharField(max_length=20, choices = STATUS_CHOICES, default='NEW')
    repetition_count = models.IntegerField(default=0)
    status_changed_date = models.DateTimeField(auto_now=True)
    was_learnt_once = models.BooleanField(default=False)
    is_freezed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'ENGLISH: Статус слова'
        verbose_name_plural = "ENGLISH: Статуси слів"


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
    status = models.CharField(max_length=20, choices = STATUS_CHOICES, default='NEW')
    repetition_count = models.IntegerField(default=0)
    status_changed_date = models.DateTimeField(auto_now=True)
    was_learnt_once = models.BooleanField(default=False)
    is_freezed = models.BooleanField(default=False)
    class Meta:
        verbose_name = 'DEUTCH: Статус слова'
        verbose_name_plural = "DEUTCH: Статуси слів"

# 
        





