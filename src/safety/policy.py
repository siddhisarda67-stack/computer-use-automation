from __future__ import annotations


class SafetyViolation(RuntimeError):
    """Raised when an automation action violates policy."""


class SafetyPolicy:
    ALLOWED_ACTIONS = {
        "goto",
        "fill",
        "click",
        "wait_for",
        "extract_text",
    }

    BLOCKED_SELECTORS = {
        ".danger-action",
        "#close-account",
        "#transfer-funds",
        "#delete-account",
    }

    def validate(
        self,
        action: str,
        selector: str | None = None,
    ) -> None:
        if action not in self.ALLOWED_ACTIONS:
            raise SafetyViolation(
                f"Unsupported action: {action}"
            )

        if selector in self.BLOCKED_SELECTORS:
            raise SafetyViolation(
                f"Blocked sensitive action: {selector}"
            )
