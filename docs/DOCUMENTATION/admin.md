## 📍ІМПОРТ БАЗИ СЛІВ в АДМІНЦІ з інших файлів

для цього

* pip install django-import-export
* Додай його в settings.py → INSTALLED_APPS:

```python
# settings.py
INSTALLED_APPS = [
    ...,
    'import_export',
]
```
* Коли ти підключаєш import_export в admin.py, ти можеш створити спеціальний клас-ресурс, що наслідує resources.ModelResource. У ньому описується:
    * яка модель використовується;
    * які поля імпортувати/експортувати;
    * додаткові правила (валидація, clean, before_import, after_import тощо).

```python
# admin.py
from import_export.admin import ImportExportModelAdmin
from import_export import resources

class WordResource(resources.ModelResource):
    class Meta:
        model = Word
        # НЕ включаємо "id" у fields
        fields = (
            "word_level", "word_type", "article", "word",
            "transcription", "translation", "translation_options", "synonims",
            "comment", "category", "sub_category", "is_irregular_verb",
            "is_modal_verb"
        )
        import_id_fields = ("word",)  # або будь-яке унікальне поле для оновлення
```

тобто адмінка моделі ВОРД вже наслідує від іншого класу, щоб можна було імпорт експорт робити в адмінці

```python
# admin.py

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
        'synonims', 'comment', 'category', 'sub_category',
        'is_irregular_verb', 'is_modal_verb'
    )
    list_editable = (
        "word_level", "word_type", "article", "word", "transcription",
        "translation", "translation_options", "synonims", "comment",
        "category", "sub_category", "is_irregular_verb", "is_modal_verb"
    )
    readonly_fields = ('id',)
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
```
* Перезапусти сервер: `python manage.py runserver`




## 📍Можливість імпорту в адмінці файлів ексель

За замовчуванням він підтримує такі формати:

CSV (.csv)

Excel (.xls, .xlsx)

TSV (табличний текст)

JSON, YAML

Але ⚠️ для Excel (.xlsx) потрібна додаткова бібліотека openpyxl.


* Встановити openpyxl: `pip install openpyxl`
* Перезапустити сервер. `python manage.py runserver`
* В адмінці при імпорті з’явиться можливість вибрати формат .xlsx.



## 📍Збільшення кількості запитів до сервера, щоб можна було імпортувати більше значень з файлу

* Django обмежує кількість полів у POST-запиті (щоб захистити від DoS-атак). За замовчуванням DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000.
* Коли імпортуєш великий .xlsx, адмінка намагається створити GET/POST-параметри для кожної клітинки, і це перевищує ліміт.

Як виправити

* В settings.py збільшити ліміт:
    * Наприклад, дозволити до 100_000 полів
```python
# settings.py
DATA_UPLOAD_MAX_NUMBER_FIELDS = 100000
```

* Перезапусти сервер.`python manage.py runserver`

---


## 📍функціонал видалення словника і обнулення лічильика айді
ChatGPT said:

Окей, зрозумів 👍 Тобі потрібно зробити в Django Admin кнопку/дію, яка буде одночасно:

Видаляти всі записи моделі (Word).

Обнуляти AUTOINCREMENT поля id, щоб наступний запис починався з 1.

Зробимо це через custom admin action.

🔹 Приклад для моделі Word
```python
from django.contrib import admin
from django.db import connection
from .models import Word
```

```python
@admin.register(Word)
class WordAdmin(ImportExportModelAdmin):
    resource_class = WordResource
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
    "is_irregular_verb",
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
    "is_irregular_verb",
    "is_modal_verb")
    readonly_fields = ('id',)

    actions = ["delete_all_and_reset_id"]

    def delete_all_and_reset_id(self, request, queryset):
        # 1. Видаляємо всі записи
        Word.objects.all().delete()

        # 2. Обнуляємо лічильник id (AUTOINCREMENT)
        table_name = Word._meta.db_table
        with connection.cursor() as cursor:
            # Для SQLite
            if 'sqlite' in connection.settings_dict['ENGINE']:
                cursor.execute(f'DELETE FROM sqlite_sequence WHERE name="{table_name}";')
            # Для PostgreSQL
            elif 'postgresql' in connection.settings_dict['ENGINE']:
                cursor.execute(f'ALTER SEQUENCE {table_name}_id_seq RESTART WITH 1;')
            # Для MySQL
            elif 'mysql' in connection.settings_dict['ENGINE']:
                cursor.execute(f'ALTER TABLE {table_name} AUTO_INCREMENT = 1;')

        self.message_user(request, "Всі записи видалено, ID обнулено!")
    
    delete_all_and_reset_id.short_description = "Видалити всі слова і обнулити ID"

```

🔹 Як це працює

У адмінці Word у списку записів з’явиться Dropdown Actions → там твоя дія “Видалити всі слова і обнулити ID”.

При виконанні:

всі слова видаляються;

AUTOINCREMENT поля id обнуляється;

наступний доданий запис отримає id = 1.