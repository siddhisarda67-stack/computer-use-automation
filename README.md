# Computer-Use Automation: Learn Once, Replay Deterministically

A browser automation prototype that demonstrates how an agent can observe a web interface, discover a workflow, record that workflow as a reusable capability artifact, and replay it deterministically without additional model calls.
# Computer-Use Automation: Learn Once, Replay Deterministically

A browser automation prototype that demonstrates how a workflow can be discovered from a web interface, recorded as a reusable capability, and replayed deterministically without additional model calls.

The project uses a fictional credit-union operations portal called **Northstar Credit Union** as the demonstration environment.

> All member, account, credential, and balance information in this project is fictional training data.

## Project Goal

The goal of this project is to separate workflow discovery from repeated execution.

The demonstration task is:

> Look up member `12345` and retrieve the member's savings balance.

During discovery, the system observes the webpage, determines the next action, executes that action through Playwright, and records the successful workflow.

After discovery, the saved capability can be replayed directly without running the planner again.

## Architecture

```text
Northstar Training Web App
          |
          v
     PageObserver
          |
          v
      Page State
          |
          v
     LocalPlanner
          |
          v
     SafetyPolicy
          |
          v
    BrowserSurface
     (Playwright)
          |
     +----+----+
     |         |
     v         v
 Event Log   CapabilityRecorder
               |
               v
        Capability JSON
               |
               v
      Deterministic Replay
               |
               v
          0 LLM Calls
```

## Main Components

### 1. Northstar Training Web Application

The `mock_bank/` directory contains a FastAPI and Jinja2 web application that simulates a fictional credit-union member operations portal.

It includes:

- Operator login
- Member search
- Member profile
- Checking and savings account information
- Member-not-found state
- Disabled transactional controls

Demo credentials:

```text
Username: operator
Password: demo123
```

### 2. Browser Surface

`src/surface/browser.py`

This module provides the Playwright browser interaction layer. It handles navigation, form filling, clicking, text extraction, waiting for elements, and screenshots.

### 3. Page Observer

`src/agent/observer.py`

The observer inspects the currently rendered webpage and converts relevant UI elements into structured page state.

This allows the planner to make decisions based on what is actually visible rather than blindly executing a fixed sequence.

### 4. Local Planner

`src/agent/planner.py`

The local planner selects the next browser action based on the observed page state.

The demonstrated planner is deterministic and rule-based. It does **not** use an LLM.

This local mode allows the complete project to run without paid API credits.

### 5. Safety Policy

`src/safety/policy.py`

The safety layer validates actions before execution.

It allows expected browser operations while blocking unsupported actions and sensitive selectors such as account-closing or fund-transfer controls.

### 6. Capability Recorder

`src/artifact/`

After a successful discovery run, the workflow is saved as a structured JSON capability.

Example:

```text
artifacts/lookup_savings_balance.json
```

The artifact contains the ordered actions, selectors, runtime inputs, expected outcome, and metadata required for replay.

The member ID is stored as a runtime placeholder so the capability is reusable.

### 7. Deterministic Replay

`src/replay/replay.py`

Replay loads the saved capability and executes its recorded browser steps directly.

The planner is not invoked during replay.

A successful replay reports:

```text
Status: success
LLM calls: 0
```

This demonstrates the central idea of the project:

**learn once → record → validate → replay deterministically**

### 8. Observability

`src/observability/logger.py`

Agent activity is written as structured JSONL events.

The log captures events such as:

- Agent started
- Page observed
- Action planned
- Agent completed

Sensitive field values such as passwords are intentionally excluded from the structured event log.

Logs are stored in:

