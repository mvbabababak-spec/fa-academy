#!/usr/bin/env python3
"""Check the internal consistency of a fictional research-architecture packet.

This tool validates fields and cross-references only. It does not evaluate
scientific novelty, architectural quality, empirical results, or authorship.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ID = "v5-ch11-research-architecture-synthetic-v1"
KNOWN_CREDIT_ROLES = {
    "Conceptualization",
    "Data curation",
    "Formal analysis",
    "Funding acquisition",
    "Investigation",
    "Methodology",
    "Project administration",
    "Resources",
    "Software",
    "Supervision",
    "Validation",
    "Visualization",
    "Writing – original draft",
    "Writing – review & editing",
}
REQUIRED_PAPER_SECTIONS = {
    "title",
    "abstract",
    "introduction",
    "related_work",
    "method",
    "architecture",
    "evaluation",
    "results",
    "limitations",
    "ethics_and_availability",
    "conclusion",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def unique_ids(items: list[dict[str, Any]], label: str) -> set[str]:
    require(isinstance(items, list) and items, f"{label} must be a non-empty list")
    identifiers = [item.get("id") for item in items if isinstance(item, dict)]
    require(len(identifiers) == len(items) and all(isinstance(value, str) and value for value in identifiers),
            f"{label} contains an item without an id")
    require(len(identifiers) == len(set(identifiers)), f"{label} contains duplicate ids")
    return set(identifiers)


def validate_packet(packet: dict[str, Any]) -> dict[str, Any]:
    require(isinstance(packet, dict), "packet must be a JSON object")
    require(packet.get("project_id") == PROJECT_ID, "unexpected project_id")
    require(packet.get("fixture_id") == PROJECT_ID, "fixture_id does not match project_id")
    require(packet.get("synthetic") is True, "fixture must be explicitly synthetic")
    require(packet.get("real_data_used") is False, "real_data_used must be false")
    require(packet.get("real_model_outputs") is False, "real_model_outputs must be false")
    require(packet.get("network_used") is False, "network_used must be false")
    require(packet.get("status") == "proposal_not_tested", "packet must remain an untested proposal")

    problem = packet.get("problem")
    require(isinstance(problem, dict), "problem block missing")
    for field in ("context", "boundary", "question"):
        require(isinstance(problem.get(field), str) and problem[field].strip(), f"problem.{field} is required")
    boundary = problem["boundary"].strip().lower()
    safe_boundary_phrases = ("خارج از دامنهٔ تولید", "بیرون از دامنهٔ تولید", "not a production", "not production", "outside production", "exclude production")
    require(any(phrase in boundary for phrase in safe_boundary_phrases),
            "problem boundary must exclude production use")

    contribution = packet.get("contribution")
    require(isinstance(contribution, dict), "contribution block missing")
    require(contribution.get("type") == "architecture", "contribution type must be architecture")
    for field in ("candidate_claim", "mechanism", "falsification_condition"):
        require(isinstance(contribution.get(field), str) and contribution[field].strip(),
                f"contribution.{field} is required")
    require(contribution.get("status") == "proposal_not_tested", "contribution status must remain untested")
    require(contribution.get("novelty_status") == "not_assessed", "novelty must remain unassessed")

    architecture = packet.get("architecture")
    require(isinstance(architecture, dict), "architecture block missing")
    require(isinstance(architecture.get("baseline"), str) and architecture["baseline"].strip(),
            "architecture baseline is required")
    require(isinstance(architecture.get("version"), str) and architecture["version"].strip(),
            "architecture version is required")
    component_ids = unique_ids(architecture.get("components", []), "architecture components")
    for component in architecture["components"]:
        for field in ("name", "input_contract", "output_contract"):
            require(isinstance(component.get(field), str) and component[field].strip(),
                    f"component {component.get('id')} needs {field}")
        require(component.get("status") == "proposed", "components must be labeled proposed")
        require(component.get("evidence_state") == "none", "proposal fixture must not imply measured evidence")
    alternatives = architecture.get("alternatives", [])
    alternative_ids = unique_ids(alternatives, "architecture alternatives")
    require(len(alternative_ids) >= 2, "at least two architecture alternatives are required")
    require(isinstance(architecture.get("invariants"), list) and architecture["invariants"],
            "architecture invariants are required")

    experiments = packet.get("evaluation_plan", [])
    experiment_ids = unique_ids(experiments, "evaluation plan")
    for experiment in experiments:
        require(experiment.get("status") == "planned" and experiment.get("has_results") is False,
                f"evaluation {experiment.get('id')} must be planned with no results")
        require(isinstance(experiment.get("question"), str) and experiment["question"].strip(),
                f"evaluation {experiment.get('id')} needs a question")
        require(isinstance(experiment.get("comparison"), str) and experiment["comparison"].strip(),
                f"evaluation {experiment.get('id')} needs a comparison")
    scenarios = packet.get("quality_scenarios", [])
    scenario_ids = unique_ids(scenarios, "quality scenarios")
    for scenario in scenarios:
        for field in ("attribute", "stimulus", "response", "priority"):
            require(isinstance(scenario.get(field), str) and scenario[field].strip(),
                    f"quality scenario {scenario.get('id')} needs {field}")
        require(scenario.get("evaluation_ref") in experiment_ids,
                f"quality scenario {scenario.get('id')} references an unknown evaluation")

    sources = packet.get("sources", [])
    source_ids = unique_ids(sources, "source registry")
    for source in sources:
        require(isinstance(source.get("title"), str) and source["title"].strip(),
                f"source {source.get('id')} needs a title")
        require(isinstance(source.get("url"), str) and source["url"].startswith("https://"),
                f"source {source.get('id')} needs an HTTPS URL")
    related_work = packet.get("related_work")
    require(isinstance(related_work, dict), "related_work block missing")
    require(related_work.get("search_status") == "illustrative_map_not_exhaustive",
            "literature map must not claim exhaustive novelty review")
    require(isinstance(related_work.get("source_refs"), list) and related_work["source_refs"],
            "related_work needs source references")
    require(set(related_work["source_refs"]).issubset(source_ids), "related_work cites an unknown source")

    claims = packet.get("claims", [])
    claim_ids = unique_ids(claims, "claim registry")
    for claim in claims:
        require(claim.get("status") == "hypothesis", f"claim {claim.get('id')} must remain a hypothesis")
        references = claim.get("evaluation_refs")
        require(isinstance(references, list) and references, f"claim {claim.get('id')} needs planned evaluations")
        require(set(references).issubset(experiment_ids), f"claim {claim.get('id')} references an unknown evaluation")

    paper_sections = packet.get("paper_outline", [])
    require(isinstance(paper_sections, list) and paper_sections, "paper_outline is required")
    section_ids = [item.get("id") for item in paper_sections if isinstance(item, dict)]
    require(len(section_ids) == len(paper_sections) and len(section_ids) == len(set(section_ids)),
            "paper_outline has missing or duplicate section ids")
    require(REQUIRED_PAPER_SECTIONS.issubset(set(section_ids)), "paper_outline omits a required section")

    contributors = packet.get("contributors", [])
    contributor_ids = unique_ids(contributors, "contributors")
    for contributor in contributors:
        roles = contributor.get("credit_roles")
        require(isinstance(roles, list) and roles, f"contributor {contributor.get('id')} needs roles")
        require(set(roles).issubset(KNOWN_CREDIT_ROLES),
                f"contributor {contributor.get('id')} has an unsupported CRediT role")
        require(contributor.get("authorship_status") == "not_decided",
                "CRediT roles must not be treated as an authorship decision")

    milestones = packet.get("roadmap", [])
    milestone_ids = unique_ids(milestones, "roadmap")
    require(len(milestone_ids) >= 3, "roadmap needs at least three milestones")
    for milestone in milestones:
        for field in ("period", "deliverable", "decision_gate"):
            require(isinstance(milestone.get(field), str) and milestone[field].strip(),
                    f"milestone {milestone.get('id')} needs {field}")
        require(milestone.get("status") == "planned", "fixture milestones must not be marked complete")

    release = packet.get("release_plan")
    require(isinstance(release, dict), "release_plan block missing")
    require(release.get("target_venue") == "not_selected", "fixture must not imply a selected venue")
    require(release.get("license_review") == "pending", "license review must remain pending")
    require(release.get("artifact_review") == "not_started", "artifact review must remain not started")
    require(release.get("human_subjects_review") == "not_assessed", "ethics review must remain unassessed")

    return {
        "project_id": PROJECT_ID,
        "fixture_id": PROJECT_ID,
        "synthetic": True,
        "validation_status": "structural_consistency_passed",
        "counts": {
            "architecture_components": len(component_ids),
            "architecture_alternatives": len(alternative_ids),
            "quality_scenarios": len(scenario_ids),
            "planned_evaluations": len(experiment_ids),
            "hypotheses": len(claim_ids),
            "paper_sections": len(section_ids),
            "contributors": len(contributor_ids),
            "roadmap_milestones": len(milestone_ids),
            "registered_sources": len(source_ids),
        },
        "scientific_conclusions": {
            "novelty_confirmed": False,
            "architecture_evaluated": False,
            "hypothesis_tested": False,
            "paper_peer_reviewed": False,
            "authorship_decided": False,
            "license_or_ethics_approved": False,
        },
        "scope": "Synthetic proposal-packet consistency only; no empirical, novelty, quality, ethics, or publication assessment.",
        "limitations": [
            "A structurally complete packet is not evidence that the architecture works.",
            "The literature map is illustrative and does not establish novelty or priority.",
            "Planned evaluations are not results and do not authorize statistical inference.",
            "Contributor roles do not decide authorship; venue and institutional rules were not checked.",
            "No real data, model, human participant, license, or artifact was reviewed.",
        ],
    }


def analyze_files(packet_path: Path, manifest_path: Path) -> dict[str, Any]:
    packet_bytes = packet_path.read_bytes()
    fixture_hash = hashlib.sha256(packet_bytes).hexdigest()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    require(manifest.get("project_id") == PROJECT_ID, "manifest project_id mismatch")
    require(manifest.get("fixture_sha256") == fixture_hash, "fixture SHA-256 mismatch")
    require(manifest.get("synthetic") is True, "manifest must mark the fixture synthetic")
    packet = json.loads(packet_bytes.decode("utf-8"))
    result = validate_packet(packet)
    result["fixture_sha256"] = fixture_hash
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, default=Path("research_packet.json"))
    parser.add_argument("--manifest", type=Path, default=Path("fixture_manifest.json"))
    parser.add_argument("--output", type=Path, default=Path("results.json"))
    args = parser.parse_args()
    try:
        result = analyze_files(args.packet, args.manifest)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"synthetic proposal only: components={result['counts']['architecture_components']}; "
          f"alternatives={result['counts']['architecture_alternatives']}; "
          f"novelty_confirmed={str(result['scientific_conclusions']['novelty_confirmed']).lower()}; "
          f"hypothesis_tested={str(result['scientific_conclusions']['hypothesis_tested']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
