import sqlite3

from django.core.management.base import BaseCommand
from django.db import connection
from mysite.models import Word

from django.contrib.staticfiles import finders



def records_to_dicts(records):
    result = []
    for rec in records:
        result.append({
            WORD_FIELDS[i]: rec[i] if rec[i] is not None else '' for i in range(len(rec))
            })
    return result

def get_scratch_db(file_path):
    connection = sqlite3.connect(f'{file_path}')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM vocabulary")
    data = records_to_dicts(cursor.fetchall())
    cursor.close()
    connection.close()

    return list(data)

def create_user_vocabulary(vocabulary_list):
    for i in range(len(vocabulary_list)):
        Word.objects.create(
            article = vocabulary_list[i]['article'],
            eng = vocabulary_list[i]['eng'],
            ukr = vocabulary_list[i]['ukr'],
            synonims = vocabulary_list[i]['synonims'],
            word_level = vocabulary_list[i]['word_level'],
            word_type = vocabulary_list[i]['word_type'],
            
        )
#===================================================> VALUES <=======================================================
WORD_FIELDS = ["ID",
                     "status_change_date",
                     "word_level",
                     "word_type",
                     "article",
                     "eng",
                     "transcription",
                     "forms",
                     "status",
                     "ukr",
                     "comment",
                     "synonims",
                     "category",
                     "subcategory"
                     ]

class Command(BaseCommand):
    help = 'Очищує таблицю Vocabulary, скидає лічильник id і (опціонально) наповнює словник заново'

    def add_arguments(self, parser):
        parser.add_argument('--only-reset', action='store_true', help='Лише очистити таблицю і обнулити id')
        parser.add_argument('--with-refresh', action='store_true', help='Оновити словник після очищення')

    def handle(self, *args, **options):
        only_reset = options['only_reset']
        with_refresh = options['with_refresh'] or not only_reset  # якщо нічого не передано або передано аргумент --with-refresh — оновлюємо словник

        # DELETING ALL RECORDS from VOCABULARY
        self.stdout.write("Видаляю всі записи з Vocabulary...")
        Word.objects.all().delete()
        
        
        table_name = Word._meta.db_table
        engine = connection.vendor

        self.stdout.write(f"Обнуляю автоінкремент для {engine}...")

        with connection.cursor() as cursor:
            if engine == 'sqlite':
                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}'")
            elif engine == 'postgresql':
                cursor.execute(f"ALTER SEQUENCE {table_name}_id_seq RESTART WITH 1")
            elif engine == 'mysql':
                cursor.execute(f"ALTER TABLE {table_name} AUTO_INCREMENT = 1")
            else:
                self.stderr.write("Невідома база даних. Скидання автоінкремента не підтримується.")
                return

        # CREATE NEW USER VOCABULARY
        if with_refresh:
            file_path = finders.find('mysite/DB/OXFORD_5000.db')
            # file_path = finders.find('mysite/DB/TEST.db') # TESTING DB
            self.stdout.write("Завантажую словник із зовнішньої бази...")
            vocabulary_list = get_scratch_db(file_path)
            create_user_vocabulary(vocabulary_list)
            self.stdout.write(self.style.SUCCESS(f"Готово: {len(vocabulary_list)} слів додано у Vocabulary."))
        else:
            self.stdout.write(self.style.SUCCESS("Готово: база очищена, автоінкремент обнулено."))
