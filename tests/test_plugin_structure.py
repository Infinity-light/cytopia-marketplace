#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
---
role: 集成测试骨架，验证 plugin 结构和迁移逻辑
depends:
  - ../.claude-plugin/marketplace.json
  - ../.claude-plugin/plugin.json
  - ../plugins/workflow-kit/
  - ../src/migrate.py
exports: []
status: IMPLEMENTED
functions:
  - test_marketplace_json_exists()
    断言 .claude-plugin/marketplace.json 存在

  - test_marketplace_json_valid()
    断言 marketplace.json 符合 schema（必需字段、格式正确）

  - test_plugin_json_exists()
    断言 plugins/workflow-kit/.claude-plugin/plugin.json 存在

  - test_plugin_json_valid()
    断言 plugin.json 符合 schema

  - test_all_skills_have_skill_md()
    断言14个 skills 都有 SKILL.md 文件

  - test_skill_md_has_frontmatter()
    断言每个 SKILL.md 都包含 frontmatter（--- 包裹的 name 和 description）

  - test_claude_md_exists()
    断言 CLAUDE.md 存在（在 plugin 根目录或根目录）
---
"""

import json
import re
from pathlib import Path
import pytest

# 项目根目录
ROOT = Path(__file__).parent.parent
PLUGIN_ROOT = ROOT / "plugins" / "workflow-kit"

# 期望的14个 skills
WORKFLOW_KIT_SKILLS = [
    "deploy",
    "diagnosis",
    "discovery",
    "documentation-update",
    "execution",
    "key-reader",
    "learned",
    "planning",
    "skills-updater",
    "verification",
    "smart-fetch",
    "ui-ux-pro-max",
    "frontend-design",
    "vue-best-practices",
]


class TestMarketplace:
    """测试 marketplace.json"""

    def test_marketplace_json_exists(self):
        """断言 .claude-plugin/marketplace.json 存在"""
        marketplace_file = ROOT / ".claude-plugin" / "marketplace.json"
        assert marketplace_file.exists(), f"marketplace.json 不存在: {marketplace_file}"

    def test_marketplace_json_valid(self):
        """断言 marketplace.json 符合 schema（必需字段、格式正确）"""
        marketplace_file = ROOT / ".claude-plugin" / "marketplace.json"

        # 能正确解析 JSON
        with open(marketplace_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 必需字段
        assert "name" in data, "marketplace.json 缺少 name 字段"
        assert "owner" in data, "marketplace.json 缺少 owner 字段"
        assert "plugins" in data, "marketplace.json 缺少 plugins 字段"

        # owner 必需有 name
        assert "name" in data["owner"], "marketplace.json owner 缺少 name 字段"

        # plugins 是列表
        assert isinstance(data["plugins"], list), "plugins 应该是列表"
        assert len(data["plugins"]) > 0, "plugins 列表不能为空"

        # 每个 plugin 必需字段
        for i, plugin in enumerate(data["plugins"]):
            assert "name" in plugin, f"plugins[{i}] 缺少 name 字段"
            assert "source" in plugin, f"plugins[{i}] 缺少 source 字段"
            assert "description" in plugin, f"plugins[{i}] 缺少 description 字段"
            assert "version" in plugin, f"plugins[{i}] 缺少 version 字段"


class TestPlugin:
    """测试 plugin.json"""

    def test_plugin_json_exists(self):
        """断言 .claude-plugin/plugin.json 存在"""
        plugin_file = ROOT / ".claude-plugin" / "plugin.json"
        assert plugin_file.exists(), f"plugin.json 不存在: {plugin_file}"

    def test_plugin_json_valid(self):
        """断言 plugin.json 符合 schema"""
        plugin_file = ROOT / ".claude-plugin" / "plugin.json"

        # 能正确解析 JSON
        with open(plugin_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 必需字段
        assert "name" in data, "plugin.json 缺少 name 字段"
        assert "version" in data, "plugin.json 缺少 version 字段"

        # name 应该是 kebab-case
        name = data["name"]
        assert " " not in name, f"plugin name 不能包含空格: {name}"
        assert name == name.lower(), f"plugin name 应该全小写: {name}"


class TestSkills:
    """测试 skills 结构"""

    def test_all_skills_have_skill_md(self):
        """断言14个 skills 都有 SKILL.md 文件"""
        skills_dir = PLUGIN_ROOT / "skills"

        missing_skills = []
        for skill_name in WORKFLOW_KIT_SKILLS:
            skill_file = skills_dir / skill_name / "SKILL.md"
            if not skill_file.exists():
                missing_skills.append(skill_name)

        assert not missing_skills, f"以下 skills 缺少 SKILL.md: {missing_skills}"

    def test_skill_md_has_frontmatter(self):
        """断言每个 SKILL.md 都包含 frontmatter（--- 包裹的 name 和 description）"""
        skills_dir = PLUGIN_ROOT / "skills"

        invalid_skills = []
        for skill_name in WORKFLOW_KIT_SKILLS:
            skill_file = skills_dir / skill_name / "SKILL.md"

            if not skill_file.exists():
                continue

            with open(skill_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 检查是否有 frontmatter
            if not content.startswith("---"):
                invalid_skills.append(f"{skill_name}: 缺少 frontmatter")
                continue

            # 检查是否有 name 和 description
            if "name:" not in content:
                invalid_skills.append(f"{skill_name}: frontmatter 缺少 name")
                continue

            if "description:" not in content:
                invalid_skills.append(f"{skill_name}: frontmatter 缺少 description")
                continue

        assert not invalid_skills, f"以下 skills 格式不正确: {invalid_skills}"


class TestDocumentation:
    """测试文档文件"""

    def test_claude_md_exists(self):
        """断言 CLAUDE.md 存在（在 plugin 根目录或根目录）"""
        root_claude = ROOT / "CLAUDE.md"
        plugin_claude = PLUGIN_ROOT / "CLAUDE.md"

        assert root_claude.exists() or plugin_claude.exists(), "CLAUDE.md 不存在（根目录或 plugin 目录）"

    def test_changelog_exists(self):
        """断言 CHANGELOG.md 存在"""
        changelog = ROOT / "CHANGELOG.md"
        assert changelog.exists(), "CHANGELOG.md 不存在"


class TestScripts:
    """测试脚本文件"""

    def test_migrate_script_exists(self):
        """断言 migrate.py 存在"""
        migrate = ROOT / "src" / "migrate.py"
        assert migrate.exists(), "migrate.py 不存在"

    def test_migrate_script_valid_python(self):
        """断言 migrate.py 是有效的 Python 代码"""
        migrate = ROOT / "src" / "migrate.py"

        # 尝试解析 Python 语法
        with open(migrate, "r", encoding="utf-8") as f:
            code = f.read()

        try:
            compile(code, str(migrate), "exec")
        except SyntaxError as e:
            pytest.fail(f"migrate.py 语法错误: {e}")

    def test_install_script_exists(self):
        """断言 install.sh 存在"""
        install = ROOT / "scripts" / "install.sh"
        assert install.exists(), "install.sh 不存在"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
