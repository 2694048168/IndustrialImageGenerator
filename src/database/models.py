"""数据模型定义。"""

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