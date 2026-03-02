#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
---
role: 用户本地热迁移脚本，将现有本地 skills 迁移到 Claude Code Plugin 系统
depends:
  - ~/.claude/skills/ (源目录)
  - ~/.claude/plugins/ (目标目录)
  - ~/.claude/settings.json (marketplace 注册)
exports:
  - main()
status: IMPLEMENTED
functions:
  - backup_existing_skills() -> bool
    备份用户现有 skills 目录到 skills.backup.{timestamp}/
    返回备份是否成功

  - register_marketplace() -> bool
    在 ~/.claude/known_marketplaces.json 中注册 infinity-workflows marketplace
    指向 Infinity-light/claude-workflow-kit
    返回注册是否成功

  - install_plugin() -> bool
    调用 Claude Code CLI 安装 workflow-kit plugin
    或提示用户手动执行安装命令
    返回安装是否成功

  - cleanup_old_skills(dry_run: bool) -> list
    清理旧 skills 目录（discovery, planning, execution, diagnosis 等已打包进 plugin 的）
    保留第三方 skills（audio-transcriber 等 symlink）
    dry_run=True 时只列出会删除的文件，不实际删除
    返回清理的文件列表

  - verify_migration() -> dict
    验证迁移结果：
    - marketplace 是否已注册
    - plugin 是否已安装
    - skills 是否可从 plugin 正常加载
    返回验证结果字典

  - main()
    主流程：备份 → 注册 marketplace → 提示安装 → 验证 → 可选清理
    每步都有确认提示，支持 --dry-run 模式
