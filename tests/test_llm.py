import pytest

from slideforge.llm import list_providers, resolve_provider
from slideforge.prompt import extract_json


def test_resolve_provider_defaults():
    cfg = resolve_provider("openai")
    assert cfg["base_url"] == "https://api.openai.com/v1"
    assert cfg["model"]


def test_resolve_custom_base_url():
    cfg = resolve_provider("myvendor", base_url="http://x/v1", model="m1")
    assert cfg["base_url"] == "http://x/v1"
    assert cfg["model"] == "m1"


def test_resolve_unknown_provider_raises():
    with pytest.raises(Exception):
        resolve_provider("no-such-provider")


def test_list_providers_has_deepseek():
    ids = {p["id"] for p in list_providers()}
    assert "deepseek" in ids
    assert "ollama" in ids


def test_extract_json_plain():
    assert extract_json('{"a": 1}') == {"a": 1}


def test_extract_json_with_fence():
    assert extract_json('```json\n{"a": 1}\n```') == {"a": 1}


def test_extract_json_with_noise():
    raw = "好的，结果如下：\n{\"slides\": []}\n希望有用！"
    assert extract_json(raw) == {"slides": []}


def test_extract_json_fixes_trailing_comma():
    assert extract_json('{"a": 1, "b": [1, 2,],}') == {"a": 1, "b": [1, 2]}


def test_extract_json_bad():
    with pytest.raises(ValueError):
        extract_json("没有 JSON")
