"""多模型商 LLM 客户端（OpenAI 兼容协议）。

支持：OpenAI / DeepSeek / Moonshot(Kimi) / Ollama / 任意自定义
OpenAI 兼容端点。全部通过统一的 chat completions 协议调用。
"""

from __future__ import annotations

import httpx

from .prompt import build_system_prompt, build_user_prompt, extract_json

# 预置模型商（可被 --base-url/--model 覆盖）
PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
    },
    "deepseek": {
        "name": "DeepSeek",
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
    },
    "moonshot": {
        "name": "Moonshot Kimi",
        "base_url": "https://api.moonshot.cn/v1",
        "model": "moonshot-v1-8k",
    },
    "ollama": {
        "name": "Ollama (本地)",
        "base_url": "http://localhost:11434/v1",
        "model": "qwen2.5:7b",
    },
    "zhipu": {
        "name": "智谱 GLM",
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "model": "glm-4-flash",
    },
}


class LLMError(RuntimeError):
    pass


def list_providers() -> list[dict]:
    return [{"id": k, "name": v["name"], "base_url": v["base_url"], "model": v["model"]}
            for k, v in PROVIDERS.items()]


def resolve_provider(provider_id: str | None,
                     base_url: str | None = None,
                     model: str | None = None) -> dict:
    pid = (provider_id or "openai").strip().lower()
    if pid not in PROVIDERS and base_url is None:
        # 未知 provider 但给了 base_url 时按自定义处理
        raise LLMError(f"未知模型商: {pid}. 可用: {', '.join(PROVIDERS)}")
    p = PROVIDERS.get(pid, {})
    return {
        "base_url": (base_url or p.get("base_url") or "https://api.openai.com/v1").rstrip("/"),
        "model": model or p.get("model") or "gpt-4o-mini",
        "api_key": "",
    }


def chat_completion(*, base_url: str, model: str, api_key: str,
                    messages: list[dict], temperature: float = 0.7,
                    timeout: float = 120.0) -> str:
    """调用 OpenAI 兼容的 chat completions 接口。"""
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    try:
        resp = httpx.post(url, json=payload, headers=headers, timeout=timeout)
        resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        detail = ""
        try:
            detail = e.response.text[:300]
        except Exception:
            pass
        raise LLMError(f"模型接口返回 {e.response.status_code}: {detail}") from e
    except httpx.HTTPError as e:
        raise LLMError(f"无法连接模型服务: {e}") from e

    try:
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError, ValueError) as e:
        raise LLMError(f"模型响应格式异常: {e}") from e


def generate_outline(*, provider: str = "openai", api_key: str = "",
                     base_url: str | None = None, model: str | None = None,
                     topic: str, slide_count: int | None = None,
                     temperature: float = 0.7) -> dict:
    """由主题生成结构化大纲（dict）。"""
    cfg = resolve_provider(provider, base_url, model)
    content = chat_completion(
        base_url=cfg["base_url"],
        model=cfg["model"],
        api_key=api_key,
        messages=[
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": build_user_prompt(topic, slide_count)},
        ],
        temperature=temperature,
    )
    return extract_json(content)
