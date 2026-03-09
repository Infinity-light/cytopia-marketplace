#!/usr/bin/env python3
"""Deterministic DOCX chapter intake for narrative media dry runs."""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Iterable, List
from xml.etree import ElementTree as ET

W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
CHAPTER_RE = re.compile(r"^(第[0-9一二三四五六七八九十百千零两〇]+[章节回幕卷篇]|chapter\s+\d+)", re.IGNORECASE)


def extract_paragraphs(docx_path: Path) -> List[str]:
    with zipfile.ZipFile(docx_path) as archive:
        xml_bytes = archive.read("word/document.xml")
    root = ET.fromstring(xml_bytes)
    paragraphs: List[str] = []
    for paragraph in root.iterfind(f".//{W_NS}p"):
        texts: List[str] = []
        for node in paragraph.iterfind(f".//{W_NS}t"):
            if node.text:
                texts.append(node.text)
        line = "".join(texts).strip()
        if line:
            paragraphs.append(line)
    return paragraphs


def normalize(text: str) -> str:
    return re.sub(r"\s+", "", text).lower()


def find_chapter_ranges(paragraphs: Iterable[str]) -> List[int]:
    starts: List[int] = []
    for idx, paragraph in enumerate(paragraphs):
        if CHAPTER_RE.match(paragraph.strip()):
            starts.append(idx)
    return starts


def select_chapter(paragraphs: List[str], chapter_title: str | None) -> tuple[str, List[str], int, int]:
    starts = find_chapter_ranges(paragraphs)
    if chapter_title:
        target = normalize(chapter_title)
        for idx, paragraph in enumerate(paragraphs):
            if target in normalize(paragraph):
                start = idx
                end = len(paragraphs)
                for candidate in starts:
                    if candidate > start:
                        end = candidate
                        break
                return paragraphs[start], paragraphs[start + 1:end], start, end
        raise ValueError(f"Chapter title not found: {chapter_title}")

    if starts:
        start = starts[0]
        end = starts[1] if len(starts) > 1 else len(paragraphs)
        return paragraphs[start], paragraphs[start + 1:end], start, end

    if not paragraphs:
        raise ValueError("No non-empty paragraphs found in DOCX")

    title = paragraphs[0][:40]
    return title, paragraphs[1:], 0, len(paragraphs)


def build_output(docx_path: Path, title: str, body: List[str], start: int, end: int, excerpt_chars: int) -> dict:
    full_text = "\n\n".join(body).strip()
    excerpt = full_text[:excerpt_chars]
    segment_count = max(len(body), 0)
    return {
        "workflow": "narrative-story-intake",
        "docx_path": str(docx_path),
        "docx_name": docx_path.name,
        "selected_chapter": {
            "title": title,
            "start_paragraph_index": start,
            "end_paragraph_index": end,
            "paragraph_count": segment_count,
            "character_count": len(full_text),
        },
        "chapter_excerpt": excerpt,
        "chapter_text": full_text,
        "story_metadata": {
            "language": "zh-CN",
            "source_format": ".docx",
            "suitable_for": [
                "story-beat-planning",
                "shot-outline",
                "prompt-pack-dry-run",
                "voiceover-draft",
            ],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--docx", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--chapter-title")
    parser.add_argument("--excerpt-chars", type=int, default=800)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    docx_path = Path(args.docx)
    output_path = Path(args.output)
    if not docx_path.exists():
        raise FileNotFoundError(f"DOCX not found: {docx_path}")

    paragraphs = extract_paragraphs(docx_path)
    title, body, start, end = select_chapter(paragraphs, args.chapter_title)
    payload = build_output(docx_path, title, body, start, end, args.excerpt_chars)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": "ok",
        "selected_title": payload["selected_chapter"]["title"],
        "paragraph_count": payload["selected_chapter"]["paragraph_count"],
        "output": str(output_path),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise
