import json
import subprocess

from .test_parsers import (
    VALID_CSV_1,
    VALID_JSONL_1,
    VALID_JSONL_2,
    create_csv_file,
    create_json_file,
)


def test_cli_json(tmp_path):
    in_file = create_json_file(tmp_path, [VALID_JSONL_1, VALID_JSONL_2])
    out_file = tmp_path / "report.json"

    execute = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "-m",
            "src.streamstats",
            "analyze",
            in_file,
            "--format",
            "jsonl",
            "--output",
            out_file,
        ],
        check=False,
    )

    assert execute.returncode == 0
    report_data = json.loads(out_file.read_text())

    assert out_file.exists()
    assert report_data["total_events"] == 2


def test_cli_csv(tmp_path):
    in_file = create_csv_file(tmp_path, [VALID_CSV_1])
    out_file = tmp_path / "report.json"

    execute = subprocess.run(
        [
            "uv",
            "run",
            "python",
            "-m",
            "src.streamstats",
            "analyze",
            in_file,
            "--format",
            "csv",
            "--output",
            out_file,
        ],
        check=False,
    )

    assert execute.returncode == 0
    report_data = json.loads(out_file.read_text())

    assert out_file.exists()
    assert report_data["total_events"] == 1