```text
evidence/agent_events.jsonl
```

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
playwright install chromium
```

Create the environment file:

```bash
cp .env.example .env
```

For the free local demonstration, configure:

```text
AGENT_MODE=local
```

## Run the Web Application

From the project root:

```bash
uvicorn mock_bank.app:app --reload
```

Then visit:

```text
http://127.0.0.1:8000
```

## Run Discovery

Open another terminal, activate the environment, and run:

```bash
source .venv/bin/activate
python -m src.agent.run_agent --member-id 12345
```

For headless execution:

```bash
python -m src.agent.run_agent --member-id 12345 --headless
```

A successful run creates:

```text
artifacts/lookup_savings_balance.json
```

The demonstrated workflow retrieves the fictional savings balance:

```text
8720.5
```

## Replay the Capability

Run:

```bash
python -m src.replay.replay lookup_savings_balance --member-id 12345 --headless
```

A successful replay produces:

```text
Status: success
LLM calls: 0
```

## Failure Handling

A nonexistent member can be tested with:

```bash
python -m src.agent.run_agent --member-id 99999
```

The observer detects the member-not-found state and the agent terminates safely instead of recording an invalid capability.

## Automated Tests

Run:

```bash
PYTHONPATH=. python -m pytest -q
```

The current test suite contains 10 passing tests covering:

- Capability serialization
- Runtime placeholders
- Planner behavior
- Login planning
- Member-search planning
- Balance extraction
- Member-not-found handling
- Allowed read operations
- Blocked sensitive actions
- Unsupported actions

## Evidence

Screenshots generated during development and execution are stored in:

```text
evidence/screenshots/
```

Current evidence includes:

```text
discovery_success.png
local_agent_success.png
lookup_savings_balance_replay.png
```

Structured execution logs are stored in:

```text
evidence/agent_events.jsonl
```

## Local and OpenAI Modes

The demonstrated implementation runs with:

```text
AGENT_MODE=local
```

No paid API credits are required.

The project configuration leaves room for an OpenAI-backed planner to be added behind the same architecture. However, the demonstrated discovery workflow in this repository is **local and rule-based** and should not be represented as an LLM-driven run.

Replay is deterministic and does not require an LLM.

## Security and Safety

This project is intentionally restricted to a fictional training environment.

Safety measures include:

- No connection to a real financial institution
- Fictional member and account data
- Disabled transactional controls in the UI
- Automation-level action validation
- Sensitive selectors blocked by policy
- Password values excluded from structured logs
- `.env` excluded from Git
- Deterministic replay rather than unrestricted autonomous execution

## Project Structure

```text
computer-use-automation/
├── mock_bank/
│   ├── app.py
│   ├── static/
│   └── templates/
│
├── src/
│   ├── agent/
│   │   ├── config.py
│   │   ├── observer.py
│   │   ├── planner.py
│   │   └── run_agent.py
│   │
│   ├── artifact/
│   │   ├── models.py
│   │   └── recorder.py
│   │
│   ├── observability/
│   │   └── logger.py
│   │
│   ├── replay/
│   │   └── replay.py
│   │
│   ├── safety/
│   │   └── policy.py
│   │
│   └── surface/
│       └── browser.py
│
├── artifacts/
├── evidence/
│   └── screenshots/
├── tests/
├── README.md
├── REPORT.md
├── requirements.txt
├── .env.example
└── .gitignore
```

## Limitations

The current planner is intentionally rule-based and designed for the included training application.

A production implementation would require additional capabilities such as:

- More general UI understanding
- Selector recovery when webpages change
- Stronger authentication and session management
- Capability versioning
- More extensive policy enforcement
- Broader integration and end-to-end testing
- An optional model-backed discovery planner

The current project demonstrates the architecture and lifecycle of reusable computer-use capabilities rather than production banking automation.

## Summary

This prototype demonstrates a complete workflow:

1. Observe a webpage.
2. Determine the next action.
3. Execute browser actions through Playwright.
4. Detect successful or failed outcomes.
5. Record successful behavior as a reusable capability.
6. Apply safety validation.
7. Generate execution logs and screenshot evidence.
8. Replay the saved capability deterministically.
9. Complete replay with zero LLM calls.

The central design principle is:

**Learn once. Record the successful capability. Replay it deterministically.**
