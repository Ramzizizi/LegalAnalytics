"""
Загружает демо-данные для ручного тестирования UI.
Использование: python manage.py load_demo
"""
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from apps.catalog.models import Контрагент
from apps.templates_engine.models import ШаблонДокумента, Переменная
from apps.accounts.utils import РОЛЬ_АДМИН, РОЛЬ_ЮРИСТ, РОЛЬ_ПОМОЩНИК

# (название, тип, файл, описание, [(ключ, подпись, тип_данных, обяз, default, порядок)])
ШАБЛОНЫ = [
    (
        'Договор оказания услуг', 'услуги', 'templates/dogovor_uslug.docx',
        'Типовой договор оказания юридических и консультационных услуг',
        [
            ('number',             'Номер договора',              'str',  True,  '001/2025', 1),
            ('data',               'Дата договора',               'date', True,  '',         2),
            ('contragent_director','ФИО директора контрагента',   'str',  True,  '',         3),
            ('executor_name',      'Наименование исполнителя',    'str',  True,  'ООО «Юридическая помощь»', 4),
            ('lawyer_name',        'ФИО подписанта исполнителя',  'str',  True,  '',         5),
            ('services_description','Описание услуг',             'str',  True,  'юридическое сопровождение', 6),
            ('summa',              'Сумма договора (цифрами, руб.)','str', True, '',         7),
            ('summa_words',        'Сумма прописью',              'str',  True,  '',         8),
            ('payment_days',       'Срок оплаты (рабочих дней)',  'int',  True,  '5',        9),
            ('date_start',         'Дата начала',                 'date', True,  '',        10),
            ('date_end',           'Дата окончания',              'date', True,  '',        11),
        ]
    ),
    (
        'Договор поставки', 'поставка', 'templates/dogovor_postavki.docx',
        'Договор поставки товара между юридическими лицами',
        [
            ('number',             'Номер договора',              'str',  True,  '002/2025', 1),
            ('data',               'Дата договора',               'date', True,  '',         2),
            ('contragent_director','ФИО директора покупателя',    'str',  True,  '',         3),
            ('executor_name',      'Наименование поставщика',     'str',  True,  '',         4),
            ('lawyer_name',        'ФИО подписанта поставщика',   'str',  True,  '',         5),
            ('tovar_naim',         'Наименование товара',         'str',  True,  '',         6),
            ('tovar_kol',          'Количество (ед.)',            'int',  True,  '',         7),
            ('tovar_price',        'Цена за единицу (руб.)',      'str',  True,  '',         8),
            ('tovar_summa',        'Общая сумма (цифрами, руб.)', 'str',  True,  '',         9),
            ('summa_words',        'Сумма прописью',              'str',  True,  '',        10),
            ('delivery_date',      'Срок поставки',               'date', True,  '',        11),
            ('delivery_address',   'Адрес доставки',              'str',  True,  '',        12),
            ('payment_days',       'Срок оплаты (рабочих дней)',  'int',  True,  '5',       13),
        ]
    ),
    (
        'Претензия', 'претензия', 'templates/pretenziya.docx',
        'Досудебная претензия контрагенту по нарушению договора',
        [
            ('number',             'Номер претензии',             'str',  True,  '',         1),
            ('data',               'Дата претензии',              'date', True,  '',         2),
            ('sender_name',        'Наименование отправителя',    'str',  True,  '',         3),
            ('sender_address',     'Адрес отправителя',           'str',  True,  '',         4),
            ('dogovor_number',     'Номер нарушенного договора',  'str',  True,  '',         5),
            ('dogovor_date',       'Дата нарушенного договора',   'date', True,  '',         6),
            ('obyazatelstvo',      'Обязательство контрагента',   'str',  True,  '',         7),
            ('narushenie',         'Суть нарушения',              'str',  True,  '',         8),
            ('trebovanie',         'Требование (что сделать)',     'str',  True,  '',         9),
            ('pretenziya_summa',   'Сумма претензии (руб.)',       'str',  True,  '',        10),
            ('summa_words',        'Сумма прописью',              'str',  True,  '',        11),
            ('srok_otveta',        'Срок ответа (рабочих дней)',  'int',  True,  '10',      12),
            ('lawyer_name',        'ФИО подписанта',              'str',  True,  '',        13),
        ]
    ),
    (
        'Доверенность', 'доверенность', 'templates/doverennost.docx',
        'Доверенность на представление интересов организации',
        [
            ('number',             'Номер доверенности',          'str',  True,  '',         1),
            ('data',               'Дата выдачи',                 'date', True,  '',         2),
            ('gorod',              'Город',                       'str',  True,  'Москва',   3),
            ('org_name',           'Наименование организации',    'str',  True,  '',         4),
            ('org_inn',            'ИНН организации',             'str',  True,  '',         5),
            ('org_address',        'Адрес организации',           'str',  True,  '',         6),
            ('director_name',      'ФИО директора',               'str',  True,  '',         7),
            ('poverenny_name',     'ФИО доверенного лица',        'str',  True,  '',         8),
            ('poverenny_pasport',  'Паспортные данные',           'str',  True,  '',         9),
            ('poverenny_address',  'Адрес доверенного лица',      'str',  True,  '',        10),
            ('polnomochiya',       'Полномочия',                  'str',  True,  '',        11),
            ('srok_do',            'Срок действия до',            'date', True,  '',        12),
        ]
    ),
    (
        'Исковое заявление', 'иск', 'templates/iskovoe.docx',
        'Исковое заявление в арбитражный суд',
        [
            ('data',               'Дата подачи',                 'date', True,  '',         1),
            ('sud_name',           'Наименование суда',           'str',  True,  'Арбитражный суд г. Москвы', 2),
            ('istec_name',         'Наименование истца',          'str',  True,  '',         3),
            ('istec_address',      'Адрес истца',                 'str',  True,  '',         4),
            ('istec_inn',          'ИНН истца',                   'str',  True,  '',         5),
            ('otvetchik_name',     'Наименование ответчика',      'str',  True,  '',         6),
            ('otvetchik_address',  'Адрес ответчика',             'str',  True,  '',         7),
            ('otvetchik_inn',      'ИНН ответчика',               'str',  True,  '',         8),
            ('dogovor_number',     'Номер договора-основания',    'str',  True,  '',         9),
            ('dogovor_date',       'Дата договора-основания',     'date', True,  '',        10),
            ('narushenie',         'Суть нарушения',              'str',  True,  '',        11),
            ('pretenziya_date',    'Дата претензии',              'date', True,  '',        12),
            ('iskovye_trebovaniya','Исковые требования',          'str',  True,  '',        13),
            ('summa_iska',         'Цена иска (руб.)',            'str',  True,  '',        14),
            ('summa_words',        'Сумма прописью',              'str',  True,  '',        15),
            ('lawyer_name',        'ФИО представителя',           'str',  True,  '',        16),
        ]
    ),
]


