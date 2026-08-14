@echo off
REM SlideForge 一键构建脚本（Windows）
cd /d %~dp0

echo ==^> 1/4 运行测试
python -m pytest -q
if errorlevel 1 exit /b 1

echo ==^> 2/4 离线自检
python -m slideforge "自检主题" --offline -o %TEMP%\slideforge_selfcheck.pptx --theme emerald

echo ==^> 3/4 打包源码归档
if not exist dist mkdir dist
powershell -Command "Compress-Archive -Path slideforge, web, assets, examples, tests, README.md, README.en.md, README.zh-TW.md, LICENSE, CONTRIBUTING.md, requirements.txt, pyproject.toml, Dockerfile -DestinationPath dist\slideforge-1.0.0.zip -Force"

echo ==^> 4/4 完成
dir /b dist
echo 构建成功
