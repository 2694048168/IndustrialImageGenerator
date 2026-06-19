"""应用全局常量。"""

import sys
from pathlib import Path


def _get_version() -> str:
    """从 VERSION 文件读取版本号（开发/打包环境兼容）。"""
    if getattr(sys, "frozen", False):
        # PyInstaller 打包后，VERSION 文件在 sys._MEIPASS 根目录
        version_file = Path(sys._MEIPASS) / "VERSION"
    else:
        # 开发环境，VERSION 在项目根目录
        version_file = Path(__file__).parent.parent / "VERSION"
    return version_file.read_text().strip()


APP_TITLE = "Industrial Image Generator"
APP_VERSION = "v" + _get_version()