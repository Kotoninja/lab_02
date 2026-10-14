class SteamStatsError(Exception):
    """Базовая ошибка SteamStats"""


class UnsupportedFormatError(SteamStatsError):
    """Неподдерживаемый формат"""

    def __init__(self, field):
        super().__init__(f"Неподдерживаемый формат {field}")


class InvalidEventError(SteamStatsError):
    """Неверное событие"""


class InvalidTimestampError(SteamStatsError):
    """Неверная временная метка"""

    def __init__(self):
        super().__init__("Неверная временная метка")


class CLIConfigurationError(SteamStatsError):
    """Ошибка конфигурации CLI"""

    def __init__(self):
        super().__init__("Ошибка конфигурации CLI")
