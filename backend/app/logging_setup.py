"""
In-memory application log store.

Captures INFO+ from `app.*` loggers and WARNING+ from everything else.
Capped at MAX_ENTRIES so memory stays bounded.  Logs are ephemeral —
they reset on container restart. Use the /admin/logs endpoint to read them.
"""
import logging
from collections import deque
from datetime import datetime, timezone
from typing import Optional

MAX_ENTRIES = 500

_store: deque[dict] = deque(maxlen=MAX_ENTRIES)


class MemoryLogHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            _store.append({
                "id": id(record),
                "level": record.levelname,
                "logger": record.name,
                "message": self.format(record),
                "created_at": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            })
        except Exception:
            pass


def setup_logging() -> None:
    handler = MemoryLogHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))

    # Capture all app.* logs at INFO+
    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.INFO)
    app_logger.addHandler(handler)

    # Capture WARNING+ from everything else (uvicorn errors, sqlalchemy warnings, etc.)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.WARNING)
    root_logger.addHandler(handler)

    # ARQ worker logs
    arq_logger = logging.getLogger("arq")
    arq_logger.setLevel(logging.INFO)
    arq_logger.addHandler(handler)


def get_logs(
    level: Optional[str] = None,
    logger_filter: Optional[str] = None,
    limit: int = 200,
) -> list[dict]:
    entries = list(_store)
    if level and level != "ALL":
        entries = [e for e in entries if e["level"] == level]
    if logger_filter:
        entries = [e for e in entries if logger_filter.lower() in e["logger"].lower()]
    return list(reversed(entries))[-limit:]
