"""LLM 提示词模板与 JSON 提取工具。"""

from __future__ import annotations

import json
import re


def build_system_prompt() -> str:
    return (
        "你是一位资深的演示文稿策划师与视觉设计师。"
        "你只输出一个合法的 JSON 对象，不要输出任何解释、Markdown 代码块标记或其他文本。\n"
        "JSON 结构如下：\n"
        "{\n"
        '  "title": "演示标题",\n'
        '  "subtitle": "副标题",\n'
        '  "author": "作者",\n'
        '  "theme": "ocean",\n'
        '  "slides": [\n'
        "    {\"type\": \"title\", \"title\": \"...\", \"subtitle\": \"...\"},\n"
        "    {\"type\": \"section\", \"title\": \"01 · 章节名\", \"bullets\": [\"...\"]},\n"
        "    {\"type\": \"bullets\", \"title\": \"...\", \"bullets\": [\"...\"], \"notes\": \"演讲备注\"},\n"
        "    {\"type\": \"two_column\", \"title\": \"...\", \"columns\": [{\"heading\": \"...\", \"bullets\": [\"...\"]}]},\n"
        "    {\"type\": \"stats\", \"title\": \"...\", \"stats\": [{\"value\": \"68%\", \"label\": \"...\"}]},\n"
        "    {\"type\": \"chart\", \"title\": \"...\", \"chart\": {\"type\": \"bar\", \"labels\": [\"Q1\"], \"datasets\": [{\"name\": \"...\", \"values\": [1]}]}},\n"
        "    {\"type\": \"quote\", \"title\": \"...\", \"quote\": \"...\", \"quote_source\": \"...\"},\n"
        "    {\"type\": \"closing\", \"title\": \"谢谢\", \"subtitle\": \"...\"}\n"
        "  ]\n"
        "}\n"
        "版式 type 可选：title / section / bullets / two_column / stats / chart / quote / closing。\n"
        "要点：\n"
        "- 第一页必须是 title，最后一页必须是 closing。\n"
        "- 每页内容精炼，bullets 3~6 条，每条不超过 30 字。\n"
        "- chart 的 labels 与 datasets[].values 长度一致，数值为数字。\n"
        "- stats 的 value 形如 '68%' 或 '3×'，label 一句话。\n"
        "- theme 可选：ocean/emerald/sunset/midnight/mono/rose/gold/forest。\n"
        "- 使用简体中文撰写内容（除非用户要求其他语言）。"
    )


def build_user_prompt(topic: str, slide_count: int | None = None) -> str:
    prompt = (
        f"请围绕以下主题设计一份演示文稿大纲：\n「{topic}」\n"
    )
    if slide_count and slide_count > 1:
        prompt += f"请生成约 {slide_count} 页（含首尾页）。\n"
    prompt += "只输出 JSON。"
    return prompt


def extract_json(text: str) -> dict:
    """从 LLM 回复中提取第一个 JSON 对象（容忍代码围栏与前后杂讯）。"""
    if not text:
        raise ValueError("模型返回为空")

    text = text.strip()

    # 去除 ```json ... ``` 围栏
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence:
        text = fence.group(1)

    # 定位第一个 { 到最后一个 }
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"模型未返回 JSON：{text[:200]!r}")
    raw = text[start:end + 1]

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        # 尝试修复未转义/多余逗号的常见问题
        fixed = re.sub(r",\s*([}\]])", r"\1", raw)
        try:
            data = json.loads(fixed)
        except json.JSONDecodeError:
            raise ValueError(f"JSON 解析失败: {e}") from e

    if not isinstance(data, dict):
        raise ValueError("JSON 顶层必须是对象")
    return data
