from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class EventLogger:
    """Write structured agent events as JSON Lines."""

    def __init__(
        self,
        path: str = "evidence/agent_events.jsonl",
    ):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        event: str,
        **data: Any,
    ) -> None:
        record = {
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "event": event,
            **data,
        }

        with self.path.open(
            "a",
            encoding="utf-8",
        ) as file:
            file.write(
                json.dumps(record) + "\n"
            )
