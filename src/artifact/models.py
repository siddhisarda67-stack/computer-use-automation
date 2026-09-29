from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, Field


ActionType = Literal[
    "goto",
    "fill",
    "click",
    "wait_for",
    "extract_text",
]


class ActionStep(BaseModel):
    """One deterministic browser action."""

    action: ActionType
    selector: Optional[str] = None
    value: Optional[str] = None
    path: Optional[str] = None
    description: str


class ExpectedOutcome(BaseModel):
    """Conditions that prove the capability succeeded."""

    selector: str
    expected_text: Optional[str] = None
    description: str


class Capability(BaseModel):
    """
    Reusable browser capability learned during an agent run.

    Replay executes these steps directly without an LLM.
    """

    capability_id: str
    name: str
    description: str

    created_at: str = Field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )

    source: str = "agent_discovery"
    version: str = "1.0"

    inputs: dict[str, str] = Field(default_factory=dict)

    steps: list[ActionStep]

    expected_outcome: ExpectedOutcome

    metadata: dict[str, str] = Field(default_factory=dict)
