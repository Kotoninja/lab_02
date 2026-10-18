from src.streamstats import analysis, parsers

from .test_parsers import (
    VALID_CSV_1,
    VALID_CSV_2,
    VALID_JSONL_1,
    VALID_JSONL_2,
    create_csv_file,
    create_json_file,
)


def test_multiple_json(tmp_path):
    f1 = create_json_file(tmp_path, [VALID_JSONL_1, VALID_JSONL_2])
    f2 = create_json_file(tmp_path, [VALID_JSONL_1, VALID_JSONL_2])
    stats = analysis.Stats()

    for f in (f1, f2):
        for event in parsers.json_parser(f, skip_invalid=False, stats=stats):
            stats.add(event)

    assert stats.total_events == 4


def test_multiple_csv(tmp_path):
    f1 = create_csv_file(tmp_path, [VALID_CSV_1, VALID_CSV_2])
    f2 = create_csv_file(tmp_path, [VALID_CSV_1, VALID_CSV_2])
    stats = analysis.Stats()

    for f in (f1, f2):
        for event in parsers.csv_parser(f, skip_invalid=False, stats=stats):
            stats.add(event)

    assert stats.total_events == 4
