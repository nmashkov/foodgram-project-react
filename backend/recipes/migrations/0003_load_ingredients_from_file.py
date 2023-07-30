import csv

from django.db import migrations

from foodgram.settings import BASE_DIR


def load_data(apps, schema_editor):
    Ingredient = apps.get_model("recipes", "Ingredient")

    data_file = 'ingredients.csv'
    dir = (f'{BASE_DIR}/data/{data_file}')

    with open(dir, 'r', newline='', encoding='utf-8') as ingredients:
        line = csv.reader(ingredients)
        for ingredient in line:
            ing_name, ing_unit = ingredient
            Ingredient.objects.get_or_create(name=ing_name,
                                             measurement_unit=ing_unit)


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.RunPython(load_data)
    ]
