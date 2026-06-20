"""
Создаёт группы и назначает им права доступа.
Запускать при первом развёртывании: python manage.py setup_roles
"""
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from apps.accounts.utils import РОЛЬ_АДМИН, РОЛЬ_ЮРИСТ, РОЛЬ_ПОМОЩНИК


def _права(app_label: str, model: str, *actions: str) -> list[Permission]:
    try:
        ct = ContentType.objects.get(app_label=app_label, model=model)
        return list(Permission.objects.filter(
            content_type=ct,
            codename__in=[f'{a}_{model}' for a in actions],
        ))
    except ContentType.DoesNotExist:
        return []


class Command(BaseCommand):
    help = 'Создаёт группы ролей с нужными правами доступа'

    def handle(self, *args, **options):
        # Модели (имена моделей в нижнем регистре для ORM)
        ШАБЛОН = 'шаблондокумента'
        ПЕРЕМЕННАЯ = 'переменная'
        КОНТРАГЕНТ = 'контрагент'
        ЮРИСТ_М = 'юрист'
        ДОКУМЕНТ = 'сгенерированныйдокумент'

        определения = {
            РОЛЬ_АДМИН: (
                _права('templates_engine', ШАБЛОН, 'add', 'change', 'delete', 'view') +
                _права('templates_engine', ПЕРЕМЕННАЯ, 'add', 'change', 'delete', 'view') +
                _права('catalog', КОНТРАГЕНТ, 'add', 'change', 'view') +
                _права('documents', ДОКУМЕНТ, 'view')
            ),
            РОЛЬ_ЮРИСТ: (
                _права('templates_engine', ШАБЛОН, 'view') +
                _права('templates_engine', ПЕРЕМЕННАЯ, 'view') +
                _права('catalog', КОНТРАГЕНТ, 'add', 'change', 'view') +
                _права('catalog', ЮРИСТ_М, 'view') +
                _права('documents', ДОКУМЕНТ, 'add', 'change', 'view')
            ),
            РОЛЬ_ПОМОЩНИК: (
                _права('templates_engine', ШАБЛОН, 'view') +
                _права('catalog', КОНТРАГЕНТ, 'view') +
                _права('documents', ДОКУМЕНТ, 'add', 'view')
            ),
        }

        for название, права in определения.items():
            группа, создана = Group.objects.get_or_create(name=название)
            группа.permissions.set(права)
            статус = 'создана' if создана else 'обновлена'
            self.stdout.write(
                self.style.SUCCESS(f'✓ Группа «{название}» {статус} ({len(права)} прав)')
            )

        self.stdout.write(self.style.SUCCESS('\nРоли настроены.'))
