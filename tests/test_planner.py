from src.agent.planner import LocalPlanner


def test_login_username_action():
    planner = LocalPlanner()

    state = {
        "url": "http://127.0.0.1:8000/",
        "elements": ["username", "password"],
        "username_filled": False,
        "password_filled": False,
    }

    action = planner.decide(state, "12345")

    assert action.action == "fill"
    assert action.selector == "#username"
    assert action.value == "operator"


def test_login_password_action():
    planner = LocalPlanner()

    state = {
        "url": "http://127.0.0.1:8000/",
        "elements": ["username", "password"],
        "username_filled": True,
        "password_filled": False,
    }

    action = planner.decide(state, "12345")

    assert action.action == "fill"
    assert action.selector == "#password"
    assert action.value == "demo123"


def test_member_search_action():
    planner = LocalPlanner()

    state = {
        "url": "http://127.0.0.1:8000/dashboard",
        "elements": ["member_id"],
        "member_id_filled": False,
    }

    action = planner.decide(state, "12345")

    assert action.action == "fill"
    assert action.selector == "#member_id"
    assert action.value == "12345"


def test_balance_extraction():
    planner = LocalPlanner()

    state = {
        "url": "http://127.0.0.1:8000/member/12345",
        "elements": ["savings-balance"],
    }

    action = planner.decide(state, "12345")

    assert action.action == "extract_text"
    assert action.selector == "#savings-balance"


def test_member_not_found():
    planner = LocalPlanner()

    state = {
        "url": "http://127.0.0.1:8000/member/99999",
        "elements": ["member-not-found"],
    }

    action = planner.decide(state, "99999")

    assert action.action == "failed"
    assert action.description == "Member was not found"
