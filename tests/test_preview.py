from slideforge.outline import sample_outline
from slideforge.preview import render_previews, render_slide


def test_preview_every_type_renders():
    outline = sample_outline()
    svgs = render_previews(outline)
    assert len(svgs) == len(outline["slides"])
    for svg in svgs:
        assert svg.startswith("<svg")
        assert "viewBox" in svg


def test_render_theme_variants():
    outline = sample_outline()
    for tid in ("ocean", "mono", "sunset"):
        svg = render_slide(outline["slides"][0], tid, 0, 8)
        assert svg.startswith("<svg")


def test_render_chart_types():
    from slideforge.preview import render_slide

    for ctype in ("bar", "line", "pie", "donut"):
        slide = {"type": "chart", "title": "c", "chart": {
            "type": ctype, "labels": ["A", "B", "C"],
            "datasets": [{"name": "s", "values": [1, 2, 3]}]}}
        assert render_slide(slide, "ocean", 0, 4).startswith("<svg")
