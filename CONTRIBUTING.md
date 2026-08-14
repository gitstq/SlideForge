# 贡献指南

感谢你愿意为 **SlideForge** 贡献力量！无论是修 bug、加特性、写文档还是提建议，都欢迎。

## 开发环境

```bash
git clone https://github.com/gitstq/slideforge.git
cd slideforge
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e ".[dev]"
```

## 常用命令

```bash
python -m pytest -q                # 运行全部测试
python -m slideforge "主题" --offline -o demo.pptx   # 离线生成自检
uvicorn slideforge.api:app --port 8000   # 启动 Web UI
```

## 代码风格

- 使用 `ruff` / `black` 风格的简洁 Python，注释以简体中文为主。
- 新功能请附带单元测试（`tests/`），保证 `pytest` 全绿。
- 提交信息遵循 Conventional Commits：
  - `feat: 新增 xxx`
  - `fix: 修复 xxx`
  - `docs: 更新文档`
  - `test: 补充测试`

## 提交流程

1. Fork 本仓库并创建特性分支（`feat/xxx` 或 `fix/xxx`）。
2. 提交改动，`git push` 后发起 Pull Request。
3. 描述清楚「改了什么、为什么、如何验证」。

## 议题建议

- 🐛 Bug 报告：请附复现步骤、期望与实际行为。
- ✨ 功能建议：请描述使用场景与收益。

感谢你的贡献！
