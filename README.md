# Cytopia Workflow

Cytopia 企业级 Claude Code 工作流统一仓库，包含完整的开发工作流套件和插件市场索引。

## 仓库结构

```
cytopia-workflow/（canonical: cytopia-marketplace）
├── .claude-plugin/
│   └── marketplace.json              # 插件市场索引
├── skills/
│   └── workflow-kit/                 # 核心工作流套件（统一入口）
│       ├── plugin.json
│       ├── CLAUDE.md
│       ├── hooks/
│       └── skills/
│           ├── discovery/
│           ├── planning/
│           ├── execution/
│           ├── deploy/
│           ├── verification/
│           ├── documentation-update/
│           ├── diagnosis/
│           ├── db-migration-safety/
│           └── ...（辅助技能）
├── CHANGELOG.md
└── README.md
```

## 安装

添加此 marketplace 到 Claude Code：

```bash
claude plugin marketplace add Infinity-light/cytopia-marketplace
```

安装核心工作流套件：

```bash
claude plugin install workflow-kit@cytopia-marketplace
```

## 更新插件

### 检查当前版本

```bash
# 查看已安装的插件列表
claude plugin list

# 查看 workflow-kit 详细信息
claude plugin list --json
```

### 更新到最新版本

```bash
# 1. 更新 marketplace 索引
claude plugin marketplace update cytopia-marketplace

# 2. 重新安装插件（会自动获取最新版本）
claude plugin install workflow-kit@cytopia-marketplace
```

### 完整重装

如果需要完全重新安装：

```bash
# 1. 卸载旧版本
claude plugin uninstall workflow-kit@cytopia-marketplace

# 2. 重新安装
claude plugin install workflow-kit@cytopia-marketplace
```

### 版本历史

查看 [CHANGELOG.md](./CHANGELOG.md) 了解版本更新记录。

## 核心工作流

```
discovery → planning → execution → deploy → verification → documentation-update
                                     ↑          ↓          ↓
                                     └── diagnosis ←───────┘
```

## 包含的技能

### 核心工作流技能（workflow-kit）

| 技能 | 用途 | 触发命令 |
|------|------|----------|
| discovery | 需求调研、信息收集 | /discovery |
| planning | 架构设计、方案规划 | /planning |
| execution | 代码实现 | /execution |
| diagnosis | 问题诊断、故障排查 | /diagnosis |
| verification | 部署验证、质量检查 | /verification |
| documentation-update | 文档更新 | /documentation-update |
| deploy | 部署同步 | /deploy |
| db-migration-safety | 数据库迁移安全护栏（部署前检查） | /db-migration-safety |

### 辅助技能

| 技能 | 用途 |
|------|------|
| key-reader | 读取密钥、配置文件 |
| smart-fetch | 智能网页抓取 |
| plugin-publisher | Claude Plugin 发布与生效验证 |
| skills-updater | 更新/创建 Skill |
| skill-creator | 创建和打包新Skill |
| ui-ux-pro-max | UI/UX 设计规范 |
| frontend-design | 前端组件设计 |
| vue-best-practices | Vue.js 最佳实践 |

## 版本信息

- **Marketplace**: cytopia-marketplace v1.0.4
- **Workflow-Kit**: v2.4.0
- **Repository**: https://github.com/Infinity-light/cytopia-marketplace

## 许可证

MIT
