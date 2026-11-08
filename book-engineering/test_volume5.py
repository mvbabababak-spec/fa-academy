"""Browser and offline-cache checks for the authored chapters in Volume 5."""
from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
from threading import Thread

from playwright.sync_api import sync_playwright

import build_volume5 as builder

ROOT = Path(__file__).resolve().parent.parent
BOOK_ID = builder.VOLUME_ID
TITLE = "هنر و علم ساخت هوش — جلد پنجم"
CHAPTER_TITLES = {
    62: "Benchmarking، طراحی آزمون، معیارها، ارزیابی انسانی، عدم‌قطعیت و آلودگی بنچمارک",
    63: "توهم، سوگیری، استحکام، تبیین‌پذیری و تفسیرپذیری",
    64: "Red Teaming، حملات خصمانه، Prompt Injection، مسموم‌سازی داده، استخراج مدل و حریم خصوصی",
    65: "هم‌ترازی، حاکمیت، مستندسازی، مدل‌کارت، داده‌کارت و مدیریت ریسک",
    66: "API و FastAPI، Backend، Frontend، برنامهٔ وب و موبایل؛ قرارداد داده و آزمایش",
    67: "سرو مدل، بهینه‌سازی استنتاج، Cache، صف، تأخیر و توان عملیاتی",
    68: "احراز هویت، محدودیت نرخ، ثبت رخداد، پایش، حریم خصوصی و پاسخ به رخداد",
    69: "استقرار ابری و محلی، نسخه‌بندی، CI/CD، مقیاس‌پذیری، بازگشت نسخه و هزینهٔ نگه‌داری",
}
PROJECT_CODES = {
    global_num: (ROOT / path).read_text(encoding="utf-8").rstrip("\n")
    for global_num, path in builder.APPENDIX_PROJECTS.items()
}
SW_TEXT = (ROOT / "sw.js").read_text(encoding="utf-8")
CACHE_NAME = re.search(r"const CACHE_NAME = '([^']+)'", SW_TEXT).group(1)
OFFLINE_PATHS = ["./" + path for path in builder._v5_offline_paths(builder.available_specs())]


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(ROOT.parent)))
    Thread(target=server.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{server.server_port}/{ROOT.name}/"
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(args=["--no-sandbox"])
            for width in (320, 390, 768, 1440):
                context = browser.new_context(viewport={"width": width, "height": 900})
                page = context.new_page()
                errors: list[str] = []
                cover_asset_requests: list[str] = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.on("requestfinished", lambda request: cover_asset_requests.append(request.url) if request.url.endswith("/assets/images/covers/volume-5-cover.png") else None)
                page.goto(url, wait_until="domcontentloaded")
                page.wait_for_selector("#loading.hidden")
                assert page.get_by_text(TITLE, exact=True).count() == 1
                metadata = page.evaluate(f"""() => {{
                  const book=DATA.books.find(item=>item.id==='{BOOK_ID}');
                  const chapters=book&&book.chapters||[];
                  return {{count:chapters.length,cover:book&&book.cover,subtitle:book&&book.subtitle,
                    chapters:chapters.map(chapter=>({{id:chapter.id,title:chapter.title,
                      sectionIds:chapter.sections.map(section=>section.id),
                      sectionTitles:chapter.sections.map(section=>section.title),
                      sectionCount:chapter.sections.length,
                      mathSections:chapter.sections.map((section,index)=>({{index,count:(section.html.match(/<math/g)||[]).length}})).filter(item=>item.count>0)}}))}};
                }}""")
                assert metadata["count"] == 8, metadata
                assert metadata["cover"] == builder.COVER_PATH, metadata
                assert metadata["subtitle"] == "ارزیابی، محصول و پژوهش | ۱۲ فصل", metadata
                assert [chapter["id"] for chapter in metadata["chapters"]] == [
                    "art-science-v5-ch01", "art-science-v5-ch02", "art-science-v5-ch03",
                    "art-science-v5-ch04", "art-science-v5-ch05", "art-science-v5-ch06",
                    "art-science-v5-ch07", "art-science-v5-ch08"
                ], metadata
                assert [chapter["title"] for chapter in metadata["chapters"]] == [
                    CHAPTER_TITLES[number] for number in (62, 63, 64, 65, 66, 67, 68, 69)
                ], metadata
                assert metadata["chapters"][0]["sectionCount"] == 26, metadata
                assert metadata["chapters"][0]["sectionIds"][0] == "art-science-v5-ch01-s01", metadata
                assert metadata["chapters"][0]["sectionIds"][-1] == "art-science-v5-ch01-s26", metadata
                assert metadata["chapters"][1]["sectionCount"] == 34, metadata
                assert metadata["chapters"][1]["sectionIds"][0] == "art-science-v5-ch02-s01", metadata
                assert metadata["chapters"][1]["sectionIds"][-1] == "art-science-v5-ch02-s34", metadata
                assert metadata["chapters"][2]["sectionCount"] == 39, metadata
                assert metadata["chapters"][2]["sectionIds"][0] == "art-science-v5-ch03-s01", metadata
                assert metadata["chapters"][2]["sectionIds"][-1] == "art-science-v5-ch03-s39", metadata
                assert metadata["chapters"][3]["sectionCount"] == 41, metadata
                assert metadata["chapters"][3]["sectionIds"][0] == "art-science-v5-ch04-s01", metadata
                assert metadata["chapters"][3]["sectionIds"][-1] == "art-science-v5-ch04-s41", metadata
                assert metadata["chapters"][4]["sectionCount"] == 40, metadata
                assert metadata["chapters"][4]["sectionIds"][0] == "art-science-v5-ch05-s01", metadata
                assert metadata["chapters"][4]["sectionIds"][-1] == "art-science-v5-ch05-s40", metadata
                assert metadata["chapters"][5]["sectionCount"] == 28, metadata
                assert metadata["chapters"][5]["sectionIds"][0] == "art-science-v5-ch06-s01", metadata
                assert metadata["chapters"][5]["sectionIds"][-1] == "art-science-v5-ch06-s28", metadata
                assert metadata["chapters"][6]["sectionCount"] == 37, metadata
                assert metadata["chapters"][6]["sectionIds"][0] == "art-science-v5-ch07-s01", metadata
                assert metadata["chapters"][6]["sectionIds"][-1] == "art-science-v5-ch07-s37", metadata
                assert metadata["chapters"][7]["sectionCount"] == 29, metadata
                assert metadata["chapters"][7]["sectionIds"][0] == "art-science-v5-ch08-s01", metadata
                assert metadata["chapters"][7]["sectionIds"][-1] == "art-science-v5-ch08-s29", metadata
                assert all(chapter["mathSections"] for chapter in metadata["chapters"]), metadata

                # Confirm the portrait cover, accessible figures and MathML in all eight authored chapters.
                page.locator(".book-card--volume img").last.evaluate("img => img.loading='eager'")
                page.wait_for_function("""() => {
                  const img=Array.from(document.querySelectorAll('.book-card--volume img'))
                    .find(node=>node.currentSrc.includes('volume-5-cover.png'));
                  return img&&img.complete&&img.naturalWidth===1024&&img.naturalHeight===1536;
                }""")
                assert cover_asset_requests, "the supplied Volume 5 PNG was not requested as the active cover"
                page.evaluate(f"openItem('{BOOK_ID}','book');openSec('{BOOK_ID}',0,0)")
                if width <= 768:
                    breadcrumb_title = page.locator(".reader-breadcrumb>span:first-child")
                    assert breadcrumb_title.evaluate("e=>getComputedStyle(e).whiteSpace") == "nowrap"
                    assert page.locator(".reader-breadcrumb").evaluate("e=>e.getBoundingClientRect().height<=32")
                for chapter_index, chapter in enumerate(metadata["chapters"]):
                    page.evaluate(f"openSec('{BOOK_ID}',{chapter_index},0)")
                    content = page.locator(".reader-content")
                    image = content.locator("img").first
                    local_figure_number = str(chapter_index + 1).translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))
                    expected_figure = f"شکل ۵-{local_figure_number}-۱"
                    assert image.get_attribute("alt") and expected_figure in image.get_attribute("alt")
                    page.wait_for_function("""() => {
                      const img=document.querySelector('.reader-content img');
                      return img&&img.complete&&img.naturalWidth===1200&&img.naturalHeight===680;
                    }""")
                    assert content.evaluate("e=>e.scrollWidth<=e.clientWidth+2")

                    math_index = chapter["mathSections"][0]["index"]
                    page.evaluate(f"openSec('{BOOK_ID}',{chapter_index},{math_index})")
                    math = page.locator(".reader-content math").first
                    assert math.count() >= 1 and math.get_attribute("aria-label"), chapter["id"]
                    assert page.locator(".reader-content").evaluate("e=>e.scrollWidth<=e.clientWidth+2")

                    summary_index = next(i for i, title in enumerate(chapter["sectionTitles"]) if "جمع‌بندی" in title)
                    page.evaluate(f"openSec('{BOOK_ID}',{chapter_index},{summary_index})")
                    answer_path = builder.ANSWER_KEYS[62 + chapter_index]
                    project_path = builder.PROJECT_DIRS[62 + chapter_index] + "/README.md"
                    report_path = f"book-engineering/chapters/{62 + chapter_index}-audit-report-fa.md"
                    assert page.locator(f".reader-content a[href='{answer_path}']").count() == 1
                    assert page.locator(f".reader-content a[href='{project_path}']").count() == 1
                    assert page.locator(f".reader-content a[href='{report_path}']").count() == 1

                    appendix_index = next(i for i, title in enumerate(chapter["sectionTitles"]) if "پیوست اجرایی" in title)
                    page.evaluate(f"openSec('{BOOK_ID}',{chapter_index},{appendix_index})")
                    assert page.locator(".reader-content pre code").last.text_content().rstrip("\n") == PROJECT_CODES[62 + chapter_index]

                # All authored chapter files are present in the active offline cache.
                sw_ready = page.evaluate("""async () => await Promise.race([
                  navigator.serviceWorker.ready.then(() => true),
                  new Promise(resolve => setTimeout(() => resolve(false), 30000))
                ])""")
                assert sw_ready, "service worker did not become ready within 30 seconds"
                page.wait_for_timeout(250)
                cache_misses = page.evaluate("""async arg => {
                  const cache=await caches.open(arg.cacheName), missing=[];
                  for(const path of arg.paths){
                    const response=await cache.match(new URL(path,location.href).href);
                    if(!response||!response.ok) missing.push(path);
                  }
                  return missing;
                }""", {"cacheName": CACHE_NAME, "paths": OFFLINE_PATHS})
                assert cache_misses == [], cache_misses
                context.set_offline(True)
                offline_cover_asset = page.evaluate("""async () => {
                  const response=await fetch('assets/images/covers/volume-5-cover.png');
                  if(!response.ok)return null;
                  const bitmap=await createImageBitmap(await response.blob());
                  const result={width:bitmap.width,height:bitmap.height};bitmap.close();return result;
                }""")
                assert offline_cover_asset == {"width":1024,"height":1536}, offline_cover_asset
                offline_answer62 = page.evaluate("fetch('book-engineering/answers/62-benchmarking-evaluation-fa.md').then(r=>r.ok?r.text():'')")
                offline_answer63 = page.evaluate("fetch('book-engineering/answers/63-hallucination-bias-robustness-fa.md').then(r=>r.ok?r.text():'')")
                offline_answer64 = page.evaluate("fetch('book-engineering/answers/64-red-teaming-security-fa.md').then(r=>r.ok?r.text():'')")
                offline_report63 = page.evaluate("fetch('book-engineering/chapters/63-audit-report-fa.md').then(r=>r.ok?r.text():'')")
                offline_source64 = page.evaluate("fetch('book-engineering/chapters/64-red-teaming-security.md').then(r=>r.ok?r.text():'')")
                offline_report64 = page.evaluate("fetch('book-engineering/chapters/64-audit-report-fa.md').then(r=>r.ok?r.text():'')")
                offline_diagram64 = page.evaluate("fetch('book-engineering/diagrams/v5-ch03-red-team-pipeline.svg').then(r=>r.ok?r.text():'')")
                offline_project63 = page.evaluate("fetch('book-engineering/projects/63-model-behavior-lab/results.json').then(r=>r.ok?r.text():'')")
                offline_project64 = page.evaluate("fetch('book-engineering/projects/64-red-team-lab/results.json').then(r=>r.ok?r.text():'')")
                offline_fixture64 = page.evaluate("fetch('book-engineering/projects/64-red-team-lab/synthetic_security_fixture.json').then(r=>r.ok?r.text():'')")
                offline_answer65 = page.evaluate("fetch('book-engineering/answers/65-alignment-governance-fa.md').then(r=>r.ok?r.text():'')")
                offline_report65 = page.evaluate("fetch('book-engineering/chapters/65-audit-report-fa.md').then(r=>r.ok?r.text():'')")
                offline_source65 = page.evaluate("fetch('book-engineering/chapters/65-alignment-governance.md').then(r=>r.ok?r.text():'')")
                offline_diagram65 = page.evaluate("fetch('book-engineering/diagrams/v5-ch04-governance-cycle.svg').then(r=>r.ok?r.text():'')")
                offline_project65 = page.evaluate("fetch('book-engineering/projects/65-governance-lab/results.json').then(r=>r.ok?r.text():'')")
                offline_fixture65 = page.evaluate("fetch('book-engineering/projects/65-governance-lab/governance_pack.json').then(r=>r.ok?r.text():'')")
                offline_answer66 = page.evaluate("fetch('book-engineering/answers/66-ai-product-api-fa.md').then(r=>r.ok?r.text():'')")
                offline_report66 = page.evaluate("fetch('book-engineering/chapters/66-audit-report-fa.md').then(r=>r.ok?r.text():'')")
                offline_source66 = page.evaluate("fetch('book-engineering/chapters/66-ai-product-api.md').then(r=>r.ok?r.text():'')")
                offline_diagram66 = page.evaluate("fetch('book-engineering/diagrams/v5-ch05-api-contract.svg').then(r=>r.ok?r.text():'')")
                offline_project66 = page.evaluate("fetch('book-engineering/projects/66-ai-product-api/results.json').then(r=>r.ok?r.text():'')")
                offline_fixture66 = page.evaluate("fetch('book-engineering/projects/66-ai-product-api/synthetic_fixture.json').then(r=>r.ok?r.text():'')")
                offline_demo66 = page.evaluate("fetch('book-engineering/projects/66-ai-product-api/demo.html').then(r=>r.ok?r.text():'')")
                offline_answer67 = page.evaluate("fetch('book-engineering/answers/67-model-serving-operations-fa.md').then(r=>r.ok?r.text():'')")
                offline_report67 = page.evaluate("fetch('book-engineering/chapters/67-audit-report-fa.md').then(r=>r.ok?r.text():'')")
                offline_source67 = page.evaluate("fetch('book-engineering/chapters/67-model-serving-operations.md').then(r=>r.ok?r.text():'')")
                offline_diagram67 = page.evaluate("fetch('book-engineering/diagrams/v5-ch06-serving-pipeline.svg').then(r=>r.ok?r.text():'')")
                offline_project67 = page.evaluate("fetch('book-engineering/projects/67-serving-lab/results.json').then(r=>r.ok?r.text():'')")
                offline_fixture67 = page.evaluate("fetch('book-engineering/projects/67-serving-lab/synthetic_serving_trace.json').then(r=>r.ok?r.text():'')")
                offline_answer68 = page.evaluate("fetch('book-engineering/answers/68-product-security-monitoring-fa.md').then(r=>r.ok?r.text():'')")
                offline_report68 = page.evaluate("fetch('book-engineering/chapters/68-audit-report-fa.md').then(r=>r.ok?r.text():'')")
                offline_source68 = page.evaluate("fetch('book-engineering/chapters/68-product-security-monitoring.md').then(r=>r.ok?r.text():'')")
                offline_diagram68 = page.evaluate("fetch('book-engineering/diagrams/v5-ch07-product-security-flow.svg').then(r=>r.ok?r.text():'')")
                offline_project68 = page.evaluate("fetch('book-engineering/projects/68-product-security-lab/results.json').then(r=>r.ok?r.text():'')")
                offline_fixture68 = page.evaluate("fetch('book-engineering/projects/68-product-security-lab/synthetic_security_events.json').then(r=>r.ok?r.text():'')")
                offline_answer69 = page.evaluate("fetch('book-engineering/answers/69-deployment-cicd-fa.md').then(r=>r.ok?r.text():'')")
                offline_report69 = page.evaluate("fetch('book-engineering/chapters/69-audit-report-fa.md').then(r=>r.ok?r.text():'')")
                offline_source69 = page.evaluate("fetch('book-engineering/chapters/69-deployment-cicd.md').then(r=>r.ok?r.text():'')")
                offline_diagram69 = page.evaluate("fetch('book-engineering/diagrams/v5-ch08-release-pipeline.svg').then(r=>r.ok?r.text():'')")
                offline_project69 = page.evaluate("fetch('book-engineering/projects/69-deployment-cicd-lab/results.json').then(r=>r.ok?r.text():'')")
                offline_fixture69 = page.evaluate("fetch('book-engineering/projects/69-deployment-cicd-lab/synthetic_release_scenarios.json').then(r=>r.ok?r.text():'')")
                offline_full_text = page.evaluate("fetch('volume-5-full-fa.md').then(r=>r.ok?r.text():'')")
                assert "پاسخ‌نامهٔ مستقل فصل ۶۲" in offline_answer62
                assert "پاسخ‌نامهٔ مستقل فصل ۶۳" in offline_answer63
                assert "پاسخ‌نامهٔ مستقل فصل ۶۴" in offline_answer64
                assert "فصل سراسری ۶۳" in offline_report63
                assert 'v5-ch02-synthetic-behavior-v1' in offline_project63
                assert "فصل محلی ۳ جلد پنجم = فصل سراسری ۶۴" in offline_source64
                assert "فصل سراسری ۶۴" in offline_report64
                assert 'v5-ch03-red-team-synthetic-v1' in offline_fixture64
                assert 'v5-ch03-red-team-synthetic-v1' in offline_project64
                assert "فرایند آزمون خصمانه" in offline_diagram64
                assert "پاسخ‌نامهٔ مستقل فصل ۶۵" in offline_answer65
                assert "فصل سراسری ۶۵" in offline_report65
                assert "فصل محلی ۴ جلد پنجم = فصل سراسری ۶۵" in offline_source65
                assert "حکمرانی" in offline_diagram65
                assert "v5-ch04-governance-pack-synthetic-v1" in offline_fixture65
                assert 'v5-ch04-governance-pack-synthetic-v1' in offline_project65
                assert "پاسخ‌نامهٔ مستقل فصل ۶۶" in offline_answer66
                assert "فصل سراسری ۶۶" in offline_report66
                assert "فصل محلی ۵ جلد پنجم = فصل سراسری ۶۶" in offline_source66
                assert "قرارداد مشترک API" in offline_diagram66
                assert "v5-ch05-api-contract-synthetic-v1" in offline_fixture66
                assert "api_cases_passed" in offline_project66 and '"api_cases_passed": 12' in offline_project66
                assert "textContent" in offline_demo66
                assert "پاسخ‌نامهٔ مستقل فصل ۶۷" in offline_answer67
                assert "فصل سراسری ۶۷" in offline_report67
                assert "فصل محلی ۶ جلد پنجم = فصل سراسری ۶۷" in offline_source67
                assert "سرو در سطح محصول" in offline_diagram67
                assert 'v5-ch06-serving-synthetic-v1' in offline_fixture67
                assert '"response_cache_hits": 12' in offline_project67
                assert "پاسخ‌نامهٔ مستقل فصل ۶۸" in offline_answer68
                assert "فصل سراسری ۶۸" in offline_report68
                assert "فصل محلی ۷ جلد پنجم = فصل سراسری ۶۸" in offline_source68
                assert "prompt / token / PII" in offline_diagram68
                assert "AUTH_FAILURE_BURST" in offline_project68 and '"allowed": 6' in offline_project68
                assert "v5-ch07-security-ops-synthetic-v1" in offline_fixture68
                assert "پاسخ‌نامهٔ مستقل فصل ۶۹" in offline_answer69
                assert "فصل سراسری ۶۹" in offline_report69
                assert "فصل محلی ۸ جلد پنجم = فصل سراسری ۶۹" in offline_source69
                assert "digest پایدارِ پیشین" in offline_diagram69 and "پیکان خط‌چین" in offline_diagram69
                assert '"rolled_back": 1' in offline_project69 and '"decision": "blocked"' in offline_project69
                assert "v5-ch08-deployment-cicd-synthetic-v1" in offline_fixture69
                assert all(term in offline_full_text for term in ("جلد پنجم", "فصل ۶۲", "فصل ۶۳", "فصل ۶۴", "فصل ۶۵", "فصل ۶۶", "فصل ۶۷", "فصل ۶۸", "فصل ۶۹"))
                assert not errors, errors
                print(f"PASS volume 5 chapters 62–69 browser/offline checks at {width}px: sections={[chapter['sectionCount'] for chapter in metadata['chapters']]}, accessible MathML/SVG, exact code appendices, {len(OFFLINE_PATHS)} offline paths")
                context.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
