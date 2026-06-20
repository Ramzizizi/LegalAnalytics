# Конструктор типовых юридических документов

Веб-приложение для автоматизации подготовки юридических документов.
Учебный проект — Цифровая кафедра ДГТУ.

**Стек:** Django 5.1 · docxtpl · LibreOffice headless · PostgreSQL / SQLite · Bootstrap 5 · HTMX · Docker Compose

## Документация

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — архитектура, модель данных, конвейер генерации, роли
- [docs/DIAGRAMS.md](docs/DIAGRAMS.md) — схемы: ER, архитектура, BPMN AS-IS/TO-BE, sequence, use case
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) — как добавить шаблон/валидатор, команды, частые задачи
- [docs/TESTING.md](docs/TESTING.md) — автотесты и ручной чек-лист тест-кейсов

---

## Быстрый старт (Docker)

```bash
# 1. Клонировать репозиторий
git clone <url> && cd legal-docs-constructor

# 2. Запустить
docker compose up --build

# 3. Открыть браузер
# http://localhost:8000
```

При первом запуске автоматически выполняются миграции и загружаются демо-данные.

**Демо-пользователи:**

| Логин | Пароль | Роль |
|-------|--------|------|
| admin | admin | Суперпользователь |
| юрист | юрист123 | Юрист |
| помощник | помощник123 | Помощник |

---

## Локальная разработка (без Docker)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py load_demo         # загрузить демо-данные
python manage.py runserver
```

---

## Тесты

```bash
pytest                             # все тесты
pytest tests/test_validators.py   # только валидаторы ИНН
pytest -v                          # подробный вывод
```

---

## Возможности

- **5 типов документов:** договор услуг, договор поставки, претензия, доверенность, исковое заявление
- **Генерация .docx** через docxtpl (Jinja2-теги в Word-шаблонах)
- **Конвертация в .pdf** через LibreOffice headless (работает в Docker)
- **Валидация ИНН** с проверкой контрольных цифр по алгоритму ФНС
- **Роли:** Администратор шаблонов / Юрист / Помощник
- **Журнал документов** с поиском, фильтрами и пагинацией (HTMX)
- **Справочник контрагентов** с автозаполнением реквизитов в форме

---

## Структура проекта

```
├── apps/
│   ├── accounts/          # роли и права (Django Groups)
│   ├── catalog/           # справочник контрагентов + валидатор ИНН
│   ├── documents/         # форма → генерация → журнал
│   └── templates_engine/  # движок генерации .docx/.pdf + шаблоны
├── fixtures/demo.json     # демо-данные (82 объекта)
├── templates/             # HTML-шаблоны (Bootstrap 5 + HTMX)
├── tests/                 # pytest: валидаторы, доступ, журнал, шаблоны
└── word_templates/        # .docx-шаблоны с тегами {{ variable }}
```

---

## Переменные окружения (.env)

| Переменная | По умолчанию | Описание |
|------------|-------------|----------|
| `SECRET_KEY` | dev-key | Django secret key |
| `DEBUG` | True | Режим отладки |
| `ALLOWED_HOSTS` | localhost,127.0.0.1 | Разрешённые хосты |
| `DATABASE_URL` | sqlite:///db.sqlite3 | URL базы данных |
| `POSTGRES_DB` | legal_docs | Имя БД (для Docker) |
| `POSTGRES_USER` | legal_user | Пользователь БД |
| `POSTGRES_PASSWORD` | legal_password | Пароль БД |
