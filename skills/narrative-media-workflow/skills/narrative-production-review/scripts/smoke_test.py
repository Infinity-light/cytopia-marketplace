#!/usr/bin/env python3
"""End-to-end smoke test for the narrative media dry-run plugin."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = THIS_DIR.parents[2]
INTAKE_SCRIPT = PLUGIN_ROOT / "skills" / "narrative-story-intake" / "scripts" / "story_intake.py"
PROVIDER_SCRIPT = PLUGIN_ROOT / "skills" / "narrative-provider-planner" / "scripts" / "provider_plan.py"
PIPELINE_SCRIPT = PLUGIN_ROOT / "skills" / "narrative-pipeline-orchestrator" / "scripts" / "pipeline_orchestrator.py"
REVIEW_SCRIPT = THIS_DIR / "production_review.py"
DEFAULT_DOCX = Path(r"C:\Users\WaterFish\Documents\WeChat Files\wxid_gr4kjgxemwho22\FileStorage\File\2026-02\知行合一_润色后完整版.docx")


def run_step(args: list[str]) -> dict:
    completed = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", check=True)
    line = completed.stdout.strip().splitlines()[-1]
    return json.loads(line)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--docx", default=str(DEFAULT_DOCX))
    parser.add_argument("--chapter-title")
    parser.add_argument("--env-file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    docx_path = Path(args.docx)
    if not docx_path.exists():
        raise FileNotFoundError(f"Sample DOCX not found: {docx_path}")

    with tempfile.TemporaryDirectory(prefix="narrative-media-smoke-") as tmp:
        tmpdir = Path(tmp)
        chapter_json = tmpdir / "chapter.json"
        provider_json = tmpdir / "provider-plan.json"
        pipeline_json = tmpdir / "pipeline-plan.json"
        review_json = tmpdir / "review.json"

        intake_cmd = [sys.executable, "-X", "utf8", str(INTAKE_SCRIPT), "--docx", str(docx_path), "--output", str(chapter_json)]
        if args.chapter_title:
            intake_cmd.extend(["--chapter-title", args.chapter_title])
        intake_result = run_step(intake_cmd)

        provider_cmd = [sys.executable, "-X", "utf8", str(PROVIDER_SCRIPT), "--output", str(provider_json)]
        if args.env_file:
            provider_cmd.extend(["--env-file", args.env_file])
        provider_result = run_step(provider_cmd)

        pipeline_result = run_step([
            sys.executable, "-X", "utf8", str(PIPELINE_SCRIPT),
            "--chapter-json", str(chapter_json),
            "--provider-plan-json", str(provider_json),
            "--output", str(pipeline_json),
        ])

        review_result = run_step([
            sys.executable, "-X", "utf8", str(REVIEW_SCRIPT),
            "--chapter-json", str(chapter_json),
            "--provider-plan-json", str(provider_json),
            "--pipeline-plan-json", str(pipeline_json),
            "--output", str(review_json),
        ])

        review_payload = json.loads(review_json.read_text(encoding="utf-8"))
        output = {
            "status": "ok",
            "docx": str(docx_path),
            "steps": {
                "story_intake": intake_result,
                "provider_plan": provider_result,
                "pipeline_orchestrator": pipeline_result,
                "production_review": review_result,
            },
            "review": review_payload,
            "artifacts": {
                "chapter_json": str(chapter_json),
                "provider_json": str(provider_json),
                "pipeline_json": str(pipeline_json),
                "review_json": str(review_json),
            },
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise
