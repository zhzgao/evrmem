"""
跨平台控制台工具
处理 Windows/Mac/Linux 的 UTF-8 输出兼容
"""

import sys
import platform


def setup_console() -> None:
    """
    初始化控制台编码设置
    - Windows: 设置 GBK 输出为 UTF-8
    - 其他平台: 确保 sys.stdout 使用默认 UTF-8
    """
    if sys.platform == "win32":
        try:
            import io

            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace"
            )
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding="utf-8", errors="replace"
            )
        except Exception:
            pass


def get_platform() -> str:
    """获取当前平台"""
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "darwin":
        return "macos"
    elif system == "linux":
        return "linux"
    return system
