#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Dashboard模块架构设计
建立可视化模块与其他系统组件的联系
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import logging

# 设置日志
logger = logging.getLogger(__name__)

@dataclass
class DashboardConfig:
    """仪表盘配置数据类"""
    refresh_interval: int = 5  # 数据刷新间隔(秒)
    max_history_records: int = 1000  # 历史数据最大记录数
    enable_realtime_monitoring: bool = True  # 是否启用实时监控
    enable_packet_capture: bool = True  # 是否启用数据包捕获
    packet_capture_limit: int = 100  # 每个设备最大捕获包数量
    attack_log_retention_days: int = 30  # 攻击日志保留天数

class DashboardIntegrationManager:
    """仪表盘集成管理器 - 负责与其他模块的数据交互"""
    
    def __init__(self, config: DashboardConfig):
        self.config = config
        self.device_manager = None  # 将在连接时设置
        self.security_manager = None  # 将在连接时设置
        self.platform_connector = None  # 将在连接时设置
        self.packet_analyzer = None  # 将在连接时设置
        logger.info("Dashboard集成管理器初始化完成")
    
    def connect_device_manager(self, device_manager):
        """连接设备管理器"""
        self.device_manager = device_manager
        logger.info("Dashboard已连接设备管理器")
        
    def connect_security_manager(self, security_manager):
        """连接安全管理器"""
        self.security_manager = security_manager
        logger.info("Dashboard已连接安全管理器")
    
    def connect_platform_connector(self, platform_connector):
        """连接平台连接器"""
        self.platform_connector = platform_connector
        logger.info("Dashboard已连接平台连接器")
    
    def connect_packet_analyzer(self, packet_analyzer):
        """连接数据包分析器"""
        self.packet_analyzer = packet_analyzer
        logger.info("Dashboard已连接数据包分析器")
    
    def get_device_status(self) -> List[Dict[str, Any]]:
        """获取所有设备状态"""
        if not self.device_manager:
            logger.warning("设备管理器未连接，无法获取设备状态")
            return []
        return self.device_manager.get_all_devices_status()
    
    def get_security_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取安全事件"""
        if not self.security_manager:
            logger.warning("安全管理器未连接，无法获取安全事件")
            return []
        return self.security_manager.get_recent_events(limit)
    
    def get_platform_metrics(self) -> Dict[str, Any]:
        """获取平台指标"""
        if not self.platform_connector:
            logger.warning("平台连接器未连接，无法获取平台指标")
            return {}
        return self.platform_connector.get_metrics()
    
    def get_packet_analysis(self, device_id: Optional[str] = None) -> Dict[str, Any]:
        """获取数据包分析结果"""
        if not self.packet_analyzer:
            logger.warning("数据包分析器未连接，无法获取分析结果")
            return {}
        return self.packet_analyzer.get_analysis_results(device_id)