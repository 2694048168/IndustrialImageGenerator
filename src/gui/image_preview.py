#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File: image_preview.py
@Python Version: 3.12.8
@Author: Wei Li (Ithaca)
@Email: weili_yzzcq@163.com
@Blog: https://2694048168.github.io/blog/
@Date: 2026-06-19
@copyright Copyright (c) 2026 Wei Li
@Description: 右侧图像预览面板 - 支持缩放、像素网格和像素信息实时显示
"""

import cv2
import numpy as np
from PySide6.QtCore import QEvent, QRectF, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPen, QPixmap, QWheelEvent
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

_PIXEL_GRID_ZOOM_THRESHOLD = 2.0  # 放大到 200% 以上显示像素格子


class PixelGridItem(QGraphicsItem):
    """像素网格叠加层，高倍放大时显示像素边界。"""

    def __init__(self, w: int, h: int):
        super().__init__()
        self._w = w
        self._h = h
        self.setZValue(1)  # 在图像上方

    def set_grid_size(self, w: int, h: int) -> None:
        self.prepareGeometryChange()
        self._w = w
        self._h = h

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self._w, self._h)

    def paint(self, painter: QPainter, option, widget=None) -> None:
        painter.setPen(QPen(QColor(255, 255, 255, 60), 0))
        # 水平线
        for y in range(self._h + 1):
            painter.drawLine(0, y, self._w, y)
        # 垂直线
        for x in range(self._w + 1):
            painter.drawLine(x, 0, x, self._h)


class ImagePreviewWidget(QWidget):
    """图像预览组件，支持鼠标滚轮缩放和像素信息显示。"""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._zoom_factor = 1.0
        self._min_zoom = 0.1
        self._max_zoom = 10.0
        self._original_image: np.ndarray | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # 图像显示区域
        self._scene = QGraphicsScene(self)
        self._view = QGraphicsView(self._scene)
        self._view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self._view.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )
        self._view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self._view.setBackgroundBrush(Qt.GlobalColor.black)
        self._view.setMouseTracking(True)
        self._view.viewport().installEventFilter(self)

        self._pixmap_item = QGraphicsPixmapItem()
        self._scene.addItem(self._pixmap_item)

        self._grid_item = PixelGridItem(0, 0)
        self._grid_item.setVisible(False)
        self._scene.addItem(self._grid_item)

        layout.addWidget(self._view)

        # 底部状态栏
        status_layout = QHBoxLayout()
        status_layout.setSpacing(16)

        self._pos_label = QLabel("X: --  Y: --")
        self._pos_label.setStyleSheet("font-family: Consolas; font-size: 13px;")
        self._pos_label.setMinimumWidth(180)

        self._gray_label = QLabel("Gray: --")
        self._gray_label.setStyleSheet("font-family: Consolas; font-size: 13px;")
        self._gray_label.setMinimumWidth(100)

        self._rgb_label = QLabel("R: --  G: --  B: --")
        self._rgb_label.setStyleSheet("font-family: Consolas; font-size: 13px;")

        self._zoom_label = QLabel("Zoom: 100%")
        self._zoom_label.setStyleSheet(
            "font-family: Consolas; font-size: 13px; color: #666;"
        )

        status_layout.addWidget(self._pos_label)
        status_layout.addWidget(self._gray_label)
        status_layout.addWidget(self._rgb_label)
        status_layout.addStretch()
        status_layout.addWidget(self._zoom_label)

        layout.addLayout(status_layout)

        # 日志回显区域
        self._log_area = QPlainTextEdit()
        self._log_area.setReadOnly(True)
        self._log_area.setMaximumBlockCount(500)
        self._log_area.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #cccccc;
                font-family: Consolas, monospace;
                font-size: 11px;
                border: 1px solid #333;
            }
        """)
        self._log_area.setMaximumHeight(120)
        layout.addWidget(self._log_area)

    def append_log(self, message: str) -> None:
        """追加日志到回显区域。"""
        self._log_area.appendPlainText(message)
        sb = self._log_area.verticalScrollBar()
        sb.setValue(sb.maximum())

    def set_image(self, image: np.ndarray) -> None:
        """设置要显示的图像（OpenCV 格式）。"""
        if image is None:
            return

        self._original_image = image.copy()

        if len(image.shape) == 2:
            h, w = image.shape
            qimg = QImage(image.tobytes(), w, h, w, QImage.Format.Format_Grayscale8)
        else:
            h, w, ch = image.shape
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            qimg = QImage(rgb.tobytes(), w, h, ch * w, QImage.Format.Format_RGB888)

        self._scene.setSceneRect(0, 0, w, h)
        self._pixmap_item.setPixmap(QPixmap.fromImage(qimg))
        self._grid_item.set_grid_size(w, h)
        self._grid_item.setVisible(self._zoom_factor >= _PIXEL_GRID_ZOOM_THRESHOLD)
        self._view.fitInView(
            self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio
        )
        self._zoom_factor = self._view.transform().m11()
        self._zoom_factor = max(self._min_zoom, min(self._max_zoom, self._zoom_factor))
        self._update_zoom_label()

    def eventFilter(self, obj, event) -> bool:
        """事件过滤器：处理鼠标移动（更新像素信息）和滚轮（缩放）。"""
        if obj is self._view.viewport():
            if event.type() == QEvent.Type.MouseMove:
                self._update_pixel_info(event)
            elif event.type() == QEvent.Type.Wheel:
                self._handle_zoom(event)
        return super().eventFilter(obj, event)

    def _handle_zoom(self, event: QWheelEvent) -> None:
        """处理鼠标滚轮缩放。"""
        zoom_in = event.angleDelta().y() > 0
        factor = 1.15 if zoom_in else 1 / 1.15
        new_zoom = self._zoom_factor * factor

        if self._min_zoom <= new_zoom <= self._max_zoom:
            self._zoom_factor = new_zoom
            self._view.scale(factor, factor)
            self._grid_item.setVisible(self._zoom_factor >= _PIXEL_GRID_ZOOM_THRESHOLD)
            self._update_zoom_label()

    def _update_pixel_info(self, event) -> None:
        """更新鼠标位置下的像素信息。"""
        if self._original_image is None:
            return

        scene_pos = self._view.mapToScene(event.position().toPoint())
        x, y = int(scene_pos.x()), int(scene_pos.y())

        h, w = self._original_image.shape[:2]
        if 0 <= x < w and 0 <= y < h:
            self._pos_label.setText(f"X: {x}  Y: {y}")
            if len(self._original_image.shape) == 2:
                gray = int(self._original_image[y, x])
                self._gray_label.setText(f"Gray: {gray}")
                self._rgb_label.setText(f"R: {gray}  G: {gray}  B: {gray}")
            else:
                b, g, r = [int(c) for c in self._original_image[y, x]]
                gray = int(0.299 * r + 0.587 * g + 0.114 * b)
                self._gray_label.setText(f"Gray: {gray}")
                self._rgb_label.setText(f"R: {r}  G: {g}  B: {b}")
        else:
            self._pos_label.setText("X: --  Y: --")
            self._gray_label.setText("Gray: --")
            self._rgb_label.setText("R: --  G: --  B: --")

    def _update_zoom_label(self) -> None:
        self._zoom_label.setText(f"Zoom: {self._zoom_factor * 100:.0f}%")
