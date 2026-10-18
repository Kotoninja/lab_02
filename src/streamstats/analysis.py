from datetime import datetime

from .models import Event


class Stats:
    def __init__(self):
        """Инициализация статистики """
        self.total_events: int = 0
        self.by_level: dict[str, int] = {}
        self.by_source: dict[str, int] = {}
        self.top_error: dict[str, int] = {}
        self.first_timestamp: datetime | None = None
        self.last_timestamp: datetime | None = None
        self.skipped: int = 0

    def add(self, event: Event):
        """Добавление новой статистики"""
        self.total_events += 1
        self.by_level[event.level] = self.by_level.get(event.level, 0) + 1
        self.by_source[event.source] = self.by_source.get(event.source, 0) + 1
        if event.level in ("ERROR", "CRITICAL"):
            self.top_error[event.source] = self.top_error.get(event.source, 0) + 1
        if self.first_timestamp is None or event.timestamp < self.first_timestamp:
            self.first_timestamp = event.timestamp
        if self.last_timestamp is None or event.timestamp > self.last_timestamp:
            self.last_timestamp = event.timestamp

    def get_top_five(
        self,
    ):
        """Получение новой статистики"""
        return [
            {"source": source, "count": self.top_error[source]}
            for source in sorted(
                self.top_error, reverse=True, key=lambda x: self.top_error[x]
            )
        ][:5]
