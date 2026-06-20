"""Тесты генерации документа, скачивания и динамической формы."""
import datetime

import pytest
from django.contrib.auth.models import User, Group
from django.test import Client

from apps.accounts.utils import РОЛЬ_ЮРИСТ
from apps.catalog.models import Контрагент
from apps.templates_engine.models import ШаблонДокумента, Переменная
from apps.documents.models import СгенерированныйДокумент
from apps.documents.forms import ДинамическаяФорма


@pytest.fixture
def роли(db):
    from django.core.management import call_command
    call_command('setup_roles', verbosity=0)


@pytest.fixture
def юрист(db, роли):
    u = User.objects.create_user('док_юрист', password='pass')
    u.groups.add(Group.objects.get(name=РОЛЬ_ЮРИСТ))
    return u


@pytest.fixture
def контрагент(db):
    return Контрагент.objects.create(
        наименование='ООО Тест', инн='7707083893',
        кпп='770701001', адрес='г. Москва',
    )


@pytest.fixture
def медиа(settings, tmp_path):
    """Изолированный MEDIA_ROOT с реальным .docx-шаблоном внутри.

    Копируем шаблон из word_templates в tmp_path/templates, чтобы
    шаблон.файл.path (он строится от MEDIA_ROOT) указывал на реальный файл,
    а сгенерированные документы не засоряли настоящую папку media/.
    """
    import shutil
    settings.MEDIA_ROOT = tmp_path
    dst = tmp_path / 'templates'
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy(settings.WORD_TEMPLATES_DIR / 'dogovor_uslug.docx', dst / 'dogovor_uslug.docx')
    return tmp_path


@pytest.fixture
def шаблон(db):
    """Шаблон с реальным .docx-файлом из word_templates (Договор услуг)."""
    s = ШаблонДокумента.objects.create(
        название='Договор оказания услуг', тип='услуги',
        файл='templates/dogovor_uslug.docx',
    )
    # Переменные, нужные шаблону dogovor_uslug.docx
    поля = [
        ('number', 'str'), ('data', 'date'), ('contragent_director', 'str'),
        ('executor_name', 'str'), ('lawyer_name', 'str'), ('services_description', 'str'),
        ('summa', 'str'), ('summa_words', 'str'), ('payment_days', 'int'),
        ('date_start', 'date'), ('date_end', 'date'),
    ]
    for i, (ключ, тип) in enumerate(поля):
        Переменная.objects.create(шаблон=s, ключ=ключ, подпись=ключ, тип_данных=тип, порядок=i)
    return s


@pytest.fixture
def клиент(юрист):
    c = Client()
    c.force_login(юрист)
    return c


def _данные_формы(контрагент):
    return {
        'контрагент': контрагент.pk,
        'number': '001/2025',
        'data': '2025-06-19',
        'contragent_director': 'Иванов И.И.',
        'executor_name': 'ООО Юрпомощь',
        'lawyer_name': 'Петров П.П.',
        'services_description': 'юридическое сопровождение',
        'summa': '100000',
        'summa_words': 'сто тысяч рублей',
        'payment_days': '5',
        'date_start': '2025-01-01',
        'date_end': '2025-12-31',
    }


@pytest.mark.django_db
class TestГенерация:
    def test_post_создаёт_документ_готов(self, клиент, шаблон, контрагент, медиа):
        resp = клиент.post(f'/create/{шаблон.pk}/', _данные_формы(контрагент))
        assert resp.status_code == 302  # редирект на detail

        doc = СгенерированныйДокумент.objects.get(автор__username='док_юрист')
        # Без LibreOffice статус может быть 'готов' (docx сгенерирован, PDF пропущен)
        assert doc.статус == 'готов', f'ошибка: {doc.ошибка}'
        assert doc.файл_docx.name
        # docx-файл реально создан
        assert (медиа / doc.файл_docx.name).exists()

    def test_post_невалидная_форма_не_создаёт(self, клиент, шаблон, контрагент):
        данные = _данные_формы(контрагент)
        del данные['number']  # обязательное поле
        resp = клиент.post(f'/create/{шаблон.pk}/', данные)
        assert resp.status_code == 200  # форма с ошибками, без редиректа
        assert not СгенерированныйДокумент.objects.exists()


@pytest.mark.django_db
class TestСкачивание:
    def test_скачать_свой_docx(self, клиент, шаблон, контрагент, медиа):
        клиент.post(f'/create/{шаблон.pk}/', _данные_формы(контрагент))
        doc = СгенерированныйДокумент.objects.get(автор__username='док_юрист')

        resp = клиент.get(f'/{doc.pk}/download/docx/')
        assert resp.status_code == 200
        assert 'wordprocessingml' in resp['Content-Type']

    def test_чужой_документ_недоступен(self, клиент, шаблон, контрагент, роли, db):
        # Документ другого пользователя
        другой = User.objects.create_user('другой_автор', password='pass')
        другой.groups.add(Group.objects.get(name=РОЛЬ_ЮРИСТ))
        чужой = СгенерированныйДокумент.objects.create(
            шаблон=шаблон, автор=другой, контрагент=контрагент,
            статус='готов', файл_docx='documents/docx/foreign.docx',
        )
        resp = клиент.get(f'/{чужой.pk}/download/docx/')
        assert resp.status_code == 404

    def test_несуществующий_формат_404(self, клиент, шаблон, контрагент, медиа):
        клиент.post(f'/create/{шаблон.pk}/', _данные_формы(контрагент))
        doc = СгенерированныйДокумент.objects.get(автор__username='док_юрист')
        resp = клиент.get(f'/{doc.pk}/download/txt/')
        assert resp.status_code == 404


@pytest.mark.django_db
class TestДинамическаяФорма:
    def test_поля_по_переменным(self, шаблон):
        форма = ДинамическаяФорма(шаблон)
        assert 'контрагент' in форма.fields
        assert 'number' in форма.fields
        assert 'data' in форма.fields
        # date-переменная даёт DateField
        from django import forms as djforms
        assert isinstance(форма.fields['data'], djforms.DateField)
        assert isinstance(форма.fields['payment_days'], djforms.IntegerField)

    def test_получить_контекст_подставляет_контрагента(self, шаблон, контрагент):
        форма = ДинамическаяФорма(шаблон, _данные_формы(контрагент))
        assert форма.is_valid(), форма.errors
        ctx = форма.получить_контекст()
        # Авто-поля контрагента
        assert ctx['contragent_name'] == 'ООО Тест'
        assert ctx['contragent_inn'] == '7707083893'
        # Даты отформатированы в ДД.ММ.ГГГГ
        assert ctx['data'] == '19.06.2025'
        # 'контрагент' удалён из контекста
        assert 'контрагент' not in ctx
