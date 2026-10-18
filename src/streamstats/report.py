import json
import sys
from pathlib import Path

from .analysis import Stats


def get_data_for_report(stats: Stats) -> dict:
    """Сформировать отчет по статистике"""
    top_five = stats.get_top_five()
    return {
        "total_events": stats.total_events,
        "by_level": dict(stats.by_level),
        "by_source": dict(stats.by_source),
        "top_error_sources": top_five,
        "first_timestamp": stats.first_timestamp.isoformat()
        if stats.first_timestamp
        else None,
        "last_timestamp": stats.last_timestamp.isoformat()
        if stats.last_timestamp
        else None,
        "skipped_lines": stats.skipped,
    }


def create_report(path: Path, stats: Stats):
    """Запись отчета в json"""
    data_report: dict = get_data_for_report(stats=stats)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data_report, file, ensure_ascii=False, indent=4)

    sys.stdout.write("Report was created\n")
