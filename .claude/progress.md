# Cytopia Workflow 项目进度

## 当前状态

- 已发布并对齐：`cytopia-marketplace v1.0.4`
- 已完成发布准备：`workflow-kit v2.4.0`
- Canonical Repository：`https://github.com/Infinity-light/cytopia-marketplace`

## 当前结构（已生效）

- Marketplace 索引：`.claude-plugin/marketplace.json`
- Workflow 套件入口：`skills/workflow-kit/plugin.json`
- 全局指南：`skills/workflow-kit/CLAUDE.md`
- Hook 配置：`skills/workflow-kit/hooks/hooks.json`
- Windows Hook 适配：`skills/workflow-kit/hooks/run-hook.cmd`

## 本轮关键能力（2.3.1 ~ 2.3.4）

1. SessionStart Hook 已支持 Windows（通过 `run-hook.cmd`）
2. 部署流程增加 `db-migration-safety` 迁移安全护栏
3. deploy 第 2 步前，`WARN` 需通过 AskUserQuestion 三选一显式确认
4. 新增 `plugin-publisher` Skill，用于 Claude Plugin 发布与安装/会话生效验证闭环
