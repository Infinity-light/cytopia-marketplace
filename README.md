# Cytopia Workflow

Cytopia 企业级 Claude Code 工作流统一仓库，包含完整的开发工作流套件和插件市场索引。

## 仓库结构

```
cytopia-workflow/
├── .claude-plugin/marketplace.json   # 插件市场索引
├── skills/
│   ├── workflow-kit/                 # 核心工作流套件
│   ├── key-reader/                   # 密钥读取
│   ├── smart-fetch/                  # 智能网页抓取
│   ├── skills-updater/               # Skill更新管理
│   ├── skill-creator/                # Skill创建工具
│   ├── ui-ux-pro-max/                # UI/UX设计
│   ├── frontend-design/              # 前端组件设计
│   └── vue-best-practices/           # Vue.js最佳实践
└── README.md
```

## 安装

添加此 marketplace 到 Claude Code：

```bash
/plugin marketplace add Infinity-light/cytopia-workflow
```

安装核心工作流套件：

```bash
/plugin install workflow-kit@cytopia-workflow
```

## 核心工作流

```
discovery → planning → execution → verification → documentation-update → deploy
                 ↓           ↓
              diagnosis ←────┘
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

### 辅助技能

| 技能 | 用途 |
|------|------|
| key-reader | 读取密钥、配置文件 |
| smart-fetch | 智能网页抓取 |
| skills-updater | 更新/创建 Skill |
| skill-creator | 创建和打包新Skill |
| ui-ux-pro-max | UI/UX 设计规范 |
| frontend-design | 前端组件设计 |
| vue-best-practices | Vue.js 最佳实践 |

## 版本信息

- **Marketplace**: cytopia-workflow v1.0.0
- **Workflow-Kit**: v2.3.0
- **Repository**: https://github.com/Infinity-light/cytopia-workflow

## 许可证

MIT
