from __future__ import annotations

import threading
from enum import Enum, auto
from typing import Optional, Set
from colorama import Fore
from loggerric._timestamp import Timestamp
from loggerric._log_to_file import LogToFile, LogToFileLevel, escape_ansi


# Module-level lock used by all Logger instances to avoid interleaved prints
_print_lock = threading.Lock()


class Level(Enum):
    INFO = auto()
    WARN = auto()
    ERROR = auto()
    DEBUG = auto()


class ThreadSafeLogger:
    """A simple thread-safe logger for console printing (and optional file logging).

    - All instances share an internal print lock so printed lines are not
      interleaved when called from multiple threads.
    - Each instance has its own enabled log level set, so you can create
      multiple loggers with different verbosity.
    - Optionally forwards messages to `LogToFile` (uses package's file writer).
    """

    def __init__(self, name: str = "root", *, enabled_levels: Optional[Set[Level]] = None,
                 forward_to_file: bool = False):
        self.name = name
        self._enabled_levels: Set[Level] = enabled_levels or {Level.INFO, Level.WARN, Level.ERROR, Level.DEBUG}
        self._forward_to_file = forward_to_file

    # Level management
    def enable(self, *levels: Level) -> None:
        self._enabled_levels.update(levels)

    def disable(self, *levels: Level) -> None:
        for l in levels:
            self._enabled_levels.discard(l)

    def set_levels(self, levels: Set[Level]) -> None:
        self._enabled_levels = set(levels)

    def is_enabled(self, level: Level) -> bool:
        return level in self._enabled_levels

    # Internal formatting
    def _format(self, level_tag: str, color: str, message: str) -> str:
        ts = ''
        try:
            ts = Timestamp.get(return_with_ansi=True)
        except Exception:
            ts = ''
        name_part = f'[{self.name}] '
        return f'{ts}{color}{level_tag} {name_part}{message}{Fore.RESET}'

    def _print(self, text: str) -> None:
        # Acquire the module-level lock so entire print is atomic
        with _print_lock:
            print(text, flush=True)

    def _maybe_forward_file(self, text_with_ansi: str, level: Level) -> None:
        if not self._forward_to_file:
            return

        # Map Level to LogToFileLevel conservatively
        mapping = {
            Level.INFO: LogToFileLevel.INFO,
            Level.WARN: LogToFileLevel.WARN,
            Level.ERROR: LogToFileLevel.ERROR,
            Level.DEBUG: LogToFileLevel.DEBUG,
        }
        ltf_level = mapping.get(level, LogToFileLevel.INFO)
        if ltf_level in LogToFile._active_levels and LogToFile._should_dump:
            # Use escape_ansi then forward to global writer
            LogToFile._log(escape_ansi(text_with_ansi))

    # Public logging methods
    def info(self, *parts: object) -> None:
        if not self.is_enabled(Level.INFO):
            return
        raw = ' '.join(str(p) for p in parts)
        formatted = self._format('[i]', Fore.GREEN, raw)
        self._print(formatted)
        self._maybe_forward_file(formatted, Level.INFO)

    def warn(self, *parts: object) -> None:
        if not self.is_enabled(Level.WARN):
            return
        raw = ' '.join(str(p) for p in parts)
        formatted = self._format('[w]', Fore.YELLOW, raw)
        self._print(formatted)
        self._maybe_forward_file(formatted, Level.WARN)

    def error(self, *parts: object, quit_after: bool = False) -> None:
        if not self.is_enabled(Level.ERROR):
            if quit_after:
                exit(1)
            return
        raw = ' '.join(str(p) for p in parts)
        formatted = self._format('[!]', Fore.RED, raw)
        self._print(formatted)
        self._maybe_forward_file(formatted, Level.ERROR)
        if quit_after:
            exit(1)

    def debug(self, *parts: object) -> None:
        if not self.is_enabled(Level.DEBUG):
            return
        raw = ' '.join(str(p) for p in parts)
        formatted = self._format('[?]', Fore.LIGHTBLACK_EX, raw)
        self._print(formatted)
        self._maybe_forward_file(formatted, Level.DEBUG)


# Convenience: a simple registry/factory
_loggers: dict[str, ThreadSafeLogger] = {}


def get_logger(name: str = 'root', *, forward_to_file: bool = False) -> ThreadSafeLogger:
    """Return a (cached) logger instance by name."""
    if name in _loggers:
        return _loggers[name]
    logger = ThreadSafeLogger(name, forward_to_file=forward_to_file)
    _loggers[name] = logger
    return logger


# Default root logger instance
ROOT_LOGGER = get_logger('root')
