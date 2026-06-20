"""Валидаторы реквизитов: ИНН (контрольные цифры по алгоритму ФНС) и суммы."""
from django.core.exceptions import ValidationError


def _контрольная_цифра_инн(digits: list[int], coefficients: list[int]) -> int:
    return sum(d * c for d, c in zip(digits, coefficients)) % 11 % 10


def валидатор_инн(value: str) -> None:
    """Проверяет ИНН по алгоритму контрольных цифр (10 цифр — юрлицо, 12 — физлицо/ИП)."""
    if not value.isdigit():
        raise ValidationError('ИНН должен содержать только цифры.')

    if len(value) == 10:
        digits = [int(c) for c in value]
        коэф = [2, 4, 10, 3, 5, 9, 4, 6, 8]
        if _контрольная_цифра_инн(digits[:9], коэф) != digits[9]:
            raise ValidationError('Неверный ИНН юридического лица (контрольная цифра не совпадает).')

    elif len(value) == 12:
        digits = [int(c) for c in value]
        коэф11 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
        коэф12 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
        if _контрольная_цифра_инн(digits[:10], коэф11) != digits[10]:
            raise ValidationError('Неверный ИНН физического лица (11-я контрольная цифра).')
        if _контрольная_цифра_инн(digits[:11], коэф12) != digits[11]:
            raise ValidationError('Неверный ИНН физического лица (12-я контрольная цифра).')

    else:
        raise ValidationError(f'ИНН должен содержать 10 (юрлицо) или 12 (физлицо) цифр, получено: {len(value)}.')


def валидатор_сумма_положительная(value) -> None:
    if value is not None and value <= 0:
        raise ValidationError('Сумма должна быть больше нуля.')