---
"""

import os
import sys
import json
import shutil
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional


# 14个属于 workflow-kit 的 skills
WORKFLOW_KIT_SKILLS = {
    'deploy', 'diagnosis', 'discovery', 'documentation-update',
    'execution', 'key-reader', 'learned', 'planning',
    'skills-updater', 'verification', 'smart-fetch',
    'ui-ux-pro-max', 'frontend-design', 'vue-best-practices'
}

MARKETPLACE_NAME = 'infinity-workflows'
MARKETPLACE_CONFIG = {
    'source': 'github',
    'repo': 'Infinity-light/claude-workflow-kit'
}

PLUGIN_NAME = 'workflow-kit'


def get_claude_dir() -> Path:
    """获取 Claude 配置目录"""
    home = Path.home()
    return home / '.claude'


def get_skills_dir() -> Path:
    """获取 skills 目录"""
    return get_claude_dir() / 'skills'


def get_plugins_dir() -> Path:
    """获取 plugins 目录"""
    return get_claude_dir() / 'plugins'


def log_info(message: str):
    """输出信息日志"""
    print(f'[INFO] {message}')


def log_warn(message: str):
    """输出警告日志"""
    print(f'[WARN] {message}', file=sys.stderr)


def log_error(message: str):
    """输出错误日志"""
    print(f'[ERROR] {message}', file=sys.stderr)


def log_success(message: str):
    """输出成功日志"""
    print(f'[OK] {message}')


def confirm(prompt: str, default: bool = True) -> bool:
    """询问用户确认，返回用户选择"""
    suffix = '[Y/n]' if default else '[y/N]'
    try:
        response = input(f'{prompt} {suffix}: ').strip().lower()
        if not response:
            return default
        return response in ('y', 'yes')
    except (KeyboardInterrupt, EOFError):
        print()
        log_info("用户取消操作")
        sys.exit(0)


def find_workflow_kit_skills() -> List[str]:
    """
    检测 ~/.claude/skills/ 中哪些属于 workflow-kit（14个 skills）
    返回找到的 skill 名称列表
    """
    skills_dir = get_skills_dir()
    found_skills = []

    if not skills_dir.exists():
        log_info(f"Skills 目录不存在: {skills_dir}")
        return found_skills

    for item in skills_dir.iterdir():
        if item.is_dir() and item.name in WORKFLOW_KIT_SKILLS:
            found_skills.append(item.name)

    return found_skills


def backup_existing_skills() -> bool:
    """
    备份用户现有 skills 目录到 skills.backup.{timestamp}/
    只备份属于 workflow-kit 的 skills
    返回备份是否成功
    """
    skills_dir = get_skills_dir()
    if not skills_dir.exists():
        log_info("Skills 目录不存在，无需备份")
        return True

    found_skills = find_workflow_kit_skills()
    if not found_skills:
        log_info("未发现属于 workflow-kit 的 skills，无需备份")
        return True

    log_info(f"发现 {len(found_skills)} 个 workflow-kit skills: {', '.join(found_skills)}")

    # 创建备份目录
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = get_claude_dir() / f'skills.backup.{timestamp}'

    try:
        backup_dir.mkdir(parents=True, exist_ok=True)
        log_info(f"创建备份目录: {backup_dir}")

        for skill_name in found_skills:
            src = skills_dir / skill_name
            dst = backup_dir / skill_name

            if src.is_symlink():
                # 复制 symlink 指向的内容
                shutil.copytree(src, dst, symlinks=False)
                log_info(f"备份 skill (解引用 symlink): {skill_name}")
            else:
                shutil.copytree(src, dst, symlinks=True)
                log_info(f"备份 skill: {skill_name}")

        log_success(f"备份完成，共备份 {len(found_skills)} 个 skills 到 {backup_dir}")
        return True

    except Exception as e:
        log_error(f"备份失败: {e}")
        return False


def register_marketplace() -> bool:
    """
    在 ~/.claude/known_marketplaces.json 中注册 infinity-workflows marketplace
    指向 Infinity-light/claude-workflow-kit
    返回注册是否成功
    """
    claude_dir = get_claude_dir()
    marketplace_file = claude_dir / 'known_marketplaces.json'

    # 读取现有配置
    marketplaces = {}
    if marketplace_file.exists():
        try:
            with open(marketplace_file, 'r', encoding='utf-8') as f:
                marketplaces = json.load(f)
            log_info(f"读取现有 marketplace 配置: {marketplace_file}")
        except json.JSONDecodeError as e:
            log_warn(f"marketplace 文件格式错误，将重新创建: {e}")
            marketplaces = {}
        except Exception as e:
            log_error(f"读取 marketplace 文件失败: {e}")
            return False

    # 检查是否已注册
    if MARKETPLACE_NAME in marketplaces:
        existing = marketplaces[MARKETPLACE_NAME]
        if existing.get('source') == MARKETPLACE_CONFIG['source'] and \
           existing.get('repo') == MARKETPLACE_CONFIG['repo']:
            log_success(f"Marketplace '{MARKETPLACE_NAME}' 已注册且配置正确")
            return True
        else:
            log_warn(f"Marketplace '{MARKETPLACE_NAME}' 已存在但配置不同，将更新")

    # 添加/更新 marketplace
    marketplaces[MARKETPLACE_NAME] = MARKETPLACE_CONFIG

    # 保存回文件
    try:
        claude_dir.mkdir(parents=True, exist_ok=True)
        with open(marketplace_file, 'w', encoding='utf-8') as f:
            json.dump(marketplaces, f, indent=2, ensure_ascii=False)
        log_success(f"Marketplace '{MARKETPLACE_NAME}' 注册成功")
        log_info(f"  来源: {MARKETPLACE_CONFIG['source']}")
        log_info(f"  仓库: {MARKETPLACE_CONFIG['repo']}")
        return True
    except Exception as e:
        log_error(f"保存 marketplace 配置失败: {e}")
        return False


def is_claude_cli_available() -> bool:
    """检查 claude CLI 是否可用"""
    try:
        result = subprocess.run(
            ['claude', '--version'],
            capture_output=True,
            timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def install_plugin() -> Optional[bool]:
    """
    调用 Claude Code CLI 安装 workflow-kit plugin
    或提示用户手动执行安装命令
    返回安装是否成功（用户手动安装时返回 None 表示未知）
    """
    command = f"claude plugin install {PLUGIN_NAME}@{MARKETPLACE_NAME}"

    if is_claude_cli_available():
        log_info("检测到 Claude CLI 可用，尝试自动安装...")
        try:
            result = subprocess.run(
                ['claude', 'plugin', 'install', f'{PLUGIN_NAME}@{MARKETPLACE_NAME}'],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                log_success(f"Plugin '{PLUGIN_NAME}' 安装成功")
                return True
            else:
                log_warn(f"自动安装失败: {result.stderr}")
                log_info("请手动运行以下命令安装:")
                print(f"\n  {command}\n")
                return False
        except subprocess.TimeoutExpired:
            log_warn("安装命令超时")
            log_info("请手动运行以下命令安装:")
            print(f"\n  {command}\n")
            return False
        except Exception as e:
            log_warn(f"自动安装出错: {e}")
            log_info("请手动运行以下命令安装:")
            print(f"\n  {command}\n")
            return False
    else:
        log_info("未检测到 Claude CLI，请手动安装 plugin")
        print(f"\n请运行以下命令安装:")
        print(f"  {command}\n")

        if confirm("是否已手动安装完成?", default=False):
            return True
        else:
            log_info("请在安装完成后重新运行此脚本进行验证")
            return None


def cleanup_old_skills(dry_run: bool = False) -> List[str]:
    """
    清理旧 skills 目录（只删除属于 workflow-kit 的14个）
    保留其他 skills（如 audio-transcriber 等 symlink）
    dry_run=True 时只列出不删除
    返回清理的文件列表
    """
    skills_dir = get_skills_dir()
    cleaned = []

    if not skills_dir.exists():
        log_info("Skills 目录不存在，无需清理")
        return cleaned

    found_skills = find_workflow_kit_skills()
    if not found_skills:
        log_info("未发现需要清理的 workflow-kit skills")
        return cleaned

    if dry_run:
        log_info("[DRY RUN] 以下 skills 将被清理:")
    else:
        log_info(f"准备清理 {len(found_skills)} 个 workflow-kit skills...")

    for skill_name in found_skills:
        skill_path = skills_dir / skill_name

        if dry_run:
            log_info(f"  [DRY RUN] 将删除: {skill_name}")
            cleaned.append(str(skill_path))
            continue

        try:
            if skill_path.is_symlink():
                skill_path.unlink()
                log_info(f"删除 symlink: {skill_name}")
            else:
                shutil.rmtree(skill_path)
                log_info(f"删除目录: {skill_name}")
            cleaned.append(str(skill_path))
        except Exception as e:
            log_error(f"删除失败 {skill_name}: {e}")

    if dry_run:
        log_info(f"[DRY RUN] 共 {len(cleaned)} 个 skills 将被清理")
    else:
        log_success(f"清理完成，共删除 {len(cleaned)} 个 skills")

    return cleaned


def verify_migration() -> Dict[str, Any]:
    """
    验证迁移结果：
    - marketplace 是否已注册
    - plugin 是否已安装（通过检查 installed_plugins.json）
    返回验证结果字典
    """
    result = {
        'marketplace_registered': False,
        'plugin_installed': False,
        'errors': []
    }

    # 检查 marketplace 是否已注册
    marketplace_file = get_claude_dir() / 'known_marketplaces.json'
    if marketplace_file.exists():
        try:
            with open(marketplace_file, 'r', encoding='utf-8') as f:
                marketplaces = json.load(f)
            if MARKETPLACE_NAME in marketplaces:
                config = marketplaces[MARKETPLACE_NAME]
                if (config.get('source') == MARKETPLACE_CONFIG['source'] and
                    config.get('repo') == MARKETPLACE_CONFIG['repo']):
                    result['marketplace_registered'] = True
                else:
                    result['errors'].append('Marketplace 配置不匹配')
            else:
                result['errors'].append(f"Marketplace '{MARKETPLACE_NAME}' 未注册")
        except Exception as e:
            result['errors'].append(f'读取 marketplace 配置失败: {e}')
    else:
        result['errors'].append('Marketplace 配置文件不存在')

    # 检查 plugin 是否已安装
    plugins_dir = get_plugins_dir()
    plugin_dir = plugins_dir / PLUGIN_NAME

    if plugin_dir.exists():
        # 检查 plugin.json 是否存在
        plugin_json = plugin_dir / '.claude-plugin' / 'plugin.json'
        if plugin_json.exists():
            try:
                with open(plugin_json, 'r', encoding='utf-8') as f:
                    plugin_config = json.load(f)
                if plugin_config.get('name') == PLUGIN_NAME:
                    result['plugin_installed'] = True
                    result['plugin_version'] = plugin_config.get('version', 'unknown')
                else:
                    result['errors'].append('Plugin 名称不匹配')
            except Exception as e:
                result['errors'].append(f'读取 plugin 配置失败: {e}')
        else:
            # 检查 installed_plugins.json
            installed_file = get_claude_dir() / 'installed_plugins.json'
            if installed_file.exists():
                try:
                    with open(installed_file, 'r', encoding='utf-8') as f:
                        installed = json.load(f)
                    if PLUGIN_NAME in installed.get('plugins', []):
                        result['plugin_installed'] = True
                    else:
                        result['errors'].append(f"Plugin '{PLUGIN_NAME}' 未在已安装列表中")
                except Exception as e:
                    result['errors'].append(f'读取已安装 plugins 失败: {e}')
            else:
                result['errors'].append('Plugin 配置文件不存在')
    else:
        result['errors'].append(f'Plugin 目录不存在: {plugin_dir}')

    return result


def print_welcome():
    """打印欢迎信息"""
    print("\n" + "=" * 60)
    print("  Claude Workflow Kit 热迁移工具")
    print("=" * 60)
    print()
    print("此工具将帮助您将现有的 workflow-kit skills 迁移到")
    print("Claude Code Plugin 系统。")
    print()
    print("迁移流程:")
    print("  1. 备份现有 workflow-kit skills")
    print("  2. 注册 infinity-workflows marketplace")
    print("  3. 安装 workflow-kit plugin")
    print("  4. 验证迁移结果")
    print("  5. 可选：清理旧的 skills")
    print()
    print("按 Ctrl+C 可随时退出")
    print("=" * 60 + "\n")


def print_summary(verification: Dict[str, Any]):
    """打印迁移结果摘要"""
    print("\n" + "=" * 60)
    print("  迁移结果")
    print("=" * 60)

    if verification['marketplace_registered']:
        log_success("Marketplace 已注册")
    else:
        log_error("Marketplace 未注册")

    if verification['plugin_installed']:
        version = verification.get('plugin_version', 'unknown')
        log_success(f"Plugin 已安装 (版本: {version})")
    else:
        log_error("Plugin 未安装")

    if verification['errors']:
        print()
        log_error("发现以下问题:")
        for error in verification['errors']:
            print(f"  - {error}")

    print("=" * 60 + "\n")


def main():
    """
    主流程：备份 → 注册 marketplace → 提示安装 → 验证 → 可选清理
    每步都有确认提示，支持 --dry-run 模式
    """
    parser = argparse.ArgumentParser(
        description='Claude Workflow Kit 热迁移工具'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='模拟运行，不实际执行修改操作'
    )
    parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help='自动确认所有提示'
    )
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='迁移完成后自动清理旧 skills'
    )

    args = parser.parse_args()

    try:
        print_welcome()

        # 步骤 1: 备份
        log_info("步骤 1/4: 备份现有 skills")
        if args.dry_run:
            log_info("[DRY RUN] 将备份以下 skills:")
            skills = find_workflow_kit_skills()
            for skill in skills:
                log_info(f"  - {skill}")
            if not skills:
                log_info("  (无)")
        else:
            if args.yes or confirm("是否开始备份现有 skills?"):
                if not backup_existing_skills():
                    log_error("备份失败，中止迁移")
                    return 1
            else:
                log_info("用户跳过备份")

        # 步骤 2: 注册 marketplace
        print()
        log_info("步骤 2/4: 注册 marketplace")
        if args.dry_run:
            log_info(f"[DRY RUN] 将注册 marketplace: {MARKETPLACE_NAME}")
            log_info(f"  来源: {MARKETPLACE_CONFIG['source']}")
            log_info(f"  仓库: {MARKETPLACE_CONFIG['repo']}")
        else:
            if args.yes or confirm("是否注册 marketplace?"):
                if not register_marketplace():
                    log_error("注册失败，中止迁移")
                    return 1
            else:
                log_info("用户跳过注册")

        # 步骤 3: 安装 plugin
        print()
        log_info("步骤 3/4: 安装 plugin")
        if args.dry_run:
            log_info(f"[DRY RUN] 将提示安装 plugin: {PLUGIN_NAME}@{MARKETPLACE_NAME}")
        else:
            if args.yes or confirm("是否安装 plugin?"):
                install_result = install_plugin()
                if install_result is False:
                    log_error("安装失败，中止迁移")
                    return 1
                # install_result 为 None 表示用户选择手动安装
            else:
                log_info("用户跳过安装")

        # 步骤 4: 验证
        print()
        log_info("步骤 4/4: 验证迁移结果")
        verification = verify_migration()
        print_summary(verification)

        if not verification['plugin_installed']:
            log_warn("Plugin 未正确安装，请检查后重试")
            return 1

        # 可选：清理旧 skills
        if args.cleanup or (not args.dry_run and confirm("是否清理旧的 skills?", default=False)):
            print()
            log_info("清理旧 skills")
            if args.dry_run:
                cleanup_old_skills(dry_run=True)
            else:
                cleanup_old_skills(dry_run=False)

        log_success("迁移完成!")
        return 0

    except KeyboardInterrupt:
        print()
        log_info("用户中断操作")
        return 130
    except Exception as e:
        log_error(f"发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
