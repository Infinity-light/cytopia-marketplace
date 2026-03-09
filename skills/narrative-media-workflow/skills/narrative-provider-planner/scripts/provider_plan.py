#!/usr/bin/env python3
"""Safe provider planning for narrative media dry runs."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, Tuple

DEFAULTS = {
    "ark": {
        "roles": ["text", "image", "video"],
        "models": {
            "text": "doubao-seed-2-0-pro-260215",
            "image": "doubao-seedream-4-5-251128",
            "video": "doubao-seedance-1-5-pro-251215",
        },
        "keys": ["ARK_API_KEY", "VOLCENGINE_API_KEY"],
    },
    "fal": {
        "roles": ["audio"],
        "models": {
            "audio": "fal-ai/index-tts-2/text-to-speech",
        },
        "keys": ["FAL_KEY", "FAL_API_KEY"],
    },
    "deepseek": {
        "roles": ["text_supplement"],
        "models": {
            "text_supplement": "openai-compatible:deepseek",
        },
        "keys": ["DEEPSEEK_API_KEY", "OPENAI_API_KEY"],
    },
}

SENSITIVE_RE = re.compile(r"(KEY|TOKEN|SECRET|PASSWORD)", re.IGNORECASE)


def load_env_file(path: Path) -> Dict[str, str]:
    data: Dict[str, str] = {}
    if not path.exists():
        raise FileNotFoundError(f"Env file not found: {path}")
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    return data


def masked_presence(keys: Iterable[str], file_values: Dict[str, str]) -> Tuple[bool, list[dict]]:
    evidence = []
    present = False
    for key in keys:
        env_has = bool(os.getenv(key))
        file_has = bool(file_values.get(key))
        key_present = env_has or file_has
        present = present or key_present
        evidence.append({
            "key": key,
            "present": key_present,
            "source": "env" if env_has else "env-file" if file_has else "missing",
            "masked": bool(SENSITIVE_RE.search(key)),
        })
    return present, evidence


def build_plan(file_values: Dict[str, str], required: set[str]) -> dict:
    providers = {}
    fallback_steps = []
    for provider_name, config in DEFAULTS.items():
        present, evidence = masked_presence(config["keys"], file_values)
        providers[provider_name] = {
            "available": present,
            "required": provider_name in required,
            "roles": config["roles"],
            "models": config["models"],
            "evidence": evidence,
            "mode": "live-capable" if present else "dry-run-only",
        }
        if not present:
            fallback_steps.append(
                f"{provider_name}: keep placeholder outputs and require human/external follow-up"
            )

    return {
        "workflow": "narrative-provider-planner",
        "dry_run": True,
        "provider_defaults": providers,
        "global_defaults": {
            "text_primary": DEFAULTS["ark"]["models"]["text"],
            "image_primary": DEFAULTS["ark"]["models"]["image"],
            "video_primary": DEFAULTS["ark"]["models"]["video"],
            "audio_primary": DEFAULTS["fal"]["models"]["audio"],
            "text_supplement_only": DEFAULTS["deepseek"]["models"]["text_supplement"],
        },
        "policy": {
            "secret_handling": "presence-only",
            "deepseek_usage": "text supplement only",
            "remote_generation": "disabled in dry-run",
        },
        "fallback_steps": fallback_steps,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--env-file")
    parser.add_argument("--require", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    file_values = load_env_file(Path(args.env_file)) if args.env_file else {}
    required = {item.strip() for item in args.require.split(",") if item.strip()}
    payload = build_plan(file_values, required)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": "ok",
        "output": str(output_path),
        "available": {name: cfg["available"] for name, cfg in payload["provider_defaults"].items()},
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise
