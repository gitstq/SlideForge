<div align="center">

# SlideForge

**把想法锻造为专业演示文稿 — AI 驱动的原生 PowerPoint 生成器**

输入一个主题，选择任意 OpenAI 兼容大模型，一键生成带**原生形状、入场动画、数据图表与演讲备注**的 `.pptx` 文件。零依赖、可离线、开箱即用。

[English](README.en.md) · [繁體中文](README.zh-TW.md)

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-1.0.0-blue)
[![Star](https://img.shields.io/github/stars/gitstq/slideforge)](https://github.com/gitstq/slideforge)

</div>

---

## ✨ 为什么是 SlideForge

市面上的「AI 生成 PPT」大多是**生成图片或网页**，导出的结果不可编辑、风格千篇一律。SlideForge 选择了一条更硬核的路线：

- 🧱 **原生 OOXML**：直接渲染 `.pptx`，每一页都是可编辑的真实形状，而不是截图。
- 🎬 **真动画**：通过底层 XML 注入原生入场动画与页面切换效果，PowerPoint 里可继续编辑。
- 📊 **数据图表**：原生柱状 / 折线 / 饼图 / 环形图，数据即改即用。
- 🔌 **模型自由**：OpenAI / DeepSeek / Moonshot(Kimi) / Ollama / 智谱 GLM / 任意兼容端点。
- 🛰️ **完全离线**：没有 API Key 也能用内置大纲一键生成演示。
- 🖥️ **Web 工作台**：左侧设定、右侧 SVG 实时预览，所见即所得。

---

## 🚀 快速开始

### 1. 安装

```bash
git clone https://github.com/gitstq/slideforge.git
cd slideforge
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

也可以直接 `pip install` 本项目（或运行 `build.sh` / `build.bat` 一键构建）。

### 2. 离线体验（无需 API Key）

```bash
python -m slideforge "AI 时代的产品设计" --offline -o demo.pptx --theme ocean
```

### 3. 使用大模型生成

```bash
# 方式一：命令行，指定模型商
export SLIDEFORGE_API_KEY="sk-..."
python -m slideforge "2026 年度技术趋势" \
    --provider deepseek -o trends.pptx --theme emerald --slides 12

# 方式二：使用现有大纲 JSON（完全离线）
python -m slideforge --outline examples/sample_outline.json -o out.pptx

# 方式三：自定义 OpenAI 兼容端点
python -m slideforge "融资路演" \
    --base-url https://your-endpoint/v1 --model your-model \
    --api-key sk-xxx -o pitch.pptx
```

常用参数：

| 参数 | 说明 |
| --- | --- |
| `--provider` | 模型商：`openai` / `deepseek` / `moonshot` / `ollama` / `zhipu` |
| `--theme` | 主题：`ocean` / `emerald` / `sunset` / `midnight` / `mono` / `rose` / `gold` / `forest` |
| `--effect` | 入场动画：`fade` / `rise` / `zoom` / `none` |
| `--transition` | 切换动画：`fade` / `push` / `split` / `wipe` / `random` / `none` |
| `--slides` | 期望页数（提示模型，非精确） |
| `--outline` | 直接用大纲 JSON 渲染，无需联网 |
| `--offline` | 内置示例大纲离线演示 |
| `--print-outline` | 打印生成的大纲 JSON |
| `--list-themes` / `--list-providers` | 列出可用主题 / 模型商 |

### 4. 启动 Web 工作台

```bash
uvicorn slideforge.api:app --host 0.0.0.0 --port 8000
# 浏览器打开 http://localhost:8000
```

### 5. Docker

```bash
docker build -t slideforge .
docker run -p 8000:8000 slideforge
```

---

## 🎨 主题

内置 8 套专业配色，深浅两色系，Web 预览与 PPTX 渲染共用同一套定义，**预览即所得**：

| 主题 | 风格 | 深浅 |
| --- | --- | --- |
| `ocean` 深洋 | 深蓝科技感 | 深色 |
| `emerald` 翡翠 | 深绿清新 | 深色 |
| `sunset` 暮光 | 暖橙玫红 | 深色 |
| `midnight` 极夜 | 暗紫星空 | 深色 |
| `mono` 素白 | 极简黑白 | 浅色 |
| `rose` 玫红 | 粉紫浪漫 | 深色 |
| `gold` 鎏金 | 深金典雅 | 深色 |
| `forest` 森林 | 墨绿自然 | 深色 |

---

## 📐 大纲结构（Outline JSON）

SlideForge 的核心契约：**LLM 输出与渲染器共用同一份大纲结构**。你可以在 `examples/sample_outline.json` 看到完整示例：

```json
{
  "title": "AI 时代的产品设计",
  "subtitle": "从洞察到交付的完整方法论",
  "author": "SlideForge",
  "theme": "ocean",
  "slides": [
    { "type": "title", "title": "AI 时代的产品设计", "subtitle": "..." },
    { "type": "section", "title": "01 · 为什么是现在", "bullets": ["技术拐点", "用户预期变化"] },
    { "type": "bullets", "title": "核心洞察", "bullets": ["...", "..."], "notes": "演讲备注", "accent": "#38BDF8" },
    { "type": "two_column", "title": "机会矩阵", "columns": [
        { "heading": "进攻区", "bullets": ["垂直场景深耕", "数据飞轮"] },
        { "heading": "防守区", "bullets": ["信任与合规", "成本结构"] }
    ]},
    { "type": "stats", "title": "数据说话", "stats": [
        { "value": "3×", "label": "交付速度提升" },
        { "value": "68%", "label": "用户留存改善" }
    ]},
    { "type": "chart", "title": "市场增长趋势", "chart": {
        "type": "bar", "labels": ["Q1", "Q2", "Q3", "Q4"],
        "datasets": [ { "name": "规模", "values": [12, 19, 28, 44] } ]
    }},
    { "type": "quote", "title": "一个判断", "quote": "真正的壁垒不是模型，而是对场景的理解。", "quote_source": "SlideForge" },
    { "type": "closing", "title": "谢谢", "subtitle": "期待与你一起锻造下一个作品" }
  ]
}
```

### 版式类型

| 类型 | 说明 |
| --- | --- |
| `title` | 封面页 |
| `section` | 章节过渡页 |
| `bullets` | 要点列表页（可带 `notes` 演讲备注、`accent` 强调色） |
| `two_column` | 双栏对比页 |
| `stats` | 数据指标页 |
| `chart` | 原生图表页（`bar` / `line` / `pie` / `donut`） |
| `quote` | 引言金句页 |
| `closing` | 结束页 |

---

## 🧠 支持的大模型服务

| Provider | 默认模型 | Base URL |
| --- | --- | --- |
| OpenAI | `gpt-4o-mini` | `https://api.openai.com/v1` |
| DeepSeek | `deepseek-chat` | `https://api.deepseek.com/v1` |
| Moonshot (Kimi) | `moonshot-v1-8k` | `https://api.moonshot.cn/v1` |
| Ollama (本地) | `qwen2.5:7b` | `http://localhost:11434/v1` |
| 智谱 GLM | `glm-4-flash` | `https://open.bigmodel.cn/api/paas/v4` |

所有模型商走统一 **OpenAI 兼容 chat completions 协议**，任意 `--base-url` / `--model` 均可覆盖。

---

## 🧪 测试与构建

```bash
python -m pytest -q          # 32 项单元测试
bash build.sh                # Linux/macOS 一键构建（测试 + 自检 + 打包）
build.bat                    # Windows 一键构建
```

构建产物输出到 `dist/slideforge-<version>.tar.gz`。

---

## 🤝 贡献

欢迎任何形式的贡献！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

- 修 bug、加特性、写文档、提建议都欢迎
- 新功能请附带单元测试，保证 `pytest` 全绿
- 提交信息遵循 Conventional Commits

## 📄 许可证

[MIT](LICENSE) © SlideForge Team
