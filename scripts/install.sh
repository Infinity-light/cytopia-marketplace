#!/bin/bash
# ---
# role: 一键安装脚本，用户 curl 下载后直接运行完成 marketplace 添加和 plugin 安装
# depends:
#   - curl
#   - claude CLI
# exports: []
# status: IMPLEMENTED
# functions:
#   - check_claude_installed() -> bool
#     检查 claude 命令是否可用
#     返回是否已安装
#
#   - download_migrate_script() -> Path
#     从 GitHub 下载 migrate.py 到临时目录
#     返回下载的文件路径
#
#   - run_migration() -> bool
#     执行 migrate.py 完成 marketplace 注册
#     返回是否成功
#
#   - install_plugin() -> bool
#     调用 claude plugin install 安装 workflow-kit
#     处理安装成功/失败情况
#     返回是否成功
#
#   - print_success_message()
#     输出安装成功后的操作指南
#     包括如何验证、如何更新、如何卸载
# ---

set -e

# 配置
MARKETPLACE_URL="https://github.com/Infinity-light/claude-workflow-kit"
PLUGIN_NAME="workflow-kit"
MARKETPLACE_NAME="infinity-workflows"
MIGRATE_SCRIPT_URL="https://raw.githubusercontent.com/Infinity-light/claude-workflow-kit/main/src/migrate.py"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_banner() {
    echo ""
    echo "========================================="
    echo "  Claude Workflow Kit 一键安装脚本"
    echo "========================================="
    echo ""
    echo "此脚本将:"
    echo "  1. 检查 Claude Code 是否已安装"
    echo "  2. 下载并运行热迁移工具"
    echo "  3. 安装 workflow-kit plugin"
    echo ""
    echo "按 Ctrl+C 可随时退出"
    echo "========================================="
    echo ""
}

check_claude_installed() {
    log_info "检查 Claude Code CLI..."
    if command -v claude &> /dev/null; then
        local version
        version=$(claude --version 2>/dev/null || echo "unknown")
        log_success "Claude Code 已安装 (版本: $version)"
        return 0
    else
        log_error "Claude Code CLI 未安装"
        echo ""
        echo "请先安装 Claude Code:"
        echo "  npm install -g @anthropic-ai/claude-code"
        echo ""
        echo "或访问: https://docs.anthropic.com/en/docs/claude-code/install"
        echo ""
        return 1
    fi
}

download_migrate_script() {
    local temp_dir
    temp_dir=$(mktemp -d)
    local migrate_script="$temp_dir/migrate.py"

    log_info "下载热迁移脚本..."

    if command -v curl &> /dev/null; then
        curl -fsSL "$MIGRATE_SCRIPT_URL" -o "$migrate_script" 2>/dev/null || {
            log_error "下载失败，请检查网络连接"
            rm -rf "$temp_dir"
            return 1
        }
    elif command -v wget &> /dev/null; then
        wget -q "$MIGRATE_SCRIPT_URL" -O "$migrate_script" 2>/dev/null || {
            log_error "下载失败，请检查网络连接"
            rm -rf "$temp_dir"
            return 1
        }
    else
        log_error "需要 curl 或 wget 来下载脚本"
        rm -rf "$temp_dir"
        return 1
    fi

    log_success "下载完成"
    echo "$migrate_script"
}

run_migration() {
    local migrate_script="$1"

    log_info "运行热迁移脚本..."
    echo ""

    python3 "$migrate_script" --yes || {
        log_error "热迁移失败"
        return 1
    }

    log_success "热迁移完成"
    return 0
}

install_plugin() {
    log_info "安装 workflow-kit plugin..."

    if claude plugin install "${PLUGIN_NAME}@${MARKETPLACE_NAME}"; then
        log_success "Plugin 安装成功"
        return 0
    else
        log_error "Plugin 安装失败"
        return 1
    fi
}

print_success_message() {
    echo ""
    echo "========================================="
    echo "  安装成功!"
    echo "========================================="
    echo ""
    echo "Workflow Kit Plugin 已安装完成。"
    echo ""
    echo "使用方法:"
    echo "  1. 重启 Claude Code"
    echo "  2. 使用技能: /workflow-kit:discovery"
    echo "              /workflow-kit:planning"
    echo "              /workflow-kit:execution"
    echo "              ..."
    echo ""
    echo "常用命令:"
    echo "  查看已安装 plugins:"
    echo "    claude plugin list"
    echo ""
    echo "  更新 plugin:"
    echo "    claude plugin update ${PLUGIN_NAME}"
    echo ""
    echo "  卸载 plugin:"
    echo "    claude plugin uninstall ${PLUGIN_NAME}"
    echo ""
    echo "  回滚到旧版本:"
    echo "    python3 ~/.claude/skills.backup.*/restore.py"
    echo ""
    echo "========================================="
}

main() {
    print_banner

    # 检查依赖
    if ! check_claude_installed; then
        exit 1
    fi

    # 下载迁移脚本
    local migrate_script
    migrate_script=$(download_migrate_script) || exit 1

    # 运行迁移
    if ! run_migration "$migrate_script"; then
        rm -f "$migrate_script"
        exit 1
    fi

    # 清理临时文件
    rm -f "$migrate_script"

    # 安装 plugin
    if ! install_plugin; then
        log_warn "自动安装失败，请手动运行:"
        echo "  claude plugin install ${PLUGIN_NAME}@${MARKETPLACE_NAME}"
        exit 1
    fi

    # 输出成功信息
    print_success_message

    exit 0
}

# 处理中断
trap 'log_error "安装被中断"; exit 130' INT

main "$@"
