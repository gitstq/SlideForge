import json

import pytest

from slideforge.outline import (
    OutlineError,
    load_outline_file,
    parse_outline,
    sample_outline,
)


def test_parse_minimal():
    data = {"title": "T", "slides": [{"type": "bullets", "title": "A", "bullets": ["x", "y"]}]}
    o = parse_outline(data)
    assert o["title"] == "T"
    assert len(o["slides"]) == 1
    assert o["slides"][0]["bullets"] == ["x", "y"]


def test_parse_from_json_string():
    raw = json.dumps({"slides": [{"title": "t"}]})
    o = parse_outline(raw)
    assert o["slides"][0]["type"] == "bullets"
    assert o["slides"][0]["bullets"]  # 默认补齐


def test_parse_missing_slides():
    with pytest.raises(OutlineError):
        parse_outline({"title": "no slides"})


def test_parse_bad_json():
    with pytest.raises(OutlineError):
        parse_outline("not json {{{")


def test_unknown_type_falls_back():
    o = parse_outline({"slides": [{"type": "weird", "title": "x"}]})
    assert o["slides"][0]["type"] == "bullets"


def test_chart_cleaning():
    o = parse_outline({"slides": [{
        "type": "chart",
        "chart": {"type": "bar", "labels": ["A", "B"],
                  "datasets": [{"name": "s", "values": [1, "2", 3]}]},
    }]})
    chart = o["slides"][0]["chart"]
    assert chart["labels"] == ["A", "B"]
    assert chart["datasets"][0]["values"] == [1.0, 2.0, 3.0]


def test_stats_default():
    o = parse_outline({"slides": [{"type": "stats", "title": "s"}]})
    assert o["slides"][0]["stats"][0]["value"]


def test_sample_outline_valid():
    o = parse_outline(sample_outline())
    assert len(o["slides"]) >= 5
    assert o["slides"][0]["type"] == "title"
    assert o["slides"][-1]["type"] == "closing"


def test_load_outline_file(tmp_path):
    p = tmp_path / "o.json"
    p.write_text(json.dumps(sample_outline()), encoding="utf-8")
    o = load_outline_file(str(p))
    assert o["title"]
