#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
@File: log_signal.py
@Python Version: 3.12.8
@Author: Wei Li (Ithaca)
@Email: weili_yzzcq@163.com
@Blog: https://2694048168.github.io/blog/
@Date: 2026-06-19
@copyright Copyright (c) 2026 Wei Li
@Description: Loguru - Qt 信号桥接模块
'''

from PySide6.QtCore import QObject, Signal


class LogSignal(QObject):
    """将 loguru 日志转发为 Qt 信号的桥接对象。"""

    new_log = Signal(str)


class LogHandler:
    """loguru sink：接收日志并发送到 LogSignal。"""

    def __init__(self, signal: LogSignal):
        self._signal = signal

    def write(self, message: str) -> None:
        msg = message.strip()
        if msg:
            self._signal.new_log.emit(msg)

    def flush(self) -> None:
        pass