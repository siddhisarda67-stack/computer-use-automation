import pytest

from src.safety.policy import (
    SafetyPolicy,
    SafetyViolation,
)


def test_safe_read_action_allowed():
    policy = SafetyPolicy()

    policy.validate(
        "extract_text",
        "#savings-balance",
    )


def test_sensitive_action_blocked():
    policy = SafetyPolicy()

    with pytest.raises(SafetyViolation):
        policy.validate(
            "click",
            ".danger-action",
        )


def test_unknown_action_blocked():
    policy = SafetyPolicy()

    with pytest.raises(SafetyViolation):
        policy.validate(
            "execute_javascript",
            None,
        )
