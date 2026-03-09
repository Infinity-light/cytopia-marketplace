---
name: narrative-production-review
description: Review narrative media dry-run readiness end to end. Use when you need to validate the chapter package, provider plan, and orchestration output, then produce a readiness report or run the local smoke test on a DOCX chapter.
---
<!-- ---
role: 生产审查 Skill，验证章节包、provider 规划、流水线计划，并输出 readiness 报告
depends:
  - scripts/production_review.py
  - scripts/smoke_test.py
status: PENDING
--- -->

# 漫剧文字—图片—视频生产审查

在需要收口 dry-run 结果并检查是否可进入人工制作或外部执行时使用本 Skill。

## 检查范围

- 章节 JSON 是否完整
- provider 规划是否符合安全与默认模型约束
- pipeline 是否包含必要阶段与 fallback
- 是否存在阻塞项

## 用法

审查已有 JSON：

```bash
python -X utf8 scripts/production_review.py \
  --chapter-json "<chapter-json>" \
  --provider-plan-json "<provider-plan-json>" \
  --pipeline-plan-json "<pipeline-plan-json>" \
  --output "<review-json>"
```

端到端 smoke test：

```bash
python -X utf8 scripts/smoke_test.py --docx "<path-to-docx>"
```

## 输出重点

- readiness verdict
- warnings 与 blockers
- 可用于 smoke validation 的汇总产物
