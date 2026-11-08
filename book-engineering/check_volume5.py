"""Structural, editorial, appendix, and offline-cache checks for Volume 5."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import struct
import unicodedata
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

import build_volume5 as builder

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data.json"
CJK_RANGES = (
    (0x2E80, 0x2FFF), (0x3040, 0x30FF), (0x3400, 0x9FFF),
    (0xF900, 0xFAFF), (0xAC00, 0xD7AF),
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def local_links(text: str, source: Path) -> list[str]:
    missing = []
    for target in re.findall(r"\]\(([^)]+)\)", text):
        target = target.strip()
        parsed = urlparse(target)
        if parsed.scheme or target.startswith("#") or target.startswith("mailto:"):
            continue
        target_path = Path(parsed.path)
        if target_path.parts and target_path.parts[0] in {"book-engineering", "assets", "volume-5-full-fa.md"}:
            path = (ROOT / target_path).resolve()
        else:
            path = (source.parent / target_path).resolve()
        if not path.is_file():
            missing.append(target)
    return missing


def cjk_chars(text: str) -> list[str]:
    return [char for char in set(text) if any(low <= ord(char) <= high for low, high in CJK_RANGES)]


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    books = [book for book in data.get("books", []) if book.get("id") == builder.VOLUME_ID]
    require(len(books) == 1, "data.json must contain exactly one volume 5 record")
    book = books[0]
    require(book.get("title") == "هنر و علم ساخت هوش — جلد پنجم", "volume 5 title mismatch")
    require(book.get("subtitle") == "ارزیابی، محصول و پژوهش | ۱۲ فصل", "volume 5 card subtitle mismatch")
    require(book.get("author") == "Babak Moradvand", "volume 5 author metadata mismatch")
    require(book.get("cover") == builder.COVER_PATH, "volume 5 cover path mismatch")
    ids = [item.get("id") for item in data.get("books", [])]
    require(ids.index(builder.VOLUME_ID) == ids.index("art-science-intelligence-v4") + 1,
            "volume 5 must immediately follow volume 4")
    for number in range(1, 5):
        legacy = next(item for item in data["books"] if item.get("id") == f"art-science-intelligence-v{number}")
        require(legacy.get("cover") == f"assets/images/covers/volume-{number}-cover.webp",
                f"legacy volume {number} cover reference changed")

    specs = builder.available_specs()
    require(bool(specs), "at least one volume 5 chapter must be authored")
    expected_chapters = [builder.build_chapter(spec) for spec in specs]
    require(book.get("chapters") == expected_chapters, "volume 5 data does not match immutable Markdown sources")
    require(len(expected_chapters) <= builder.PLANNED_CHAPTERS, "volume 5 exceeds the roadmap chapter count")
    require([chapter.get("num") for chapter in book["chapters"]] == list(range(1, len(specs) + 1)),
            "volume 5 local chapter numbering is not contiguous")

    for _, global_num, slug, _, _ in specs:
        source = ROOT / "book-engineering/chapters" / f"{slug}.md"
        answer_relative = builder.ANSWER_KEYS.get(global_num, f"book-engineering/answers/{slug}-fa.md")
        answer = ROOT / answer_relative
        report = ROOT / f"book-engineering/chapters/{global_num}-audit-report-fa.md"
        project_relative = builder.PROJECT_DIRS.get(global_num, f"book-engineering/projects/{global_num}-evaluation-lab")
        project_dir = ROOT / project_relative
        for path in (source, answer, report, project_dir / "README.md"):
            require(path.is_file(), f"missing chapter {global_num} deliverable: {path.relative_to(ROOT)}")
        source_text = source.read_text(encoding="utf-8")
        require(f"فصل محلی {fa_num(global_num - 61)} جلد پنجم = فصل سراسری {fa_num(global_num)}" in source_text,
                f"chapter {global_num} local/global mapping missing")
        expected_review_date = "۷ نوامبر ۲۰۲۶" if global_num <= 67 else "۴ نوامبر ۲۰۲۶"
        require(f"تاریخ بازبینی منابع: {expected_review_date}" in source_text, f"chapter {global_num} source date missing or does not match its review date")
        require(bool(re.search(r"^##\s+.*منابع و تاریخ بازبینی", source_text, flags=re.MULTILINE)), f"chapter {global_num} dated bibliography missing")
        require(bool(re.search(r"^##\s+.*تمرین‌ها", source_text, flags=re.MULTILINE)) and bool(re.search(r"^##\s+.*جمع‌بندی", source_text, flags=re.MULTILINE)), f"chapter {global_num} needs exercises and summary")
        require("پاسخ‌نامهٔ مستقل" in source_text and "پروژهٔ فصل" in source_text and "گزارش ممیزی" in source_text,
                f"chapter {global_num} must link its independent companion files")
        require(not local_links(source_text.split("## پیوست اجرایی", 1)[0], source),
                f"chapter {global_num} contains a broken local link: {local_links(source_text, source)}")
        require(not local_links(answer.read_text(encoding="utf-8"), answer),
                f"chapter {global_num} answer key contains a broken local link")
        math_nodes = re.findall(r"<math\b[^>]*>", source_text)
        require(all("aria-label=" in node for node in math_nodes), f"chapter {global_num} MathML lacks aria-label")
        require(source_text.count("**متن جایگزین فرمول:**") >= len(math_nodes),
                f"chapter {global_num} must provide a visible text alternative for each formula")
        images = re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", source_text)
        require(bool(images), f"chapter {global_num} has no figure")
        for alt, image_path in images:
            require(bool(alt.strip()), f"chapter {global_num} figure has empty alt text")
            image_relative = Path(image_path)
            image_path_on_disk = (ROOT / image_relative if image_relative.parts and image_relative.parts[0] in {"book-engineering", "assets"}
                                  else source.parent / image_relative)
            require(image_path_on_disk.is_file(), f"chapter {global_num} missing figure {image_path}")
        if global_num in (62, 63, 64, 65, 66, 67, 68, 69):
            exercise_match = re.search(r"(?ms)^##\s+[^\n]*تمرین‌ها[^\n]*\n(.*?)(?=^##\s|\Z)", source_text)
            require(exercise_match is not None, f"chapter {global_num} exercise section missing")
            questions = re.findall(r"(?m)^([۱-۸])\. (.+)$", exercise_match.group(1))
            answer_questions = re.findall(r"(?m)^\*\*صورت پرسش:\*\* (.+)$", answer.read_text(encoding="utf-8"))
            require(len(questions) == 8 and [question for _, question in questions] == answer_questions,
                    f"chapter {global_num} answer key must preserve all eight question texts exactly")
        if global_num == 62:
            require(len(book["chapters"][0]["sections"]) == 26, "chapter 62 expected 26 sections")
        if global_num == 63:
            require(len(book["chapters"][1]["sections"]) == 34, "chapter 63 expected 34 sections")
        if global_num == 64:
            require(len(book["chapters"][2]["sections"]) == 39, "chapter 64 expected 39 sections")
            project_files = (
                "environment.json", "fixture_manifest.json", "results.json",
                "synthetic_security_fixture.json", "test_red_team_lab.py", "red_team_lab.py",
                "requirements.txt",
            )
            for filename in project_files:
                require((project_dir / filename).is_file(), f"chapter 64 project file missing: {filename}")
            fixture_path = project_dir / "synthetic_security_fixture.json"
            fixture_hash = hashlib.sha256(fixture_path.read_bytes()).hexdigest()
            manifest = json.loads((project_dir / "fixture_manifest.json").read_text(encoding="utf-8"))
            result = json.loads((project_dir / "results.json").read_text(encoding="utf-8"))
            environment = json.loads((project_dir / "environment.json").read_text(encoding="utf-8"))
            require(manifest.get("sha256") == fixture_hash and manifest.get("case_count") == 7,
                    "chapter 64 fixture manifest does not match fixture bytes")
            require(result.get("fixture_sha256") == fixture_hash and result.get("case_count") == 7,
                    "chapter 64 results do not match fixture bytes")
            require(result.get("attack_case_count") == 6 and result.get("benign_control_count") == 1
                    and result.get("control_checks_passed") == 7 and result.get("control_checks_failed") == 0
                    and result.get("simulated_attack_goals_reached") == 0
                    and result.get("simulated_attack_goal_rate") == 0.0,
                    "chapter 64 results exceed or contradict the documented fixture outcomes")
            require(environment.get("python") == "CPython 3.13.16"
                    and environment.get("network_used") is False
                    and environment.get("external_model_or_api") is False,
                    "chapter 64 environment metadata mismatch")
        if global_num == 65:
            require(len(book["chapters"][3]["sections"]) == 41, "chapter 65 expected 41 sections")
            project_files = (
                "environment.json", "fixture_manifest.json", "results.json",
                "governance_pack.json", "test_governance_check.py", "governance_check.py",
                "requirements.txt",
            )
            for filename in project_files:
                require((project_dir / filename).is_file(), f"chapter 65 project file missing: {filename}")
            fixture_path = project_dir / "governance_pack.json"
            fixture_hash = hashlib.sha256(fixture_path.read_bytes()).hexdigest()
            manifest = json.loads((project_dir / "fixture_manifest.json").read_text(encoding="utf-8"))
            result = json.loads((project_dir / "results.json").read_text(encoding="utf-8"))
            environment = json.loads((project_dir / "environment.json").read_text(encoding="utf-8"))
            require(manifest.get("sha256") == fixture_hash and manifest.get("risk_count") == 4,
                    "chapter 65 fixture manifest does not match governance-pack bytes")
            require(result.get("fixture_sha256") == fixture_hash and result.get("risk_count") == 4
                    and result.get("structurally_valid") is True
                    and result.get("release_authorized") is False
                    and result.get("gate_status") == "hold",
                    "chapter 65 results overstate or contradict the synthetic governance pack")
            require(environment.get("python", "").startswith("CPython 3.13")
                    and environment.get("network_used") is False
                    and environment.get("external_model_or_api") is False,
                    "chapter 65 environment metadata mismatch")

        if global_num == 66:
            require(len(book["chapters"][4]["sections"]) == 40, "chapter 66 expected 40 sections")
            project_files = (
                "environment.json", "fixture_manifest.json", "results.json",
                "synthetic_fixture.json", "app.py", "demo.html", "audit.py",
                "test_api.py", "test_frontend.py", "requirements.txt",
            )
            for filename in project_files:
                require((project_dir / filename).is_file(), f"chapter 66 project file missing: {filename}")
            fixture_path = project_dir / "synthetic_fixture.json"
            fixture_hash = hashlib.sha256(fixture_path.read_bytes()).hexdigest()
            manifest = json.loads((project_dir / "fixture_manifest.json").read_text(encoding="utf-8"))
            result = json.loads((project_dir / "results.json").read_text(encoding="utf-8"))
            environment = json.loads((project_dir / "environment.json").read_text(encoding="utf-8"))
            require(manifest.get("sha256") == fixture_hash
                    and manifest.get("fixture_id") == "v5-ch05-api-contract-synthetic-v1"
                    and manifest.get("synthetic") is True
                    and manifest.get("contains_personal_data") is False,
                    "chapter 66 fixture manifest does not match the synthetic fixture bytes")
            require(result.get("fixture_sha256") == fixture_hash
                    and result.get("fixture_id") == manifest.get("fixture_id")
                    and result.get("api_case_count") == 12
                    and result.get("api_cases_passed") == 12
                    and result.get("api_cases_failed") == 0
                    and result.get("frontend_case_count") == 2
                    and result.get("frontend_cases_passed") == 2
                    and result.get("frontend_cases_failed") == 0
                    and result.get("external_http_requests") == 0
                    and result.get("live_model_calls") == 0
                    and result.get("personal_records") == 0,
                    "chapter 66 results overstate or contradict the synthetic test runs")
            require(environment.get("python", {}).get("implementation") == "CPython"
                    and environment.get("python", {}).get("version") == "3.13.16"
                    and environment.get("execution", {}).get("external_http_requests") == 0
                    and environment.get("execution", {}).get("live_model_calls") == 0
                    and environment.get("execution", {}).get("real_user_or_personal_records") == 0,
                    "chapter 66 environment metadata mismatch")

        if global_num == 67:
            require(len(book["chapters"][5]["sections"]) == 28, "chapter 67 expected 28 sections")
            project_files = (
                "environment.json", "fixture_manifest.json", "results.json",
                "synthetic_serving_trace.json", "serving_lab.py", "test_serving_lab.py",
                "README.md", "requirements.txt",
            )
            for filename in project_files:
                require((project_dir / filename).is_file(), f"chapter 67 project file missing: {filename}")
            fixture_path = project_dir / "synthetic_serving_trace.json"
            fixture_hash = hashlib.sha256(fixture_path.read_bytes()).hexdigest()
            manifest = json.loads((project_dir / "fixture_manifest.json").read_text(encoding="utf-8"))
            result = json.loads((project_dir / "results.json").read_text(encoding="utf-8"))
            environment = json.loads((project_dir / "environment.json").read_text(encoding="utf-8"))
            require(manifest.get("fixture_id") == "v5-ch06-serving-synthetic-v1"
                    and manifest.get("sha256") == fixture_hash
                    and manifest.get("synthetic") is True
                    and manifest.get("request_count") == 24
                    and manifest.get("unique_exact_cache_keys") == 12
                    and manifest.get("contains_personal_data") is False
                    and manifest.get("contains_production_trace") is False,
                    "chapter 67 fixture manifest does not match the synthetic trace")
            require(result.get("fixture_id") == manifest.get("fixture_id")
                    and result.get("fixture_sha256") == fixture_hash
                    and result.get("synthetic") is True
                    and result.get("request_count") == 24
                    and result.get("unique_exact_cache_keys") == 12
                    and result.get("run_count") == 4
                    and result.get("external_http_requests") == 0
                    and result.get("live_model_calls") == 0
                    and result.get("gpu_used") is False
                    and result.get("production_trace_used") is False
                    and result.get("personal_records") == 0
                    and result.get("model_quality_evaluated") is False
                    and len(result.get("limitations", [])) == 6,
                    "chapter 67 results overstate or contradict the synthetic simulation")
            runs = {run.get("name"): run for run in result.get("runs", [])}
            require(set(runs) == {
                "baseline_one_at_a_time", "microbatch_only",
                "exact_response_cache_only", "microbatch_plus_exact_cache",
            }, "chapter 67 run names or count mismatch")
            baseline = runs["baseline_one_at_a_time"]
            microbatch = runs["microbatch_only"]
            cache_only = runs["exact_response_cache_only"]
            combined = runs["microbatch_plus_exact_cache"]
            require(baseline.get("successful_responses") == 20
                    and baseline.get("queue_rejections") == 4
                    and baseline.get("response_cache_hits") == 0
                    and baseline.get("response_latency_p95_ms") == 333.6,
                    "chapter 67 baseline results mismatch")
            require(microbatch.get("successful_responses") == 24
                    and microbatch.get("queue_rejections") == 0
                    and microbatch.get("model_batches") == 6
                    and microbatch.get("response_latency_p95_ms") == 179.5,
                    "chapter 67 microbatch results mismatch")
            require(cache_only.get("successful_responses") == 22
                    and cache_only.get("queue_rejections") == 2
                    and cache_only.get("model_compute_requests") == 12
                    and cache_only.get("response_cache_hits") == 10,
                    "chapter 67 exact-cache results mismatch")
            require(combined.get("successful_responses") == 24
                    and combined.get("queue_rejections") == 0
                    and combined.get("model_compute_requests") == 12
                    and combined.get("response_cache_hits") == 12
                    and combined.get("model_batches") == 3
                    and combined.get("response_cache_payload_bytes_peak") == 2460,
                    "chapter 67 combined results mismatch")
            require(all(run.get("output_integrity_rate") == 1.0
                        and run.get("max_waiting_queue_depth", 999) <= run.get("max_queue_size", 0)
                        for run in runs.values()),
                    "chapter 67 result integrity or bounded-queue check failed")
            require(environment.get("python", {}).get("implementation") == "CPython"
                    and environment.get("python", {}).get("version") == "3.13.16"
                    and environment.get("dependencies") == []
                    and environment.get("execution", {}).get("external_http_requests") == 0
                    and environment.get("execution", {}).get("live_model_calls") == 0
                    and environment.get("execution", {}).get("gpu_used") is False
                    and environment.get("execution", {}).get("production_trace_used") is False
                    and environment.get("execution", {}).get("personal_records") == 0,
                    "chapter 67 environment metadata mismatch")

        if global_num == 68:
            require(len(book["chapters"][6]["sections"]) == 37, "chapter 68 expected 37 sections")
            project_files = (
                "environment.json", "fixture_manifest.json", "results.json",
                "synthetic_security_events.json", "security_ops.py", "test_security_ops.py",
                "README.md", "requirements.txt",
            )
            for filename in project_files:
                require((project_dir / filename).is_file(), f"chapter 68 project file missing: {filename}")
            fixture_path = project_dir / "synthetic_security_events.json"
            fixture_hash = hashlib.sha256(fixture_path.read_bytes()).hexdigest()
            manifest = json.loads((project_dir / "fixture_manifest.json").read_text(encoding="utf-8"))
            result = json.loads((project_dir / "results.json").read_text(encoding="utf-8"))
            environment = json.loads((project_dir / "environment.json").read_text(encoding="utf-8"))
            require(manifest.get("fixture_id") == "v5-ch07-security-ops-synthetic-v1"
                    and manifest.get("sha256") == fixture_hash
                    and manifest.get("synthetic") is True
                    and manifest.get("event_count") == 14
                    and manifest.get("credential_count") == 4
                    and manifest.get("contains_personal_data") is False
                    and manifest.get("contains_real_credentials") is False
                    and manifest.get("contains_production_trace") is False,
                    "chapter 68 fixture manifest does not match the synthetic events")
            require(result.get("project_id") == manifest.get("fixture_id")
                    and result.get("fixture_id") == manifest.get("fixture_id")
                    and result.get("fixture_sha256") == fixture_hash
                    and result.get("synthetic") is True
                    and result.get("request_count") == 14
                    and result.get("decision_counts") == {"allowed": 6, "denied": 6, "rate_limited": 2}
                    and result.get("reason_counts") == {
                        "invalid_credential": 2, "missing_credential": 1, "policy_allow": 6,
                        "rate_limit_exceeded": 2, "role_required": 1, "tenant_boundary": 2,
                    }
                    and result.get("auth_failure_count") == 3
                    and result.get("authorization_denial_count") == 3
                    and result.get("rate_limited_count") == 2
                    and result.get("audit_event_count") == 14
                    and result.get("incident_count") == 1
                    and result.get("alerts", [{}])[0].get("alert_code") == "AUTH_FAILURE_BURST"
                    and result.get("incidents", [{}])[0].get("state") == "closed"
                    and result.get("external_http_requests") == 0
                    and result.get("live_auth_provider_calls") == 0
                    and result.get("live_model_calls") == 0
                    and result.get("gpu_used") is False
                    and result.get("personal_records") == 0
                    and result.get("real_credentials_used") is False,
                    "chapter 68 results overstate or contradict the synthetic policy simulation")
            metrics = result.get("metrics", {})
            require(metrics.get("private_fields_logged") == 0
                    and metrics.get("dimension_fields") == ["outcome", "reason_code"]
                    and "tenant_ref" not in metrics and "actor_ref" not in metrics,
                    "chapter 68 metrics contain high-cardinality or personal dimensions")
            serialized_result = json.dumps(result, ensure_ascii=False)
            require(all(value not in serialized_result for value in (
                "SYNTHETIC-CREDENTIAL-CANARY-DO-NOT-LOG",
                "SYNTHETIC-PRIVATE-PROMPT-DO-NOT-LOG",
                "synthetic-person@example.invalid", "198.51.100.",
            )), "chapter 68 result contains a private canary or source address")
            require(environment.get("audit_date") == "2026-11-08"
                    and environment.get("python", {}).get("implementation") == "CPython"
                    and environment.get("python", {}).get("version") == "3.13.16"
                    and environment.get("dependencies") == []
                    and environment.get("fixture_sha256") == fixture_hash
                    and environment.get("execution", {}).get("external_http_requests") == 0
                    and environment.get("execution", {}).get("live_auth_provider_calls") == 0
                    and environment.get("execution", {}).get("live_model_calls") == 0
                    and environment.get("execution", {}).get("gpu_used") is False
                    and environment.get("execution", {}).get("production_trace_used") is False
                    and environment.get("execution", {}).get("personal_records") == 0
                    and environment.get("execution", {}).get("unit_tests") == "25/25 passed",
                    "chapter 68 environment metadata mismatch")

        if global_num == 69:
            require(len(book["chapters"][7]["sections"]) == 29, "chapter 69 expected 29 sections, including its executable appendix")
            project_files = (
                "environment.json", "fixture_manifest.json", "results.json",
                "synthetic_release_scenarios.json", "deployment_gate.py", "local_stub.py",
                "test_deployment_gate.py", "test_local_stub.py", "README.md", "requirements.txt",
            )
            for filename in project_files:
                require((project_dir / filename).is_file(), f"chapter 69 project file missing: {filename}")
            fixture_path = project_dir / "synthetic_release_scenarios.json"
            fixture_hash = hashlib.sha256(fixture_path.read_bytes()).hexdigest()
            manifest = json.loads((project_dir / "fixture_manifest.json").read_text(encoding="utf-8"))
            result = json.loads((project_dir / "results.json").read_text(encoding="utf-8"))
            environment = json.loads((project_dir / "environment.json").read_text(encoding="utf-8"))
            require(manifest.get("fixture_id") == "v5-ch08-deployment-cicd-synthetic-v1"
                    and manifest.get("sha256") == fixture_hash
                    and manifest.get("synthetic") is True
                    and manifest.get("scenario_count") == 3
                    and manifest.get("scenario_names") == [
                        "healthy_staged_rollout", "latency_regression_rolls_back",
                        "missing_provenance_is_blocked",
                    ]
                    and manifest.get("contains_model_weights") is False
                    and manifest.get("contains_production_traffic") is False
                    and manifest.get("contains_personal_data") is False
                    and manifest.get("contains_credentials") is False
                    and manifest.get("external_network_required") is False,
                    "chapter 69 fixture manifest does not match the synthetic release scenarios")
            require(result.get("project_id") == manifest.get("fixture_id")
                    and result.get("fixture_id") == manifest.get("fixture_id")
                    and result.get("fixture_sha256") == fixture_hash
                    and result.get("synthetic") is True
                    and result.get("scenario_count") == 3
                    and result.get("decision_counts") == {
                        "blocked": 1, "hold": 0, "rolled_back": 1, "promoted": 1,
                    }
                    and result.get("external_network_requests") == 0
                    and result.get("cloud_deployments") == 0
                    and result.get("production_writes") == 0
                    and result.get("model_inference_calls") == 0
                    and result.get("gpu_used") is False
                    and result.get("personal_records") == 0,
                    "chapter 69 results overstate or contradict the synthetic release scenarios")
            scenarios = {item.get("scenario"): item for item in result.get("results", [])}
            require(set(scenarios) == set(manifest["scenario_names"])
                    and all(item.get("simulated_only") is True for item in scenarios.values()),
                    "chapter 69 result scenarios or simulated-only declarations mismatch")
            promoted = scenarios["healthy_staged_rollout"]
            rolled_back = scenarios["latency_regression_rolls_back"]
            blocked = scenarios["missing_provenance_is_blocked"]
            require(promoted.get("decision") == "promoted"
                    and promoted.get("promoted_stages_percent") == [5, 25, 100]
                    and promoted.get("active_release_id") == "candidate-r4"
                    and promoted.get("rollback_performed") is False,
                    "chapter 69 healthy rollout result mismatch")
            require(rolled_back.get("decision") == "rolled_back"
                    and rolled_back.get("failed_at_percent") == 25
                    and rolled_back.get("observed_p95_ms") == 930
                    and rolled_back.get("active_release_id") == "stable-r3"
                    and rolled_back.get("rollback_performed") is True,
                    "chapter 69 canary rollback result mismatch")
            require(blocked.get("decision") == "blocked"
                    and blocked.get("preflight_passed") is False
                    and blocked.get("blocked_reasons") == ["provenance_not_verified"]
                    and blocked.get("promoted_stages_percent") == [],
                    "chapter 69 provenance gate result mismatch")
            execution = environment.get("execution", {})
            require(environment.get("audit_date") == "2026-11-04"
                    and environment.get("project_id") == manifest.get("fixture_id")
                    and environment.get("python", {}).get("implementation") == "CPython"
                    and environment.get("python", {}).get("version") == "3.13.16"
                    and environment.get("dependencies") == []
                    and environment.get("fixture_sha256") == fixture_hash
                    and execution.get("unit_tests") == "41/41 passed"
                    and execution.get("external_network_requests") == 0
                    and execution.get("loopback_http_smoke_tests") == 5
                    and execution.get("cloud_deployments") == 0
                    and execution.get("production_writes") == 0
                    and execution.get("model_inference_calls") == 0
                    and execution.get("model_weights_loaded") is False
                    and execution.get("gpu_used") is False
                    and execution.get("personal_records") == 0
                    and execution.get("real_credentials_used") is False,
                    "chapter 69 environment metadata mismatch")

        diagram_relative = builder.DIAGRAMS.get(global_num)
        if diagram_relative:
            diagram = ROOT / diagram_relative
            svg_root = ET.parse(diagram).getroot()
            require(svg_root.attrib.get("role") == "img", f"chapter {global_num} diagram must use role=img")
            require("aria-labelledby" in svg_root.attrib and svg_root.attrib.get("{http://www.w3.org/XML/1998/namespace}lang") == "fa",
                    f"chapter {global_num} SVG needs linked accessible title/description and Persian language")
            svg_ids = {element.attrib["id"] for element in svg_root.iter() if "id" in element.attrib}
            for element_id in svg_root.attrib["aria-labelledby"].split():
                require(element_id in svg_ids, f"chapter {global_num} SVG references missing ID {element_id}")

    cover_bytes = (ROOT / builder.COVER_PATH).read_bytes()
    require(cover_bytes.startswith(b"\x89PNG\r\n\x1a\n") and len(cover_bytes) >= 24,
            "volume 5 cover must be a valid PNG")
    require(hashlib.sha256(cover_bytes).hexdigest() == builder.COVER_SHA256,
            "volume 5 cover bytes do not match the supplied image")
    require(struct.unpack(">II", cover_bytes[16:24]) == (1024, 1536),
            "volume 5 supplied cover dimensions must remain 1024 by 1536")

    markdown_path = ROOT / "volume-5-full-fa.md"
    require(markdown_path.is_file(), "volume-5-full-fa.md is missing")
    require(markdown_path.read_text(encoding="utf-8") == builder.expected_markdown(expected_chapters, specs),
            "full Markdown does not match the chapter sources")

    sw = (ROOT / "sw.js").read_text(encoding="utf-8")
    cache_match = re.search(r"(?m)^const CACHE_NAME = 'fa-academy-v(\d+)';$", sw)
    header_match = re.search(r"Service Worker v(\d+)", sw.splitlines()[0])
    require(cache_match and header_match and cache_match.group(1) == header_match.group(1),
            "service-worker header and cache name must share a version")
    require(int(cache_match.group(1)) >= 97, "service-worker cache version was not advanced for volume 5")
    array_match = re.search(r"const CORE_FILES = \[(.*?)\n\];", sw, flags=re.DOTALL)
    require(array_match is not None, "service worker CORE_FILES list missing")
    cache_paths = re.findall(r"['\"](\./[^'\"]+)['\"]", array_match.group(1))
    require(len(cache_paths) == len(set(cache_paths)), "service worker CORE_FILES has duplicates")
    required = ["./" + path for path in builder._v5_offline_paths(specs)]
    require(set(required).issubset(cache_paths), f"service worker is missing volume 5 offline paths: {set(required)-set(cache_paths)}")
    for relative in builder._v5_offline_paths(specs):
        path = ROOT / relative
        require(path.is_file() and path.stat().st_size > 0, f"offline asset missing or empty: {relative}")
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        found = cjk_chars(text)
        require(not found, f"unexpected CJK codepoints in {relative}: {sorted(found)}")

    print(
        f"PASS volume 5 structure: {len(expected_chapters)}/{builder.PLANNED_CHAPTERS} chapters; "
        f"sections={[len(ch['sections']) for ch in expected_chapters]}; "
        f"accessible SVG/MathML, exact answer prompts and code appendix, Markdown, legacy covers, "
        f"{len(required)} offline paths; Service Worker v{cache_match.group(1)}"
    )


def fa_num(value: int) -> str:
    return str(value).translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))


if __name__ == "__main__":
    main()
