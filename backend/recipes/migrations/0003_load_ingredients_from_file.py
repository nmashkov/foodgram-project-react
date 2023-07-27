import csv

from django.db import migrations
from foodgram_backend.settings import BASE_DIR


def load_data(apps, schema_editor):
    Ingredient = apps.get_model("recipes", "Ingredient")

    data_file = 'ingredients.csv'
    dir = (f'{BASE_DIR}/data/{data_file}')

    with open(dir, 'r', encoding='utf-8') as ingredients:
        line = csv.reader(ingredients)
        for ingredient in line:
            in_name, in_unit = ingredient[0], ingredient[1]
            Ingredient(name=in_name,
                       measurement_unit=in_unit,
                       ).save()


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.RunPython(load_data)
    ]
