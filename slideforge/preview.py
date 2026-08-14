"""SVG 预览渲染器。

把同一份 Outline 渲染为 SVG 缩略图，供 Web UI 与文档展示
「预览即所得」。逻辑与 pptx 渲染器保持一致的版式结构。
"""

from __future__ import annotations

import html
import math

from .themes import get_theme

W, H = 1280, 720


def _esc(text: str) -> str:
    return html.escape(str(text))


def _wrap(text: str, chars: int) -> list[str]:
    """按字符数近似折行（中文/ASCII 混合）。"""
    if not text:
        return [""]
    lines, cur = [], ""
    for ch in str(text):
        cur += ch
        w = 2 if ord(ch) > 0x2E80 else 1
        if w == 1 and len(cur) >= chars:
            lines.append(cur.rstrip())
            cur = ""
        elif w == 2 and len(cur) >= chars * 0.5:
            lines.append(cur.rstrip())
            cur = ""
    if cur:
        lines.append(cur)
    return lines or [""]


def _text(x, y, s, size, fill, weight="normal", anchor="start", family="sans-serif",
          spacing=None):
    sp = f' letter-spacing="{spacing}"' if spacing else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
            f'font-family="{family}" font-weight="{weight}" text-anchor="{anchor}"{sp}>{_esc(s)}</text>')


def _rect(x, y, w, h, fill, rx=0, stroke=None, stroke_w=1, opacity=1):
    st = f' stroke="{stroke}" stroke-width="{stroke_w}"' if stroke else ""
    op = f' opacity="{opacity}"' if opacity < 1 else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{st}{op}/>')


def _wrap_lines(text: str, max_chars: int) -> list[str]:
    out: list[str] = []
    for line in str(text).splitlines() or [""]:
        out.extend(_wrap(line, max_chars))
    return out


