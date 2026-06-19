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
NAME_EN = "IndustrialImageGenerator"
ICO_PATH = ASSETS_DIR / "app_icon.ico"
VERSION_FILE = PROJECT_ROOT / "VERSION"


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
    """执行打包构建，生成中文和英文两个 exe。"""
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
    # VERSION 文件
    if VERSION_FILE.exists():
        cmd += ["--add-data", f"{VERSION_FILE}{os.pathsep}."]

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
        exe_cn = OUTPUT_DIR / f"{NAME}.exe"
        exe_en = OUTPUT_DIR / f"{NAME_EN}.exe"
        print("-" * 60)
        print(f"中文版: {exe_cn}")

        # 复制生成英文版（内容相同，仅文件名不同）
        import shutil
        shutil.copy2(exe_cn, exe_en)
        print(f"英文版: {exe_en}")
        print("打包成功")
    else:
        print("打包失败，请检查上方错误信息。")
        sys.exit(result.returncode)


if __name__ == "__main__":
    build()