class Command(BaseCommand):
    help = 'Загружает демо-данные: пользователи, контрагенты, шаблоны с переменными'

    def handle(self, *args, **options):
        call_command('setup_roles', verbosity=0)

        # ── пользователи ──
        admin = self._создать_пользователя('admin', 'admin', superuser=True)
        admin.groups.add(Group.objects.get(name=РОЛЬ_АДМИН))

        юрист = self._создать_пользователя('юрист', 'юрист123', first='Иван', last='Иванов')
        юрист.groups.add(Group.objects.get(name=РОЛЬ_ЮРИСТ))

        помощник = self._создать_пользователя('помощник', 'помощник123', first='Пётр', last='Петров')
        помощник.groups.add(Group.objects.get(name=РОЛЬ_ПОМОЩНИК))

        # ── контрагенты ──
        for инн, наим, кпп, адрес in [
            ('7707083893', 'ООО «Ромашка»',   '770701001', 'г. Москва, ул. Ленина, д. 1'),
            ('7736207543', 'ПАО «Газпром»',   '773601001', 'г. Москва, ул. Наметкина, д. 16'),
            ('3664069397', 'ООО «Южный ветер»','366401001', 'г. Ростов-на-Дону, пр. Соколова, д. 50'),
        ]:
            к, created = Контрагент.objects.get_or_create(
                инн=инн,
                defaults={'наименование': наим, 'тип': 'юр', 'кпп': кпп, 'адрес': адрес}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Контрагент: {к}'))

        # ── шаблоны ──
        всего_переменных = 0
        for название, тип, файл, описание, переменные in ШАБЛОНЫ:
            шаблон, created = ШаблонДокумента.objects.get_or_create(
                название=название,
                defaults={'тип': тип, 'файл': файл, 'описание': описание, 'активен': True}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Шаблон: {название}'))
            for ключ, подпись, тип_д, обяз, default, порядок in переменные:
                _, c = Переменная.objects.get_or_create(
                    шаблон=шаблон, ключ=ключ,
                    defaults={
                        'подпись': подпись, 'тип_данных': тип_д,
                        'обязательное': обяз, 'значение_по_умолчанию': default,
                        'порядок': порядок,
                    }
                )
                if c:
                    всего_переменных += 1

        self.stdout.write(self.style.SUCCESS(f'✓ Переменных создано: {всего_переменных}'))
        self.stdout.write(self.style.SUCCESS(
            '\nДемо-данные загружены.\n'
            '  admin / admin       — суперпользователь\n'
            '  юрист / юрист123    — роль Юрист\n'
            '  помощник / помощник123 — роль Помощник\n'
            'Запустите: python manage.py runserver'
        ))

    def _создать_пользователя(self, username, password, *, superuser=False, first='', last=''):
        if User.objects.filter(username=username).exists():
            self.stdout.write(f'  пользователь {username} уже существует')
            return User.objects.get(username=username)
        if superuser:
            u = User.objects.create_superuser(username, f'{username}@example.com', password)
        else:
            u = User.objects.create_user(username, password=password, first_name=first, last_name=last)
        self.stdout.write(self.style.SUCCESS(f'✓ Создан пользователь {username} / {password}'))
        return u
