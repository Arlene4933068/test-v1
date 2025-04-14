#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志工具模块
提供配置和获取日志记录器的功能
"""

import os
import logging
import logging.config
from typing import Dict, Any, Optional

# 默认日志配置
DEFAULT_LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': 'logs/aiot_edge_security.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file']
    }
}

_logger_initialized = False
_log_config = DEFAULT_LOG_CONFIG.copy()

def setup_logger(config: Optional[Dict[str, Any]] = None, level: int = logging.INFO) -> None:
    """
    配置日志系统
    
    Args:
        config: 日志配置字典
        level: 日志级别
    """
    global _logger_initialized, _log_config
    
    # 如果提供了配置，则使用提供的配置
    if config:
        _log_config = config
    
    # 确保日志目录存在
    log_dir = os.path.dirname(_log_config['handlers']['file']['filename'])
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # 更新根日志级别
    _log_config['root']['level'] = level
    
    # 配置日志系统
    logging.config.dictConfig(_log_config)
    
    _logger_initialized = True

def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器
    
    Args:
        name: 日志记录器名称
    
    Returns:
        logging.Logger: 日志记录器
    """
    global _logger_initialized, _log_config
    
    # 如果日志系统尚未初始化，则进行初始化
    if not _logger_initialized:
        setup_logger()
    
    # 获取日志记录器
    logger = logging.getLogger(name)
    
    # 确保日志记录器具有正确的级别
    if _log_config and 'root' in _log_config and 'level' in _log_config['root']:
        logger.setLevel(_log_config['root']['level'])
    else:
        # 如果配置中没有根级别，则使用默认级别
        logger.setLevel(logging.INFO)
    
    return logger