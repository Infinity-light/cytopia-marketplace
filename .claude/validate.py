#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
契约验证脚本 - Planning 阶段检查骨架完整性
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

def check_file_exists(rel_path, description):
    """检查文件是否存在"""
    full_path = ROOT / rel_path
    if full_path.exists():
        print(f"  [OK] {rel_path} ({description})")
        return True
    else:
        print(f"  [FAIL] {rel_path} ({description}) - 文件不存在")
        return False

def validate_marketplace_json():
    """验证 marketplace.json 格式"""
    path = ROOT / ".claude-plugin" / "marketplace.json"
    if not path.exists():
        return False, ["marketplace.json 不存在"]

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"marketplace.json JSON 解析错误: {e}"]

    errors = []
    required = ["name", "owner", "plugins"]
    for field in required:
        if field not in data:
            errors.append(f"marketplace.json 缺少必需字段: {field}")

    if "owner" in data and "name" not in data.get("owner", {}):
        errors.append("marketplace.json owner 缺少 name 字段")

    if "plugins" in data:
        for i, plugin in enumerate(data["plugins"]):
            plugin_required = ["name", "source", "description", "version"]
            for field in plugin_required:
                if field not in plugin:
                    errors.append(f"plugins[{i}] 缺少 {field}")

    return len(errors) == 0, errors

def validate_plugin_json():
    """验证 plugin.json 格式"""
    path = ROOT / ".claude-plugin" / "plugin.json"
    if not path.exists():
        return False, ["plugin.json 不存在"]

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"plugin.json JSON 解析错误: {e}"]

    errors = []
    required = ["name", "version"]
    for field in required:
        if field not in data:
            errors.append(f"plugin.json 缺少必需字段: {field}")

    return len(errors) == 0, errors

def main():
    print("=" * 60)
    print("Planning Validation: Workflow Kit Plugin Skeleton Check")
    print("=" * 60)

    errors = []

    # 检查核心配置文件
    print("\n[1/4] 检查核心配置文件...")
    files = [
        (".claude-plugin/marketplace.json", "Marketplace 清单"),
        (".claude-plugin/plugin.json", "Plugin 元数据"),
    ]
    for rel_path, desc in files:
        if not check_file_exists(rel_path, desc):
            errors.append(f"缺少文件: {rel_path}")

    # 验证 marketplace.json 格式
    print("\n[2/4] Validate marketplace.json format...")
    ok, errs = validate_marketplace_json()
    if ok:
        print("  [OK] marketplace.json format correct")
    else:
        for e in errs:
            print(f"  [FAIL] {e}")
            errors.append(e)

    # 验证 plugin.json 格式
    print("\n[3/4] Validate plugin.json format...")
    ok, errs = validate_plugin_json()
    if ok:
        print("  [OK] plugin.json format correct")
    else:
        for e in errs:
            print(f"  [FAIL] {e}")
            errors.append(e)

    # 检查脚本文件
    print("\n[4/4] 检查脚本和测试骨架...")
    script_files = [
        ("src/migrate.py", "热迁移脚本"),
        ("scripts/install.sh", "一键安装脚本"),
        ("tests/test_plugin_structure.py", "测试骨架"),
        (".claude/validate.py", "验证脚本自身"),
        ("CHANGELOG.md", "版本日志"),
    ]
    for rel_path, desc in script_files:
        if not check_file_exists(rel_path, desc):
            errors.append(f"缺少文件: {rel_path}")

    # 总结
    print("\n" + "=" * 60)
    if errors:
        print(f"[FAIL] Validation failed: {len(errors)} errors")
        for e in errors:
            print(f"  ERROR: {e}")
        sys.exit(1)
    else:
        print("[OK] Validation passed! All contract files exist and format correct")
        print("\nFiles:")
        print("  - .claude-plugin/marketplace.json")
        print("  - .claude-plugin/plugin.json")
        print("  - src/migrate.py")
        print("  - scripts/install.sh")
        print("  - tests/test_plugin_structure.py")
        print("  - .claude/validate.py")
        print("  - CHANGELOG.md")
        sys.exit(0)

if __name__ == "__main__":
    main()
