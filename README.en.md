<div align="center">

# SlideForge

**Forge your ideas into professional decks — an AI-powered, native PowerPoint generator.**

Give it a topic, pick any OpenAI-compatible model, and get a real `.pptx` with **native shapes, entrance animations, data charts, and speaker notes** — fully editable, offline-capable, and ready to use out of the box.

[简体中文](README.md) · [繁體中文](README.zh-TW.md)

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-1.0.0-blue)
[![Star](https://img.shields.io/github/stars/gitstq/slideforge)](https://github.com/gitstq/slideforge)

</div>

---

## ✨ Why SlideForge

Most "AI PPT" tools generate **images or web pages** — not editable, and samey by default. SlideForge takes a harder, more valuable path:

- 🧱 **Native OOXML**: renders real `.pptx`, every slide is an editable vector shape, not a screenshot.
- 🎬 **Real animations**: injects native entrance animations and slide transitions via low-level XML — still editable in PowerPoint.
- 📊 **Data charts**: native bar / line / pie / donut charts you can edit on the fly.
- 🔌 **Bring your own model**: OpenAI / DeepSeek / Moonshot(Kimi) / Ollama / Zhipu GLM / any OpenAI-compatible endpoint.
- 🛰️ **Fully offline**: generate a deck with zero API keys using the built-in sample outline.
- 🖥️ **Web workspace**: configure on the left, live SVG preview on the right — what you see is what you get.

---

## 🚀 Quick Start

### 1. Install

```bash
git clone https://github.com/gitstq/slideforge.git
cd slideforge
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

You can also `pip install` this project directly (or run `build.sh` / `build.bat` for a one-shot build).

### 2. Try it offline (no API key)

```bash
python -m slideforge "AI Era Product Design" --offline -o demo.pptx --theme ocean
```

### 3. Generate with an LLM

```bash
# CLI, pick a provider
export SLIDEFORGE_API_KEY="sk-..."
python -m slideforge "2026 Tech Trends" \
    --provider deepseek -o trends.pptx --theme emerald --slides 12

# Reuse an existing outline JSON (fully offline)
python -m slideforge --outline examples/sample_outline.json -o out.pptx

# Custom OpenAI-compatible endpoint
python -m slideforge "Startup Pitch" \
    --base-url https://your-endpoint/v1 --model your-model \
    --api-key sk-xxx -o pitch.pptx
```

Key options:

| Option | Description |
| --- | --- |
| `--provider` | `openai` / `deepseek` / `moonshot` / `ollama` / `zhipu` |
| `--theme` | `ocean` / `emerald` / `sunset` / `midnight` / `mono` / `rose` / `gold` / `forest` |
| `--effect` | entrance: `fade` / `rise` / `zoom` / `none` |
| `--transition` | slide: `fade` / `push` / `split` / `wipe` / `random` / `none` |
| `--slides` | desired page count (hint to the model, not exact) |
| `--outline` | render from an outline JSON without network |
| `--offline` | demo with the built-in sample outline |
| `--print-outline` | print the generated outline JSON |
| `--list-themes` / `--list-providers` | list themes / providers |

### 4. Web workspace

```bash
uvicorn slideforge.api:app --host 0.0.0.0 --port 8000
# open http://localhost:8000
```

### 5. Docker

```bash
docker build -t slideforge .
docker run -p 8000:8000 slideforge
```

---

## 🎨 Themes

8 professional palettes across light and dark. The web preview and the PPTX renderer share one definition, so **the preview is the output**:

| Theme | Vibe | Tone |
| --- | --- | --- |
| `ocean` | deep-blue tech | dark |
| `emerald` | fresh dark-green | dark |
| `sunset` | warm orange/rose | dark |
| `midnight` | dark violet night | dark |
| `mono` | minimalist mono | light |
| `rose` | pink-violet romance | dark |
| `gold` | gilded elegance | dark |
| `forest` | natural ink-green | dark |

---

## 📐 Outline JSON

The core contract of SlideForge: **the LLM output and the renderer share one outline schema**. See `examples/sample_outline.json` for the full sample:

```json
{
  "title": "AI Era Product Design",
  "subtitle": "From insight to delivery",
  "author": "SlideForge",
  "theme": "ocean",
  "slides": [
    { "type": "title", "title": "AI Era Product Design", "subtitle": "..." },
    { "type": "section", "title": "01 · Why now", "bullets": ["Inflection point", "Shifting expectations"] },
    { "type": "bullets", "title": "Core insights", "bullets": ["...", "..."], "notes": "speaker notes", "accent": "#38BDF8" },
    { "type": "two_column", "title": "Opportunity matrix", "columns": [
        { "heading": "Attack", "bullets": ["Vertical depth", "Data flywheel"] },
        { "heading": "Defend", "bullets": ["Trust & compliance", "Cost structure"] }
    ]},
    { "type": "stats", "title": "Numbers", "stats": [
        { "value": "3×", "label": "Faster delivery" },
        { "value": "68%", "label": "Better retention" }
    ]},
    { "type": "chart", "title": "Growth trend", "chart": {
        "type": "bar", "labels": ["Q1", "Q2", "Q3", "Q4"],
        "datasets": [ { "name": "Scale", "values": [12, 19, 28, 44] } ]
    }},
    { "type": "quote", "title": "A take", "quote": "The real moat is not the model, but your understanding of the domain.", "quote_source": "SlideForge" },
    { "type": "closing", "title": "Thanks", "subtitle": "Let's forge the next great deck together" }
  ]
}
```

### Layout types

| Type | Description |
| --- | --- |
| `title` | cover slide |
| `section` | section divider |
| `bullets` | bullet list (optional `notes`, `accent`) |
| `two_column` | side-by-side comparison |
| `stats` | KPI highlight |
| `chart` | native chart (`bar` / `line` / `pie` / `donut`) |
| `quote` | pull quote |
| `closing` | end slide |

---

## 🧠 Supported LLM providers

| Provider | Default model | Base URL |
| --- | --- | --- |
| OpenAI | `gpt-4o-mini` | `https://api.openai.com/v1` |
| DeepSeek | `deepseek-chat` | `https://api.deepseek.com/v1` |
| Moonshot (Kimi) | `moonshot-v1-8k` | `https://api.moonshot.cn/v1` |
| Ollama (local) | `qwen2.5:7b` | `http://localhost:11434/v1` |
| Zhipu GLM | `glm-4-flash` | `https://open.bigmodel.cn/api/paas/v4` |

All providers speak the same **OpenAI-compatible chat completions protocol**; any `--base-url` / `--model` overrides work.

---

## 🧪 Tests & Build

```bash
python -m pytest -q          # 32 unit tests
bash build.sh                # Linux/macOS one-shot build (tests + self-check + archive)
build.bat                    # Windows one-shot build
```

Artifacts land in `dist/slideforge-<version>.tar.gz`.

---

## 🤝 Contributing

Contributions of any kind are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

- Bug fixes, features, docs, and suggestions all welcome
- Please ship unit tests with new features and keep `pytest` green
- Conventional Commits for commit messages

## 📄 License

[MIT](LICENSE) © SlideForge Team
