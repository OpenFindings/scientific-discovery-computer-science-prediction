from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Union


class ResearchMemory:
    def __init__(self, path: Union[str, Path]):
        self.path = Path(path)
        self.events: list[dict] = []

    def record(self, event_type: str, payload: dict) -> None:
        self.events.append({"event_type": event_type, "payload": payload})

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.events, indent=2, sort_keys=True) + "\n")
