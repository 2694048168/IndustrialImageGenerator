#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File: main.py
@Python Version: 3.12.8
@Author: Wei Li (Ithaca)
@Email: weili_yzzcq@163.com
@Blog: https://2694048168.github.io/blog/
@Date: 2026-06-19
@copyright Copyright (c) 2026 Wei Li
@Description: 应用程序入口 - 带进度条启动画面，标题/版本从代码设置
"""

import sys
from pathlib import Path

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen

from utils.logger import get_logger
from database.db_manager import DatabaseManager
from gui.main_window import MainWindow
from config import APP_TITLE


def _get_logo_path() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).parent.parent.parent.parent
    return base / "assets" / "logo.png"


def _get_icon_path() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).parent.parent.parent.parent
    return base / "assets" / "app_icon.ico"


def _get_qss_path() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).parent.parent.parent.parent
    return base / "assets" / "industrial_style.qss"


class SplashScreen(QSplashScreen):
    """带进度文字和代码控制标题/版本的自定义启动画面。"""

    def __init__(self, pixmap: QPixmap):
        super().__init__(pixmap)
        self._progress = 0
        self._steps = [45, 75, 90, 100]
        self._step_idx = 0
        self._done_callback = None

    def start_progress(self, done_callback) -> None:
        self._step_idx = 0
        self._done_callback = done_callback
        self._advance()

    def _advance(self) -> None:
        if self._step_idx < len(self._steps):
            self._progress = self._steps[self._step_idx]
            self._step_idx += 1
            self.repaint()
            QTimer.singleShot(500, self._advance)
        else:
            # 100% 完成，直接回调
            if self._done_callback:
                self._done_callback()

    def drawContents(self, painter: QPainter) -> None:
        super().drawContents(painter)
        w = self.width()
        h = self.height()

        # 标题 — 从代码设置
        painter.setPen(QColor(220, 220, 220))
        title_font = QFont()
        title_font.setPointSize(22)
        title_font.setBold(True)
        painter.setFont(title_font)
        painter.drawText(
            0, int(h * 0.15), w, 300, Qt.AlignmentFlag.AlignCenter, APP_TITLE
        )

        # 进度文字
        painter.setPen(QColor(200, 200, 200))
        prog_font = QFont()
        prog_font.setPointSize(11)
        painter.setFont(prog_font)
        painter.drawText(
            0,
            int(h * 0.72),
            w,
            30,
            Qt.AlignmentFlag.AlignCenter,
            f"正在加载... {self._progress}%",
        )

        # 进度条
        bar_w = int(w * 0.5)
        bar_h = 6
        bar_x = (w - bar_w) // 2
        bar_y = int(h * 0.72) + 35

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(60, 60, 60))
        painter.drawRoundedRect(bar_x, bar_y, bar_w, bar_h, 3, 3)

        painter.setBrush(QColor(0, 120, 212))
        fill_w = int(bar_w * self._progress / 100)
        painter.drawRoundedRect(bar_x, bar_y, fill_w, bar_h, 3, 3)


def main() -> None:
    """主入口函数。"""
    logger = get_logger()
    try:
        app = QApplication(sys.argv)
        app.setApplicationName(APP_TITLE)
        app.setOrganizationName("ImageGenerator")

        # 设置应用图标
        icon_path = _get_icon_path()
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))

        # 加载工业视觉风格 QSS 样式表
        qss_path = _get_qss_path()
        if qss_path.exists():
            app.setStyleSheet(qss_path.read_text(encoding="utf-8"))
            logger.info("QSS 样式表加载成功: {}", qss_path)
        else:
            logger.warning("QSS 样式表未找到: {}", qss_path)

        # 启动画面
        logo_path = _get_logo_path()
        splash = None
        if logo_path.exists():
            pix = QPixmap(str(logo_path)).scaled(
                600,
                300,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            splash = SplashScreen(pix)
            splash.show()
            app.processEvents()

        db = DatabaseManager()
        main_window = MainWindow(db)

        # 设置窗口图标
        if icon_path.exists():
            main_window.setWindowIcon(QIcon(str(icon_path)))

        def _finish():
            main_window.show()
            if splash:
                splash.finish(main_window)

        if splash:
            splash.start_progress(_finish)
        else:
            main_window.show()

        sys.exit(app.exec())
    except Exception as e:
        logger.exception("程序异常退出: {}", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
