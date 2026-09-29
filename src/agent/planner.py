from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class PlannedAction:
    action: str
    selector: Optional[str] = None
    value: Optional[str] = None
    description: str = ""


class LocalPlanner:
    """
    Deterministic planner used for the free local demo.

    This planner does not call an LLM. It chooses actions from
    observable page state using simple rules.
    """

    def decide(
        self,
        page_state: dict,
        member_id: str,
    ) -> PlannedAction:

        url = page_state["url"]
        elements = page_state["elements"]

        # Login page
        if "username" in elements and "password" in elements:
            if not page_state.get("username_filled"):
                return PlannedAction(
                    action="fill",
                    selector="#username",
                    value="operator",
                    description="Enter operator username",
                )

            if not page_state.get("password_filled"):
                return PlannedAction(
                    action="fill",
                    selector="#password",
                    value="demo123",
                    description="Enter operator password",
                )

            return PlannedAction(
                action="click",
                selector="button[type='submit']",
                description="Sign in",
            )

        # Member search page
        if "member_id" in elements:
            if not page_state.get("member_id_filled"):
                return PlannedAction(
                    action="fill",
                    selector="#member_id",
                    value=member_id,
                    description="Enter member ID",
                )

            return PlannedAction(
                action="click",
                selector=".search-button",
                description="Search for member",
            )

        # Successful member page
        if "savings-balance" in elements:
            return PlannedAction(
                action="extract_text",
                selector="#savings-balance",
                description="Read savings balance",
            )

        # Known failure page
        if "member-not-found" in elements:
            return PlannedAction(
                action="failed",
                selector="#member-not-found",
                description="Member was not found",
            )

        return PlannedAction(
            action="failed",
            description=f"Unknown page state at {url}",
        )
