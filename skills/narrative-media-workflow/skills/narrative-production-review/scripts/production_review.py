#!/usr/bin/env python3
"""Validate narrative media dry-run readiness."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED_STAGES = [
    "story-analysis",
    "supplement-pass",
    "shot-outline",
    "voiceover-draft",
    "assembly-review",
]


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def review(chapter: dict, provider_plan: dict, pipeline_plan: dict) -> dict:
    warnings = []
    blockers = []

    if not chapter.get("chapter_text"):
        blockers.append("chapter_text is empty")
    if chapter.get("selected_chapter", {}).get("paragraph_count", 0) <= 0:
        blockers.append("selected chapter has no body paragraphs")

    defaults = provider_plan.get("global_defaults", {})
    if defaults.get("text_primary") != "doubao-seed-2-0-pro-260215":
        blockers.append("Ark text default does not match required model")
    if defaults.get("text_supplement_only") != "openai-compatible:deepseek":
        blockers.append("DeepSeek supplement default does not match required model")

    deepseek_policy = provider_plan.get("policy", {}).get("deepseek_usage")
    if deepseek_policy != "text supplement only":
        blockers.append("DeepSeek policy must remain text supplement only")

    stages = pipeline_plan.get("stages", [])
    stage_ids = [stage.get("id") for stage in stages]
    missing = [stage for stage in REQUIRED_STAGES if stage not in stage_ids]
    if missing:
        blockers.append(f"missing required stages: {', '.join(missing)}")

    if not pipeline_plan.get("dry_run"):
        blockers.append("pipeline plan must remain dry_run")

    fallback_count = sum(1 for stage in stages if stage.get("mode") == "human-fallback")
    if fallback_count:
        warnings.append(f"{fallback_count} stage(s) require human fallback due to unavailable providers")

    placeholders = pipeline_plan.get("asset_placeholders", {})
    if placeholders.get("image_slots", 0) < 3:
        warnings.append("image slot estimate is unusually low")

    readiness = "blocked" if blockers else "ready-with-warnings" if warnings else "ready"
    return {
        "workflow": "narrative-production-review",
        "readiness": readiness,
        "warnings": warnings,
        "blockers": blockers,
        "summary": {
            "chapter_title": chapter.get("selected_chapter", {}).get("title"),
            "stage_count": len(stages),
            "provider_availability": {
                name: cfg.get("available")
                for name, cfg in provider_plan.get("provider_defaults", {}).items()
            },
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapter-json", required=True)
    parser.add_argument("--provider-plan-json", required=True)
    parser.add_argument("--pipeline-plan-json", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = review(
        load_json(args.chapter_json),
        load_json(args.provider_plan_json),
        load_json(args.pipeline_plan_json),
    )
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": "ok",
        "output": str(output_path),
        "readiness": payload["readiness"],
        "blockers": len(payload["blockers"]),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise
