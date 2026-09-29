from src.artifact.models import (
    ActionStep,
    Capability,
    ExpectedOutcome,
)
from src.artifact.recorder import CapabilityRecorder


def test_capability_round_trip(tmp_path):
    recorder = CapabilityRecorder(
        artifact_dir=str(tmp_path)
    )

    capability = Capability(
        capability_id="test_lookup",
        name="Test Lookup",
        description="Test capability serialization",
        inputs={"member_id": "12345"},
        steps=[
            ActionStep(
                action="fill",
                selector="#member_id",
                value="{{member_id}}",
                description="Enter member ID",
            )
        ],
        expected_outcome=ExpectedOutcome(
            selector="#savings-balance",
            expected_text="8720.5",
            description="Balance visible",
        ),
    )

    recorder.save(capability)
    loaded = recorder.load("test_lookup")

    assert loaded.capability_id == "test_lookup"
    assert loaded.inputs["member_id"] == "12345"
    assert len(loaded.steps) == 1
    assert loaded.steps[0].selector == "#member_id"
    assert loaded.expected_outcome.expected_text == "8720.5"


def test_runtime_placeholder_is_preserved():
    step = ActionStep(
        action="fill",
        selector="#member_id",
        value="{{member_id}}",
        description="Enter member ID",
    )

    assert step.value == "{{member_id}}"
