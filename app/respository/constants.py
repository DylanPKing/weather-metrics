from enum import StrEnum, auto


class Metric(StrEnum):
    TEMPERATURE = auto()
    HUMIDITY = auto()
    WIND_SPEED = auto()


class Statistic(StrEnum):
    MIN = auto()
    MAX = auto()
    SUM = auto()
    AVERAGE = auto()
