---
name: db-migration-safety
description: Deploy 前数据库迁移护栏、风险评估、回滚检查。仅在 deploy 前置检查且检测到数据库变更风险信号时触发，输出 PASS/WARN/BLOCK 并给出可执行建议。
---

# DB Migration Safety

用于在 **Deploy 前** 做数据库迁移安全预检，避免高风险变更直接上线。

## 触发条件（两个前提，必须同时满足）

仅当以下两个前提都成立时，才进入护栏评估：

1. **A. 当前动作是 deploy 前置检查（deploy intent）**
   - 通过 `--deploy-intent` 显式声明。
2. **B. 检测到数据库变更风险信号**
   - 例如：迁移文件、DDL、schema 相关变更。

任一前提不满足时输出 `SKIP`，不阻断流程。

## 调用命令示例

```bash
python -X utf8 "skills/workflow-kit/skills/db-migration-safety/scripts/preflight.py" --repo . --deploy-intent --since-ref HEAD~1 --json
```

## 输出规范

- `PASS`：风险可控，可继续 deploy。
- `WARN`：存在风险提示，建议补充说明后再 deploy。
- `BLOCK`：高风险且缺少关键保障，**必须中止 deploy**。
- `SKIP`：未命中触发前提，不执行护栏评估。

输出字段：
- `status`: `PASS | WARN | BLOCK | SKIP`
- `reasons`: 评估结论原因列表
- `signals`: 检测到的风险信号列表

## BLOCK 处理原则

当结果为 `BLOCK`：

**中止 deploy，先补齐回滚与备份方案。**

至少补齐：
- 可执行回滚路径（如 down migration / rollback / revert）
- 备份与恢复方案（backup / runbook / migration-plan）
