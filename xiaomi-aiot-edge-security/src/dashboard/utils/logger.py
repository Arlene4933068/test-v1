# src/dashboard/utils/logger.py
import logging
import os
from datetime import datetime

def get_logger(name):
    """获取日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        logging.Logger: 日志记录器实例
    """
    # 创建日志目录
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 创建日志文件
    log_file = os.path.join(log_dir, f"dashboard_{datetime.now().strftime('%Y%m%d')}.log")
    
    # 创建格式器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 创建文件处理器
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # 获取日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 添加处理器
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger