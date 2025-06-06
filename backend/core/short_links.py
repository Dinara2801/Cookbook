import base64


def encode_id(recipe_id: int) -> str:
    """Функция кодирования id рецепта для короткой ссылки."""
    return base64.urlsafe_b64encode(f"{recipe_id}".encode()).decode()


def decode_id(encoded: str) -> int:
    """Функция декодирования id рецепта в короткой ссылки."""
    try:
        decoded = base64.urlsafe_b64decode(encoded).decode()
        return int(decoded)
    except Exception:
        return None
