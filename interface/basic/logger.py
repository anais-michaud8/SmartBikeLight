

import gc
gc.collect()

import time
from micropython import const

from interface.basic.utils import adjuster

CRITICAL = const(50)
ERROR = const(40)
WARNING = const(30)
SUCCESS = const(25)
INFO = const(20)
DEBUG = const(10)
TRACE = const(5)


_LEVELS_STR = {
    CRITICAL: "CRITICAL",
    ERROR: "ERROR",
    WARNING: "WARNING",
    SUCCESS: "SUCCESS",
    INFO: "INFO",
    DEBUG: "DEBUG",
    TRACE: "TRACE",
}

_LEVELS_COLOURS = {
    CRITICAL: "RED",
    ERROR: "ORANGE",
    WARNING: "YELLOW",
    SUCCESS: "GREEN",
    INFO: "BLUE",
    DEBUG: "CYAN",
    TRACE: "GREY",
}


_LEVEL_LENGTH = const(7)
_NAME_LENGTH = const(20)


gc.collect()


def _get_level_int(level: str | int) -> int:
    if isinstance(level, int):
        return level
    for key, value in _LEVELS_STR.items():
        if level.upper() == value:
            return key
    return DEBUG


def _get_level_str(level: str | int) -> str:
    if isinstance(level, int):
        return _LEVELS_STR.get(level, "DEBUG")
    return level.upper()


gc.collect()


class Logging:
    is_logging: bool = False
    level: str | int = DEBUG
    clock=None
    styler=None
    stream_str=print
    stream_dict=None

    def __init__(self, name: str | None = None, is_logging: bool | None = None,
                 obj: object | None = None, style: str | None = None, **kwargs):
        if name is not None:
            self._name = name
        if obj is not None:
            self._obj = obj
        if is_logging is not None:
            self.is_logging = is_logging
        if style is not None:
            self.style = style

    @property
    def name(self) -> str:
        return self._name if hasattr(self, "_name") else self._obj.__class__.__name__ if hasattr(self, "_obj") else "Logging"

    @property
    def now(self) -> str:
        return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}".format(*time.localtime()[:6]) if self.clock is None else self.clock.iso

    def to_dict(self, message: str, level: str | int = "DEBUG", style: str | None = None) -> dict:
        return {
                   "name": self.name, "message": message, "level": _get_level_int(level), "time": self.now
            } | ({"style": style} if style is not None else {"style": self.style} if hasattr(self, "style") else {})

    def to_str(self, message: str, level: str | int = "DEBUG", style: str | None = None):
        gc.collect()
        msg = f"{adjuster(self.name, padding=_NAME_LENGTH, character=' ', left=True, right=False)} | " \
            + f"{adjuster(_get_level_str(level), padding=_LEVEL_LENGTH, character=' ', left=True, right=False)} | " \
            + f"{self.now} | {message}"
        return self.__class__.styler(
            msg,
            self.style if hasattr(self, "style") else style if style is not None
                else _LEVELS_COLOURS.get(_get_level_int(level), "WHITE")
        ) if self.styler is not None else msg

    def _logging(self, message: str, level: str = "DEBUG", style: str | None = None):
        if self.stream_str:
            self.stream_str(self.to_str(message, level, style))
        if self.stream_dict:
            self.stream_dict(self.to_dict(message, level, style))

    def logging(self, message: str, level: str = "DEBUG", style: str | None = None, **kwargs):
        if self.is_logging:
            self._logging(message, level=level, style=style)

    def __call__(self, message: str, level: str = "DEBUG", style: str | None = None, **kwargs):
        self.logging(message, level=level, style=style, **kwargs)


gc.collect()
