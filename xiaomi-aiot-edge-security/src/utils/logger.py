# src/utils/logger.py
import os
import yaml
import logging
import logging.config
import logging.handlers
from pathlib import Path

_loggers = {}

def setup_logger():
    """初始化日志配置
    
    从配置文件加载日志配置并应用
    """
    config_path = Path(__file__).parent.parent.parent / 'config' / 'logging.yaml'
    if not config_path.exists():
        raise FileNotFoundError(f'日志配置文件不存在: {config_path}')
        
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        
    # 确保日志目录存在
    log_dir = Path(config['handlers']['file']['filename']).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 应用配置
    logging.config.dictConfig(config)


_log_config = None

def _load_log_config():
    """加载日志配置"""
    global _log_config
    
    if _log_config is not None:
        return _log_config
    
    # 默认配置
    default_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] [%(name)s] %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'standard',
                'stream': 'ext://sys.stdout',
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'standard',
                'filename': 'logs/xiaomi_aiot_edge_security.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8',
            },
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
                'propagate': True
            }
        }
    }
    
    # 尝试从配置文件加载
    config_file = os.path.join('config', 'logging.yaml')
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                loaded_config = yaml.safe_load(f)
                _log_config = loaded_config
                return _log_config
        except Exception:
            pass
    
    # 使用默认配置
    _log_config = default_config
    
    # 确保日志目录存在
    log_dir = os.path.dirname(default_config['handlers']['file']['filename'])
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    return _log_config

def get_logger(name):
    """获取日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        logging.Logger: 日志记录器
    """
    global _loggers
    
    if name in _loggers:
        return _loggers[name]
    
    # 加载配置
    config = _load_log_config()
    
    # 创建日志记录器
    logger = logging.getLogger(name)
    
    # 如果已经配置了处理程序，则跳过
    if logger.handlers:
        _loggers[name] = logger
        return logger
    
    # 配置控制台输出
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(config['formatters']['standard']['format'])
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(config['handlers']['console']['level'])
    logger.addHandler(console_handler)
    
    # 配置文件输出
    file_handler = RotatingFileHandler(
        filename=config['handlers']['file']['filename'],
        maxBytes=config['handlers']['file']['maxBytes'],
        backupCount=config['handlers']['file']['backupCount'],
        encoding=config['handlers']['file']['encoding'],
    )
    file_formatter = logging.Formatter(config['formatters']['standard']['format'])
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(config['handlers']['file']['level'])
    logger.addHandler(file_handler)
    
    # 设置日志级别
    logger.setLevel(config['root']['level'])
    
    _loggers[name] = logger
    return logger
from logging.handlers import RotatingFileHandler