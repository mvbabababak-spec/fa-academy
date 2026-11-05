"""Rasterize the source SVG for chapter 41 with Chromium; no remote resources."""
from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SVG_PATH = ROOT / "book-engineering/diagrams/v3-ch09-training-loop.svg"
OUTPUT = ROOT / "assets/images/babak-ai/v3-ch09-training-loop.webp"


def main() -> None:
    svg = SVG_PATH.read_text(encoding="utf-8")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(args=["--no-sandbox"])
        try:
            page = browser.new_page(viewport={"width": 1600, "height": 1000}, device_scale_factor=1)
            page.set_content(
                "<!doctype html><html><body style='margin:0;line-height:0'>" + svg + "</body></html>",
                wait_until="load",
            )
            page.evaluate("document.fonts.ready")
            png = page.locator("svg").screenshot()
        finally:
            browser.close()
    with Image.open(BytesIO(png)) as image:
        if image.size != (1600, 1000):
            raise RuntimeError(f"unexpected diagram size: {image.size}")
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        image.convert("RGB").save(OUTPUT, format="WEBP", lossless=True, method=6)
    print(f"Wrote {OUTPUT.relative_to(ROOT)} ({OUTPUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
