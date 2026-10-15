class StreamStatsError(Exception):
    """Базовая ошибка SteamStats"""


class UnsupportedFormatError(StreamStatsError):
    """Неподдерживаемый формат"""

    def __init__(self, field):
        super().__init__(f"Неподдерживаемый формат {field}")


class InvalidEventError(StreamStatsError):
    """Неверное событие"""


class InvalidTimestampError(StreamStatsError):
    """Неверная временная метка"""

    def __init__(self):
        super().__init__("Неверная временная метка")


class CLIConfigurationError(StreamStatsError):
    """Ошибка конфигурации CLI"""

    def __init__(self):
        super().__init__("Ошибка конфигурации CLI")