def render_slide(slide: dict, theme_id: str, idx: int, total: int) -> str:
    theme = get_theme(theme_id)
    accent = slide.get("accent") or theme.accent
    bg = theme.bg
    ink, muted = theme.ink, theme.muted
    stype = slide.get("type", "bullets")
    title = slide.get("title", f"第 {idx + 1} 页")

    body: list[str] = []
    body.append(_rect(0, 0, W, H, bg))
    # 微妙渐变
    g0, g1 = theme.gradient
    body.append(f'<defs><linearGradient id="g{idx}" x1="0" y1="0" x2="1" y2="1">'
                f'<stop offset="0" stop-color="{g0}"/><stop offset="1" stop-color="{g1}"/>'
                f'</linearGradient></defs>')
    body.append(_rect(0, 0, W, H, f"url(#g{idx})", opacity=0.55))

    if stype == "title":
        body.append(f'<circle cx="1020" cy="60" r="200" fill="{accent}" opacity="0.9"/>')
        body.append(f'<circle cx="1180" cy="560" r="150" fill="none" stroke="{accent}" stroke-width="2"/>')
        body.append(f'<circle cx="80" cy="620" r="36" fill="{theme.accent2}"/>')
        body.append(_rect(90, 268, 40, 10, accent, rx=5))
        body.append(_text(90, 310, "SlideForge", 20, muted))
        y = 380
        for line in _wrap_lines(title, 18):
            body.append(_text(90, y, line, 64, ink, weight="bold", family="Georgia"))
            y += 78
        sub = slide.get("subtitle", "")
        if sub:
            y += 10
            for line in _wrap_lines(sub, 34):
                body.append(_text(92, y, line, 26, muted))
                y += 36
        body.append(_text(90, 648, f"{idx+1:02d} / {total:02d}", 16, muted))

    elif stype == "section":
        body.append(_rect(90, 150, 150, 58, accent, rx=8))
        num = title.split("·")[0].strip()
        body.append(_text(165, 190, num[:8], 26, "#FFFFFF" if theme.is_dark else "#111", weight="bold"))
        y = 320
        for line in _wrap_lines(title, 20):
            body.append(_text(90, y, line, 48, ink, weight="bold", family="Georgia"))
            y += 60
        y += 20
        for b in (slide.get("bullets") or slide.get("points") or []):
            body.append(_rect(92, y - 14, 12, 12, accent, rx=3))
            for line in _wrap_lines(b, 44):
                body.append(_text(116, y, line, 24, muted))
                y += 34
            y += 8

    elif stype == "two_column":
        body.append(_rect(90, 120, 40, 10, accent, rx=5))
        body.append(_text(90, 158, title, 40, ink, weight="bold", family="Georgia"))
        cols = slide.get("columns") or []
        n = len(cols)
        cw = (W - 180 - (n - 1) * 40) / n
        for i, col in enumerate(cols):
            x = 90 + i * (cw + 40)
            body.append(_rect(x, 210, cw, 380, theme.card, rx=14))
            body.append(_rect(x + 26, 238, 30, 9, accent, rx=4))
            body.append(_text(x + 26, 282, col.get("heading", ""), 28, ink, weight="bold"))
            y = 340
            for b in (col.get("bullets") or []):
                body.append(_rect(x + 28, y - 12, 10, 10, accent, rx=2))
                for line in _wrap_lines(b, 22):
                    body.append(_text(x + 50, y, line, 21, ink))
                    y += 30
                y += 10

    elif stype == "quote":
        body.append(_rect(90, 120, 40, 10, accent, rx=5))
        body.append(_text(90, 158, title, 40, ink, weight="bold", family="Georgia"))
        y = 300
        q = "\u201C" + slide.get("quote", "")
        for line in _wrap_lines(q, 20):
            body.append(_text(92, y, line, 40, ink, weight="bold", family="Georgia"))
            y += 58
        src = slide.get("quote_source", "")
        if src:
            body.append(_text(94, y + 26, "— " + src, 22, accent))

    elif stype == "stats":
        body.append(_rect(90, 120, 40, 10, accent, rx=5))
        body.append(_text(90, 158, title, 40, ink, weight="bold", family="Georgia"))
        stats = slide.get("stats") or []
        n = len(stats)
        cw = (W - 180 - (n - 1) * 40) / n
        for i, st in enumerate(stats):
            x = 90 + i * (cw + 40)
            body.append(_rect(x, 230, cw, 330, theme.card, rx=16))
            body.append(_rect(x + 28, 262, 60, 9, accent, rx=4))
            y = 360
            for line in _wrap_lines(st.get("value", ""), 8):
                body.append(_text(x + 28, y, line, 56, accent, weight="bold"))
                y += 64
            y = 480
            for line in _wrap_lines(st.get("label", ""), 12):
                body.append(_text(x + 28, y, line, 22, muted))
                y += 30

    elif stype == "chart":
        body.append(_rect(90, 120, 40, 10, accent, rx=5))
        body.append(_text(90, 158, title, 40, ink, weight="bold", family="Georgia"))
        chart = slide.get("chart") or {}
        labels = chart.get("labels") or []
        datasets = chart.get("datasets") or []
        ctype = chart.get("type", "bar")
        if not datasets:
            datasets = [{"name": "数据", "values": []}]
        vals = [d.get("values") or [] for d in datasets]
        max_v = max([max((v for v in vs if isinstance(v, (int, float))), default=0)
                     for vs in vals] or [1], default=1)
        max_v = max_v or 1
        colors = [accent, theme.accent2, "#FBBF24", "#A78BFA", "#34D399"]
        cx0, cy0, cw, ch = 120, 220, W - 240, 360
        if ctype == "bar":
            n = max(len(labels), 1)
            gw = cw / n
            bar_w = min(gw * 0.55, 60)
            per_ds = len(datasets)
            bw = bar_w / per_ds
            for di, ds in enumerate(datasets):
                color = colors[di % len(colors)]
                for li, v in enumerate(ds.get("values") or []):
                    if not isinstance(v, (int, float)):
                        continue
                    bh = (v / max_v) * ch
                    bx = cx0 + li * gw + gw * 0.5 - bar_w / 2 + di * bw
                    body.append(_rect(bx, cy0 + ch - bh, bw - 3, bh, color, rx=3))
                    body.append(_text(bx + bw / 2 - 8, cy0 + ch - bh - 8, str(v), 16, muted))
            for li, lab in enumerate(labels):
                body.append(_text(cx0 + li * gw + gw * 0.5, cy0 + ch + 32, str(lab), 18, muted,
                                  anchor="middle"))
            body.append(_rect(cx0, cy0 + ch, cw, 2, muted, opacity=0.6))
        elif ctype == "line":
            n = max(len(labels), 1)
            for di, ds in enumerate(datasets):
                color = colors[di % len(colors)]
                pts = []
                for li, v in enumerate(ds.get("values") or []):
                    if not isinstance(v, (int, float)):
                        continue
                    px = cx0 + (li / max(n - 1, 1)) * cw
                    py = cy0 + ch - (v / max_v) * ch
                    pts.append(f"{px:.0f},{py:.0f}")
                if pts:
                    body.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" '
                                f'stroke-width="4"/>')
                    for p in pts:
                        x, y = p.split(",")
                        body.append(f'<circle cx="{x}" cy="{y}" r="6" fill="{color}"/>')
            for li, lab in enumerate(labels):
                body.append(_text(cx0 + (li / max(n - 1, 1)) * cw, cy0 + ch + 32, str(lab), 18,
                                  muted, anchor="middle"))
            body.append(_rect(cx0, cy0 + ch, cw, 2, muted, opacity=0.6))
        elif ctype in ("pie", "donut"):
            total = sum(v for v in (datasets[0].get("values") or []) if isinstance(v, (int, float)))
            total = total or 1
            cx, cy, r = 540, 400, 170
            start = -math.pi / 2
            for li, v in enumerate(datasets[0].get("values") or []):
                if not isinstance(v, (int, float)):
                    continue
                frac = v / total
                end = start + 2 * math.pi * frac
                x1, y1 = cx + r * math.cos(start), cy + r * math.sin(start)
                x2, y2 = cx + r * math.cos(end), cy + r * math.sin(end)
                large = 1 if (end - start) > math.pi else 0
                color = colors[li % len(colors)]
                if ctype == "donut":
                    body.append(f'<path d="M {cx} {cy} L {x1:.0f} {y1:.0f} '
                                f'A {r} {r} 0 {large} 1 {x2:.0f} {y2:.0f} Z" fill="{color}" '
                                f'stroke="{bg}" stroke-width="46"/>')
                else:
                    body.append(f'<path d="M {cx} {cy} L {x1:.0f} {y1:.0f} '
                                f'A {r} {r} 0 {large} 1 {x2:.0f} {y2:.0f} Z" fill="{color}"/>')
                start = end
            if ctype == "donut":
                body.append(f'<circle cx="{cx}" cy="{cy}" r="90" fill="{bg}"/>')
            # 图例
            ly = 300
            for li, lab in enumerate(datasets[0].get("values") or []):
                lx = 860
                body.append(_rect(lx, ly, 20, 20, colors[li % len(colors)], rx=5))
                body.append(_text(lx + 30, ly + 18, str(labels[li]) if li < len(labels) else "",
                                  18, ink))
                ly += 42

    else:  # bullets 默认
        body.append(_rect(90, 120, 40, 10, accent, rx=5))
        body.append(_text(90, 158, title, 40, ink, weight="bold", family="Georgia"))
        y = 250
        for b in (slide.get("bullets") or slide.get("points") or []):
            body.append(_rect(92, y - 16, 16, 16, accent, rx=4))
            for line in _wrap_lines(b, 34):
                body.append(_text(124, y, line, 28, ink))
                y += 40
            y += 18

    # 页脚页码
    if stype not in ("title", "closing"):
        body.append(_text(W - 90, H - 40, f"{idx+1:02d} / {total:02d}", 16, muted, anchor="end"))

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}">' + "".join(body) + "</svg>"
    )


def render_previews(outline: dict) -> list[str]:
    theme = outline.get("theme", "ocean")
    total = len(outline["slides"])
    return [render_slide(s, theme, i, total) for i, s in enumerate(outline["slides"])]
