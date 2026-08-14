"""命令行入口。

示例：
  python -m slideforge "AI 时代的产品设计" -o out.pptx --theme ocean
  python -m slideforge --outline sample.json -o out.pptx
  python -m slideforge "主题" --provider deepseek --api-key sk-xxx -o out.pptx
  python -m slideforge "主题" --offline -o demo.pptx
"""

from __future__ import annotations

import argparse
import sys
import tempfile
import os

from . import __version__
from .builder import build_pptx
from .llm import LLMError, generate_outline, list_providers
from .outline import OutlineError, load_outline_file, parse_outline, sample_outline
from .themes import list_themes


def _write_or_stdout(data: bytes, path: str | None):
    if path:
        with open(path, "wb") as fh:
            fh.write(data)
        print(f"[OK] 已生成: {path} ({len(data):,} bytes)")
    else:
        sys.stdout.buffer.write(data)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="slideforge",
        description="SlideForge - AI 驱动的原生 PowerPoint 生成器",
    )
    p.add_argument("topic", nargs="?", default=None, help="演示主题（使用 --outline 时忽略）")
    p.add_argument("-o", "--out", default=None, help="输出 .pptx 路径（缺省输出到 stdout）")
    p.add_argument("--outline", default=None, help="直接使用大纲 JSON 文件渲染（无需联网）")
    p.add_argument("--offline", action="store_true", help="使用内置示例大纲离线生成（演示）")
    p.add_argument("--provider", default="openai",
                   help="模型商: " + ",".join(pv["id"] for pv in list_providers()))
    p.add_argument("--api-key", default=os.environ.get("SLIDEFORGE_API_KEY", ""),
                   help="API Key（也可用环境变量 SLIDEFORGE_API_KEY）")
    p.add_argument("--base-url", default=None, help="自定义 OpenAI 兼容 base_url")
    p.add_argument("--model", default=None, help="模型名（覆盖模型商默认）")
    p.add_argument("--theme", default="ocean", help="主题: " + "/".join(t["id"] for t in list_themes()))
    p.add_argument("--slides", type=int, default=None, help="期望页数（提示模型，非精确）")
    p.add_argument("--effect", default="fade", choices=["fade", "rise", "zoom", "none"], help="入场动画")
    p.add_argument("--transition", default="fade", choices=["fade", "push", "split", "wipe", "random", "none"],
                   help="页面切换动画")
    p.add_argument("--temperature", type=float, default=0.7, help="生成温度")
    p.add_argument("--print-outline", action="store_true", help="打印生成的大纲 JSON")
    p.add_argument("--list-themes", action="store_true", help="列出可用主题")
    p.add_argument("--list-providers", action="store_true", help="列出可用模型商")
    p.add_argument("--version", action="version", version=f"slideforge {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.list_themes:
        for t in list_themes():
            print(f"{t['id']:10s} {t['name']}")
        return 0
    if args.list_providers:
        for pv in list_providers():
            print(f"{pv['id']:10s} {pv['name']:18s} default-model={pv['model']}")
        return 0

    try:
        if args.outline:
            outline = load_outline_file(args.outline)
        elif args.offline:
            outline = sample_outline(args.topic or "AI 时代的产品设计")
            outline["theme"] = args.theme
        else:
            if not args.topic:
                build_parser().print_help()
                return 2
            if not args.api_key and args.provider != "ollama":
                print("[WARN] 未提供 --api-key，尝试无鉴权调用（Ollama 等本地服务可用）。",
                      file=sys.stderr)
            outline = generate_outline(
                provider=args.provider, api_key=args.api_key,
                base_url=args.base_url, model=args.model,
                topic=args.topic, slide_count=args.slides,
                temperature=args.temperature,
            )
            outline.setdefault("theme", args.theme)
    except (OutlineError, LLMError, ValueError) as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1

    if args.print_outline:
        import json
        print(json.dumps(outline, ensure_ascii=False, indent=2))

    data = build_pptx(outline, effect=args.effect, transition=args.transition).getvalue()
    _write_or_stdout(data, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
