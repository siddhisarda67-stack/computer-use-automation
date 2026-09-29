from __future__ import annotations

from playwright.sync_api import Page


class PageObserver:
    """Convert the current webpage into a small structured state."""

    TRACKED_ELEMENTS = {
        "username": "#username",
        "password": "#password",
        "member_id": "#member_id",
        "savings-balance": "#savings-balance",
        "member-not-found": "#member-not-found",
    }

    def observe(self, page: Page) -> dict:
        elements: list[str] = []

        for name, selector in self.TRACKED_ELEMENTS.items():
            locator = page.locator(selector)

            if locator.count() > 0:
                elements.append(name)

        state = {
            "url": page.url,
            "title": page.title(),
            "elements": elements,
            "username_filled": self._has_value(
                page,
                "#username",
            ),
            "password_filled": self._has_value(
                page,
                "#password",
            ),
            "member_id_filled": self._has_value(
                page,
                "#member_id",
            ),
        }

        if "savings-balance" in elements:
            state["savings_balance"] = (
                page.locator(
                    "#savings-balance"
                ).inner_text().strip()
            )

        if "member-not-found" in elements:
            state["error"] = (
                page.locator(
                    "#member-not-found"
                ).inner_text().strip()
            )

        return state

    @staticmethod
    def _has_value(
        page: Page,
        selector: str,
    ) -> bool:
        locator = page.locator(selector)

        if locator.count() == 0:
            return False

        try:
            return bool(locator.input_value().strip())
        except Exception:
            return False
