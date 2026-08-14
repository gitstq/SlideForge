import pytest

from slideforge.themes import THEMES, get_theme, list_themes, validate_hex


def test_all_themes_valid_hex():
    colors = []
    for d in THEMES.values():
        colors += [d["bg"], d["accent"], d["accent2"], d["ink"], d["muted"]]
    # 不应抛错
    validate_hex(colors)


def test_get_theme_default():
    t = get_theme("ocean")
    assert t.accent == "#38BDF8"


def test_get_theme_case_insensitive():
    assert get_theme("OCEAN").id == "ocean"


def test_get_theme_unknown():
    with pytest.raises(KeyError):
        get_theme("nope")


def test_list_themes():
    themes = list_themes()
    assert isinstance(themes, list)
    assert len(themes) == len(THEMES)
    assert all({"id", "name", "accent", "bg"} <= set(t) for t in themes)
