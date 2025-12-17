# =====================================================================
# FILE: src/teamdynamix/event.py
# (kept close to refactor style; compatible with Logger above)
# =====================================================================
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any


@dataclass(slots=True)
class Event:
    message: str
    level: int = 20
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    context: Optional[Dict[str, Any]] = None

    def __str__(self) -> str:
        ts = self.created_at.isoformat()
        ctx = f" | context={self.context}" if self.context else ""
        return f"{ts} [{self.level}] {self.message}{ctx}\n"
