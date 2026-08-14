"""结构化大纲模型与校验。

SlideForge 的核心数据契约：LLM 输出的 JSON 大纲（Outline）与
渲染器共用同一套结构，保证「AI 生成 → 原生渲染」无缝衔接。
"""

from __future__ import annotations

import json
import re
from typing import Any

SLIDE_TYPES = {
    "title", "section", "bullets", "two_column",
    "quote", "stats", "chart", "closing",
}

# 每个版式允许的顶层字段（用于温和清洗未知键）
ALLOWED_KEYS = {
    "type", "title", "subtitle", "bullets", "points", "columns",
    "quote", "quote_source", "stats", "chart", "notes", "accent",
}

CHART_TYPES = {"bar", "line", "pie", "donut"}


class OutlineError(ValueError):
    """大纲数据不合法。"""


def _as_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip()


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [s.strip() for s in re.split(r"[\n;]+", value) if s.strip()]
    if isinstance(value, (list, tuple)):
        return [str(x).strip() for x in value if str(x).strip()]
    return []


def _as_number(value: Any) -> float | str:
    """图表数值：数字或数字字符串转 float，否则保留原值。"""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).strip())
    except ValueError:
        return _as_str(value)


def _clean_slide(slide: dict, index: int) -> dict:
    if not isinstance(slide, dict):
        raise OutlineError(f"slide[{index}] 必须是对象")

    stype = str(slide.get("type", "bullets")).strip().lower()
    if stype not in SLIDE_TYPES:
        # 未知类型回退为 bullets，保证渲染不中断
        stype = "bullets"

    cleaned = {"type": stype, "title": _as_str(slide.get("title"), f"第 {index + 1} 页")}
    for key in ALLOWED_KEYS:
        if key in ("type", "title"):
            continue
        if key not in slide:
            continue
        if key in ("bullets", "points"):
            cleaned[key] = _as_list(slide.get(key))
        elif key == "columns":
            cols = []
            for c in slide.get(key) or []:
                if isinstance(c, dict):
                    cols.append({
                        "heading": _as_str(c.get("heading"), "要点"),
                        "bullets": _as_list(c.get("bullets")),
                    })
            cleaned[key] = cols
        elif key == "stats":
            stats = []
            for s in slide.get(key) or []:
                if isinstance(s, dict):
                    stats.append({
                        "value": _as_str(s.get("value"), "—"),
                        "label": _as_str(s.get("label")),
                    })
            cleaned[key] = stats
        elif key == "chart":
            ch = slide.get(key)
            if isinstance(ch, dict):
                ctype = str(ch.get("type", "bar")).lower()
                if ctype not in CHART_TYPES:
                    ctype = "bar"
                cleaned["chart"] = {
                    "type": ctype,
                    "title": _as_str(ch.get("title")),
                    "labels": _as_list(ch.get("labels")),
                    "datasets": [
                        {"name": _as_str(d.get("name"), "数据"),
                         "values": [_as_number(v)
                                    for v in (d.get("values") or [])]}
                        for d in (ch.get("datasets") or []) if isinstance(d, dict)
                    ],
                }
        elif key == "notes":
            cleaned[key] = _as_str(slide.get(key))
        elif key == "quote":
            cleaned[key] = _as_str(slide.get(key))
        elif key == "quote_source":
            cleaned[key] = _as_str(slide.get(key))
        elif key == "accent":
            cleaned[key] = _as_str(slide.get(key))

    # 按版式补齐默认内容，保证渲染器拿到稳定结构
    if stype == "quote" and not cleaned.get("quote"):
        cleaned["quote"] = "没有引言内容。"
    if stype == "stats" and not cleaned.get("stats"):
        cleaned["stats"] = [{"value": "100%", "label": "示例指标"}]
    if stype == "chart" and not cleaned.get("chart"):
        cleaned["chart"] = {"type": "bar", "labels": ["A", "B", "C"],
                            "datasets": [{"name": "数据", "values": [3, 5, 4]}]}
    if stype in ("bullets",) and not cleaned.get("bullets"):
        cleaned["bullets"] = ["要点一", "要点二", "要点三"]
    return cleaned


def parse_outline(data: Any) -> dict:
    """解析并校验 Outline。接受 dict 或 JSON 字符串。"""
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            raise OutlineError(f"大纲 JSON 解析失败: {e}") from e

    if not isinstance(data, dict):
        raise OutlineError("大纲必须是 JSON 对象")

    slides_raw = data.get("slides")
    if not isinstance(slides_raw, list) or not slides_raw:
        raise OutlineError("大纲缺少非空 slides 数组")

    return {
        "title": _as_str(data.get("title"), "未命名演示文稿"),
        "subtitle": _as_str(data.get("subtitle")),
        "author": _as_str(data.get("author")),
        "date": _as_str(data.get("date")),
        "theme": _as_str(data.get("theme"), "ocean"),
        "slides": [_clean_slide(s, i) for i, s in enumerate(slides_raw)],
    }


def load_outline_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return parse_outline(fh.read())


def dumps(outline: dict) -> str:
    return json.dumps(outline, ensure_ascii=False, indent=2)


def sample_outline(title: str = "AI 时代的产品设计") -> dict:
    """内置演示大纲，供离线模式 / 无 API Key 快速体验。"""
    return {
        "title": title,
        "subtitle": "从洞察到交付的完整方法论",
        "author": "SlideForge",
        "theme": "ocean",
        "slides": [
            {"type": "title", "title": title, "subtitle": "从洞察到交付的完整方法论"},
            {"type": "section", "title": "01 · 为什么是现在", "bullets": ["技术拐点", "用户预期变化"]},
            {"type": "bullets", "title": "核心洞察", "bullets": [
                "AI 让「做出」不再是瓶颈，「想清楚」才是。",
                "产品价值 = 决策质量 × 执行速度。",
                "可解释、可回滚、可度量成为新的设计底线。",
            ], "notes": "强调三个洞察的内在联系。", "accent": "#38BDF8"},
            {"type": "two_column", "title": "机会矩阵", "columns": [
                {"heading": "进攻区", "bullets": ["垂直场景深耕", "数据飞轮", "生态卡位"]},
                {"heading": "防守区", "bullets": ["信任与合规", "成本结构", "渠道壁垒"]},
            ]},
            {"type": "stats", "title": "数据说话", "stats": [
                {"value": "3×", "label": "交付速度提升"},
                {"value": "68%", "label": "用户留存改善"},
                {"value": "40%", "label": "人力成本下降"},
            ]},
            {"type": "chart", "title": "市场增长趋势", "chart": {
                "type": "bar", "labels": ["Q1", "Q2", "Q3", "Q4"],
                "datasets": [
                    {"name": "规模", "values": [12, 19, 28, 44]},
                    {"name": "增速", "values": [8, 14, 20, 32]},
                ],
            }},
            {"type": "quote", "title": "一个判断", "quote": "真正的壁垒不是模型，而是对场景的理解与持续交付的能力。",
             "quote_source": "SlideForge 观点"},
            {"type": "closing", "title": "谢谢", "subtitle": "期待与你一起锻造下一个作品"},
        ],
    }
