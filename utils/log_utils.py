# utils/log_utils.py - 日志工具

import os
import sys
from datetime import datetime

# 日志级别
LOG_LEVELS = {
    "DEBUG": 0,
    "INFO": 1,
    "WARNING": 2,
    "ERROR": 3,
    "CRITICAL": 4
}

class Logger:
    """简单的日志记录器"""

    def __init__(self, name: str = "AI播客", log_level: str = "INFO"):
        """
        初始化日志记录器

        Args:
            name: 日志名称
            log_level: 日志级别
        """
        self.name = name
        self.log_level = log_level.upper()
        self.log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
        os.makedirs(self.log_dir, exist_ok=True)

        # 创建日志文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(self.log_dir, f"{name}_{timestamp}.log")

    def _log(self, level: str, message: str):
        """
        记录日志

        Args:
            level: 日志级别
            message: 日志消息
        """
        if LOG_LEVELS[level] < LOG_LEVELS[self.log_level]:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] [{self.name}] {message}"

        # 输出到控制台
        print(log_message)

        # 写入日志文件
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(log_message + "\n")
        except Exception as e:
            print(f"日志写入失败: {e}")

    def debug(self, message: str):
        """记录调试日志"""
        self._log("DEBUG", message)

    def info(self, message: str):
        """记录信息日志"""
        self._log("INFO", message)

    def warning(self, message: str):
        """记录警告日志"""
        self._log("WARNING", message)

    def error(self, message: str):
        """记录错误日志"""
        self._log("ERROR", message)

    def critical(self, message: str):
        """记录严重错误日志"""
        self._log("CRITICAL", message)

# 创建全局日志实例
logger = Logger()

# 便捷函数
def debug(message: str):
    logger.debug(message)

def info(message: str):
    logger.info(message)

def warning(message: str):
    logger.warning(message)

def error(message: str):
    logger.error(message)

def critical(message: str):
    logger.critical(message)
