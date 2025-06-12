def generate_shopping_list_text(ingredients):
    lines = ['Список покупок:\n']
    for item in ingredients:
        lines.append(
            f'{item["name"]} - {item["total_amount"]} {item["unit"]}\n'
        )
    return ''.join(lines)
