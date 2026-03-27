"""
QMD CLI 入口
python -m qmd
"""

import os

# 必须在导入任何 HF 库之前设置（防止网络探测卡住）
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

# 跨平台控制台编码
from .utils.console import setup_console

setup_console()

from .cli import main

if __name__ == "__main__":
    main()
