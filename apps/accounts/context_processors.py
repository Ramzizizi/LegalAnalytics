from .roles import is_analyst, is_editor, get_role_label


def user_roles(request):
    if not request.user.is_authenticated:
        return {'is_analyst': False, 'is_editor': False, 'role_label': None}
    return {
        'is_analyst': is_analyst(request.user),
        'is_editor': is_editor(request.user),
        'role_label': get_role_label(request.user),
    }
