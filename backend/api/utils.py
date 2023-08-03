from datetime import datetime

from django.http import HttpResponse


def data_generation(user, ingredients):
    """Функция создания списка ингредиентов в текстовом файле."""
    today = datetime.today()
    shopping_list = (
        f'Список покупок для: {user.get_full_name()}\n\n'
        f'Дата: {today:%Y-%m-%d}\n\n'
    )
    shopping_list += '\n'.join([
        f'- {ingredient["ingredient__name"]} '
        f'({ingredient["ingredient__measurement_unit"]})'
        f' - {ingredient["amount"]}'
        for ingredient in ingredients
    ])
    shopping_list += f'\n\nFoodgram ({today:%Y})'
    filename = f'{user.username}_shopping_list.txt'
    response = HttpResponse(
        shopping_list,
        content_type='text/plain; charset=utf8'
    )
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response
