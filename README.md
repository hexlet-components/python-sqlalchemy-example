<div align="center">

<a href="https://hexlet.io/?utm_source=github&utm_medium=link&utm_campaign=python-sqlalchemy-example">
    <picture>
        <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Hexlet/brand-assets/master/images/svg/hexlet_wordmark_white_rus.svg">
        <img src="https://raw.githubusercontent.com/Hexlet/brand-assets/master/images/svg/hexlet_wordmark_primary_rus.svg" alt="Хекслет" height="64">
    </picture>
</a>

# Трекер задач на SQLAlchemy

[![CI](https://github.com/hexlet-components/python-sqlalchemy-example/actions/workflows/main.yml/badge.svg)](https://github.com/hexlet-components/python-sqlalchemy-example/actions/workflows/main.yml)
[![Check](https://github.com/hexlet-components/python-sqlalchemy-example/actions/workflows/check.yml/badge.svg)](https://github.com/hexlet-components/python-sqlalchemy-example/actions/workflows/check.yml)

</div>

Компонент создаёт и поддерживает команда [Хекслета](https://hexlet.io/?utm_source=github&utm_medium=link&utm_campaign=python-sqlalchemy-example), образовательного проекта.

В курсе «Python: SQLAlchemy» один трекер проходит путь от таблицы задач до отчёта по проектам. В [first_steps](first_steps) лежит первая версия модели с полем `title`. В [tracker](tracker) находится версия после миграций с полем `name`, проектами и метками.

## Подготовка

Понадобятся Python 3.12 или новее, uv и PostgreSQL. Команды ниже выполняются из каталога репозитория. Они предполагают, что текущий пользователь имеет доступ к локальному PostgreSQL и может создавать учебные базы. При подключении к другому серверу укажите его адрес и имя пользователя в `DATABASE_URL`.

```sh
uv sync --locked
createdb tracker_first
createdb tracker_course
```

## Первые шаги

Начальные скрипты сами создают таблицу в учебной базе. Запуск первого примера сохраняет задачу и читает её из новой сессии.

```sh
export DATABASE_URL='postgresql+psycopg:///tracker_first'
uv run python -m first_steps.first_task
uv run python -m first_steps.crud
uv run python -m first_steps.transactions
```

Скрипт CRUD добавляет три задачи, показывает открытые, закрывает одну и удаляет другую. Вывод включает и открытые задачи от предыдущих запусков. Скрипт транзакций прерывает импорт и показывает, что новая сессия не находит добавленную запись. SQL виден в журнале.

## Переименование на заполненной базе

Переключимся на вторую базу. Начальная ревизия создаст таблицу со столбцом `title`. Сохраним в ней задачу, затем применим остальные ревизии.

```sh
export DATABASE_URL='postgresql+psycopg:///tracker_course'
uv run alembic upgrade 32e016547c7d
psql -d tracker_course -c "INSERT INTO tasks (title, is_done) VALUES ('Проверить выпуск', FALSE) RETURNING id"
uv run alembic upgrade head
psql -d tracker_course -c 'SELECT id, name, is_done FROM tasks'
```

У строки останутся прежний ключ и название. Команда `uv run alembic history` покажет четыре перехода, а `uv run alembic check` сравнит текущую схему с [моделями трекера](tracker/models.py).

## Проекты, метки и отчёт

```sh
uv run python -m tracker.demo
```

Если таблица проектов пуста, программа добавит три проекта. При повторном запуске она читает те же данные. Для этих проектов отложенная загрузка выполняет четыре запроса, предварительная два. В отчёте по открытым задачам у «Сайта» две задачи, у пустого «Архива» и у «Справки» с закрытой задачей по нулю.

В начале каждой строки с проектом напечатан его ключ. Передайте два ключа асинхронному отчёту, чтобы получить названия задач в каждом проекте. Например, если у «Сайта» и «Справки» ключи 2 и 3, команда выглядит так.

```sh
uv run python -m tracker.async_report 2 3
```

## Проверки

`mise run setup` устанавливает зависимости и хуки, `mise run check` проверяет код и разметку. Интеграционный тест создаёт в указанной тестовой базе отдельную схему и удаляет её после проверки.

```sh
createdb tracker_test
TEST_DATABASE_URL='postgresql+psycopg:///tracker_test' mise run test
```
