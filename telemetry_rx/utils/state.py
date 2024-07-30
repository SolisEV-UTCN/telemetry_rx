from enum import auto, IntEnum


class AppState(IntEnum):
    INIT = 0
    COMM = auto()
    STOP = auto()
    ERROR = auto()
