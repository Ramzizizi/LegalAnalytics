import pytest
from django.contrib.auth.models import User, Group
from django.test import Client
from apps.accounts.utils import РОЛЬ_ЮРИСТ
from apps.catalog.models import Контрагент
from apps.templates_engine.models import ШаблонДокумента
from apps.documents.models import СгенерированныйДокумент


@pytest.fixture
def юрист(db):
    from django.core.management import call_command
    call_command('setup_roles', verbosity=0)
    u = User.objects.create_user('j_юрист', password='pass')
    u.groups.add(Group.objects.get(name=РОЛЬ_ЮРИСТ))
    return u


@pytest.fixture
def шаблон(db):
    return ШаблонДокумента.objects.create(
        название='Договор услуг', тип='услуги', файл='templates/test.docx'
    )


@pytest.fixture
def контрагент(db):
    return Контрагент.objects.create(наименование='ООО Тест', инн='7707083893')


@pytest.fixture
def документы(юрист, шаблон, контрагент):
    docs = []
    for i in range(12):
        docs.append(СгенерированныйДокумент.objects.create(
            шаблон=шаблон, автор=юрист, контрагент=контрагент,
            статус='готов' if i % 2 == 0 else 'ошибка',
        ))
    return docs


@pytest.fixture
def клиент(юрист):
    c = Client()
    c.force_login(юрист)
    return c


@pytest.mark.django_db
class TestЖурнал:
    def test_страница_доступна(self, клиент, документы):
        resp = клиент.get('/journal/')
        assert resp.status_code == 200

    def test_пагинация_первая_страница_10(self, клиент, документы):
        resp = клиент.get('/journal/')
        assert len(resp.context['docs'].object_list) == 10

    def test_пагинация_вторая_страница(self, клиент, документы):
        resp = клиент.get('/journal/?page=2')
        assert len(resp.context['docs'].object_list) == 2

    def test_фильтр_по_статусу_готов(self, клиент, документы):
        resp = клиент.get('/journal/?статус=готов')
        for doc in resp.context['docs']:
            assert doc.статус == 'готов'

    def test_фильтр_по_статусу_ошибка(self, клиент, документы):
        resp = клиент.get('/journal/?статус=ошибка')
        for doc in resp.context['docs']:
            assert doc.статус == 'ошибка'

    def test_поиск_по_имени_контрагента(self, клиент, документы):
        resp = клиент.get('/journal/?q=ООО Тест')
        assert resp.context['total'] == 12

    def test_поиск_без_совпадений(self, клиент, документы):
        resp = клиент.get('/journal/?q=несуществующий контрагент')
        assert resp.context['total'] == 0

    def test_фильтр_по_типу(self, клиент, документы):
        resp = клиент.get('/journal/?тип=услуги')
        assert resp.context['total'] == 12

    def test_фильтр_по_типу_без_совпадений(self, клиент, документы):
        resp = клиент.get('/journal/?тип=иск')
        assert resp.context['total'] == 0

    def test_htmx_возвращает_партиал(self, клиент, документы):
        resp = клиент.get(
            '/journal/?q=Тест',
            HTTP_HX_REQUEST='true',
            HTTP_HX_TARGET='journal-body',
        )
        assert resp.status_code == 200
        # Партиал не содержит полного HTML-скелета
        content = resp.content.decode()
        assert '<html' not in content
        assert '<tr' in content

    def test_чужие_документы_не_видны(self, клиент, шаблон, контрагент, db):
        другой = User.objects.create_user('другой', password='pass')
        from django.core.management import call_command
        call_command('setup_roles', verbosity=0)
        другой.groups.add(Group.objects.get(name=РОЛЬ_ЮРИСТ))
        СгенерированныйДокумент.objects.create(
            шаблон=шаблон, автор=другой, контрагент=контрагент
        )
        resp = клиент.get('/journal/')
        # Журнал юриста пуст — он не создавал документов
        assert resp.context['total'] == 0
