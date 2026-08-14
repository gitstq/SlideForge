"""将 Word 文档（.docx）抽取为大纲草稿（可选功能，需 python-docx）。"""

from __future__ import annotations

from .outline import parse_outline


def docx_to_outline(path: str, max_paragraphs: int = 200) -> dict:
    """读取 .docx，把标题段落映射为 section/bullets 结构。"""
    try:
        import docx
    except ImportError:
        raise RuntimeError("请先安装 python-docx: pip install python-docx")

    document = docx.Document(path)
    slides: list[dict] = []
    title = ""
    current: dict | None = None
    count = 0

    for para in document.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        style = (para.style.name or "").lower()
        if count >= max_paragraphs:
            break

        if "heading 1" in style or "标题 1" in style:
            if not title:
                title = text
            slides.append({"type": "section", "title": text[:60], "bullets": []})
            current = slides[-1]
        elif "heading 2" in style or "标题 2" in style:
            slides.append({"type": "bullets", "title": text[:60], "bullets": []})
            current = slides[-1]
        elif current is not None:
            current.setdefault("bullets", []).append(text[:80])
        count += 1

    if not slides:
        raise ValueError("文档中没有可识别的标题结构（Heading 1/2）。")

    return {
        "title": title or "文档演示",
        "subtitle": "由 Word 文档自动提取",
        "slides": slides,
    }


def docx_to_pptx(path: str, out: str, theme: str = "ocean") -> None:
    """便捷函数：docx → outline → pptx。"""
    from .builder import build_pptx

    outline = docx_to_outline(path)
    outline["theme"] = theme
    data = build_pptx(outline).getvalue()
    with open(out, "wb") as fh:
        fh.write(data)
