import logging
import logging.handlers
import os
from pathlib import Path
import version as __version

SRC_PATH = Path.absolute(Path(__file__)).parent
LOG_PATH = SRC_PATH / 'resources' / 'logs' / 'wxdown.log'
LOG_FILE = str(LOG_PATH)

def setup_logger(
        name: str,
        log_file: str = "app.log",
        level: int = logging.INFO,
        when: str = "midnight",
        backup_count: int = 7,
        console: bool = True,
        version: str = "",
) -> logging.Logger:
    """
    设置并返回一个功能全面的logger。

    :param name: logger名称
    :param log_file: 日志文件名
    :param level: 日志级别
    :param when: 日志轮转的时间间隔（'midnight'为每天轮转，'S', 'M', 'H', 'D', 'W0'-'W6'等）
    :param backup_count: 保留旧日志文件的数量
    :param console: 是否输出到控制台
    :param version: 程序版本
    :return: 配置好的logger对象
    """
    _logger = logging.getLogger(name)
    _logger.setLevel(level)
    _logger.propagate = False  # 防止日志重复

    formatter = logging.Formatter(
        fmt=f"[%(asctime)s] [%(levelname)s] [%(name)s:v{version}] [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 日志目录处理
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 文件日志处理器，按时间轮转
    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_file, when=when, backupCount=backup_count, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    _logger.addHandler(file_handler)

    # 控制台日志处理器
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        _logger.addHandler(console_handler)

    return _logger


logger = setup_logger(
    name="wxdown",
    log_file=LOG_FILE,
    level=logging.DEBUG,
    when="midnight",
    backup_count=14,
    console=False,
    version=__version.version,
)
