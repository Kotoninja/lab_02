# Лабораторная работа №2 — streamstats

**streamstats** — консольное приложение для анализа потока событий из файлов в форматах CSV и JSONL.
Приложение читает файлы, собирает статистику и сохраняет отчёт в JSON.

## Формат входных данных

Каждое событие содержит четыре обязательных поля:

timestamp : str - время события в формате ISO 8601, например 2024-01-01T10:00:00  
level: str - `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`  
source: str - источник события, непустая строка  
message: str - текст сообщения

JSON Lines — один JSON-объект на строку:

```json
{"timestamp": "2024-01-01T10:00:00", "level": "INFO", "source": "test1", "message": "ok"}
{"timestamp": "2024-01-01T10:05:00", "level": "ERROR", "source": "test2", "message": "not ok"}
```

CSV — первая строка содержит заголовок:

```csv
timestamp,level,source,message
2024-01-01T10:00:00,INFO,test1,ok
2024-01-01T10:05:00,ERROR,test2,not ok
```

## Установка

Требуется Python 3.12+ и пакетный менеджер [uv](https://github.com/astral-sh/uv).

```bash
git clone <url репозитория>
cd lab_02/src

echo '{"timestamp": "2023-04-12T12:34:56Z", "level": "ERROR", "source": "привет", "message": "This is a debug message"}' > test.jsonl

uv sync

source .venv/bin/activate

uv run python -m streamstats analyze test.jsonl --format jsonl --output Report.json
```

## Использование

Приложение запускается как модуль из корня репозитория:

```bash
uv run python -m src.streamstats analyze <файл> [<файл> ...] --format {csv,jsonl} --output <отчёт.json> [--skip-invalid]
```

| Аргумент         | Описание                                                     |
|------------------|--------------------------------------------------------------|
| `input`          | Пути к файлам                     |
| `--format`       | Формат `csv` или `jsonl`          |
| `--output`       | Куда записывать JSON-отчёт        |
| `--skip-invalid` | Пропускать невалидные строки      |

Пример:

```bash
python -m src.streamstats analyze app1.jsonl app2.jsonl --format jsonl --output report.json --skip-invalid
```

## Формат отчёта

```json
{
    "total_events": 2,
    "by_level": {"INFO": 1, "ERROR": 1},
    "by_source": {"auth": 1, "db": 1},
    "top_error_sources": [{"source": "test", "count": 1}],
    "first_timestamp": "2024-01-01T10:00:00",
    "last_timestamp": "2024-01-01T10:05:00",
    "skipped_lines": 1
}
```

| Поле                | Описание                                                       |
|---------------------|----------------------------------------------------------------|
| `total_events`      | Общее количество корректных событий                            |
| `by_level`          | Количество событий по каждому уровню                           |
| `by_source`         | Количество событий по каждому источнику                        |
| `top_error_sources` | Источники событий уровня `ERROR` и `CRITICAL` с их количеством |
| `first_timestamp`   | Время самого раннего события        |
| `last_timestamp`    | Время самого позднего события |
| `skipped_lines`     | Количество пропущенных невалидных строк                        |

## Структура проекта

<pre>
.
├── src/
│   └── streamstats/
│       ├── __main__.py        # Точка входа. CLI и запуск анализа
│       ├── parser.py          # Парсеры CSV и JSONL
│       ├── models.py          # Модель Event и валидация входных данных
│       ├── analysis.py        # Класс Stats — накопление статистики по событиям
│       ├── report.py          # Формирование и запись JSON-отчёта
│       └── errors.py          # Исключения приложения
├── tests/
│   ├── test_models.py         # Проверка валидации событий
│   ├── test_parsers.py        # Проверка парсеров CSV/JSONL, пропуск невалидных строк, ошибки
│   ├── test_multiple_files.py # Проверка обработки нескольких файлов
│   └── test_unicode.py        # Проверка Unicode
├── pyproject.toml             # Метаданные проекта и настройки coverage
├── uv.lock                    # Зависимости проекта
├── .pre-commit-config.yaml
└── README.md
</pre>


## Исключения (`errors.py`):

`StreamStatsError` — базовое исключение  
`InvalidEventError` — некорректное   событие или невалидный JSON  
`InvalidTimestampError` — некорректная временная метка  
`UnsupportedFormatError` — неподдерживаемый формат  
`CLIConfigurationError` — ошибка конфигурации CLI  

## Тестирование

```bash
uv run pytest .
```

