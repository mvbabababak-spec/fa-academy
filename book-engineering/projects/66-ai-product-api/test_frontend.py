"""Browser tests for the static web client using an intercepted synthetic API."""
from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from threading import Thread
import unittest

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
SUCCESS = {
    "contract_version": "1.0",
    "request_id": "req-browser-demo",
    "status": "completed",
    "answer": "<script>این متن فقط داده است.</script>",
    "sources": [{"id": "guide-001", "title": "راهنمای ساختگی"}],
}


class FrontendContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = ThreadingHTTPServer(
            ("127.0.0.1", 0),
            partial(SimpleHTTPRequestHandler, directory=str(ROOT)),
        )
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}/demo.html"
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(args=["--no-sandbox"])

    @classmethod
    def tearDownClass(cls) -> None:
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_success_loading_accessibility_and_small_viewports(self) -> None:
        for width in (320, 390, 768):
            with self.subTest(width=width):
                context = self.browser.new_context(viewport={"width": width, "height": 820})
                page = context.new_page()
                page.add_init_script(
                    """(() => {
                      const realFetch = window.fetch.bind(window);
                      window.fetch = (...args) => new Promise((resolve, reject) => {
                        window.__releaseFetch = () => realFetch(...args).then(resolve, reject);
                      });
                    })();"""
                )
                page.route(
                    "**/v1/assist",
                    lambda route: route.fulfill(
                        status=200,
                        headers={"content-type": "application/json; charset=utf-8"},
                        body=json.dumps(SUCCESS, ensure_ascii=False),
                    ),
                )
                page.goto(self.base_url, wait_until="domcontentloaded")
                self.assertEqual(page.locator("html").get_attribute("lang"), "fa")
                self.assertEqual(page.locator("html").get_attribute("dir"), "rtl")
                self.assertTrue(page.get_by_label("پرسش کوتاه و غیرشخصی").is_visible())
                self.assertFalse(page.locator("#answer").is_visible())
                self.assertLessEqual(
                    page.evaluate("document.documentElement.scrollWidth"),
                    width,
                )
                page.get_by_label("پرسش کوتاه و غیرشخصی").fill("سلام")
                page.get_by_role("button", name="دریافت پاسخِ نمایشی").click()
                page.wait_for_function("document.querySelector('#status').textContent === 'در حال ارسال…'")
                self.assertTrue(page.get_by_role("button", name="دریافت پاسخِ نمایشی").is_disabled())
                page.evaluate("window.__releaseFetch()")
                page.wait_for_function("document.querySelector('#status').textContent === 'پاسخ آماده است.'")
                self.assertTrue(page.locator("#answer").is_visible())
                self.assertEqual(page.locator("#answer-text").text_content(), SUCCESS["answer"])
                self.assertEqual(page.locator("#answer-text script").count(), 0)
                self.assertEqual(page.locator("#sources li").text_content(), "راهنمای ساختگی (guide-001)")
                self.assertFalse(page.get_by_role("button", name="دریافت پاسخِ نمایشی").is_disabled())
                self.assertLessEqual(page.evaluate("document.documentElement.scrollWidth"), width)
                context.close()

    def test_problem_details_are_not_echoed_to_the_user(self) -> None:
        context = self.browser.new_context(viewport={"width": 390, "height": 820})
        page = context.new_page()
        secret = "PRIVATE_DIAGNOSTIC_SENTINEL"
        page.route(
            "**/v1/assist",
            lambda route: route.fulfill(
                status=422,
                headers={"content-type": "application/problem+json; charset=utf-8"},
                body=json.dumps(
                    {
                        "type": "https://example.invalid/problems/invalid-request",
                        "title": "درخواست معتبر نیست",
                        "status": 422,
                        "detail": secret,
                    },
                    ensure_ascii=False,
                ),
            ),
        )
        page.goto(self.base_url, wait_until="domcontentloaded")
        page.get_by_label("پرسش کوتاه و غیرشخصی").fill("سلام")
        page.get_by_role("button", name="دریافت پاسخِ نمایشی").click()
        page.get_by_role("alert").wait_for(state="visible")
        self.assertEqual(page.get_by_role("alert").text_content(), "پاسخ در دسترس نیست؛ بعداً دوباره تلاش کنید.")
        self.assertNotIn(secret, page.locator("body").text_content())
        self.assertFalse(page.locator("#answer").is_visible())
        context.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
