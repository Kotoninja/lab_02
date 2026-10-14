import pytest

from src.streamstats import analysis, errors, parser

VALID_JSONL_1 = (
    '{"timestamp": "2024-01-01T10:00:00", "level": "INFO", '
    '"source": "test1", "message": "да"}'
)
VALID_JSONL_2 = (
    '{"timestamp": "2024-01-01T10:00:05", "level": "ERROR", '
    '"source": "test2", "message": "нет"}'
)
INVALID_JSONL = '{"timestamp": "2024-01-01T10:00:00", "level": "INFO"'


HEADER = "timestamp,level,source,message"
VALID_CSV_1 = "2024-01-01T10:00:00,INFO,test1,да"
VALID_CSV_2 = "2024-01-01T10:00:05,ERROR,test2,нет"


def create_json_file(tmp_path, lines):
    f = tmp_path / "events.json"

    f.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return f


def create_csv_file(tmp_path, lines, header=HEADER):
    f = tmp_path / "events.csv"

    content = f"{header}\n" + "\n".join(lines) + "\n"
    f.write_text(content, encoding="utf-8")

    return f


# JSON
def test_jsonl_parser_main_logic(tmp_path):
    """Проверка основной логики"""
    f = create_json_file(tmp_path, [VALID_JSONL_1, VALID_JSONL_2])

    stats = analysis.Stats()
    events = list(parser.json_parser(f, skip_invalid=True, stats=stats))

    assert len(events) == 2
    assert events[0].level == "INFO"
    assert events[0].source == "test1"
    assert events[1].level == "ERROR"
    assert stats.skipped == 0


def test_jsonl_parser_skips_empty_lines(tmp_path):
    """Пропуск пустых строк"""
    f = create_json_file(tmp_path, [VALID_JSONL_1, "", VALID_JSONL_2])

    stats = analysis.Stats()
    events = list(parser.json_parser(f, skip_invalid=False, stats=stats))

    assert len(events) == 2
    assert stats.skipped == 0


def test_jsonl_parser_invalid_json_raises(tmp_path):
    """Невалидный JSON выбрасывает InvalidEventError с номером строки"""
    f = create_json_file(tmp_path, [INVALID_JSONL])

    stats = analysis.Stats()
    with pytest.raises(errors.InvalidEventError, match="Невалидный json. Line 1"):
        list(parser.json_parser(f, skip_invalid=False, stats=stats))


def test_jsonl_parser_invalid_date_raises_and_without_skip(tmp_path):
    """Невалидная дата выбрасывает SteamStatsError"""
    invalid_date_jsonl = (
        '{"timestamp": "2024-13-45T99:99:99", "level": "INFO", '
        '"source": "test1", "message": "да"}'
    )
    f = create_json_file(tmp_path, [invalid_date_jsonl])

    stats = analysis.Stats()
    with pytest.raises(errors.SteamStatsError):
        list(parser.json_parser(f, skip_invalid=False, stats=stats))


def test_jsonl_parser_invalid_date_raises_and_skip(tmp_path):
    """Невалидная дата с включенным skip_invalid"""
    invalid_date_jsonl = (
        '{"timestamp": "2024-13-45T99:99:99", "level": "INFO", '
        '"source": "test1", "message": "да"}'
    )
    f = create_json_file(tmp_path, [invalid_date_jsonl])

    stats = analysis.Stats()
    list(parser.json_parser(f, skip_invalid=True, stats=stats))


def test_jsonl_parser_skips_invalid_events(tmp_path):
    """Пропуск невалидных событий при skip_invalid"""
    f = create_json_file(tmp_path, [VALID_JSONL_1, INVALID_JSONL, VALID_JSONL_2])

    stats = analysis.Stats()
    events = list(parser.json_parser(f, skip_invalid=True, stats=stats))

    assert len(events) == 2
    assert stats.skipped == 1


def test_jsonl_parser_file_not_found(tmp_path):
    """Отсутствующий файл"""
    f = tmp_path / "missing.json"
    stats = analysis.Stats()
    with pytest.raises(FileNotFoundError, match="Файл не найден"):
        list(parser.json_parser(f, skip_invalid=True, stats=stats))


# CSV
def test_csv_parser_main_logic(tmp_path):
    """Проверка основной логики"""
    f = create_csv_file(tmp_path, [VALID_CSV_1, VALID_CSV_2])

    stats = analysis.Stats()
    events = list(parser.csv_parser(f, skip_invalid=True, stats=stats))

    assert len(events) == 2
    assert events[0].level == "INFO"
    assert events[0].source == "test1"
    assert events[1].level == "ERROR"
    assert stats.skipped == 0


def test_csv_parser_skips_empty_lines(tmp_path):
    """Пропуск пустых строк в CSV"""
    f = tmp_path / "events.csv"

    f.write_text(
        f"{HEADER}\n{VALID_CSV_1}\n\n{VALID_CSV_2}\n",
        encoding="utf-8",
    )

    stats = analysis.Stats()
    events = list(parser.csv_parser(f, skip_invalid=True, stats=stats))

    assert len(events) == 2
    assert stats.skipped == 0


def test_csv_parser_invalid_json_raises(tmp_path):
    """Невалидная запись выбрасывает SteamStatsError без skip_invalid"""
    # строка с недостающим полем message -> SteamStatsError при create_event
    invalid_csv = "2024-01-01T10:00:00,INFO,test1"
    f = create_csv_file(tmp_path, [invalid_csv])

    stats = analysis.Stats()
    with pytest.raises(errors.SteamStatsError):
        list(parser.csv_parser(f, skip_invalid=False, stats=stats))


def test_csv_parser_skips_invalid_events(tmp_path):
    """Пропуск невалидных событий при skip_invalid=True"""
    invalid_csv = "2024-01-01T10:00:00,INFO,test1"  # не хватает message
    f = create_csv_file(tmp_path, [VALID_CSV_1, invalid_csv, VALID_CSV_2])

    stats = analysis.Stats()
    events = list(parser.csv_parser(f, skip_invalid=True, stats=stats))

    assert len(events) == 2
    assert stats.skipped == 1


def test_csv_parser_file_not_found(tmp_path):
    """Отсутствующий файл выбрасывает FileNotFoundError"""
    f = tmp_path / "missing.csv"
    stats = analysis.Stats()
    with pytest.raises(FileNotFoundError, match="Файл не найден"):
        list(parser.csv_parser(f, skip_invalid=True, stats=stats))


# get parser
def test_get_parser_jsonl():
    """Для 'jsonl' возвращается json_parser"""
    assert parser.get_parser("jsonl") is parser.json_parser


def test_get_parser_csv():
    """Для 'csv' возвращается csv_parser"""
    assert parser.get_parser("csv") is parser.csv_parser


def test_get_parser_unsupported_format():
    """Для неизвестного формата выбрасывается UnsupportedFormatError"""
    with pytest.raises(errors.UnsupportedFormatError):
        parser.get_parser("xml")
