---
name: narrative-story-intake
description: Extract a realistic dry-run chapter package from a DOCX novel chapter for narrative media workflows. Use when you need deterministic DOCX parsing, chapter selection, metadata extraction, and JSON output without calling remote media services.
---
<!-- ---
role: DOCX 小说章节提取 Skill，生成后续 provider planning 和 orchestration 可消费的章节 JSON
depends:
  - scripts/story_intake.py
status: PENDING
--- -->

# 漫剧文字—图片—视频故事输入

在处理 DOCX 小说章节时使用本 Skill。

## 目标

- 使用标准库解析 `.docx`
- 提取首章或指定章节
- 生成稳定的 JSON 元数据与正文摘录
- 不依赖远端服务

## 用法

```bash
python -X utf8 scripts/story_intake.py --docx "<path-to-docx>" --output "<chapter-json>"
```

可选参数：

- `--chapter-title "第1章"`：按标题匹配章节
- `--excerpt-chars 800`：控制正文摘录长度

## 输出重点

- 文档路径与文件名
- 命中的章节标题或首章推断结果
- 正文段落数、字符数、摘录
- 适合后续分镜与制作规划的章节 JSON
