#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
平台连接器基类
提供连接边缘计算平台的通用功能
"""

from abc import ABC, abstractmethod

class PlatformConnector(ABC):
    """平台连接器基类"""
    
    def __init__(self, config):
        """
        初始化平台连接器
        
        Args:
            config: 平台配置字典
        """
        self.config = config

# 为向后兼容保留的别名
ConnectorBase = PlatformConnector