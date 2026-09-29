from __future__ import annotations

from pathlib import Path
from typing import Optional

from playwright.sync_api import Browser, BrowserContext, Page, Playwright


class BrowserSurface:
    """Small wrapper around Playwright for interacting with the mock UI."""

    def __init__(
        self,
        playwright: Playwright,
        base_url: str = "http://127.0.0.1:8000",
        headless: bool = False,
    ):
        self.playwright = playwright
        self.base_url = base_url.rstrip("/")
        self.headless = headless

        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def start(self) -> Page:
        self.browser = self.playwright.chromium.launch(
            headless=self.headless
        )

        self.context = self.browser.new_context(
            viewport={"width": 1440, "height": 900}
        )

        self.page = self.context.new_page()
        return self.page

    def open(self, path: str = "/") -> None:
        self._require_page()
        self.page.goto(
            f"{self.base_url}{path}",
            wait_until="networkidle",
        )

    def click(self, selector: str) -> None:
        self._require_page()
        self.page.locator(selector).click()

    def fill(self, selector: str, value: str) -> None:
        self._require_page()
        self.page.locator(selector).fill(value)

    def text(self, selector: str) -> str:
        self._require_page()
        return self.page.locator(selector).inner_text().strip()

    def exists(self, selector: str) -> bool:
        self._require_page()
        return self.page.locator(selector).count() > 0

    def wait_for(self, selector: str) -> None:
        self._require_page()
        self.page.locator(selector).wait_for(state="visible")

    def screenshot(self, output_path: str) -> None:
        self._require_page()

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        self.page.screenshot(
            path=str(path),
            full_page=True,
        )

    def current_url(self) -> str:
        self._require_page()
        return self.page.url

    def close(self) -> None:
        if self.context:
            self.context.close()

        if self.browser:
            self.browser.close()

        self.page = None
        self.context = None
        self.browser = None

    def _require_page(self) -> None:
        if self.page is None:
            raise RuntimeError(
                "BrowserSurface.start() must be called first."
            )
