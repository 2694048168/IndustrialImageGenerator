"""打包构建脚本 - 使用 PyInstaller 生成独立 exe 程序。"""

import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
ASSETS_DIR = PROJECT_ROOT / "assets"
MAIN_SCRIPT = SRC_DIR / "main.py"
OUTPUT_DIR = PROJECT_ROOT / "dist"
NAME = "工业图像生成器"
ICO_PATH = ASSETS_DIR / "app_icon.ico"


def ensure_pyinstaller() -> None:
    """确保 PyInstaller 已安装。"""
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("PyInstaller 未安装，正在安装...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pyinstaller"]
        )


def build() -> None:
    """执行打包构建。"""
    ensure_pyinstaller()

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", NAME,
        "--distpath", str(OUTPUT_DIR),
        "--workpath", str(PROJECT_ROOT / "build"),
        "--specpath", str(PROJECT_ROOT),
        "--clean",
        "--noconfirm",
    ]

    if ICO_PATH.exists():
        cmd += ["--icon", str(ICO_PATH)]

    # 添加 assets 目录
    logo_path = ASSETS_DIR / "logo.png"
    if logo_path.exists():
        cmd += ["--add-data", f"{logo_path}{os.pathsep}assets"]
    ico_path = ASSETS_DIR / "app_icon.ico"
    if ico_path.exists():
        cmd += ["--add-data", f"{ico_path}{os.pathsep}assets"]

    cmd += [
        "--hidden-import", "loguru._file_sink",
        "--hidden-import", "loguru._recattrs",
        "--hidden-import", "loguru._datetime",
        "--hidden-import", "loguru._ctime_functions",
        "--hidden-import", "win32_setctime",
        str(MAIN_SCRIPT),
    ]

    print(f"开始打包: {NAME}")
    print(f"输出目录: {OUTPUT_DIR}")
    print("-" * 60)

    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    if result.returncode == 0:
        exe_path = OUTPUT_DIR / f"{NAME}.exe"
        print("-" * 60)
        print(f"打包成功: {exe_path}")
    else:
        print("打包失败，请检查上方错误信息。")
        sys.exit(result.returncode)


if __name__ == "__main__":
    build()