import csv
import json
import logging
import sys
from collections.abc import Iterator
from pathlib import Path

from . import errors
from .analysis import Stats
from .models import Event, create_event

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format="%(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


def log(file, line, error):
    logger.warning(f"file '{file}' line {line}: {error}")


def json_parser(f: Path, skip_invalid: bool, stats: Stats) -> Iterator[Event]:
    try:
        with f.open("r", encoding="utf-8") as file:
            for number, line in enumerate(file, start=1):
                line = line.rstrip("\n")

                if not line:
                    continue

                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    raise errors.InvalidEventError(f"Невалидный json. Line {number}")

                try:
                    yield create_event(data)
                except errors.SteamStatsError as e:
                    if skip_invalid:
                        stats.skipped += 1
                        continue
                    log(f, number, e)
                    raise

    except FileNotFoundError:
        raise FileNotFoundError(f"Файл не найден: {f}")


def csv_parser(f: Path, skip_invalid: bool, stats) -> Iterator[Event]:
    try:
        with f.open("r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for number, line in enumerate(reader, start=2):
                try:
                    yield create_event(line)
                except errors.SteamStatsError as e:
                    if skip_invalid:
                        stats.skipped += 1
                        continue
                    log(f, number, e)
                    raise
    except FileNotFoundError:
        raise FileNotFoundError(f"Файл не найден: {f}")


def get_parser(format: str):
    match format:
        case "jsonl":
            data_parser = json_parser
        case "csv":
            data_parser = csv_parser
        case _:
            raise errors.UnsupportedFormatError(field=format)
    return data_parser
