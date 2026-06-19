"""日志记录模块 - 基于 loguru，支持文件按天/大小轮转。"""

import sys

from loguru import logger

from utils.paths import get_log_dir

LOG_DIR = get_log_dir()

# 移除默认 handler
logger.remove()

# 控制台输出（仅在非 windowed 模式下可用）
if sys.stderr is not None:
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG",
        colorize=True,
    )

# 文件输出 - 按天轮转 + 10MB 大小轮转
LOG_DIR.mkdir(parents=True, exist_ok=True)
logger.add(
    LOG_DIR / "app_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="10 MB",  # 超过 10MB 轮转
    retention="30 days",  # 保留 30 天
    encoding="utf-8",
    enqueue=True,  # 多进程安全
)


def get_logger():
    """获取 logger 实例。"""
    return logger
