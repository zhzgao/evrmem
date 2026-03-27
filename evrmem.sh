#!/bin/bash
# evrmem - QMD CLI 快捷命令 (Linux/Mac)
# 用法: evrmem add/search/rag/query/stats

# 设置离线模式
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1
export EVREM_HOME="$HOME/.evrmem"

# 查找 Python
if command -v python3 &> /dev/null; then
    PYTHON="python3"
elif command -v python &> /dev/null; then
    PYTHON="python"
else
    echo "[ERROR] 未找到 Python，请安装 Python 3.9+"
    exit 1
fi

# 执行
if [ -z "$1" ]; then
    "$PYTHON" -m qmd
else
    "$PYTHON" -m qmd "$@"
fi
