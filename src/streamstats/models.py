from dataclasses import dataclass
from datetime import datetime

from . import errors

LEVELS_ENUM: set[str] = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


@dataclass
class Event:
    timestamp: datetime
    level: str
    source: str
    message: str


def create_event(data: dict) -> Event:
    """Создание события"""
    if not isinstance(data, dict):
        raise errors.InvalidEventError("Невалидное событие")

    for field in ["timestamp", "level", "source", "message"]:
        if field not in data:
            raise errors.InvalidEventError(f"Недопустипое поле {field}")

    try:
        timestamp = datetime.fromisoformat(data["timestamp"])
        if timestamp.tzinfo is None:
            raise errors.InvalidTimestampError
    except (TypeError, ValueError):
        raise errors.InvalidTimestampError

    level = data["level"]
    if not isinstance(level, str) or level not in LEVELS_ENUM:
        raise errors.InvalidEventError(f"Неизвестный level {level}")

    source = data["source"]
    if not isinstance(source, str) or not len(source.rstrip()):
        raise errors.InvalidEventError("Source должен быть не пустой строкой")

    message = data["message"]
    if not isinstance(message, str):
        raise errors.InvalidEventError("Message должен быть строкой")

    return Event(
        timestamp=datetime.fromisoformat(data["timestamp"]),
        level=data["level"],
        source=data["source"],
        message=data["message"],
    )
