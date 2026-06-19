#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File: main_window.py
@Python Version: 3.12.8
@Author: Wei Li (Ithaca)
@Email: weili_yzzcq@163.com
@Blog: https://2694048168.github.io/blog/
@Date: 2026-06-19
@copyright Copyright (c) 2026 Wei Li
@Description: 主窗口 - 左右分栏,多线程图像生成,日志回显
"""

import os
import subprocess
import sys
from datetime import datetime

import cv2
import numpy as np
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStatusBar,
    QWidget,
)

from core.image_generator import ImageGenerator
from database.db_manager import DatabaseManager
from database.models import User
from gui.image_preview import ImagePreviewWidget
from gui.login_dialog import LoginDialog
from gui.param_panel import ParamPanel
from config import APP_TITLE, APP_VERSION
from utils.log_signal import LogHandler, LogSignal
from utils.logger import get_logger, logger as loguru_logger
from utils.paths import get_log_dir

logger = get_logger()


class GenerationWorker(QThread):
    """后台线程：执行图像生成。"""

    finished = Signal(np.ndarray)
    error = Signal(str)

    def __init__(self, generator: ImageGenerator, params: dict):
        super().__init__()
        self._generator = generator
        self._params = params

    def run(self) -> None:
        try:
            self._generator.set_resolution(
                self._params["width"], self._params["height"]
            )
            self._generator.set_pixel_size(
                self._params["pixel_size_x"], self._params["pixel_size_y"]
            )
            self._generator.set_generation_config(
                mode=self._params["image_mode"],
                gray_value=self._params["gray_value"],
                r_value=self._params["r_value"],
                g_value=self._params["g_value"],
                b_value=self._params["b_value"],
            )
            image = self._generator.generate(
                shapes=self._params.get("shapes"),
                defects=self._params.get("defects"),
            )
            self.finished.emit(image)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """主窗口。"""

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self._db = db_manager
        self._user: User | None = None
        self._generator = ImageGenerator()
        self._worker: GenerationWorker | None = None
        self._setup_ui()
        self._setup_log_signal()
        self._connect_signals()
        self._log("软件启动完成")
        self._on_generate()

    def _setup_ui(self) -> None:
        self.setWindowTitle("工业图像生成器")
        self.resize(1200, 750)
        self.setMinimumSize(900, 550)

        self._setup_menu_bar()

        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)
        layout.setContentsMargins(6, 6, 6, 6)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(2)

        self._param_panel = ParamPanel()
        self._param_panel.setMinimumWidth(260)
        self._param_panel.setMaximumWidth(350)
        splitter.addWidget(self._param_panel)

        self._preview_panel = ImagePreviewWidget()
        splitter.addWidget(self._preview_panel)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([280, 900])

        layout.addWidget(splitter)

        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage("就绪 — 请先登录管理员账户以解锁高级参数")

    def _setup_log_signal(self) -> None:
        """设置 loguru → Qt 信号桥接。"""
        self._log_signal = LogSignal()
        self._log_signal.new_log.connect(self._preview_panel.append_log)
        handler = LogHandler(self._log_signal)
        loguru_logger.add(
            handler,
            format="{time:HH:mm:ss} | {level: <8} | {message}",
            level="INFO",
        )

    def _setup_menu_bar(self) -> None:
        menu_bar = self.menuBar()
        login_action = menu_bar.addAction("用户登录")
        login_action.triggered.connect(self._on_login)
        logs_action = menu_bar.addAction("查看日志")
        logs_action.triggered.connect(self._on_open_logs)
        about_action = menu_bar.addAction("关于")
        about_action.triggered.connect(self._on_about)

    def _connect_signals(self) -> None:
        self._param_panel.generate_requested.connect(self._on_generate)
        self._param_panel.save_requested.connect(self._on_save)
        self._param_panel.admin_required.connect(self._on_admin_required)

    def _log(self, message: str) -> None:
        """记录用户操作日志。"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        user_info = f"[{self._user.username}]" if self._user else "[未登录]"
        logger.info("{} {}", user_info, message)

    # ===================== 菜单操作 =====================

    def _on_login(self) -> None:
        dialog = LoginDialog(self._db, self)
        if dialog.exec() == LoginDialog.DialogCode.Accepted:
            self._user = dialog.get_user()
            if self._user:
                is_admin = self._user.is_admin
                self._param_panel.set_admin(is_admin)
                self.setWindowTitle(
                    f"工业图像生成器 - {self._user.username} [{self._user.role}]"
                )
                role_label = "管理员" if is_admin else "普通用户"
                self._status_bar.showMessage(
                    f"已登录: {self._user.username} ({role_label})"
                    + (" — 高级参数已解锁" if is_admin else " — 高级参数需要管理员权限")
                )
                self._log(f"用户登录: {self._user.username} (角色: {role_label})")

    def _on_open_logs(self) -> None:
        log_dir = str(get_log_dir())
        os.makedirs(log_dir, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(log_dir)
        elif sys.platform == "darwin":
            subprocess.run(["open", log_dir])
        else:
            subprocess.run(["xdg-open", log_dir])
        self._log("打开日志文件夹")

    def _on_about(self) -> None:
        """显示关于对话框。"""
        about_text = (
            f"<h2>{APP_TITLE}</h2>"
            f"<p><b>版本：</b>{APP_VERSION}</p>"
            f"<hr>"
            f"<p>工业图像生成器是一款用于模拟工业相机采集图像过程的桌面软件。</p>"
            f"<p>支持自定义图像分辨率、单像素精度、视场范围(FOV)等参数，"
            f"可叠加常见的工业形状（圆形、矩形、三角形）和缺陷类型"
            f"（划痕、沾污、黑点、气泡），生成逼真的工业检测图像。</p>"
            f"<p><b>技术栈：</b>Python + OpenCV + PySide6 + NumPy + loguru + SQLite</p>"
        )
        QMessageBox.about(self, f"关于 {APP_TITLE}", about_text)

    def _on_admin_required(self) -> None:
        """非管理员尝试访问高级功能时的提示。"""
        admins = self._db.get_admin_users()
        admin_names = "、".join(u.username for u in admins) if admins else "无"
        msg = (
            f"高级功能（形状叠加 / 缺陷叠加）需要管理员权限，请先登录管理员账户。\n\n"
            f"管理员账户：{admin_names}\n"
            f"默认密码: admin123"
        )
        self._status_bar.showMessage("高级功能需要管理员权限，请先登录")
        self._log("尝试访问高级功能被拒绝（未登录管理员）")
        QMessageBox.warning(self, "权限不足", msg)

    # ===================== 图像生成（多线程） =====================

    def _on_generate(self) -> None:
        """通过后台线程生成图像。"""
        self._param_panel._generate_btn.setEnabled(False)
        self._status_bar.showMessage("图像生成中...")
        QApplication.processEvents()

        params = self._param_panel.get_params()
        self._log(
            f"生成图像: {params['width']}×{params['height']}, "
            f"模式={'灰度' if params['image_mode'] == 'gray' else 'RGB'}, "
            f"形状×{len(params.get('shapes', []))}, 缺陷×{len(params.get('defects', []))}"
        )

        self._worker = GenerationWorker(self._generator, params)
        self._worker.finished.connect(self._on_generation_done)
        self._worker.error.connect(self._on_generation_error)
        self._worker.start()

    def _on_generation_done(self, image: np.ndarray) -> None:
        """后台线程生成完成。"""
        self._preview_panel.set_image(image)
        self._param_panel._generate_btn.setEnabled(True)

        params = self._param_panel.get_params()
        mode_label = "灰度" if params["image_mode"] == "gray" else "RGB"
        color_info = (
            f"灰度={params['gray_value']}"
            if params["image_mode"] == "gray"
            else f"R={params['r_value']} G={params['g_value']} B={params['b_value']}"
        )
        shape_count = len(params.get("shapes", []))
        defect_count = len(params.get("defects", []))
        msg = (
            f"图像已生成: {params['width']}×{params['height']} px | "
            f"{mode_label} | {color_info} | "
            f"形状×{shape_count} 缺陷×{defect_count} | "
            f"精度: {params['pixel_size_x']:.4f}×{params['pixel_size_y']:.4f} mm/px"
        )
        self._status_bar.showMessage(msg)
        self._log("图像生成完成")

    def _on_generation_error(self, error_msg: str) -> None:
        """后台线程生成出错。"""
        self._param_panel._generate_btn.setEnabled(True)
        self._status_bar.showMessage(f"生成失败: {error_msg}")
        self._log(f"图像生成失败: {error_msg}")

    # ===================== 保存图像 =====================

    def _on_save(self) -> None:
        """保存当前图像到文件。"""
        image = self._generator.image
        if image is None:
            QMessageBox.warning(self, "提示", "请先生成图像。")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存图像",
            "generated_image.png",
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp);;All Files (*)",
        )
        if not file_path:
            return

        try:
            cv2.imwrite(file_path, image)
            self._status_bar.showMessage(f"图像已保存: {file_path}")
            self._log(f"图像已保存: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"保存图像失败:\n{e}")
            self._log(f"保存失败: {e}")
