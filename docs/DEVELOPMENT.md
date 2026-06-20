# Руководство разработчика

Частые задачи при работе над проектом.

## Локальная разработка

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # затем впишите SECRET_KEY (или DEBUG=True)
python manage.py migrate
python manage.py load_demo         # демо-пользователи, контрагенты, шаблоны
python manage.py runserver
```

> PDF-конвертация локально не работает без LibreOffice — документы будут
> создаваться в `.docx`, а PDF пропускаться (статус всё равно `готов`).
> Полный сценарий с PDF проверяется через Docker.

## Как добавить новый шаблон документа

Шаблон — это Word-файл `.docx` с Jinja2-тегами `{{ ключ }}` плюс запись в БД,
описывающая его переменные. Путь к файлу **всегда берётся из БД**, не хардкодится.

### 1. Создайте .docx с тегами

В обычном Word напишите текст документа, подставив теги вместо переменных:

```
ДОГОВОР АРЕНДЫ № {{ number }} от {{ data }}

Арендодатель: {{ contragent_name }}, ИНН {{ contragent_inn }}
Предмет аренды: {{ predmet }}
Арендная плата: {{ summa }} руб. ({{ summa_words }}) в месяц
```

Авто-поля контрагента доступны всегда (заполняются из выбранного контрагента):
`contragent_name`, `contragent_inn`, `contragent_kpp`, `contragent_address`.

Сохраните файл, например `arenda.docx`. Положите его в `word_templates/`
(исходники-генераторы) и в `media/templates/` (откуда читает Django).

> Для программной генерации .docx используйте `word_templates/create_templates.py`
> как образец (он строит шаблоны через python-docx).

### 2. Зарегистрируйте шаблон в БД

Вариант A — через админку (`/admin/` → Шаблоны документов → Добавить),
затем добавьте Переменные.

Вариант B — добавьте в `apps/templates_engine/management/commands/load_demo.py`
в список `ШАБЛОНЫ` по образцу:

```python
(
    'Договор аренды', 'иное', 'templates/arenda.docx',
    'Типовой договор аренды помещения',
    [
        # (ключ, подпись, тип_данных, обязательное, default, порядок)
        ('number',  'Номер договора', 'str',  True, '', 1),
        ('data',    'Дата договора',  'date', True, '', 2),
        ('predmet', 'Предмет аренды', 'str',  True, '', 3),
        ('summa',   'Сумма (руб.)',   'str',  True, '', 4),
        ('summa_words', 'Сумма прописью', 'str', True, '', 5),
    ]
),
```

`тип_данных`: `str` | `date` | `decimal` | `int` | `choice`.
Поле формы строится автоматически по типу (`documents/forms.py::_сделать_поле`).

### 3. Добавьте тест

В `tests/test_templates.py` допишите кортеж `(имя_файла, контекст)` в
`ШАБЛОНЫ_И_КОНТЕКСТЫ` — тест проверит, что шаблон рендерится без незакрытых тегов.

### 4. Перезагрузите демо-данные

```bash
python manage.py load_demo     # идемпотентна — повторный запуск не дублирует
```

## Как добавить валидатор реквизита

Валидаторы живут в `apps/catalog/validators.py`. Пример — `валидатор_инн`.
Подключается к полю модели:

```python
from .validators import валидатор_кпп
кпп = models.CharField('КПП', max_length=9, validators=[валидатор_кпп])
```

После изменения модели — миграция:
```bash
python manage.py makemigrations && python manage.py migrate
```

## Как ограничить доступ к вьюхе

Используйте декораторы из `apps/accounts/utils.py`:

```python
from apps.accounts.utils import требует_группу, ВСЕ_РОЛИ, РОЛЬ_АДМИН

@требует_группу(*ВСЕ_РОЛИ)        # любой авторизованный с ролью
def journal(request): ...

@требует_группу(РОЛЬ_АДМИН)       # только администратор шаблонов
def manage_template(request): ...
```

`требует_группу` редиректит на логин; `требует_группу_или_403` отдаёт 403.
Суперпользователь проходит любую проверку.

## Команды управления

| Команда | Назначение |
|---------|------------|
| `python manage.py setup_roles` | Создаёт группы и права (идемпотентна) |
| `python manage.py load_demo` | Демо-данные: пользователи, контрагенты, шаблоны |
| `python manage.py test_generate` | Генерирует тестовый документ из CLI |
| `pytest` | Запуск всех тестов |

## Структура проекта

```
someProject/
├── manage.py
├── config/            # settings, urls, wsgi, asgi
├── apps/
│   ├── accounts/      # роли, доступ
│   ├── catalog/       # контрагенты, юристы, валидаторы
│   ├── templates_engine/  # шаблоны + движок генерации (services.py)
│   └── documents/     # форма, генерация, журнал
├── templates/         # HTML (Django + Bootstrap + HTMX)
├── word_templates/    # .docx-шаблоны и скрипт их генерации
├── fixtures/          # demo.json — демо-данные
├── tests/             # pytest
├── docs/              # эта документация
├── Dockerfile
└── docker-compose.yml
```

> Проект использует стандартный Django-layout (manage.py в корне). Папка `src/`
> не применяется — это конвенция для упаковываемых библиотек, не для Django-приложений.
