"""Роли и разграничение доступа: имена групп и декораторы проверки членства."""
from functools import wraps
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

РОЛЬ_АДМИН = 'Администратор шаблонов'
РОЛЬ_ЮРИСТ = 'Юрист'
РОЛЬ_ПОМОЩНИК = 'Помощник'

ВСЕ_РОЛИ = (РОЛЬ_АДМИН, РОЛЬ_ЮРИСТ, РОЛЬ_ПОМОЩНИК)


def в_группе(user, *group_names: str) -> bool:
    """Проверяет, входит ли пользователь хотя бы в одну из указанных групп."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=group_names).exists()


def требует_группу(*group_names: str):
    """Декоратор: требует членства в одной из указанных групп. Редиректит на логин."""
    def check(user):
        return в_группе(user, *group_names)
    return user_passes_test(check, login_url='/accounts/login/')


def требует_группу_или_403(*group_names: str):
    """Декоратор: требует членства в группе, иначе 403."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not в_группе(request.user, *group_names):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
