#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Deploy 前数据库迁移护栏预检脚本。"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import List, Tuple


DB_PATH_PATTERNS = [
    re.compile(r"(^|/)(db|database|schema|sql)(/|$)", re.IGNORECASE),
    re.compile(r"(^|/)migrations?(/|$)", re.IGNORECASE),
    re.compile(r"(^|/)(alembic|flyway|liquibase)(/|$)", re.IGNORECASE),
    re.compile(r"(^|/).*\.sql$", re.IGNORECASE),
    re.compile(r"(^|/).*schema.*\.(sql|json|yaml|yml|prisma)$", re.IGNORECASE),
]

DB_DIFF_KEYWORDS = [
    re.compile(r"\bCREATE\s+TABLE\b", re.IGNORECASE),
    re.compile(r"\bALTER\s+TABLE\b", re.IGNORECASE),
    re.compile(r"\bCREATE\s+INDEX\b", re.IGNORECASE),
    re.compile(r"\bDROP\s+TABLE\b", re.IGNORECASE),
    re.compile(r"\bDROP\s+COLUMN\b", re.IGNORECASE),
    re.compile(r"\bTRUNCATE\b", re.IGNORECASE),
    re.compile(r"\bRENAME\s+COLUMN\b", re.IGNORECASE),
    re.compile(r"\bADD\s+COLUMN\b", re.IGNORECASE),
]

DESTRUCTIVE_DDL_PATTERNS = [
    re.compile(r"\bDROP\s+TABLE\b", re.IGNORECASE),
    re.compile(r"\bDROP\s+COLUMN\b", re.IGNORECASE),
    re.compile(r"\bTRUNCATE\b", re.IGNORECASE),
    re.compile(r"\bRENAME\s+COLUMN\b", re.IGNORECASE),
    re.compile(r"\bALTER\s+TABLE\b[\s\S]*?\bDROP\s+COLUMN\b", re.IGNORECASE),
]

ROLLBACK_PATTERNS = [
    re.compile(r"\bdown\s*\(", re.IGNORECASE),
    re.compile(r"\brollback\b", re.IGNORECASE),
    re.compile(r"\brevert\b", re.IGNORECASE),
    re.compile(r"\bdown\.sql\b", re.IGNORECASE),
    re.compile(r"\bundo\b", re.IGNORECASE),
]

BACKUP_PLAN_PATTERNS = [
    re.compile(r"migration[-_ ]plan", re.IGNORECASE),
    re.compile(r"\bbackup\b", re.IGNORECASE),
    re.compile(r"\brunbook\b", re.IGNORECASE),
    re.compile(r"\brestore\b", re.IGNORECASE),
]


def run_git_diff(repo: Path, since_ref: str) -> Tuple[List[str], str, bool]:
    cmd_files = ["git", "-C", str(repo), "diff", "--name-only", since_ref, "--"]
    cmd_patch = ["git", "-C", str(repo), "diff", since_ref, "--"]

    files_proc = subprocess.run(cmd_files, capture_output=True, text=True)
    patch_proc = subprocess.run(cmd_patch, capture_output=True, text=True)

    if files_proc.returncode != 0 or patch_proc.returncode != 0:
        return [], "", False

    files = [line.strip().replace("\\", "/") for line in files_proc.stdout.splitlines() if line.strip()]
    return files, patch_proc.stdout or "", True


def fallback_scan_files(repo: Path) -> List[str]:
    ignored_dirs = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__"}
    files: List[str] = []
    for p in repo.rglob("*"):
        if not p.is_file():
            continue
        if any(part in ignored_dirs for part in p.parts):
            continue
        try:
            rel = p.relative_to(repo).as_posix()
        except Exception:
            rel = p.as_posix()
        files.append(rel)
    return files


def match_any(patterns: List[re.Pattern], text: str) -> bool:
    return any(p.search(text) for p in patterns)


def collect_db_signals(files: List[str], diff_text: str) -> List[str]:
    signals: List[str] = []

    matched_files = [f for f in files if any(p.search(f) for p in DB_PATH_PATTERNS)]
    for f in matched_files[:20]:
        signals.append(f"db-path:{f}")
    if len(matched_files) > 20:
        signals.append(f"db-path:+{len(matched_files) - 20} more")

    for p in DB_DIFF_KEYWORDS:
        m = p.search(diff_text)
        if m:
            signals.append(f"ddl-keyword:{m.group(0).upper()}")

    deduped = []
    seen = set()
    for s in signals:
        if s in seen:
            continue
        seen.add(s)
        deduped.append(s)
    return deduped


def evaluate_guardrail(files: List[str], diff_text: str, used_git_diff: bool, deploy_intent: bool) -> dict:
    reasons: List[str] = []
    signals = collect_db_signals(files, diff_text)
    has_risk_signal = len(signals) > 0

    if not deploy_intent:
        reasons.append("未声明 deploy intent（--deploy-intent 未设置），跳过数据库迁移护栏。")
        return {"status": "SKIP", "reasons": reasons, "signals": signals}

    if not has_risk_signal:
        reasons.append("未检测到数据库变更风险信号，跳过数据库迁移护栏。")
        return {"status": "SKIP", "reasons": reasons, "signals": signals}

    rollback_text_space = "\n".join(files) + "\n" + diff_text
    has_rollback = match_any(ROLLBACK_PATTERNS, rollback_text_space)
    has_destructive = match_any(DESTRUCTIVE_DDL_PATTERNS, diff_text)
    has_backup_plan = match_any(BACKUP_PLAN_PATTERNS, rollback_text_space)

    if not used_git_diff:
        reasons.append("git diff 获取失败，已降级为仓库文件名扫描，结论保守。")

    if has_destructive:
        reasons.append("检测到潜在破坏性 DDL（如 DROP/TRUNCATE/RENAME COLUMN）。")
    if not has_rollback:
        reasons.append("未发现明确回滚证据（down/rollback/revert/down.sql）。")
    if not has_backup_plan:
        reasons.append("未发现备份或迁移计划证据（migration-plan/backup/runbook）。")

    if has_destructive and (not has_rollback or not has_backup_plan):
        status = "BLOCK"
        reasons.append("高风险迁移缺少关键保障：中止 deploy，先补齐回滚与备份方案。")
    elif (not has_rollback) or (not has_backup_plan):
        status = "WARN"
        reasons.append("存在迁移风险保障缺口，建议补齐后再 deploy。")
    else:
        status = "PASS"
        reasons.append("检测到数据库变更风险信号，但回滚与备份证据齐全，可继续 deploy。")

    return {"status": status, "reasons": reasons, "signals": signals}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deploy 前数据库迁移护栏预检")
    parser.add_argument("--repo", default=".", help="仓库路径，默认当前目录")
    parser.add_argument("--deploy-intent", action="store_true", help="声明当前为 deploy 前置检查")
    parser.add_argument("--since-ref", default="HEAD~1", help="git diff 起始引用，默认 HEAD~1")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).resolve()

    files, diff_text, used_git_diff = run_git_diff(repo, args.since_ref)
    if not used_git_diff:
        files = fallback_scan_files(repo)
        diff_text = ""

    result = evaluate_guardrail(
        files=files,
        diff_text=diff_text,
        used_git_diff=used_git_diff,
        deploy_intent=args.deploy_intent,
    )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"status: {result['status']}")
        print("reasons:")
        for r in result["reasons"]:
            print(f"- {r}")
        print("signals:")
        for s in result["signals"]:
            print(f"- {s}")

    return 2 if result["status"] == "BLOCK" else 0


if __name__ == "__main__":
    raise SystemExit(main())
