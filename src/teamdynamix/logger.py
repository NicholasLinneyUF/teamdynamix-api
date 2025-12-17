# =====================================================================
# FILE: src/teamdynamix/logger.py
# =====================================================================
from __future__ import annotations

from pathlib import Path
from typing import List, Optional
import threading
import time

from .event import Event


_LEVELS = {
    "CRITICAL": 50,
    "ERROR": 40,
    "WARNING": 30,
    "WARN": 30,
    "INFO": 20,
    "DEBUG": 10,
}


class Logger:
    """
    Minimal logger:
    - Keeps an in-memory list of Event objects
    - Writes to a timestamped file under log_dir
    - Prints to console (optional)
    - Default level behavior: ERROR (catches errors/exceptions, ignores warnings)
    """
    def __init__(
        self,
        log_dir: str | Path = "./logs",
        level: str = "ERROR",
        console: bool = True,
        name_prefix: str = "log",
    ):
        self._lock = threading.RLock()
        self.events: List[Event] = []

        self.level_name = (level or "ERROR").strip().upper()
        self.level = _LEVELS.get(self.level_name, 40)

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        ts = time.strftime("%Y%m%d%H%M%S")
        self.log_file = self.log_dir / f"{name_prefix}-{ts}.txt"
        self.console = bool(console)

    def log(self, message: str, level: int | None = None, context: Optional[dict] = None) -> None:
        lvl = self.level if level is None else int(level)

        # Filter: only record if lvl >= configured level
        if lvl < self.level:
            return

        event = Event(message=message, level=lvl, context=context)
        with self._lock:
            self.events.append(event)

        # Console behavior requirement: print(event, end='')
        if self.console:
            print(event, end="")

        # File append
        with self.log_file.open("a", encoding="utf-8") as f:
            f.write(str(event))

    def clear_events(self) -> None:
        with self._lock:
            self.events.clear()
