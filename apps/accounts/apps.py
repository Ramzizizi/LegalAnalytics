from django.apps import AppConfig
from django.db.models.signals import post_migrate


def _create_groups(sender, **kwargs):
    from django.contrib.auth.models import Group
    from .roles import ALL_ROLES
    for name in ALL_ROLES:
        Group.objects.get_or_create(name=name)


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = 'Пользователи'

    def ready(self):
        post_migrate.connect(_create_groups, sender=self)
