"""FastAPI 应用：Web UI + 生成 API。

启动：
  uvicorn slideforge.api:app --host 0.0.0.0 --port 8000
或：
  python -m uvicorn slideforge.api:app --port 8000
"""

from __future__ import annotations

import base64
import json
import os
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import __version__
from .builder import build_pptx
from .llm import LLMError, generate_outline, list_providers
from .outline import OutlineError, parse_outline, sample_outline
from .preview import render_previews
from .themes import list_themes

WEB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "web")

app = FastAPI(
    title="SlideForge API",
    description="AI 驱动的原生 PowerPoint 生成器",
    version=__version__,
)


class GenerateRequest(BaseModel):
    topic: str = ""  # 演示主题（提供 outline 时可省略）
    provider: str = "openai"
    api_key: str = ""
    base_url: Optional[str] = None
    model: Optional[str] = None
    theme: str = "ocean"
    slides: Optional[int] = None
    temperature: float = 0.7
    effect: str = "fade"
    transition: str = "fade"
    outline: Optional[dict] = None  # 直接传入大纲（离线 / 已有大纲）


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "name": "SlideForge", "version": __version__}


@app.get("/api/themes")
def themes() -> list[dict]:
    return list_themes()


@app.get("/api/providers")
def providers() -> list[dict]:
    return list_providers()


@app.get("/api/sample-outline")
def sample() -> dict:
    return sample_outline()


@app.post("/api/generate")
def generate(req: GenerateRequest) -> dict:
    try:
        if req.outline:
            outline = parse_outline(req.outline)
        else:
            if not req.topic.strip():
                raise HTTPException(status_code=400, detail="缺少演示主题 topic")
            outline = generate_outline(
                provider=req.provider, api_key=req.api_key,
                base_url=req.base_url, model=req.model,
                topic=req.topic, slide_count=req.slides,
                temperature=req.temperature,
            )
        outline.setdefault("theme", req.theme)
        outline["theme"] = req.theme or outline.get("theme", "ocean")
    except (OutlineError, LLMError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    try:
        pptx = build_pptx(outline, effect=req.effect, transition=req.transition).getvalue()
        previews = render_previews(outline)
    except Exception as e:  # 渲染层兜底
        raise HTTPException(status_code=500, detail=f"渲染失败: {e}") from e

    return {
        "filename": _safe_filename(outline.get("title", "slideforge")) + ".pptx",
        "title": outline.get("title", ""),
        "slide_count": len(outline.get("slides", [])),
        "theme": outline.get("theme", req.theme),
        "pptx_base64": base64.b64encode(pptx).decode("ascii"),
        "previews": previews,
        "generator": f"SlideForge v{__version__}",
    }


def _safe_filename(name: str) -> str:
    cleaned = "".join(c for c in name if c.isalnum() or c in "-_ .").strip()
    return (cleaned or "slideforge")[:80]


# 静态资源：/ → web/index.html
app.mount("/assets", StaticFiles(directory=os.path.join(WEB_DIR, "assets")), name="assets")


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    with open(os.path.join(WEB_DIR, "index.html"), "r", encoding="utf-8") as fh:
        return fh.read()
