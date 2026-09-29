from __future__ import annotations

import argparse

from playwright.sync_api import sync_playwright

from src.agent.observer import PageObserver
from src.agent.planner import LocalPlanner
from src.artifact.models import (
    ActionStep,
    Capability,
    ExpectedOutcome,
)
from src.artifact.recorder import CapabilityRecorder
from src.surface.browser import BrowserSurface
from src.observability.logger import EventLogger


MAX_STEPS = 15


def run_local_agent(
    member_id: str,
    headless: bool = False,
) -> Capability:
    observer = PageObserver()
    planner = LocalPlanner()
    logger = EventLogger("evidence/agent_events.jsonl")
    recorded_steps: list[ActionStep] = []

    logger.log(
        "agent_started",
        member_id=member_id,
        mode="local",
        llm_used=False,
    )

    with sync_playwright() as playwright:
        surface = BrowserSurface(
            playwright=playwright,
            base_url="http://127.0.0.1:8000",
            headless=headless,
        )

        page = surface.start()

        try:
            # Initial navigation
            surface.open("/")

            recorded_steps.append(
                ActionStep(
                    action="goto",
                    path="/",
                    description="Open application",
                )
            )

            for step_number in range(1, MAX_STEPS + 1):
                state = observer.observe(page)

                print(
                    f"\n[agent step {step_number}] "
                    f"{state['title']}"
                )
                print(
                    f"[observe] elements={state['elements']}"
                )

                logger.log(
                    "page_observed",
                    step=step_number,
                    url=state["url"],
                    title=state["title"],
                    elements=state["elements"],
                )

                action = planner.decide(
                    state,
                    member_id,
                )

                logger.log(
                    "action_planned",
                    step=step_number,
                    action=action.action,
                    selector=action.selector,
                    description=action.description,
                )

                print(
                    f"[plan] {action.action}: "
                    f"{action.description}"
                )

                if action.action == "failed":
                    raise RuntimeError(
                        action.description
                    )

                if action.action == "extract_text":
                    value = surface.text(
                        action.selector
                    )

                    recorded_steps.append(
                        ActionStep(
                            action="extract_text",
                            selector=action.selector,
                            description=action.description,
                        )
                    )

                    print(
                        f"[result] Savings balance: {value}"
                    )

                    capability = Capability(
                        capability_id=(
                            "lookup_savings_balance"
                        ),
                        name="Lookup Savings Balance",
                        description=(
                            "Search the Northstar training "
                            "portal for a member and retrieve "
                            "their savings balance."
                        ),
                        inputs={
                            "member_id": member_id,
                        },
                        steps=recorded_steps,
                        expected_outcome=ExpectedOutcome(
                            selector="#savings-balance",
                            expected_text=value,
                            description=(
                                "Savings balance is visible"
                            ),
                        ),
                        metadata={
                            "planner": "local_rule_based",
                            "llm_used": "false",
                            "replay_mode":
                                "deterministic",
                            "environment": "training",
                        },
                    )

                    path = CapabilityRecorder().save(
                        capability
                    )

                    surface.screenshot(
                        "evidence/screenshots/"
                        "local_agent_success.png"
                    )

                    print(
                        f"[artifact] Saved to {path}"
                    )

                    logger.log(
                        "agent_completed",
                        status="success",
                        capability_id=capability.capability_id,
                        result=value,
                        recorded_steps=len(recorded_steps),
                    )

                    return capability

                if action.action == "fill":
                    surface.fill(
                        action.selector,
                        action.value or "",
                    )

                    recorded_value = action.value

                    if action.selector == "#member_id":
                        recorded_value = "{{member_id}}"

                    recorded_steps.append(
                        ActionStep(
                            action="fill",
                            selector=action.selector,
                            value=recorded_value,
                            description=action.description,
                        )
                    )

                elif action.action == "click":
                    surface.click(
                        action.selector
                    )

                    recorded_steps.append(
                        ActionStep(
                            action="click",
                            selector=action.selector,
                            description=action.description,
                        )
                    )

                elif action.action == "wait_for":
                    surface.wait_for(
                        action.selector
                    )

                    recorded_steps.append(
                        ActionStep(
                            action="wait_for",
                            selector=action.selector,
                            description=action.description,
                        )
                    )

            raise RuntimeError(
                f"Agent exceeded {MAX_STEPS} steps."
            )

        finally:
            surface.close()



def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the local UI-observing automation agent."
    )

    parser.add_argument(
        "--member-id",
        default="12345",
    )

    parser.add_argument(
        "--headless",
        action="store_true",
    )

    args = parser.parse_args()

    try:
        capability = run_local_agent(
            member_id=args.member_id,
            headless=args.headless,
        )

        print("\nAgent run complete")
        print(
            f"Capability: {capability.capability_id}"
        )
        print(
            f"Recorded steps: {len(capability.steps)}"
        )
        print("LLM used during discovery: No")

    except RuntimeError as exc:
        print("\nAgent run stopped safely")
        print(f"Reason: {exc}")
        print("Capability recorded: No")


if __name__ == "__main__":
    main()
