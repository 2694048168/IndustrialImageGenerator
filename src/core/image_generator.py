#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
@File: image_generator.py
@Python Version: 3.12.8
@Author: Wei Li (Ithaca)
@Email: weili_yzzcq@163.com
@Blog: https://2694048168.github.io/blog/
@Date: 2026-06-19
@copyright Copyright (c) 2026 Wei Li
@Description: 图像生成核心模块 - 基于 OpenCV 生成工业检测图像
'''

import random

import cv2
import numpy as np


class ImageGenerator:
    """工业图像生成器，模拟工业相机采集图像。"""

    def __init__(self):
        self._width: int = 640
        self._height: int = 480
        self._pixel_size_x: float = 0.01
        self._pixel_size_y: float = 0.01
        self._image: np.ndarray | None = None
        self._mode: str = "gray"
        self._gray_value: int = 128
        self._r_value: int = 128
        self._g_value: int = 128
        self._b_value: int = 128

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def pixel_size_x(self) -> float:
        return self._pixel_size_x

    @property
    def pixel_size_y(self) -> float:
        return self._pixel_size_y

    @property
    def image(self) -> np.ndarray | None:
        return self._image

    def set_resolution(self, width: int, height: int) -> None:
        self._width = max(1, width)
        self._height = max(1, height)

    def set_pixel_size(self, size_x: float, size_y: float) -> None:
        self._pixel_size_x = max(0.0, size_x)
        self._pixel_size_y = max(0.0, size_y)

    def set_generation_config(
        self,
        mode: str,
        gray_value: int = 128,
        r_value: int = 128,
        g_value: int = 128,
        b_value: int = 128,
    ) -> None:
        self._mode = mode
        self._gray_value = np.clip(gray_value, 0, 255)
        self._r_value = np.clip(r_value, 0, 255)
        self._g_value = np.clip(g_value, 0, 255)
        self._b_value = np.clip(b_value, 0, 255)

    def _get_color(self, gray: int, r: int = 0, g: int = 0, b: int = 0):
        """根据当前图像模式返回 Python int 颜色值。"""
        if self._mode == "gray":
            return int(np.clip(gray, 0, 255))
        return (int(np.clip(b, 0, 255)), int(np.clip(g, 0, 255)), int(np.clip(r, 0, 255)))

    def generate(
        self,
        shapes: list[dict] | None = None,
        defects: list[dict] | None = None,
    ) -> np.ndarray:
        """生成工业图像：纯色背景 + 形状叠加 + 缺陷叠加。"""
        h, w = self._height, self._width

        # 1. 纯色背景
        if self._mode == "gray":
            image = np.full((h, w), self._gray_value, dtype=np.uint8)
        else:
            image = np.zeros((h, w, 3), dtype=np.uint8)
            image[:, :] = (self._b_value, self._g_value, self._r_value)

        # 2. 叠加形状
        if shapes:
            for shape in shapes:
                self._draw_shape(image, shape)

        # 3. 叠加缺陷
        if defects:
            for defect in defects:
                self._draw_defects(image, defect)

        self._image = image
        return image

    # --- 形状绘制 ---

    def _draw_shape(self, image: np.ndarray, shape: dict) -> None:
        """在图像上绘制指定的形状。"""
        shape_type = shape.get("type", "circle")
        x = int(shape.get("x", 0))
        y = int(shape.get("y", 0))
        size = max(1, int(shape.get("size", 50)))
        color = self._get_color(
            shape.get("gray", 200),
            shape.get("r", 200),
            shape.get("g", 200),
            shape.get("b", 200),
        )
        thickness = -1  # 填充

        if shape_type == "circle":
            cv2.circle(image, (x, y), size // 2, color, thickness)
        elif shape_type == "rectangle":
            rw = max(1, int(shape.get("width", size)))
            rh = max(1, int(shape.get("height", size)))
            cv2.rectangle(image, (x, y), (x + rw, y + rh), color, thickness)
        elif shape_type == "triangle":
            half = size // 2
            pts = np.array(
                [[x, y - half], [x - half, y + half], [x + half, y + half]],
                dtype=np.int32,
            )
            cv2.fillPoly(image, [pts], color)

    # --- 缺陷绘制 ---

    def _draw_defects(self, image: np.ndarray, defect: dict) -> None:
        """在图像随机位置生成指定类型的缺陷。"""
        defect_type = defect.get("type", "scratch")
        count = int(defect.get("count", 1))
        min_size = max(1, int(defect.get("min_size", 5)))
        max_size = max(min_size, int(defect.get("max_size", 20)))
        color = self._get_color(
            defect.get("gray", 0),
            defect.get("r", 0),
            defect.get("g", 0),
            defect.get("b", 0),
        )
        h, w = image.shape[:2]

        for _ in range(count):
            rx = random.randint(0, w - 1)
            ry = random.randint(0, h - 1)
            size = random.randint(min_size, max_size)

            if defect_type == "scratch":
                self._draw_scratch(image, rx, ry, size, color)
            elif defect_type == "stain":
                self._draw_stain(image, rx, ry, size, color)
            elif defect_type == "spot":
                self._draw_spot(image, rx, ry, size, color)
            elif defect_type == "bubble":
                self._draw_bubble(image, rx, ry, size, color)

    def _draw_scratch(self, image: np.ndarray, x: int, y: int, size: int, color) -> None:
        """绘制划痕：随机角度的线段。"""
        angle = random.uniform(0, 2 * np.pi)
        length = size * random.uniform(1, 3)
        dx = int(length * np.cos(angle))
        dy = int(length * np.sin(angle))
        x2 = np.clip(x + dx, 0, image.shape[1] - 1)
        y2 = np.clip(y + dy, 0, image.shape[0] - 1)
        thickness = max(1, size // 5)
        cv2.line(image, (x, y), (x2, y2), color, thickness)

    def _draw_stain(self, image: np.ndarray, x: int, y: int, size: int, color) -> None:
        """绘制沾污：随机角度的椭圆。"""
        axes = (size // 2, size // 3)
        angle = random.randint(0, 360)
        cv2.ellipse(image, (x, y), axes, angle, 0, 360, color, -1)

    def _draw_spot(self, image: np.ndarray, x: int, y: int, size: int, color) -> None:
        """绘制黑点：小圆点，可带轻微模糊边缘。"""
        radius = max(1, size // 2)
        cv2.circle(image, (x, y), radius, color, -1)

    def _draw_bubble(self, image: np.ndarray, x: int, y: int, size: int, color) -> None:
        """绘制气泡：空心圆。"""
        radius = max(1, size // 2)
        thickness = max(1, size // 10)
        cv2.circle(image, (x, y), radius, color, thickness)

    def get_pixel_info(self, x: int, y: int) -> dict:
        """获取指定坐标的像素信息。"""
        if self._image is None:
            return {"x": x, "y": y, "gray": 0, "r": 0, "g": 0, "b": 0}
        x = max(0, min(x, self._width - 1))
        y = max(0, min(y, self._height - 1))
        if len(self._image.shape) == 2:
            gray = int(self._image[y, x])
            return {"x": x, "y": y, "gray": gray, "r": gray, "g": gray, "b": gray}
        b, g, r = [int(c) for c in self._image[y, x]]
        gray = int(0.299 * r + 0.587 * g + 0.114 * b)
        return {"x": x, "y": y, "gray": gray, "r": r, "g": g, "b": b}