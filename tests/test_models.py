import pytest
from django.contrib.auth.models import User
from apps.catalog.models import Контрагент, Юрист
from apps.templates_engine.models import ШаблонДокумента, Переменная
from apps.documents.models import СгенерированныйДокумент


@pytest.fixture
def контрагент(db):
    return Контрагент.objects.create(
        наименование='ООО Ромашка',
        тип='юр',
        инн='7707083893',
        кпп='770701001',
        адрес='г. Москва, ул. Ленина, 1',
    )


@pytest.fixture
def шаблон(db, tmp_path):
    docx = tmp_path / 'test.docx'
    docx.write_bytes(b'PK')  # минимальный docx-контент
    шаблон = ШаблонДокумента.objects.create(
        название='Договор оказания услуг',
        тип='услуги',
        описание='Тестовый шаблон',
    )
    шаблон.файл.name = 'templates/test.docx'
    шаблон.save()
    return шаблон


@pytest.fixture
def пользователь(db):
    return User.objects.create_user(
        username='testuser',
        first_name='Иван',
        last_name='Иванов',
        password='testpass123',
    )


@pytest.mark.django_db
class TestКонтрагент:
    def test_создание(self, контрагент):
        assert контрагент.pk is not None
        assert контрагент.наименование == 'ООО Ромашка'
        assert контрагент.инн == '7707083893'

    def test_str(self, контрагент):
        assert 'ООО Ромашка' in str(контрагент)
        assert '7707083893' in str(контрагент)

    def test_тип_по_умолчанию(self, db):
        # ИНН валидный (12 знаков, корректные контрольные цифры) — данные
        # должны соответствовать тому, что реально проходит форму.
        к = Контрагент.objects.create(наименование='Тест', инн='770708389324')
        assert к.тип == 'юр'


@pytest.mark.django_db
class TestЮрист:
    def test_создание(self, пользователь):
        юрист = Юрист.objects.create(пользователь=пользователь, должность='Старший юрист')
        assert юрист.pk is not None
        assert юрист.должность == 'Старший юрист'

    def test_str(self, пользователь):
        юрист = Юрист.objects.create(пользователь=пользователь)
        assert 'Иванов' in str(юрист) or 'testuser' in str(юрист)


@pytest.mark.django_db
class TestШаблонДокумента:
    def test_создание(self, шаблон):
        assert шаблон.pk is not None
        assert шаблон.активен is True

    def test_str(self, шаблон):
        assert шаблон.название in str(шаблон)

    def test_переменные(self, шаблон):
        п = Переменная.objects.create(
            шаблон=шаблон,
            ключ='contragent_name',
            подпись='Наименование контрагента',
            тип_данных='str',
        )
        assert п.шаблон == шаблон
        assert шаблон.переменные.count() == 1

    def test_уникальность_ключа(self, шаблон):
        Переменная.objects.create(шаблон=шаблон, ключ='summa', подпись='Сумма')
        with pytest.raises(Exception):
            Переменная.objects.create(шаблон=шаблон, ключ='summa', подпись='Дубль')


@pytest.mark.django_db
class TestСгенерированныйДокумент:
    def test_создание(self, шаблон, контрагент, пользователь):
        doc = СгенерированныйДокумент.objects.create(
            шаблон=шаблон,
            контрагент=контрагент,
            автор=пользователь,
            значения={'summa': '100000', 'data': '01.01.2025'},
        )
        assert doc.pk is not None
        assert doc.статус == 'черновик'

    def test_str(self, шаблон, контрагент, пользователь):
        doc = СгенерированныйДокумент.objects.create(
            шаблон=шаблон, контрагент=контрагент, автор=пользователь
        )
        assert 'Ромашка' in str(doc)
        assert 'Договор' in str(doc)
