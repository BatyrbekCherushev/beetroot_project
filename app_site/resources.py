# app_site/resources.py
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import UserCustomWord, WordCategory

class UserCustomWordResource(resources.ModelResource):
    category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(WordCategory, field='name')
    )

    sub_category = fields.Field(
        column_name='category',
        attribute='category',
        widget=ForeignKeyWidget(WordCategory, field='name')
    )

    class Meta:
        model = UserCustomWord
        fields = (
            'id'
            'language',
            'word_level',
            'word_type',
            'article',
            'word',
            'translation',
            'transcription',
            'translation',
            'translation_options',
            'synonims',
            'comment',
            'link',
            'category',
            'sub_category',

        )