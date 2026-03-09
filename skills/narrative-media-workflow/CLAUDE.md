<!-- ---
role: 插件级上下文注入，定义 narrative-media-workflow 的边界、默认模型和安全约束
depends:
  - ./plugin.json
status: ACTIVE
--- -->

# 漫剧文字—图片—视频工作流指南

本插件服务于基于小说章节的 漫剧文字—图片—视频干跑工作流，不直接执行远端媒体生成。

## 范围

- 输入：DOCX 小说章节、可选章节名、可选 provider 配置来源
- 输出：章节提取 JSON、provider 规划 JSON、流水线计划 JSON、生产就绪审查 JSON
- 目标：支持可复现的本地 dry-run，帮助后续人工或外部系统接管制作

## 默认模型

- Ark text: `doubao-seed-2-0-pro-260215`
- Ark image: `doubao-seedream-4-5-251128`
- Ark video: `doubao-seedance-1-5-pro-251215`
- FAL audio: `fal-ai/index-tts-2/text-to-speech`
- DeepSeek supplement: `openai-compatible:deepseek`

## 安全边界

- 只允许输出 provider presence、来源和掩码状态，不输出任何明文 secret
- DeepSeek 仅作为文本补充，不承担图像、音频、视频主生成职责
- 所有脚本默认 dry-run；不发起远端生成请求
- 章节抽取优先使用 Python 标准库，避免额外依赖
