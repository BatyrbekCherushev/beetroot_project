<h1 style = "text-align:center"><b>HEROES OF WORDS</b></h1>



## СТРУКТУРА ПРОЕКТА

* сторінка профілю користувача
* сторінка словника
* сторінка "зброярні" - ігрового магазину
* сторінка арени


## Основний функціонал

* надання користувачу можливості вивчення слів по інтервальному методу
* можливість купляти амуніцію для свого персонажу для впокращення характеристик персонажа в боях арени
* ведення боїв ПВП по принципу комбатс




* кожного дня створювати список слів для вивчення на основі базового словника OXFORD 5000
* ведення статистики для кожного користувача
    * статус слова міняється по методу інтервального вивчення
* користувач при вивченні слова отримує валюту, за яку можна купляти амуніцію для свого персонажадля участі у битвах на арені
* арена зроблена по принципу комбатс і надає можливість онлайн гри, гри із залишеним персонажем. За перемогу користувач отримує валюту
* зброярня - реалізована по приницпу магазину товарів

## CUSTOM EVENTS

* pages library, vocabulary:
    * `user_info_refreshed`
    * `create_study_list`
    * `statistics_refreshed`
    * `test_words`
    * `study_words`
    * `settings_refreshed`



## ІМПОРТ БАЗИ СЛІВ в АДМІНЦІ ЧЕРЕЗ ЕКСЕЛЬ

для цього

pip install django-import-export

Додай його в settings.py → INSTALLED_APPS:

INSTALLED_APPS = [
    ...,
    'import_export',
]



Перезапусти сервер:

python manage.py runserver

За замовчуванням він підтримує такі формати:

CSV (.csv)

Excel (.xls, .xlsx)

TSV (табличний текст)

JSON, YAML

Але ⚠️ для Excel (.xlsx) потрібна додаткова бібліотека openpyxl.


Встановити openpyxl:

pip install openpyxl


Перезапустити сервер.

В адмінці при імпорті з’явиться можливість вибрати формат .xlsx.





-----------------

Django обмежує кількість полів у POST-запиті (щоб захистити від DoS-атак). За замовчуванням DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000.

Коли імпортуєш великий .xlsx, адмінка намагається створити GET/POST-параметри для кожної клітинки, і це перевищує ліміт.

Як виправити

В settings.py збільшити ліміт:

# Наприклад, дозволити до 100_000 полів
DATA_UPLOAD_MAX_NUMBER_FIELDS = 100000


Перезапусти сервер.

--------------------------------

к в адмінку додати функціонал видалення і обнулення лічильика айді
ChatGPT said:

Окей, зрозумів 👍 Тобі потрібно зробити в Django Admin кнопку/дію, яка буде одночасно:

Видаляти всі записи моделі (Word).

Обнуляти AUTOINCREMENT поля id, щоб наступний запис починався з 1.

Зробимо це через custom admin action.

🔹 Приклад для моделі Word
from django.contrib import admin
from django.db import connection
from .models import Word

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
