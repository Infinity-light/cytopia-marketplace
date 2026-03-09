#!/usr/bin/env python3
"""Compose a deterministic narrative media dry-run pipeline."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def provider_mode(plan: dict, provider: str) -> str:
    return "provider-ready" if plan["provider_defaults"][provider]["available"] else "human-fallback"


def build_pipeline(chapter: dict, provider_plan: dict) -> dict:
    title = chapter["selected_chapter"]["title"]
    ark_mode = provider_mode(provider_plan, "ark")
    fal_mode = provider_mode(provider_plan, "fal")
    deepseek_mode = provider_mode(provider_plan, "deepseek")
    excerpt = chapter.get("chapter_excerpt", "")
    stages = [
        {
            "id": "story-analysis",
            "owner": "ark",
            "mode": ark_mode,
            "inputs": ["chapter_text"],
            "outputs": ["story_beats", "character_notes", "scene_seed_prompts"],
            "notes": f"Use {provider_plan['global_defaults']['text_primary']} for beat extraction on {title}",
        },
        {
            "id": "supplement-pass",
            "owner": "deepseek",
            "mode": deepseek_mode,
            "inputs": ["story_beats", "scene_seed_prompts"],
            "outputs": ["alt_wording", "risk_notes"],
            "notes": "DeepSeek is supplement-only and must not replace main media providers.",
        },
        {
            "id": "shot-outline",
            "owner": "ark",
            "mode": ark_mode,
            "inputs": ["story_beats", "character_notes"],
            "outputs": ["shot_list", "image_prompt_pack", "video_prompt_pack"],
            "notes": "Generate prompt placeholders only during dry-run.",
        },
        {
            "id": "voiceover-draft",
            "owner": "fal",
            "mode": fal_mode,
            "inputs": ["story_beats", "alt_wording"],
            "outputs": ["voiceover_script", "tts_placeholder"],
            "notes": f"Preferred voice synthesis model: {provider_plan['global_defaults']['audio_primary']}",
        },
        {
            "id": "assembly-review",
            "owner": "human",
            "mode": "required",
            "inputs": ["shot_list", "image_prompt_pack", "video_prompt_pack", "voiceover_script"],
            "outputs": ["production_packet", "qa_notes"],
            "notes": "Manual handoff stage before any external generation or editing.",
        },
    ]

    placeholders = {
        "image_slots": max(6, min(18, chapter["selected_chapter"]["paragraph_count"] or 6)),
        "video_segments": max(3, min(10, (chapter["selected_chapter"]["paragraph_count"] // 2) or 3)),
        "audio_segments": max(2, min(8, (len(excerpt) // 200) or 2)),
    }

    return {
        "workflow": "narrative-pipeline-orchestrator",
        "dry_run": True,
        "chapter_title": title,
        "pipeline_summary": {
            "stage_count": len(stages),
            "has_provider_fallbacks": any(stage["mode"] == "human-fallback" for stage in stages),
            "final_handoff": "assembly-review",
        },
        "asset_placeholders": placeholders,
        "stages": stages,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapter-json", required=True)
    parser.add_argument("--provider-plan-json", required=True)
    parser.add_argument("--output", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    chapter = load_json(args.chapter_json)
    provider_plan = load_json(args.provider_plan_json)
    payload = build_pipeline(chapter, provider_plan)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": "ok",
        "output": str(output_path),
        "stage_count": payload["pipeline_summary"]["stage_count"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise
