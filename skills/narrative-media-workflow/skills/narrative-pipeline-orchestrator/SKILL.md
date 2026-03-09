---
name: narrative-pipeline-orchestrator
description: Compose a narrative-media dry-run production pipeline from chapter intake JSON and provider planning JSON. Use when you need deterministic stage planning, asset expectations, and fallback logic without performing remote generation.
---
<!-- ---
role: 流水线编排 Skill，组合章节与 provider 规划，输出 漫剧文字—图片—视频阶段计划
depends:
  - scripts/pipeline_orchestrator.py
status: PENDING
--- -->

# 漫剧文字—图片—视频流水线编排

在已有章节 JSON 与 provider plan JSON 后使用本 Skill。

## 目标

- 生成可执行但不真正调用远端的 stage plan
- 明确文本、分镜、提示词、媒体占位和审校顺序
- 对缺失 provider 给出 deterministic fallback

## 用法

```bash
python -X utf8 scripts/pipeline_orchestrator.py \
  --chapter-json "<chapter-json>" \
  --provider-plan-json "<provider-plan-json>" \
  --output "<pipeline-plan-json>"
```

## 输出重点

- 阶段列表与顺序
- 每阶段输入、输出、owner provider
- dry-run 交付物占位
- 缺失能力时的人工接管策略
