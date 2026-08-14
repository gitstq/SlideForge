#!/usr/bin/env bash
# SlideForge 一键构建脚本（Linux / macOS）
set -euo pipefail
cd "$(dirname "$0")"

echo "==> 1/4 运行测试"
python3 -m pytest -q

echo "==> 2/4 离线自检（生成示例 .pptx）"
python3 -m slideforge "自检主题" --offline -o /tmp/slideforge_selfcheck.pptx --theme emerald
echo "    自检产物: /tmp/slideforge_selfcheck.pptx ($(stat -c%s /tmp/slideforge_selfcheck.pptx 2>/dev/null || echo -n '?') bytes)"

echo "==> 3/4 打包源码归档"
rm -rf dist && mkdir -p dist
VERSION=$(python3 -c "from slideforge import __version__; print(__version__)")
FILES="slideforge web assets examples tests README.md LICENSE CONTRIBUTING.md requirements.txt pyproject.toml Dockerfile build.sh build.bat .gitignore"
for f in README.en.md README.zh-TW.md; do
    [ -f "$f" ] && FILES="$FILES $f"
done
tar -czf "dist/slideforge-${VERSION}.tar.gz" \
    --exclude='*__pycache__*' --exclude='.pytest_cache' --exclude='.git' \
    $FILES

echo "==> 4/4 完成"
ls -lh dist/
echo "构建成功 ✅"
