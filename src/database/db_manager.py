"""数据库管理模块 - 基于 SQLite 存储用户信息。"""

import hashlib
import sqlite3
from datetime import datetime
from pathlib import Path

from database.models import User
from utils.logger import get_logger
from utils.paths import get_data_dir

logger = get_logger()

DB_PATH = get_data_dir() / "users.db"


def _hash_password(password: str) -> str:
    """对密码进行 SHA-256 哈希。"""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


class DatabaseManager:
    """SQLite 数据库管理器。"""

    def __init__(self, db_path: Path | None = None):
        self._db_path = db_path or DB_PATH
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _init_db(self) -> None:
        """初始化数据库表结构。"""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    username    TEXT    NOT NULL UNIQUE,
                    password    TEXT    NOT NULL,
                    role        TEXT    NOT NULL DEFAULT 'user',
                    created_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
                    last_login  TEXT
                )
            """)
            # 迁移旧表：如果没有 role 列则添加
            cols = {r[1] for r in conn.execute("PRAGMA table_info(users)")}
            if "role" not in cols:
                conn.execute(
                    "ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user'"
                )
                # 将 admin 用户更新为 admin 角色
                conn.execute("UPDATE users SET role = 'admin' WHERE username = 'admin'")
                logger.info("数据库已迁移：添加 role 列")

            cursor = conn.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                self._create_default_admin(conn)
        logger.info("数据库初始化完成: {}", self._db_path)

    def _create_default_admin(self, conn: sqlite3.Connection) -> None:
        """创建默认管理员账户（admin/admin123）。"""
        conn.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin", _hash_password("admin123"), "admin"),
        )
        conn.commit()
        logger.info("已创建默认管理员账户: admin (role=admin)")

    def authenticate(self, username: str, password: str) -> User | None:
        """验证用户登录，成功返回 User 对象，失败返回 None。"""
        password_hash = _hash_password(password)
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE username = ? AND password = ?",
                (username, password_hash),
            ).fetchone()
            if row is None:
                logger.warning("用户登录失败: {}", username)
                return None
            conn.execute(
                "UPDATE users SET last_login = datetime('now', 'localtime') WHERE id = ?",
                (row["id"],),
            )
            conn.commit()
            logger.info("用户登录成功: {} (role={})", username, row["role"])
            return User(
                id=row["id"],
                username=row["username"],
                password_hash=row["password"],
                role=row["role"],
                created_at=datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S"),
                last_login=datetime.now(),
            )

    def create_user(self, username: str, password: str, role: str = "user") -> bool:
        """创建新用户。"""
        password_hash = _hash_password(password)
        try:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                    (username, password_hash, role),
                )
                conn.commit()
            logger.info("创建用户成功: {} (role={})", username, role)
            return True
        except sqlite3.IntegrityError:
            logger.warning("创建用户失败，用户名已存在: {}", username)
            return False

    def list_users(self) -> list[User]:
        """列出所有用户。"""
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
        return [
            User(
                id=row["id"],
                username=row["username"],
                password_hash=row["password"],
                role=row["role"],
                created_at=datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S"),
                last_login=(
                    datetime.strptime(row["last_login"], "%Y-%m-%d %H:%M:%S")
                    if row["last_login"]
                    else None
                ),
            )
            for row in rows
        ]

    def get_admin_users(self) -> list[User]:
        """获取所有管理员用户。"""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM users WHERE role = 'admin' ORDER BY id"
            ).fetchall()
        return [
            User(
                id=row["id"],
                username=row["username"],
                password_hash=row["password"],
                role=row["role"],
                created_at=datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S"),
                last_login=(
                    datetime.strptime(row["last_login"], "%Y-%m-%d %H:%M:%S")
                    if row["last_login"]
                    else None
                ),
            )
            for row in rows
        ]
