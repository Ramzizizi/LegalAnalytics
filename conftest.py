"""
Исправление совместимости Django 5.1 + Python 3.14:
BaseContext.__copy__ использует copy(super()), что не работает в Python 3.14,
так как super()-объект не поддерживает __dict__ для произвольных атрибутов.

На Python < 3.14 штатный метод работает корректно, поэтому патч не применяем.
"""
import sys

if sys.version_info >= (3, 14):
    import django.template.context as _ctx

    def _patched_copy(self):
        duplicate = self.__class__.__new__(self.__class__)
        duplicate.__dict__.update(self.__dict__)
        duplicate.dicts = self.dicts[:]
        return duplicate

    _ctx.BaseContext.__copy__ = _patched_copy
