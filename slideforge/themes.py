"""Theme presets for SlideForge.

每个主题定义一套可被原生渲染（python-pptx）与 SVG 预览共用的配色与字体，
保证「预览即所得」。
"""

import re

HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


class Theme:
    def __init__(self, data: dict):
        self.id = data["id"]
        self.name = data["name"]
        self.bg = data["bg"]          # slide background
        self.gradient = data.get("gradient", [data["bg"], data["bg"]])
        self.accent = data["accent"]
        self.accent2 = data.get("accent2", data["accent"])
        self.ink = data["ink"]        # primary text
        self.muted = data["muted"]    # secondary text
        self.card = data.get("card", data["bg"])
        self.heading_font = data.get("heading_font", "Arial")
        self.body_font = data.get("body_font", "Arial")
        self.is_dark = data.get("is_dark", True)

    def hex(self, key: str) -> str:
        """返回十六进制颜色字符串（带 # 前缀）。"""
        return str(getattr(self, key, "#333333"))


THEMES = {
    "ocean": dict(
        id="ocean", name="Ocean 深洋",
        bg="#0B1526", gradient=["#0B1526", "#122A4C"], accent="#38BDF8", accent2="#22D3EE",
        ink="#E2E8F0", muted="#94A3B8", card="#12233F",
        heading_font="Arial", body_font="Arial", is_dark=True,
    ),
    "emerald": dict(
        id="emerald", name="Emerald 翡翠",
        bg="#06110C", gradient=["#06110C", "#0B2E1F"], accent="#34D399", accent2="#10B981",
        ink="#E7F5EF", muted="#8FB8A6", card="#0B2118",
        heading_font="Arial", body_font="Arial", is_dark=True,
    ),
    "sunset": dict(
        id="sunset", name="Sunset 暮光",
        bg="#16080E", gradient=["#16080E", "#3B1226"], accent="#FB7185", accent2="#FBBF24",
        ink="#FEF2F2", muted="#D8A7B8", card="#2A1220",
        heading_font="Georgia", body_font="Arial", is_dark=True,
    ),
    "midnight": dict(
        id="midnight", name="Midnight 极夜",
        bg="#0A0A0F", gradient=["#0A0A0F", "#1A1A2E"], accent="#A78BFA", accent2="#818CF8",
        ink="#EEF2FF", muted="#9CA3C4", card="#15152B",
        heading_font="Georgia", body_font="Arial", is_dark=True,
    ),
    "mono": dict(
        id="mono", name="Mono 素白",
        bg="#FAFAF7", gradient=["#FAFAF7", "#EFEDE6"], accent="#111111", accent2="#6B7280",
        ink="#1C1917", muted="#78716C", card="#FFFFFF",
        heading_font="Georgia", body_font="Arial", is_dark=False,
    ),
    "rose": dict(
        id="rose", name="Rose 玫红",
        bg="#1C0A12", gradient=["#1C0A12", "#421A2E"], accent="#F472B6", accent2="#F9A8D4",
        ink="#FDF2F8", muted="#D9A9BE", card="#2E1430",
        heading_font="Arial", body_font="Arial", is_dark=True,
    ),
    "gold": dict(
        id="gold", name="Gold 鎏金",
        bg="#100F0A", gradient=["#100F0A", "#2A2416"], accent="#FACC15", accent2="#EAB308",
        ink="#FEFCE8", muted="#B9AF8F", card="#1F1B10",
        heading_font="Georgia", body_font="Arial", is_dark=True,
    ),
    "forest": dict(
        id="forest", name="Forest 森林",
        bg="#0C1208", gradient=["#0C1208", "#1E2E14"], accent="#A3E635", accent2="#84CC16",
        ink="#F7FEE7", muted="#A8B58A", card="#18210F",
        heading_font="Arial", body_font="Arial", is_dark=True,
    ),
}


def get_theme(theme_id: str | None) -> Theme:
    tid = (theme_id or "ocean").strip().lower()
    if tid not in THEMES:
        raise KeyError(f"Unknown theme: {theme_id}. Available: {', '.join(sorted(THEMES))}")
    return Theme(THEMES[tid])


def list_themes() -> list[dict]:
    return [dict(id=t.id, name=t.name, accent=t.accent, bg=t.bg, is_dark=t.is_dark)
            for t in (Theme(d) for d in THEMES.values())]


def validate_hex(colors: list[str]) -> list[str]:
    for c in colors:
        if not HEX_RE.match(c):
            raise ValueError(f"Invalid hex color: {c!r}")
    return colors
