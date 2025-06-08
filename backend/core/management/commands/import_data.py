import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import ForeignKey

from recipes.models import Ingredient


CSV_DATA_PATH = os.getenv('CSV_DATA_PATH', '')


FILE_MODEL_MAP = {
    'ingredients.csv': {
        'model': Ingredient,
        'fields': ('name', 'measurement_unit'),
    },
}


class Command(BaseCommand):
    help = 'Импортирует данные из всех CSV-файлов в базу данных'

    def handle(self, *args, **options):
        for filename, info in FILE_MODEL_MAP.items():
            model = info['model']
            field_names = info['fields']
            file_path = os.path.join(settings.BASE_DIR, '..', 'data', filename)
            if not CSV_DATA_PATH:
                file_path = os.path.join(
                    settings.BASE_DIR, 'data',
                    filename
                )
            with open(file_path, encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                data = []
                for row in reader:
                    row_data = dict(zip(field_names, row))
                    data.append(model(**self.get_fields(row_data, model)))
                model.objects.bulk_create(data, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS(
                f'Импортирован файл: {filename}')
            )
        self.stdout.write(self.style.SUCCESS('Импорт всех данных завершён!'))

    def get_fields(self, row, model):
        fields = {}
        for field_name, value in row.items():
            field = model._meta.get_field(field_name)
            if isinstance(field, ForeignKey):
                fields[field.name] = field.remote_field.model.objects.filter(
                    pk=value
                ).first()
            else:
                fields[field_name] = value
        return fields
