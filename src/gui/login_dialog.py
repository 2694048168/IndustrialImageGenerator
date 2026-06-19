"""用户登录对话框。"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from database.db_manager import DatabaseManager
from database.models import User
from utils.logger import get_logger

logger = get_logger()


class LoginDialog(QDialog):
    """用户登录对话框。"""

    login_success = Signal(User)

    def __init__(self, db_manager: DatabaseManager, parent: QWidget | None = None):
        super().__init__(parent)
        self._db = db_manager
        self._user: User | None = None
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        self.setWindowTitle("工业图像生成器 - 用户登录")
        self.setFixedSize(380, 220)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("用户登录")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 8px;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(8)

        self._username_edit = QLineEdit()
        self._username_edit.setPlaceholderText("请输入用户名")
        self._username_edit.setMinimumHeight(30)
        form.addRow("用户名:", self._username_edit)

        self._password_edit = QLineEdit()
        self._password_edit.setPlaceholderText("请输入密码")
        self._password_edit.setEchoMode(QLineEdit.Password)
        self._password_edit.setMinimumHeight(30)
        form.addRow("密码:", self._password_edit)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self._login_btn = QPushButton("登录")
        self._login_btn.setMinimumHeight(32)
        self._login_btn.setDefault(True)
        btn_layout.addWidget(self._login_btn)

        self._cancel_btn = QPushButton("取消")
        self._cancel_btn.setMinimumHeight(32)
        btn_layout.addWidget(self._cancel_btn)

        layout.addLayout(btn_layout)

    def _connect_signals(self) -> None:
        self._login_btn.clicked.connect(self._on_login)
        self._cancel_btn.clicked.connect(self.reject)
        self._password_edit.returnPressed.connect(self._on_login)

    def _on_login(self) -> None:
        username = self._username_edit.text().strip()
        password = self._password_edit.text()

        if not username or not password:
            QMessageBox.warning(self, "提示", "用户名和密码不能为空。")
            return

        self._user = self._db.authenticate(username, password)
        if self._user is None:
            QMessageBox.critical(self, "登录失败", "用户名或密码错误。")
            logger.warning("登录失败: {}", username)
            return

        logger.info("用户 {} 登录成功 (role={})", username, self._user.role)
        self.login_success.emit(self._user)
        self.accept()

    def get_user(self) -> User | None:
        return self._user
