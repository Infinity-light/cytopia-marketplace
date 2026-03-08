#!/usr/bin/env python3
"""
Check Claude plugin local installation state.

This script inspects installed_plugins.json, known_marketplaces.json, cache paths,
and optional content anchors for a Claude plugin installation.

Examples:
    # Marketplace name is an input, not a hard-coded constant.
    python -X utf8 check_local_plugin_state.py --plugin workflow-kit --marketplace cytopia-workflow
    python -X utf8 check_local_plugin_state.py --plugin workflow-kit --marketplace cytopia-workflow --anchor-file skills/plugin-publisher/SKILL.md
    python -X utf8 check_local_plugin_state.py --plugin workflow-kit --marketplace cytopia-workflow --anchor-text "# Plugin Publisher"
    python -X utf8 check_local_plugin_state.py --plugin workflow-kit --marketplace <your-marketplace-name> --json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class CheckResult:
    plugin: str
    marketplace: str
    plugin_key: str
    plugins_dir: str
    installed_plugins_path: str
    known_marketplaces_path: str
    installed_entry_found: bool
    marketplace_known: bool
    installed_version: Optional[str]
    install_path: Optional[str]
    install_path_exists: bool
    cache_version_dir_exists: bool
    git_commit_sha: Optional[str]
    anchor_file: Optional[str]
    anchor_file_exists: bool
    anchor_text: Optional[str]
    anchor_text_found: bool
    inspected_files: List[str]
    warnings: List[str]


def get_plugins_dir() -> Path:
    return Path.home() / ".claude" / "plugins"


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def normalize_installed_entry(raw_entry: Any) -> Optional[Dict[str, Any]]:
    if isinstance(raw_entry, list):
        if not raw_entry:
            return None
        first = raw_entry[0]
        return first if isinstance(first, dict) else None
    if isinstance(raw_entry, dict):
        return raw_entry
    return None


def resolve_install_path(entry: Optional[Dict[str, Any]]) -> Optional[Path]:
    if not entry:
        return None
    install_path = entry.get("installPath")
    if not install_path or not isinstance(install_path, str):
        return None
    return Path(install_path).expanduser()


def check_anchor_text(install_path: Path, anchor_text: str) -> bool:
    for path in install_path.rglob("*"):
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if anchor_text in content:
            return True
    return False


def inspect_plugin_state(
    plugin: str,
    marketplace: str,
    anchor_file: Optional[str] = None,
    anchor_text: Optional[str] = None,
) -> CheckResult:
    plugins_dir = get_plugins_dir()
    installed_plugins_path = plugins_dir / "installed_plugins.json"
    known_marketplaces_path = plugins_dir / "known_marketplaces.json"
    plugin_key = f"{plugin}@{marketplace}"

    installed = load_json(installed_plugins_path, {"version": 2, "plugins": {}})
    marketplaces = load_json(known_marketplaces_path, {})

    raw_entry = installed.get("plugins", {}).get(plugin_key)
    entry = normalize_installed_entry(raw_entry)
    install_path = resolve_install_path(entry)

    install_path_exists = bool(install_path and install_path.exists())
    cache_version_dir_exists = install_path_exists

    anchor_file_exists = False
    inspected_files: List[str] = []
    if install_path:
        inspected_files.append(str(install_path))

    if anchor_file and install_path:
        anchor_target = install_path / anchor_file
        inspected_files.append(str(anchor_target))
        anchor_file_exists = anchor_target.exists()

    anchor_text_found = False
    if anchor_text and install_path and install_path_exists:
        anchor_text_found = check_anchor_text(install_path, anchor_text)

    warnings: List[str] = []
    if not installed_plugins_path.exists():
        warnings.append("installed_plugins.json not found")
    if not known_marketplaces_path.exists():
        warnings.append("known_marketplaces.json not found")
    if raw_entry is not None and entry is None:
        warnings.append("installed plugin entry has an unexpected shape")
    if entry and not install_path:
        warnings.append("installPath missing from installed entry")
    if install_path and not install_path_exists:
        warnings.append("installPath recorded but directory does not exist")
    if anchor_file and install_path_exists and not anchor_file_exists:
        warnings.append("anchor file not found in installed payload")
    if anchor_text and install_path_exists and not anchor_text_found:
        warnings.append("anchor text not found in installed payload")
    if marketplace not in marketplaces:
        warnings.append("marketplace not found in known_marketplaces.json")

    return CheckResult(
        plugin=plugin,
        marketplace=marketplace,
        plugin_key=plugin_key,
        plugins_dir=str(plugins_dir),
        installed_plugins_path=str(installed_plugins_path),
        known_marketplaces_path=str(known_marketplaces_path),
        installed_entry_found=entry is not None,
        marketplace_known=marketplace in marketplaces,
        installed_version=entry.get("version") if entry else None,
        install_path=str(install_path) if install_path else None,
        install_path_exists=install_path_exists,
        cache_version_dir_exists=cache_version_dir_exists,
        git_commit_sha=entry.get("gitCommitSha") if entry else None,
        anchor_file=anchor_file,
        anchor_file_exists=anchor_file_exists,
        anchor_text=anchor_text,
        anchor_text_found=anchor_text_found,
        inspected_files=inspected_files,
        warnings=warnings,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect Claude plugin local install state")
    parser.add_argument("--plugin", required=True, help="Plugin name, for example workflow-kit")
    parser.add_argument(
        "--marketplace",
        required=True,
        help="Marketplace name to inspect, for example cytopia-workflow or another installed marketplace name",
    )
    parser.add_argument(
        "--anchor-file",
        help="Relative path inside installPath that should exist, for example skills/plugin-publisher/SKILL.md",
    )
    parser.add_argument(
        "--anchor-text",
        help="Unique text anchor that should be found somewhere inside installPath",
    )
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    return parser


def print_human(result: CheckResult) -> None:
    print("Claude Plugin Local State")
    print("=" * 28)
    print(f"Plugin key: {result.plugin_key}")
    print(f"Plugins dir: {result.plugins_dir}")
    print(f"Installed entry found: {'yes' if result.installed_entry_found else 'no'}")
    print(f"Marketplace known: {'yes' if result.marketplace_known else 'no'}")
    print(f"Installed version: {result.installed_version or 'unknown'}")
    print(f"Install path: {result.install_path or 'missing'}")
    print(f"Install path exists: {'yes' if result.install_path_exists else 'no'}")
    print(f"Cache version dir exists: {'yes' if result.cache_version_dir_exists else 'no'}")
    print(f"Git commit SHA: {result.git_commit_sha or 'unknown'}")

    if result.anchor_file:
        print(f"Anchor file: {result.anchor_file}")
        print(f"Anchor file exists: {'yes' if result.anchor_file_exists else 'no'}")

    if result.anchor_text:
        print(f"Anchor text: {result.anchor_text}")
        print(f"Anchor text found: {'yes' if result.anchor_text_found else 'no'}")

    if result.inspected_files:
        print("Inspected paths:")
        for path in result.inspected_files:
            print(f"- {path}")

    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"- {warning}")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    result = inspect_plugin_state(
        plugin=args.plugin,
        marketplace=args.marketplace,
        anchor_file=args.anchor_file,
        anchor_text=args.anchor_text,
    )

    if args.json:
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        print_human(result)

    return 0


if __name__ == "__main__":
    sys.exit(main())
