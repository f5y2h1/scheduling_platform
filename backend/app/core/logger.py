"""
日志配置
使用 loguru 替代标准 logging
"""

import sys
from loguru import logger


def setup_logger():
    """配置 loguru 日志"""
    logger.remove()

    fmt = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stdout,
        format=fmt,
        level="DEBUG",
        colorize=True,
    )

    logger.add(
        "logs/scheduling_{time:YYYY-MM-DD}.log",
        format=fmt,
        level="INFO",
        rotation="10 MB",
        retention="30 days",
        encoding="utf-8",
    )

    return logger
