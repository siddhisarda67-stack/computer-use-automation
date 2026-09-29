from __future__ import annotations

import argparse
from typing import Any

from playwright.sync_api import sync_playwright

from src.artifact.models import ActionStep, Capability
from src.artifact.recorder import CapabilityRecorder
from src.surface.browser import BrowserSurface


def resolve_value(
    value: str | None,
    inputs: dict[str, str],
) -> str:
    """Replace {{input_name}} placeholders with runtime values."""

    if value is None:
        return ""

    resolved = value

    for key, replacement in inputs.items():
        resolved = resolved.replace(
            "{{" + key + "}}",
            replacement,
        )

    return resolved


class CapabilityReplayer:
    """
    Execute a saved capability deterministically.

    No LLM is used during replay.
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        headless: bool = False,
    ):
        self.base_url = base_url
        self.headless = headless

    def execute_step(
        self,
        surface: BrowserSurface,
        step: ActionStep,
        inputs: dict[str, str],
    ) -> Any:

        if step.action == "goto":
            if not step.path:
                raise ValueError(
                    "goto action requires a path"
                )

            surface.open(
                resolve_value(step.path, inputs)
            )

        elif step.action == "fill":
            if not step.selector:
                raise ValueError(
                    "fill action requires a selector"
                )

            surface.fill(
                step.selector,
                resolve_value(step.value, inputs),
            )

        elif step.action == "click":
            if not step.selector:
                raise ValueError(
                    "click action requires a selector"
                )

            surface.click(step.selector)

        elif step.action == "wait_for":
            if not step.selector:
                raise ValueError(
                    "wait_for action requires a selector"
                )

            surface.wait_for(step.selector)

        elif step.action == "extract_text":
            if not step.selector:
                raise ValueError(
                    "extract_text action requires a selector"
                )

            return surface.text(step.selector)

        else:
            raise ValueError(
                f"Unsupported action: {step.action}"
            )

        return None

    def replay(
        self,
        capability: Capability,
        runtime_inputs: dict[str, str] | None = None,
    ) -> dict[str, Any]:

        inputs = dict(capability.inputs)

        if runtime_inputs:
            inputs.update(runtime_inputs)

        extracted: list[str] = []

        with sync_playwright() as playwright:

            surface = BrowserSurface(
                playwright=playwright,
                base_url=self.base_url,
                headless=self.headless,
            )

            surface.start()

            try:
                for number, step in enumerate(
                    capability.steps,
                    start=1,
                ):
                    print(
                        f"[{number}/{len(capability.steps)}] "
                        f"{step.description}"
                    )

                    result = self.execute_step(
                        surface,
                        step,
                        inputs,
                    )

                    if result is not None:
                        extracted.append(str(result))

                outcome = capability.expected_outcome

                surface.wait_for(outcome.selector)

                actual_text = surface.text(
                    outcome.selector
                )

                if (
                    outcome.expected_text
                    and outcome.expected_text
                    not in actual_text
                ):
                    raise AssertionError(
                        "Expected outcome validation failed.\n"
                        f"Expected text: "
                        f"{outcome.expected_text}\n"
                        f"Actual text: {actual_text}"
                    )

                surface.screenshot(
                    "evidence/screenshots/"
                    f"{capability.capability_id}_replay.png"
                )

                return {
                    "status": "success",
                    "capability_id":
                        capability.capability_id,
                    "final_url":
                        surface.current_url(),
                    "outcome_text":
                        actual_text,
                    "extracted":
                        extracted,
                    "llm_calls": 0,
                }

            finally:
                surface.close()


def main() -> None:

    parser = argparse.ArgumentParser(
        description=(
            "Replay a saved browser capability "
            "without an LLM."
        )
    )

    parser.add_argument(
        "capability_id",
        help="Capability artifact ID",
    )

    parser.add_argument(
        "--member-id",
        dest="member_id",
        help="Optional runtime member ID",
    )

    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser without opening a window",
    )

    args = parser.parse_args()

    recorder = CapabilityRecorder()

    capability = recorder.load(
        args.capability_id
    )

    runtime_inputs: dict[str, str] = {}

    if args.member_id:
        runtime_inputs["member_id"] = args.member_id

    replayer = CapabilityReplayer(
        headless=args.headless
    )

    result = replayer.replay(
        capability,
        runtime_inputs=runtime_inputs,
    )

    print("\nReplay complete")
    print(f"Status: {result['status']}")
    print(f"Final URL: {result['final_url']}")
    print(f"LLM calls: {result['llm_calls']}")


if __name__ == "__main__":
    main()
