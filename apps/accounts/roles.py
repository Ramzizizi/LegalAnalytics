ROLE_EDITOR = 'Редактор базы'
ROLE_ANALYST = 'Аналитик'
ROLE_READER = 'Читатель'

ALL_ROLES = [ROLE_EDITOR, ROLE_ANALYST, ROLE_READER]


def is_editor(user):
    return user.is_authenticated and (
        user.is_staff or user.groups.filter(name=ROLE_EDITOR).exists()
    )


def is_analyst(user):
    return user.is_authenticated and (
        user.is_staff or user.groups.filter(name__in=[ROLE_EDITOR, ROLE_ANALYST]).exists()
    )


def get_role_label(user):
    if not user.is_authenticated:
        return None
    if user.is_superuser:
        return 'Суперпользователь'
    if user.is_staff or user.groups.filter(name=ROLE_EDITOR).exists():
        return ROLE_EDITOR
    if user.groups.filter(name=ROLE_ANALYST).exists():
        return ROLE_ANALYST
    if user.groups.filter(name=ROLE_READER).exists():
        return ROLE_READER
    return None
