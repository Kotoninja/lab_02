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
    f = create_json_file(tmp_path, [VALID_JSONL_1, VALID_JSONL_2])

    stats = analysis.Stats()
    events = list(parser.json_parser(f, skip_invalid=True, stats=stats))

    assert len(events) == 2
    assert events[0].level == "INFO"
    assert events[0].source == "test1"
    assert events[1].level == "ERROR"
    assert stats.skipped == 0


def test_jsonl_parser_skips_empty_lines(tmp_path):
    f = create_json_file(tmp_path, [VALID_JSONL_1, "", VALID_JSONL_2])

    stats = analysis.Stats()
    events = list(parser.json_parser(f, skip_invalid=False, stats=stats))

    assert len(events) == 2
    assert stats.skipped == 0


def test_jsonl_parser_invalid_json_raises(tmp_path):
    f = create_json_file(tmp_path, [INVALID_JSONL])

    stats = analysis.Stats()
    with pytest.raises(errors.InvalidEventError, match="Невалидный json. Line 1"):
        list(parser.json_parser(f, skip_invalid=False, stats=stats))


def test_jsonl_parser_invalid_date_raises_and_without_skip(tmp_path):
    invalid_date_jsonl = (
        '{"timestamp": "2024-13-45T99:99:99", "level": "INFO", '
        '"source": "test1", "message": "да"}'
    )
    f = create_json_file(tmp_path, [invalid_date_jsonl])

    stats = analysis.Stats()
    with pytest.raises(errors.SteamStatsError):
        list(parser.json_parser(f, skip_invalid=False, stats=stats))


def test_jsonl_parser_skips_invalid_events(tmp_path):
    f = create_json_file(tmp_path, [VALID_JSONL_1, INVALID_JSONL, VALID_JSONL_2])

    stats = analysis.Stats()
    events = list(parser.json_parser(f, skip_invalid=True, stats=stats))

    assert len(events) == 2
    assert stats.skipped == 1


def test_jsonl_parser_file_not_found(tmp_path):
    f = tmp_path / "missing.json"
    stats = analysis.Stats()
    with pytest.raises(FileNotFoundError, match="Файл не найден"):
        list(parser.json_parser(f, skip_invalid=True, stats=stats))


# CSV
def test_csv_parser_main_logic(tmp_path):
    f = create_csv_file(tmp_path, [VALID_CSV_1, VALID_CSV_2])

    stats = analysis.Stats()
    events = list(parser.csv_parser(f, skip_invalid=True, stats=stats))

    assert len(events) == 2
    assert events[0].level == "INFO"
    assert events[0].source == "test1"
    assert events[1].level == "ERROR"
    assert stats.skipped == 0


def test_csv_parser_skips_empty_lines(tmp_path):
    f = tmp_path / "events.csv"

    f.write_text(
        f"{HEADER}\n{VALID_CSV_1}\n\n{VALID_CSV_2}\n",
        encoding="utf-8",
    )

    stats = analysis.Stats()
    events = list(parser.csv_parser(f, skip_invalid=True, stats=stats))

    assert len(events) == 2
    assert stats.skipped == 0


def test_csv_parser_invalid_raises(tmp_path):
    invalid_csv = "2024-01-01T10:00:00,INFO,test1"
    f = create_csv_file(tmp_path, [invalid_csv])

    stats = analysis.Stats()
    with pytest.raises(errors.SteamStatsError):
        list(parser.csv_parser(f, skip_invalid=False, stats=stats))


def test_csv_parser_skips_invalid_events(tmp_path):
    invalid_csv = "2024-01-01T10:00:00,INFO,test1"
    f = create_csv_file(tmp_path, [VALID_CSV_1, invalid_csv, VALID_CSV_2])

    stats = analysis.Stats()
    events = list(parser.csv_parser(f, skip_invalid=True, stats=stats))

    assert len(events) == 2
    assert stats.skipped == 1


def test_csv_parser_file_not_found(tmp_path):
    f = tmp_path / "missing.csv"
    stats = analysis.Stats()
    with pytest.raises(FileNotFoundError, match="Файл не найден"):
        list(parser.csv_parser(f, skip_invalid=True, stats=stats))


# get parser
def test_get_parser_jsonl():
    assert parser.get_parser("jsonl") is parser.json_parser


def test_get_parser_csv():
    assert parser.get_parser("csv") is parser.csv_parser


def test_get_parser_unsupported_format():
    with pytest.raises(errors.UnsupportedFormatError):
        parser.get_parser("xml")
