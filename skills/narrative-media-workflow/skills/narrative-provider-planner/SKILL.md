---
name: narrative-provider-planner
description: Build a safe provider availability plan for narrative media dry runs. Use when you need masked provider-presence detection, default model selection, and role assignment for text, image, video, audio, and DeepSeek supplement without exposing secret values.
---
<!-- ---
role: Provider 规划 Skill，基于安全 presence 检测输出模型与职责规划
depends:
  - scripts/provider_plan.py
status: PENDING
--- -->

# 漫剧文字—图片—视频供应商规划

在需要判断当前环境是否具备 Ark、FAL、DeepSeek 等 provider 条件时使用本 Skill。

## 核心规则

- 只报告 key 是否存在、来源是否为 env 或文件、是否掩码
- 不输出任何原始 secret
- DeepSeek 只做文本补充
- 默认仍生成 dry-run 计划，即使 provider 缺失

## 用法

```bash
python -X utf8 scripts/provider_plan.py --output "<provider-plan-json>"
```

可选参数：

- `--env-file "<path-to-env>"`：读取本地配置文件，但仅输出 presence 与掩码摘要
- `--require ark,fal`：标记关键 provider

## 输出重点

- provider presence 矩阵
- 默认模型绑定
- 角色分工
- 缺失项与 dry-run 回退建议
