#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File: param_panel.py
@Python Version: 3.12.8
@Author: Wei Li (Ithaca)
@Email: weili_yzzcq@163.com
@Blog: https://2694048168.github.io/blog/
@Date: 2026-06-19
@copyright Copyright (c) 2026 Wei Li
@Description: 左侧参数设置面板 - 三 Tab 布局,按钮独立于 Tab 之外
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class ParamPanel(QWidget):
    """参数设置面板。"""

    params_changed = Signal(dict)
    generate_requested = Signal()
    save_requested = Signal()
    admin_required = Signal()     # 非管理员点击高级功能时发出
    image_load_requested = Signal()  # 用户请求加载底图
    clear_base_requested = Signal()  # 用户请求清除底图

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._shapes: list[dict] = []
        self._defects: list[dict] = []
        self._is_admin = False
        self._setup_ui()

    def set_admin(self, is_admin: bool) -> None:
        """设置管理员权限。"""
        self._is_admin = is_admin

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Tab 控件
        self._tabs = QTabWidget()
        self._tabs.addTab(self._build_basic_tab(), "基础参数")
        self._tabs.addTab(self._build_shapes_tab(), "形状叠加")
        self._tabs.addTab(self._build_defects_tab(), "缺陷叠加")
        self._tabs.currentChanged.connect(self._on_tab_changed)
        layout.addWidget(self._tabs)

        # 按钮独立于 Tab 之外
        layout.addLayout(self._build_button_row())

        self._connect_all_signals()

    # ===================== Tab 构建 =====================

    def _build_basic_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(10)

        layout.addWidget(self._build_resolution_group())
        layout.addWidget(self._build_precision_group())
        layout.addWidget(self._build_config_group())
        layout.addWidget(self._build_fov_group())
        layout.addWidget(self._build_image_load_group())
        layout.addStretch()

        scroll.setWidget(content)
        return scroll

    def _build_shapes_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(10)
        layout.addWidget(self._build_shapes_group())
        layout.addStretch()
        scroll.setWidget(content)
        return scroll

    def _build_defects_tab(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(10)
        layout.addWidget(self._build_defects_group())
        layout.addStretch()
        scroll.setWidget(content)
        return scroll

    # ===================== Group 构建 =====================

    def _build_resolution_group(self) -> QGroupBox:
        group = QGroupBox("图像分辨率")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)
        self._width_spin = self._create_spinbox(0, 999999, 640)
        layout.addLayout(self._make_param_row("宽度 (W)", "px", self._width_spin))
        self._height_spin = self._create_spinbox(0, 999999, 480)
        layout.addLayout(self._make_param_row("高度 (H)", "px", self._height_spin))
        return group

    def _build_precision_group(self) -> QGroupBox:
        group = QGroupBox("单像素精度")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)
        self._pixel_size_x_spin = self._create_double_spinbox(0.0, 1.0, 0.01, 4)
        layout.addLayout(
            self._make_param_row("X 轴精度", "mm/px", self._pixel_size_x_spin)
        )
        self._pixel_size_y_spin = self._create_double_spinbox(0.0, 1.0, 0.01, 4)
        layout.addLayout(
            self._make_param_row("Y 轴精度", "mm/px", self._pixel_size_y_spin)
        )
        return group

    def _build_config_group(self) -> QGroupBox:
        group = QGroupBox("生成配置")
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        type_layout = QHBoxLayout()
        type_layout.setSpacing(6)
        type_layout.addWidget(QLabel("图像类型"))
        self._image_type_combo = QComboBox()
        self._image_type_combo.addItems(["灰度图", "RGB 彩色图"])
        self._image_type_combo.setFixedWidth(110)
        type_layout.addWidget(self._image_type_combo)
        type_layout.addStretch()
        layout.addLayout(type_layout)

        self._gray_value_widget = QWidget()
        gl = QHBoxLayout(self._gray_value_widget)
        gl.setContentsMargins(0, 0, 0, 0)
        gl.setSpacing(6)
        gl.addWidget(QLabel("灰度值"))
        self._gray_value_spin = self._create_spinbox(0, 255, 128)
        gl.addWidget(self._gray_value_spin)
        gl.addStretch()
        layout.addWidget(self._gray_value_widget)

        self._rgb_value_widget = QWidget()
        rl = QVBoxLayout(self._rgb_value_widget)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(6)
        self._r_spin = self._create_spinbox(0, 255, 128)
        rl.addLayout(self._make_param_row("R", "", self._r_spin))
        self._g_spin = self._create_spinbox(0, 255, 128)
        rl.addLayout(self._make_param_row("G", "", self._g_spin))
        self._b_spin = self._create_spinbox(0, 255, 128)
        rl.addLayout(self._make_param_row("B", "", self._b_spin))
        self._rgb_value_widget.setVisible(False)
        layout.addWidget(self._rgb_value_widget)

        return group

    def _build_shapes_group(self) -> QGroupBox:
        group = QGroupBox("形状叠加 — 需管理员权限")
        layout = QVBoxLayout(group)
        layout.setSpacing(6)

        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("类型"))
        self._shape_type_combo = QComboBox()
        self._shape_type_combo.addItems(["圆形", "矩形", "三角形"])
        self._shape_type_combo.setFixedWidth(90)
        self._shape_type_combo.currentIndexChanged.connect(self._on_shape_type_changed)
        type_row.addWidget(self._shape_type_combo)
        type_row.addStretch()
        layout.addLayout(type_row)

        self._shape_x_spin = self._create_spinbox(0, 999999, 100)
        layout.addLayout(self._make_param_row("位置 X", "px", self._shape_x_spin))
        self._shape_y_spin = self._create_spinbox(0, 999999, 100)
        layout.addLayout(self._make_param_row("位置 Y", "px", self._shape_y_spin))

        # 圆形/三角形：大小；矩形：宽 + 高
        self._shape_size_widget = QWidget()
        ssl = QHBoxLayout(self._shape_size_widget)
        ssl.setContentsMargins(0, 0, 0, 0)
        ssl.setSpacing(6)
        self._shape_size_spin = self._create_spinbox(1, 9999, 50)
        ssl.addLayout(self._make_param_row("大小", "px", self._shape_size_spin))
        layout.addWidget(self._shape_size_widget)

        self._shape_rect_widget = QWidget()
        srl2 = QVBoxLayout(self._shape_rect_widget)
        srl2.setContentsMargins(0, 0, 0, 0)
        srl2.setSpacing(4)
        self._shape_width_spin = self._create_spinbox(1, 9999, 50)
        srl2.addLayout(self._make_param_row("宽度", "px", self._shape_width_spin))
        self._shape_height_spin = self._create_spinbox(1, 9999, 50)
        srl2.addLayout(self._make_param_row("高度", "px", self._shape_height_spin))
        self._shape_rect_widget.setVisible(False)
        layout.addWidget(self._shape_rect_widget)

        self._shape_gray_widget = QWidget()
        sgl = QHBoxLayout(self._shape_gray_widget)
        sgl.setContentsMargins(0, 0, 0, 0)
        sgl.setSpacing(6)
        sgl.addWidget(QLabel("灰度"))
        self._shape_gray_spin = self._create_spinbox(0, 255, 200)
        sgl.addWidget(self._shape_gray_spin)
        sgl.addStretch()
        layout.addWidget(self._shape_gray_widget)

        self._shape_rgb_widget = QWidget()
        srl = QVBoxLayout(self._shape_rgb_widget)
        srl.setContentsMargins(0, 0, 0, 0)
        srl.setSpacing(4)
        self._shape_r_spin = self._create_spinbox(0, 255, 200)
        srl.addLayout(self._make_param_row("R", "", self._shape_r_spin))
        self._shape_g_spin = self._create_spinbox(0, 255, 200)
        srl.addLayout(self._make_param_row("G", "", self._shape_g_spin))
        self._shape_b_spin = self._create_spinbox(0, 255, 200)
        srl.addLayout(self._make_param_row("B", "", self._shape_b_spin))
        self._shape_rgb_widget.setVisible(False)
        layout.addWidget(self._shape_rgb_widget)

        add_btn = QPushButton("+ 添加形状")
        add_btn.setMinimumHeight(28)
        add_btn.clicked.connect(self._on_add_shape)
        layout.addWidget(add_btn)

        self._shape_list = QListWidget()
        self._shape_list.setMaximumHeight(80)
        layout.addWidget(self._shape_list)

        del_row = QHBoxLayout()
        del_row.setSpacing(6)
        del_btn = QPushButton("删除选中")
        del_btn.setMinimumHeight(28)
        del_btn.clicked.connect(self._on_remove_shape)
        del_row.addWidget(del_btn)
        clear_all_btn = QPushButton("删除所有")
        clear_all_btn.setMinimumHeight(28)
        clear_all_btn.clicked.connect(self._on_remove_all_shapes)
        del_row.addWidget(clear_all_btn)
        del_row.addStretch()
        layout.addLayout(del_row)

        return group

    def _build_defects_group(self) -> QGroupBox:
        group = QGroupBox("缺陷叠加 — 需管理员权限")
        layout = QVBoxLayout(group)
        layout.setSpacing(6)

        type_row = QHBoxLayout()
        type_row.addWidget(QLabel("类型"))
        self._defect_type_combo = QComboBox()
        self._defect_type_combo.addItems(["划痕", "沾污", "黑点", "气泡"])
        self._defect_type_combo.setFixedWidth(90)
        type_row.addWidget(self._defect_type_combo)
        type_row.addStretch()
        layout.addLayout(type_row)

        self._defect_count_spin = self._create_spinbox(1, 999, 1)
        layout.addLayout(self._make_param_row("数量", "个", self._defect_count_spin))
        self._defect_min_spin = self._create_spinbox(1, 9999, 5)
        layout.addLayout(self._make_param_row("最小尺寸", "px", self._defect_min_spin))
        self._defect_max_spin = self._create_spinbox(1, 9999, 20)
        layout.addLayout(self._make_param_row("最大尺寸", "px", self._defect_max_spin))

        self._defect_gray_widget = QWidget()
        dgl = QHBoxLayout(self._defect_gray_widget)
        dgl.setContentsMargins(0, 0, 0, 0)
        dgl.setSpacing(6)
        dgl.addWidget(QLabel("灰度"))
        self._defect_gray_spin = self._create_spinbox(0, 255, 0)
        dgl.addWidget(self._defect_gray_spin)
        dgl.addStretch()
        layout.addWidget(self._defect_gray_widget)

        self._defect_rgb_widget = QWidget()
        drl = QVBoxLayout(self._defect_rgb_widget)
        drl.setContentsMargins(0, 0, 0, 0)
        drl.setSpacing(4)
        self._defect_r_spin = self._create_spinbox(0, 255, 0)
        drl.addLayout(self._make_param_row("R", "", self._defect_r_spin))
        self._defect_g_spin = self._create_spinbox(0, 255, 0)
        drl.addLayout(self._make_param_row("G", "", self._defect_g_spin))
        self._defect_b_spin = self._create_spinbox(0, 255, 0)
        drl.addLayout(self._make_param_row("B", "", self._defect_b_spin))
        self._defect_rgb_widget.setVisible(False)
        layout.addWidget(self._defect_rgb_widget)

        add_btn = QPushButton("+ 添加缺陷")
        add_btn.setMinimumHeight(28)
        add_btn.clicked.connect(self._on_add_defect)
        layout.addWidget(add_btn)

        self._defect_list = QListWidget()
        self._defect_list.setMaximumHeight(80)
        layout.addWidget(self._defect_list)

        del_row = QHBoxLayout()
        del_row.setSpacing(6)
        del_btn = QPushButton("删除选中")
        del_btn.setMinimumHeight(28)
        del_btn.clicked.connect(self._on_remove_defect)
        del_row.addWidget(del_btn)
        clear_all_btn = QPushButton("删除所有")
        clear_all_btn.setMinimumHeight(28)
        clear_all_btn.clicked.connect(self._on_remove_all_defects)
        del_row.addWidget(clear_all_btn)
        del_row.addStretch()
        layout.addLayout(del_row)

        return group

    def _build_fov_group(self) -> QGroupBox:
        group = QGroupBox("视场范围 (FOV)")
        layout = QVBoxLayout(group)
        self._fov_label = QLabel("FOV: 6.40 × 4.80 mm")
        self._fov_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self._fov_label)
        return group

    def _build_image_load_group(self) -> QGroupBox:
        group = QGroupBox("底图加载（数据集增强）")
        layout = QVBoxLayout(group)
        layout.setSpacing(6)

        self._base_image_label = QLabel("未加载底图")
        self._base_image_label.setStyleSheet("color: #888; font-size: 11px;")
        self._base_image_label.setWordWrap(True)
        layout.addWidget(self._base_image_label)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        self._load_image_btn = QPushButton("加载图像")
        self._load_image_btn.setMinimumHeight(28)
        self._load_image_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._load_image_btn.clicked.connect(self.image_load_requested.emit)
        btn_row.addWidget(self._load_image_btn)

        self._clear_base_btn = QPushButton("清除底图")
        self._clear_base_btn.setMinimumHeight(28)
        self._clear_base_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._clear_base_btn.setVisible(False)
        self._clear_base_btn.clicked.connect(self.clear_base_requested.emit)
        btn_row.addWidget(self._clear_base_btn)

        btn_row.addStretch()
        layout.addLayout(btn_row)
        return group

    def set_base_image_loaded(self, file_path: str, width: int, height: int, mode: str) -> None:
        """底图加载成功后更新 UI：锁定分辨率/类型，显示文件信息。"""
        import os
        self._base_image_label.setText(f"已加载: {os.path.basename(file_path)}\n{width}×{height} px | {'灰度' if mode == 'gray' else 'RGB'}")
        self._base_image_label.setStyleSheet("color: #4caf50; font-size: 11px;")
        self._load_image_btn.setVisible(False)
        self._clear_base_btn.setVisible(True)

        # 锁定分辨率与图像类型
        self._width_spin.setEnabled(False)
        self._height_spin.setEnabled(False)
        self._image_type_combo.setEnabled(False)
        self._gray_value_spin.setEnabled(False)
        self._r_spin.setEnabled(False)
        self._g_spin.setEnabled(False)
        self._b_spin.setEnabled(False)

        # 同步显示值
        self._width_spin.setValue(width)
        self._height_spin.setValue(height)
        self._image_type_combo.setCurrentIndex(0 if mode == "gray" else 1)

    def clear_base_image_state(self) -> None:
        """清除底图后恢复 UI：解锁分辨率/类型。"""
        self._base_image_label.setText("未加载底图")
        self._base_image_label.setStyleSheet("color: #888; font-size: 11px;")
        self._load_image_btn.setVisible(True)
        self._clear_base_btn.setVisible(False)

        self._width_spin.setEnabled(True)
        self._height_spin.setEnabled(True)
        self._image_type_combo.setEnabled(True)
        self._gray_value_spin.setEnabled(True)
        self._r_spin.setEnabled(True)
        self._g_spin.setEnabled(True)
        self._b_spin.setEnabled(True)

    def _build_button_row(self) -> QHBoxLayout:
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self._generate_btn = QPushButton("生成图像")
        self._generate_btn.setMinimumHeight(36)
        self._generate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._generate_btn.setObjectName("generateBtn")
        btn_layout.addWidget(self._generate_btn)

        self._save_btn = QPushButton("保存图像")
        self._save_btn.setMinimumHeight(36)
        self._save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._save_btn.setObjectName("saveBtn")
        btn_layout.addWidget(self._save_btn)
        return btn_layout

    # ===================== 信号连接 =====================

    def _connect_all_signals(self) -> None:
        self._width_spin.valueChanged.connect(self._on_params_changed)
        self._height_spin.valueChanged.connect(self._on_params_changed)
        self._pixel_size_x_spin.valueChanged.connect(self._on_params_changed)
        self._pixel_size_y_spin.valueChanged.connect(self._on_params_changed)
        self._image_type_combo.currentIndexChanged.connect(self._on_image_type_changed)
        self._gray_value_spin.valueChanged.connect(self._on_params_changed)
        self._r_spin.valueChanged.connect(self._on_params_changed)
        self._g_spin.valueChanged.connect(self._on_params_changed)
        self._b_spin.valueChanged.connect(self._on_params_changed)
        self._generate_btn.clicked.connect(self.generate_requested.emit)
        self._save_btn.clicked.connect(self.save_requested.emit)

    # ===================== 形状 / 缺陷操作 =====================

    def _on_shape_type_changed(self) -> None:
        is_rect = self._shape_type_combo.currentText() == "矩形"
        self._shape_size_widget.setVisible(not is_rect)
        self._shape_rect_widget.setVisible(is_rect)

    def _on_add_shape(self) -> None:
        shape_type_map = {"圆形": "circle", "矩形": "rectangle", "三角形": "triangle"}
        shape = {
            "type": shape_type_map[self._shape_type_combo.currentText()],
            "x": self._shape_x_spin.value(),
            "y": self._shape_y_spin.value(),
            "size": self._shape_size_spin.value(),
            "width": self._shape_width_spin.value(),
            "height": self._shape_height_spin.value(),
            "gray": self._shape_gray_spin.value(),
            "r": self._shape_r_spin.value(),
            "g": self._shape_g_spin.value(),
            "b": self._shape_b_spin.value(),
        }
        self._shapes.append(shape)
        self._refresh_shape_list()
        self._on_params_changed()

    def _on_remove_shape(self) -> None:
        for item in self._shape_list.selectedItems():
            idx = self._shape_list.row(item)
            if 0 <= idx < len(self._shapes):
                self._shapes.pop(idx)
        self._refresh_shape_list()
        self._on_params_changed()

    def _on_remove_all_shapes(self) -> None:
        self._shapes.clear()
        self._refresh_shape_list()
        self._on_params_changed()

    def _refresh_shape_list(self) -> None:
        self._shape_list.clear()
        for s in self._shapes:
            if s["type"] == "rectangle":
                size_str = f"{s.get('width', s['size'])}×{s.get('height', s['size'])}"
            else:
                size_str = str(s["size"])
            label = f"{s['type']} @ ({s['x']},{s['y']}) size={size_str}"
            self._shape_list.addItem(QListWidgetItem(label))

    def _on_add_defect(self) -> None:
        defect_type_map = {
            "划痕": "scratch",
            "沾污": "stain",
            "黑点": "spot",
            "气泡": "bubble",
        }
        defect = {
            "type": defect_type_map[self._defect_type_combo.currentText()],
            "count": self._defect_count_spin.value(),
            "min_size": self._defect_min_spin.value(),
            "max_size": self._defect_max_spin.value(),
            "gray": self._defect_gray_spin.value(),
            "r": self._defect_r_spin.value(),
            "g": self._defect_g_spin.value(),
            "b": self._defect_b_spin.value(),
        }
        self._defects.append(defect)
        self._refresh_defect_list()
        self._on_params_changed()

    def _on_remove_defect(self) -> None:
        for item in self._defect_list.selectedItems():
            idx = self._defect_list.row(item)
            if 0 <= idx < len(self._defects):
                self._defects.pop(idx)
        self._refresh_defect_list()
        self._on_params_changed()

    def _on_remove_all_defects(self) -> None:
        self._defects.clear()
        self._refresh_defect_list()
        self._on_params_changed()

    def _refresh_defect_list(self) -> None:
        self._defect_list.clear()
        for d in self._defects:
            label = f"{d['type']} ×{d['count']} size={d['min_size']}~{d['max_size']}"
            self._defect_list.addItem(QListWidgetItem(label))

    # ===================== 工厂方法 =====================

    @staticmethod
    def _create_spinbox(min_val: int, max_val: int, default: int) -> QSpinBox:
        spin = QSpinBox()
        spin.setRange(min_val, max_val)
        spin.setValue(default)
        spin.setFixedWidth(100)
        return spin

    @staticmethod
    def _create_double_spinbox(
        min_val: float, max_val: float, default: float, decimals: int
    ) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(min_val, max_val)
        spin.setValue(default)
        spin.setDecimals(decimals)
        spin.setSingleStep(0.001)
        spin.setFixedWidth(100)
        return spin

    @staticmethod
    def _make_param_row(name: str, unit: str, widget: QWidget) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(6)
        name_label = QLabel(name)
        name_label.setMinimumWidth(70)
        row.addWidget(name_label)
        row.addWidget(widget)
        if unit:
            unit_label = QLabel(unit)
            unit_label.setStyleSheet("color: #888;")
            row.addWidget(unit_label)
        row.addStretch()
        return row

    # ===================== 信号处理 =====================

    def _on_image_type_changed(self, index: int) -> None:
        is_gray = index == 0
        self._gray_value_widget.setVisible(is_gray)
        self._rgb_value_widget.setVisible(not is_gray)
        self._shape_gray_widget.setVisible(is_gray)
        self._shape_rgb_widget.setVisible(not is_gray)
        self._defect_gray_widget.setVisible(is_gray)
        self._defect_rgb_widget.setVisible(not is_gray)
        self._on_params_changed()

    def _on_tab_changed(self, index: int) -> None:
        """非管理员点击高级功能 Tab 时拦截并提示。"""
        if index > 0 and not self._is_admin:
            self._tabs.setCurrentIndex(0)
            self.admin_required.emit()

    def _on_params_changed(self) -> None:
        self._update_fov()
        self.params_changed.emit(self.get_params())

    def _update_fov(self) -> None:
        fov_w = self._width_spin.value() * self._pixel_size_x_spin.value()
        fov_h = self._height_spin.value() * self._pixel_size_y_spin.value()
        self._fov_label.setText(f"FOV: {fov_w:.2f} × {fov_h:.2f} mm")

    def get_params(self) -> dict:
        is_gray = self._image_type_combo.currentIndex() == 0
        return {
            "width": self._width_spin.value(),
            "height": self._height_spin.value(),
            "pixel_size_x": self._pixel_size_x_spin.value(),
            "pixel_size_y": self._pixel_size_y_spin.value(),
            "image_mode": "gray" if is_gray else "rgb",
            "gray_value": self._gray_value_spin.value(),
            "r_value": self._r_spin.value(),
            "g_value": self._g_spin.value(),
            "b_value": self._b_spin.value(),
            "shapes": list(self._shapes),
            "defects": list(self._defects),
        }
