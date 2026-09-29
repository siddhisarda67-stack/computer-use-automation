from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


# ---------------------------------------------------------
# Application setup
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Northstar Credit Union Member Operations",
    description="Fictional banking operations portal for automation testing",
)

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)


# ---------------------------------------------------------
# Fictional test data
# ---------------------------------------------------------

MEMBERS = {
    "12345": {
        "name": "Alex Morgan",
        "status": "Active",
        "member_since": "2018",
        "email": "alex.morgan@example.test",
        "phone": "(555) 010-1234",
        "address": "100 Market Street, Test City",
        "accounts": [
            {
                "type": "Checking",
                "number": "•••• 4821",
                "balance": 2450.00,
                "status": "Open",
            },
            {
                "type": "Savings",
                "number": "•••• 7712",
                "balance": 8720.50,
                "status": "Open",
            },
        ],
    },

    "67890": {
        "name": "Jordan Lee",
        "status": "Active",
        "member_since": "2021",
        "email": "jordan.lee@example.test",
        "phone": "(555) 010-5678",
        "address": "200 Oak Avenue, Test City",
        "accounts": [
            {
                "type": "Checking",
                "number": "•••• 1159",
                "balance": 1100.25,
                "status": "Open",
            },
            {
                "type": "Savings",
                "number": "•••• 3308",
                "balance": 4250.75,
                "status": "Open",
            },
        ],
    },

    "24680": {
        "name": "Taylor Brooks",
        "status": "Active",
        "member_since": "2016",
        "email": "taylor.brooks@example.test",
        "phone": "(555) 010-2468",
        "address": "55 Pine Road, Test City",
        "accounts": [
            {
                "type": "Checking",
                "number": "•••• 9012",
                "balance": 5340.80,
                "status": "Open",
            },
            {
                "type": "Savings",
                "number": "•••• 6634",
                "balance": 12950.25,
                "status": "Open",
            },
        ],
    },
}


# ---------------------------------------------------------
# Login
# ---------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={},
    )


@app.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
):
    """
    Fake authentication for this local demonstration only.
    No real credentials are used.
    """

    if username == "operator" and password == "demo123":
        return RedirectResponse(
            url="/dashboard",
            status_code=303,
        )

    return RedirectResponse(
        url="/?error=1",
        status_code=303,
    )


# ---------------------------------------------------------
# Dashboard
# ---------------------------------------------------------

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={},
    )


# ---------------------------------------------------------
# Member search
# ---------------------------------------------------------

@app.post("/members/search", response_class=HTMLResponse)
def search_member(
    request: Request,
    member_id: str = Form(...),
):
    member_id = member_id.strip()

    member = MEMBERS.get(member_id)

    # Expected business outcome:
    # the system worked correctly, but no matching member exists.
    if member is None:
        return templates.TemplateResponse(
            request=request,
            name="not_found.html",
            context={
                "member_id": member_id,
            },
            status_code=404,
        )

    return templates.TemplateResponse(
        request=request,
        name="member.html",
        context={
            "member_id": member_id,
            "member": member,
        },
    )


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "ok",
        "application": "northstar-member-operations",
    }
