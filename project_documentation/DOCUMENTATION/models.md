
[![ER-діаграма](../RES/er_diagram_colored.png)](../RES/er_diagram_colored.png)


## 📍 SETTINGS, USERS, PROFILE
### 📋UserSettings

### 📋UserProfile

## 📍CATEGORIES, WORD VOCABULARIES MODELS

### 📋💾 WordCategory, WordSubCategory
* можна імпортувати / експортувати з файла ексель через адмiнку проекту

`models.py`
```python
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
```

`admin.py`
```python
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
```

### 📋WordSubcategory

### 📋UserCustomWord

### 📋💾Word
* можна імпортувати / експортувати з файла ексель через адмiнку проекту

### 📋UserWordsProgress

### 📋💾 WordDeutch
* можна імпортувати / експортувати з файла ексель через адмiнку проекту

### 📋UserWordsDeutchProgress

## 📍GAME MODELS

### 📋PlayerProfile
### 📋💾 BossProfile
* можна імпортувати / експортувати з файла ексель через адмiнку проекту

`models.py`
```python
class BossProfile(models.Model):
    name = models.CharField(max_length=200, blank=True)
    level = models.IntegerField(default=0)

    # #abilities
    strength = models.IntegerField(default=1)
    dexterity = models.IntegerField(default=1)
    intelligence = models.IntegerField(default=1)

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
```
`admin.py`
```python
class BossProfileResource(resources.ModelResource):
    class Meta:
        model = BossProfile
        fields = (
        'id',
        'name', 'level', 'strength', 'dexterity', 'intelligence',
        'damage_physical', 'endurance', 'hitpoints',
        'damage_magical', 'mana',
        'dodge', 'critical_chance', 'accuracy',
        'armor', 'defence_fire', 'defence_earth', 'defence_water', 'defence_wind',
    )

        export_order = fields

        import_id_fields = ("id",)  
        """означає, що під час імпорту система буде шукати існуючі записи у базі за полем id.
            Якщо запис з таким id існує → він оновлюється. 
            Якщо запису з таким id немає → створюється новий запис."""
        

@admin.register(BossProfile)
class BossProfileAdmin(ImportExportModelAdmin):
    resource_class = BossProfileResource
    list_display = (
        'id',
        'name', 'level', 'strength', 'dexterity', 'intelligence',
        'damage_physical', 'endurance', 'hitpoints',
        'damage_magical', 'mana',
        'dodge', 'critical_chance', 'accuracy',
        'armor', 'defence_fire', 'defence_earth', 'defence_water', 'defence_wind',
    )

    list_editable = (
        'level', 'strength', 'dexterity', 'intelligence',
        'damage_physical', 'endurance', 'hitpoints',
        'damage_magical', 'mana',
        'dodge', 'critical_chance', 'accuracy',
        'armor', 'defence_fire', 'defence_earth', 'defence_water', 'defence_wind',
    )

    list_filter = ('level', 'strength', 'dexterity', 'intelligence', 'name')
    search_fields = ('name',)
```
### 📋💾 Skill
* можна імпортувати / експортувати з файла ексель через адмунку проекту

`models.py`
```python
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
```

`admin.py`
```python
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
```
### 📋PlayerSkill
### 📋Items
```python
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
```
### 📋Battle
```python
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
```

### 📋BattleTurn
```python
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
```

### 📋

### 📋

### 📋

### 📋


