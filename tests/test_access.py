import pytest
from django.contrib.auth.models import User, Group
from django.test import Client
from apps.accounts.utils import в_группе, РОЛЬ_АДМИН, РОЛЬ_ЮРИСТ, РОЛЬ_ПОМОЩНИК, ВСЕ_РОЛИ
from apps.catalog.models import Контрагент
from apps.templates_engine.models import ШаблонДокумента
from apps.documents.models import СгенерированныйДокумент


# ──────────────── фикстуры ────────────────

@pytest.fixture
def группы(db):
    from django.core.management import call_command
    call_command('setup_roles', verbosity=0)
    return {
        РОЛЬ_АДМИН: Group.objects.get(name=РОЛЬ_АДМИН),
        РОЛЬ_ЮРИСТ: Group.objects.get(name=РОЛЬ_ЮРИСТ),
        РОЛЬ_ПОМОЩНИК: Group.objects.get(name=РОЛЬ_ПОМОЩНИК),
    }


@pytest.fixture
def пользователь_юрист(группы):
    u = User.objects.create_user('test_юрист', password='pass')
    u.groups.add(группы[РОЛЬ_ЮРИСТ])
    return u


@pytest.fixture
def пользователь_помощник(группы):
    u = User.objects.create_user('test_помощник', password='pass')
    u.groups.add(группы[РОЛЬ_ПОМОЩНИК])
    return u


@pytest.fixture
def пользователь_без_роли(db):
    return User.objects.create_user('test_без_роли', password='pass')


@pytest.fixture
def superuser(db):
    return User.objects.create_superuser('test_super', password='pass')


@pytest.fixture
def шаблон(db):
    return ШаблонДокумента.objects.create(
        название='Тест', тип='иное', файл='templates/test.docx'
    )


@pytest.fixture
def контрагент(db):
    return Контрагент.objects.create(наименование='ООО Тест', инн='7707083893')


@pytest.fixture
def документ(пользователь_юрист, шаблон, контрагент):
    return СгенерированныйДокумент.objects.create(
        шаблон=шаблон, автор=пользователь_юрист,
        контрагент=контрагент, статус='готов',
    )


# ──────────────── тесты в_группе ────────────────

@pytest.mark.django_db
class TestВГруппе:
    def test_суперпользователь_всегда_в_группе(self, superuser):
        assert в_группе(superuser, РОЛЬ_ЮРИСТ) is True
        assert в_группе(superuser, РОЛЬ_ПОМОЩНИК) is True
        assert в_группе(superuser, РОЛЬ_АДМИН) is True

    def test_юрист_в_своей_группе(self, пользователь_юрист):
        assert в_группе(пользователь_юрист, РОЛЬ_ЮРИСТ) is True

    def test_юрист_не_в_чужой_группе(self, пользователь_юрист):
        assert в_группе(пользователь_юрист, РОЛЬ_АДМИН) is False
        assert в_группе(пользователь_юрист, РОЛЬ_ПОМОЩНИК) is False

    def test_помощник_в_своей_группе(self, пользователь_помощник):
        assert в_группе(пользователь_помощник, РОЛЬ_ПОМОЩНИК) is True

    def test_без_роли_нигде_нет(self, пользователь_без_роли):
        for роль in ВСЕ_РОЛИ:
            assert в_группе(пользователь_без_роли, роль) is False

    def test_неаутентифицированный(self, db):
        from django.contrib.auth.models import AnonymousUser
        assert в_группе(AnonymousUser(), РОЛЬ_ЮРИСТ) is False


# ──────────────── тесты доступа к views ────────────────

@pytest.mark.django_db
class TestДоступКViews:
    def _клиент(self, user):
        c = Client()
        c.force_login(user)
        return c

    def test_анонимный_редиректится_на_логин(self):
        c = Client()
        for url in ['/create/', '/create/1/']:
            resp = c.get(url)
            assert resp.status_code == 302
            assert '/accounts/login/' in resp['Location']

    def test_юрист_видит_страницу_выбора(self, пользователь_юрист, шаблон):
        resp = self._клиент(пользователь_юрист).get('/create/')
        assert resp.status_code == 200

    def test_помощник_видит_страницу_выбора(self, пользователь_помощник, шаблон):
        resp = self._клиент(пользователь_помощник).get('/create/')
        assert resp.status_code == 200

    def test_без_роли_редиректится(self, пользователь_без_роли, шаблон):
        resp = self._клиент(пользователь_без_роли).get('/create/')
        assert resp.status_code == 302

    def test_суперпользователь_имеет_доступ(self, superuser, шаблон):
        resp = self._клиент(superuser).get('/create/')
        assert resp.status_code == 200


# ──────────────── тесты изоляции документов ────────────────

@pytest.mark.django_db
class TestИзоляцияДокументов:
    def test_автор_видит_свой_документ(self, пользователь_юрист, документ):
        c = Client()
        c.force_login(пользователь_юрист)
        resp = c.get(f'/{документ.pk}/')
        assert resp.status_code == 200

    def test_чужой_пользователь_не_видит_документ(self, пользователь_помощник, документ, шаблон, контрагент):
        c = Client()
        c.force_login(пользователь_помощник)
        resp = c.get(f'/{документ.pk}/')
        assert resp.status_code == 404

    def test_суперпользователь_не_видит_чужой_документ_через_ui(self, superuser, документ):
        # UI намеренно фильтрует по автору; суперпользователь использует admin
        c = Client()
        c.force_login(superuser)
        resp = c.get(f'/{документ.pk}/')
        assert resp.status_code == 404
