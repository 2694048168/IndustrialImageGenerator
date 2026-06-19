#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
@File: models.py
@Python Version: 3.12.8
@Author: Wei Li (Ithaca)
@Email: weili_yzzcq@163.com
@Blog: https://2694048168.github.io/blog/
@Date: 2026-06-19
@copyright Copyright (c) 2026 Wei Li
@Description: 数据模型定义
'''

from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    """用户模型。"""
    id: int | None = None
    username: str = ""
    password_hash: str = ""
    role: str = "user"       # "admin" | "user"
    created_at: datetime | None = None
    last_login: datetime | None = None

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"