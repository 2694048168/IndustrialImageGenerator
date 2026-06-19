"""应用路径工具 - 处理开发环境和 PyInstaller 打包环境的路径差异。"""

import sys
from pathlib import Path


def get_app_dir() -> Path:
    """获取应用程序数据目录。

    打包环境下使用 exe 所在目录；
    开发环境下使用项目根目录。
    """
    if getattr(sys, "frozen", False):
        # PyInstaller 打包环境
        return Path(sys.executable).parent
    # 开发环境：项目根目录
    return Path(__file__).parent.parent.parent.parent


def get_log_dir() -> Path:
    """获取日志目录。"""
    return get_app_dir() / "logs"


def get_data_dir() -> Path:
    """获取数据目录。"""
    return get_app_dir() / "data"
