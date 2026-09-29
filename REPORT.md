# Technical Report — Computer-Use Automation

## 1. Overview

This project explores a simple idea: browser workflows should not need to be rediscovered every time they are executed.

The prototype separates workflow discovery from workflow replay. During discovery, the system observes a web interface, determines appropriate actions, executes them, and records the successful sequence as a reusable capability artifact.

That artifact can then be executed deterministically without invoking the planner again.

A fictional credit-union operations portal, Northstar Credit Union, was created to provide a controlled environment for demonstrating the approach.

## 2. Demonstration Task

The primary task is:

> Look up a member and retrieve the balance of their savings account.

Member `12345` is used as the successful demonstration case.

The workflow requires the system to:

1. Open the portal.
2. Authenticate.
3. Navigate to member search.
4. Enter the member ID.
5. Submit the search.
6. Recognize the member-details page.
7. Locate the savings account.
8. Extract the savings balance.

For the demonstration data, the resulting savings balance is `8720.5`.

## 3. System Design

The implementation is divided into several small components rather than placing all browser logic in one automation script.

### Browser Surface

The browser surface wraps Playwright and provides operations such as navigation, filling inputs, clicking controls, extracting text, waiting for elements, and taking screenshots.

### Observer

The observer examines the rendered webpage and produces structured state describing relevant visible elements.

This means the discovery loop can react to the current UI rather than assuming that it is always on a particular page.

### Planner

The current runnable planner is a deterministic local planner.

It receives the observed page state and selects the next action.

This implementation does not use an LLM. This was an intentional development choice so the complete demonstration can run locally without requiring paid API credits.

The architecture separates planning from execution so that a model-backed planner could later replace the local planner without requiring the browser, artifact, or replay layers to be redesigned.

### Safety Policy

Before a planned action is executed, it is checked against a safety policy.

The policy permits the browser operations required for the read-only workflow and rejects unsupported operations or explicitly sensitive selectors.

### Capability Recorder

After successful discovery, the executed workflow is serialized into a JSON capability artifact.

The artifact contains the sequence of actions required to reproduce the workflow.

Runtime information such as the member ID is represented using a placeholder rather than permanently hard-coding the discovery value.

### Replay Engine

The replay engine loads the capability and executes the stored actions directly.

The discovery planner is not used during replay.

The successful demonstration therefore reports:

`LLM calls: 0`

during replay.

## 4. Discovery Loop

The discovery process follows an observe-plan-act cycle:

`Observe → Plan → Safety Check → Execute → Observe Again`

The loop continues until one of three conditions occurs:

- the target information is successfully extracted;
- a known failure state is detected; or
- the maximum allowed number of steps is reached.

Successful actions are recorded during this process.

Only a successful workflow is converted into the reusable capability.

## 5. Failure Handling

The prototype includes a member-not-found scenario.

When an invalid member ID such as `99999` is entered, the observer identifies the failure state.

The planner returns a failure result and the discovery process stops rather than continuing to interact with an unexpected page or recording an invalid capability.

This is important because a reusable artifact should represent a verified successful workflow rather than simply a sequence of attempted clicks.

## 6. Deterministic Replay

The most important distinction in the prototype is between discovery and replay.

Discovery determines how to perform the workflow.

Replay already knows how to perform it.

For that reason, replay reads the recorded artifact and executes its actions directly through the browser surface.

In the demonstrated run:

- replay completed successfully;
- the expected savings-balance element was reached;
- screenshot evidence was generated; and
- replay required zero LLM calls.

## 7. Observability

The system records structured JSONL events during discovery.

Events include:

- agent start;
- page observations;
- planned actions; and
- successful completion.

Passwords and other form values are not included in the structured action logs.

Screenshots are also generated for successful discovery and replay runs.

This provides both machine-readable execution history and visual evidence.

## 8. Safety

The demonstration is intentionally limited to a fictional environment.

Several safeguards are used:

- all financial data is fictional;
- no real banking service is contacted;
- transactional controls in the mock UI are disabled;
- the automation contains an explicit action policy;
- sensitive selectors are blocked;
- environment secrets are excluded from Git; and
- logs avoid recording password values.

The task itself is read-only.

## 9. Testing

Automated tests were added for the reusable components.

The current suite contains 10 passing tests covering:

- artifact serialization;
- preservation of runtime placeholders;
- login planning;
- member-search planning;
- balance extraction planning;
- member-not-found behavior;
- allowed read actions;
- blocked sensitive actions; and
- rejection of unsupported operations.

Tests can be executed with:

`PYTHONPATH=. python -m pytest -q`

## 10. Evidence

The project generates evidence under the `evidence/` directory.

Screenshots include successful discovery and replay states.

Structured agent events are stored as JSONL.

The reusable workflow itself is stored under `artifacts/`.

Together, these provide evidence of discovery, recording, and deterministic replay.

## 11. LLM Integration

The project includes configuration for an optional OpenAI-backed mode, but the demonstrated implementation uses the local planner.

An API connection was not required for the final runnable workflow.

This distinction is intentional and documented explicitly: the local discovery process should not be described as LLM-driven.

A future model-backed planner could consume richer observations and produce the same action representation already used by the execution layer.

The capability recorder and deterministic replay system would remain unchanged.

## 12. Limitations

The prototype is deliberately narrow.

The local planner understands the included Northstar workflow rather than arbitrary websites.

The current implementation also relies on known selectors and does not provide sophisticated recovery if the application's DOM changes substantially.

A production system would require additional work in areas such as:

- general visual/UI understanding;
- selector recovery;
- capability versioning;
- stronger authentication handling;
- session recovery;
- expanded safety policies;
- richer error classification;
- end-to-end regression tests; and
- artifact validation across application versions.

## 13. Future Improvements

The next major improvement would be implementing a model-backed discovery planner behind the existing planner abstraction.

Another useful extension would be selector fallback strategies. A capability could store several possible ways to locate an element and attempt recovery if the preferred selector changes.

Capabilities could also include application-version information and confidence or validation metadata.

A production implementation could maintain a capability registry so previously learned workflows could be retrieved, validated, versioned, and reused across tasks.

## 14. Conclusion

The prototype demonstrates that browser automation can be divided into two distinct stages: discovering a workflow and executing a known workflow.

The discovery process observes the interface and records a successful sequence as structured data.

The replay process consumes that structured artifact directly.

For the demonstrated Northstar workflow, the system successfully retrieves the fictional member's savings balance, stores the workflow as a reusable capability, and subsequently replays it deterministically with zero LLM calls.

The central design principle is:

**Learn once → record → validate → replay deterministically.**
