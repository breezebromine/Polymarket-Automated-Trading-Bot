"""日志配置模块"""

import sys
from pathlib import Path
from loguru import logger

from ..utils.config import get_config


def setup_logging():
    """设置日志系统"""
    config = get_config()

    # 移除默认handler
    logger.remove()

    # 控制台输出
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=config.log_level,
        colorize=True
    )

    # 确保日志目录存在
    log_dir = config.root_dir / "logs"
    log_dir.mkdir(exist_ok=True)

    # 交易日志文件
    logger.add(
        log_dir / "trading_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="INFO",
        rotation="00:00",  # 每天午夜轮转
        retention="30 days",  # 保留30天
        compression="zip"  # 压缩旧日志
    )

    # 错误日志文件
    logger.add(
        log_dir / "errors_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="00:00",
        retention="90 days",
        compression="zip"
    )

    # 性能日志文件(如果启用调试)
    if config.debug:
        logger.add(
            log_dir / "debug_{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            rotation="100 MB",  # 按大小轮转
            retention="7 days"
        )

    logger.info("日志系统已初始化")
    return logger


def get_logger(name: str):
    """
    获取logger实例

    Args:
        name: logger名称

    Returns:
        logger实例
    """
    return logger.bind(name=name)
