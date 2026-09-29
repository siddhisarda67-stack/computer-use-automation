from __future__ import annotations

import json
from pathlib import Path

from src.artifact.models import Capability


class CapabilityRecorder:
    """Save and load reusable capability artifacts."""

    def __init__(self, artifact_dir: str = "artifacts"):
        self.artifact_dir = Path(artifact_dir)
        self.artifact_dir.mkdir(parents=True, exist_ok=True)

    def save(self, capability: Capability) -> Path:
        output_path = (
            self.artifact_dir /
            f"{capability.capability_id}.json"
        )

        with output_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                capability.model_dump(),
                file,
                indent=2,
                ensure_ascii=False,
            )

        return output_path

    def load(self, capability_id: str) -> Capability:
        input_path = (
            self.artifact_dir /
            f"{capability_id}.json"
        )

        if not input_path.exists():
            raise FileNotFoundError(
                f"Capability not found: {input_path}"
            )

        with input_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        return Capability.model_validate(data)
