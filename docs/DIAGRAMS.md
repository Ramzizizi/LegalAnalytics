# Схемы проекта

Диаграммы в формате [Mermaid](https://mermaid.js.org/). Рендерятся автоматически:
- в **PyCharm/IDEA** — превью Markdown (плагин Mermaid встроен),
- на **GitHub/GitLab** — прямо в просмотре файла,
- онлайн — вставить код в [mermaid.live](https://mermaid.live) и экспортировать в PNG/SVG для слайдов.

Содержание:
1. [ER-диаграмма (модель данных)](#1-er-диаграмма-модель-данных)
2. [Архитектура развёртывания](#2-архитектура-развёртывания)
3. [BPMN AS-IS — процесс без системы](#3-bpmn-as-is--процесс-без-системы)
4. [BPMN TO-BE — процесс с системой](#4-bpmn-to-be--процесс-с-системой)
5. [Sequence — генерация документа](#5-sequence--генерация-документа)
6. [Use case — роли и действия](#6-use-case--роли-и-действия)
7. [Состояния документа](#7-состояния-документа)

---

## 1. ER-диаграмма (модель данных)

```mermaid
erDiagram
    User ||--o{ СгенерированныйДокумент : "автор"
    Контрагент ||--o{ СгенерированныйДокумент : "контрагент"
    ШаблонДокумента ||--o{ СгенерированныйДокумент : "шаблон"
    ШаблонДокумента ||--o{ Переменная : "переменные"
    User ||--o| Юрист : "профиль"

    Контрагент {
        string наименование
        string тип "юр | физ"
        string инн "валидация ФНС"
        string кпп
        text   адрес
        string телефон
        string email
    }

    ШаблонДокумента {
        string  название
        string  тип
        file    файл "docx"
        text    описание
        bool    активен
    }

    Переменная {
        string ключ "тег в шаблоне"
        string подпись "label в форме"
        string тип_данных "str|date|decimal|int|choice"
        bool   обязательное
        string значение_по_умолчанию
        int    порядок
    }

    СгенерированныйДокумент {
        json   значения "снимок данных формы"
        file   файл_docx
        file   файл_pdf
        string статус "черновик|готов|ошибка"
        text   ошибка
        date   создан
    }

    Юрист {
        string должность
        string телефон
    }
```

> FK к шаблону, контрагенту и автору используют `on_delete=PROTECT` — нельзя
> удалить объект, по которому уже есть сгенерированные документы.

---

## 2. Архитектура развёртывания

```mermaid
flowchart TB
    user([Юрист в браузере])

    subgraph docker["Docker Compose"]
        subgraph web["Контейнер web (appuser, non-root)"]
            gunicorn["gunicorn (2 воркера)"]
            django["Django 5.1"]
            whitenoise["WhiteNoise — статика"]
            libre["LibreOffice headless"]
            gunicorn --> django
            django --> whitenoise
            django --> libre
        end
        db[("PostgreSQL")]
        vol_media[["том: media (docx/pdf, шаблоны)"]]
        vol_static[["том: staticfiles"]]
    end

    user -->|"HTTP / HTMX"| gunicorn
    django -->|"ORM"| db
    django -->|"чтение шаблонов / запись документов"| vol_media
    whitenoise --- vol_static
    libre -->|"docx → pdf"| vol_media
```

---

## 3. BPMN AS-IS — процесс без системы

Как юрист готовит документ вручную (текущее состояние):

```mermaid
flowchart LR
    start([Нужен документ]) --> find["Найти похожий<br/>документ в архиве"]
    find --> copy["Скопировать файл<br/>Word"]
    copy --> edit["Вручную заменить<br/>реквизиты по тексту"]
    edit --> check{"Все поля<br/>заменены?"}
    check -->|"нет"| miss["Пропущен реквизит<br/>/ опечатка"]
    miss --> edit
    check -->|"да"| inn["Вручную проверить<br/>ИНН контрагента"]
    inn --> pdf["Сохранить как PDF<br/>через 'Печать'"]
    pdf --> save["Сохранить в папку,<br/>придумать имя"]
    save --> done([Документ готов])

    classDef pain fill:#ffe0e0,stroke:#c00;
    class miss,edit,inn pain
```

**Проблемы AS-IS:** ручная замена реквизитов → опечатки и пропуски; нет проверки
ИНН; копии шаблонов расходятся по версиям; документы теряются в папках; нет журнала.

---

## 4. BPMN TO-BE — процесс с системой

```mermaid
flowchart LR
    start([Нужен документ]) --> login["Войти в систему"]
    login --> tpl["Выбрать шаблон<br/>из списка"]
    tpl --> contr["Выбрать контрагента<br/>(реквизиты подставятся)"]
    contr --> form["Заполнить форму<br/>(поля по шаблону)"]
    form --> submit["Нажать<br/>'Сгенерировать'"]
    submit --> valid{"Валидация<br/>ИНН и полей"}
    valid -->|"ошибка"| hint["Понятная подсказка<br/>в форме"]
    hint --> form
    valid -->|"ок"| gen["Система генерирует<br/>.docx и .pdf"]
    gen --> journal["Документ в журнале,<br/>готов к скачиванию"]
    journal --> done([Документ готов])

    classDef auto fill:#e0ffe0,stroke:#0a0;
    class contr,gen,valid,journal auto
```

**Выгоды TO-BE:** автоподстановка реквизитов; автоматическая проверка ИНН;
единый источник шаблонов; журнал с поиском; .docx и .pdf одним действием.

---

## 5. Sequence — генерация документа

```mermaid
sequenceDiagram
    actor Ю as Юрист
    participant V as views.create
    participant F as ДинамическаяФорма
    participant S as services
    participant L as LibreOffice
    participant DB as БД

    Ю->>V: POST форма (контрагент + поля)
    V->>F: is_valid()
    F-->>V: cleaned_data
    V->>F: получить_контекст()
    F-->>V: context (+ авто-поля контрагента, даты→строки)

    rect rgb(235,245,255)
    note over V,DB: transaction.atomic
    V->>DB: создать документ (статус=черновик)
    V->>S: render_docx(шаблон, context)
    S-->>V: .docx сохранён
    alt LibreOffice доступен
        V->>S: convert_to_pdf(.docx)
        S->>L: subprocess --convert-to pdf
        L-->>S: .pdf
        S-->>V: .pdf сохранён
    end
    V->>DB: статус=готов, save()
    end

    V-->>Ю: redirect → страница документа
```

> Любое исключение внутри блока → `статус=ошибка`, текст в поле `ошибка`;
> транзакция гарантирует отсутствие «висячих» черновиков при сбое.

---

## 6. Use case — роли и действия

```mermaid
flowchart TB
    admin([Администратор шаблонов])
    lawyer([Юрист])
    helper([Помощник])

    uc_tpl["Управлять шаблонами<br/>и переменными"]
    uc_create["Создавать документы"]
    uc_view["Просматривать свои<br/>документы"]
    uc_download["Скачивать .docx / .pdf"]
    uc_journal["Журнал: поиск,<br/>фильтры"]

    admin --> uc_tpl
    admin --> uc_create
    lawyer --> uc_create
    helper --> uc_create
    admin --> uc_view
    lawyer --> uc_view
    helper --> uc_view
    uc_create --> uc_download
    uc_view --> uc_journal
    uc_view --> uc_download
```

> Каждый пользователь видит и скачивает **только свои** документы
> (`автор=request.user`). Суперпользователь проходит любую проверку доступа.

---

## 7. Состояния документа

```mermaid
stateDiagram-v2
    state "черновик" as draft
    state "готов" as ready
    state "ошибка" as failed

    [*] --> draft: запись создана
    draft --> ready: .docx (+ .pdf) сгенерированы
    draft --> failed: исключение при генерации
    ready --> [*]
    failed --> [*]

    note right of ready
        файл_docx заполнен,
        файл_pdf — если был LibreOffice
    end note
    note right of failed
        текст исключения
        в поле «ошибка»
    end note
```

---

## Экспорт в изображения

Для вставки в презентацию:

1. **Онлайн (быстро):** открыть [mermaid.live](https://mermaid.live), вставить код
   блока, нажать **Actions → PNG/SVG**.
2. **Локально (если есть Node.js):**
   ```bash
   npm install -g @mermaid-js/mermaid-cli
   mmdc -i docs/DIAGRAMS.md -o docs/diagram.png
   ```
