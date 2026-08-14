<div align="center">

# SlideForge

**把想法鍛造成專業簡報 — AI 驅動的原生 PowerPoint 生成器**

輸入一個主題，選擇任意的 OpenAI 相容大模型，一鍵生成帶**原生形狀、入場動畫、資料圖表與演講備註**的 `.pptx` 檔案。零依賴、可離線、開箱即用。

[简体中文](README.md) · [English](README.en.md)

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-1.0.0-blue)
[![Star](https://img.shields.io/github/stars/gitstq/slideforge)](https://github.com/gitstq/slideforge)

</div>

---

## ✨ 為什麼是 SlideForge

市面上的「AI 生成簡報」大多是**產生圖片或網頁**，匯出結果不可編輯、風格千篇一律。SlideForge 選擇了一條更硬核的路線：

- 🧱 **原生 OOXML**：直接渲染 `.pptx`，每一頁都是可編輯的真實形狀，而不是截圖。
- 🎬 **真動畫**：透過底層 XML 注入原生入場動畫與頁面切換效果，PowerPoint 中仍可繼續編輯。
- 📊 **資料圖表**：原生長條 / 折線 / 圓餅 / 環形圖，資料即改即用。
- 🔌 **模型自由**：OpenAI / DeepSeek / Moonshot(Kimi) / Ollama / 智譜 GLM / 任意相容端點。
- 🛰️ **完全離線**：沒有 API Key 也能用內建大綱一鍵生成簡報。
- 🖥️ **Web 工作台**：左側設定、右側 SVG 即時預覽，所見即所得。

---

## 🚀 快速開始

### 1. 安裝

```bash
git clone https://github.com/gitstq/slideforge.git
cd slideforge
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

也可以直接 `pip install` 本專案（或執行 `build.sh` / `build.bat` 一鍵建置）。

### 2. 離線體驗（無需 API Key）

```bash
python -m slideforge "AI 時代的產品設計" --offline -o demo.pptx --theme ocean
```

### 3. 使用大模型生成

```bash
# 方式一：命令列，指定模型商
export SLIDEFORGE_API_KEY="sk-..."
python -m slideforge "2026 年度科技趨勢" \
    --provider deepseek -o trends.pptx --theme emerald --slides 12

# 方式二：使用現有大綱 JSON（完全離線）
python -m slideforge --outline examples/sample_outline.json -o out.pptx

# 方式三：自訂 OpenAI 相容端點
python -m slideforge "募資路演" \
    --base-url https://your-endpoint/v1 --model your-model \
    --api-key sk-xxx -o pitch.pptx
```

常用參數：

| 參數 | 說明 |
| --- | --- |
| `--provider` | 模型商：`openai` / `deepseek` / `moonshot` / `ollama` / `zhipu` |
| `--theme` | 主題：`ocean` / `emerald` / `sunset` / `midnight` / `mono` / `rose` / `gold` / `forest` |
| `--effect` | 入場動畫：`fade` / `rise` / `zoom` / `none` |
| `--transition` | 切換動畫：`fade` / `push` / `split` / `wipe` / `random` / `none` |
| `--slides` | 期望頁數（提示模型，非精確） |
| `--outline` | 直接用大綱 JSON 渲染，無需聯網 |
| `--offline` | 內建範例大綱離線示範 |
| `--print-outline` | 列印生成的大綱 JSON |
| `--list-themes` / `--list-providers` | 列出可用主題 / 模型商 |

### 4. 啟動 Web 工作台

```bash
uvicorn slideforge.api:app --host 0.0.0.0 --port 8000
# 瀏覽器開啟 http://localhost:8000
```

### 5. Docker

```bash
docker build -t slideforge .
docker run -p 8000:8000 slideforge
```

---

## 🎨 主題

內建 8 套專業配色，深淺兩色系，Web 預覽與 PPTX 渲染共用同一套定義，**預覽即所得**：

| 主題 | 風格 | 深淺 |
| --- | --- | --- |
| `ocean` 深洋 | 深藍科技感 | 深色 |
| `emerald` 翡翠 | 深綠清新 | 深色 |
| `sunset` 暮光 | 暖橙玫紅 | 深色 |
| `midnight` 極夜 | 暗紫星空 | 深色 |
| `mono` 素白 | 極簡黑白 | 淺色 |
| `rose` 玫紅 | 粉紫浪漫 | 深色 |
| `gold` 鎏金 | 深金典雅 | 深色 |
| `forest` 森林 | 墨綠自然 | 深色 |

---

## 📐 大綱結構（Outline JSON）

SlideForge 的核心契約：**LLM 輸出與渲染器共用同一份大綱結構**。你可以在 `examples/sample_outline.json` 看到完整範例：

```json
{
  "title": "AI 時代的產品設計",
  "subtitle": "從洞察到交付的完整方法論",
  "author": "SlideForge",
  "theme": "ocean",
  "slides": [
    { "type": "title", "title": "AI 時代的產品設計", "subtitle": "..." },
    { "type": "section", "title": "01 · 為什麼是現在", "bullets": ["技術拐點", "使用者預期變化"] },
    { "type": "bullets", "title": "核心洞察", "bullets": ["...", "..."], "notes": "演講備註", "accent": "#38BDF8" },
    { "type": "two_column", "title": "機會矩陣", "columns": [
        { "heading": "進攻區", "bullets": ["垂直場景深耕", "資料飛輪"] },
        { "heading": "防守區", "bullets": ["信任與合規", "成本結構"] }
    ]},
    { "type": "stats", "title": "資料說話", "stats": [
        { "value": "3×", "label": "交付速度提升" },
        { "value": "68%", "label": "使用者留存改善" }
    ]},
    { "type": "chart", "title": "市場成長趨勢", "chart": {
        "type": "bar", "labels": ["Q1", "Q2", "Q3", "Q4"],
        "datasets": [ { "name": "規模", "values": [12, 19, 28, 44] } ]
    }},
    { "type": "quote", "title": "一個判斷", "quote": "真正的壁壘不是模型，而是對場景的理解。", "quote_source": "SlideForge" },
    { "type": "closing", "title": "謝謝", "subtitle": "期待與你一起鍛造下一個作品" }
  ]
}
```

### 版式類型

| 類型 | 說明 |
| --- | --- |
| `title` | 封面頁 |
| `section` | 章節過渡頁 |
| `bullets` | 要點列表頁（可帶 `notes` 演講備註、`accent` 強調色） |
| `two_column` | 雙欄對比頁 |
| `stats` | 資料指標頁 |
| `chart` | 原生圖表頁（`bar` / `line` / `pie` / `donut`） |
| `quote` | 引言金句頁 |
| `closing` | 結束頁 |

---

## 🧠 支援的大模型服務

| Provider | 預設模型 | Base URL |
| --- | --- | --- |
| OpenAI | `gpt-4o-mini` | `https://api.openai.com/v1` |
| DeepSeek | `deepseek-chat` | `https://api.deepseek.com/v1` |
| Moonshot (Kimi) | `moonshot-v1-8k` | `https://api.moonshot.cn/v1` |
| Ollama (本地) | `qwen2.5:7b` | `http://localhost:11434/v1` |
| 智譜 GLM | `glm-4-flash` | `https://open.bigmodel.cn/api/paas/v4` |

所有模型商走統一 **OpenAI 相容 chat completions 協議**，任意 `--base-url` / `--model` 均可覆蓋。

---

## 🧪 測試與建置

```bash
python -m pytest -q          # 32 項單元測試
bash build.sh                # Linux/macOS 一鍵建置（測試 + 自檢 + 打包）
build.bat                    # Windows 一鍵建置
```

建置產物輸出到 `dist/slideforge-<version>.tar.gz`。

---

## 🤝 貢獻

歡迎任何形式的貢獻！請閱讀 [CONTRIBUTING.md](CONTRIBUTING.md)。

- 修 bug、加功能、寫文件、提建議都歡迎
- 新功能請附上單元測試，保證 `pytest` 全綠
- 提交訊息遵循 Conventional Commits

## 📄 授權

[MIT](LICENSE) © SlideForge Team
