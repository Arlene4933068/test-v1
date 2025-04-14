#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网关设备模拟器
模拟AIoT边缘网关，负责连接和管理其他设备
"""

import logging
import time
import random
from typing import Dict, Any, List, Optional
from .device_base import DeviceBase

class Gateway(DeviceBase):
    """网关设备模拟器类"""
    
    def __init__(self, device_id: str, edgex_id: Optional[str] = None,
                 tb_device_info: Optional[Dict[str, Any]] = None,
                 tb_credentials: Optional[Dict[str, Any]] = None,
                 edgex_connector=None, thingsboard_connector=None,
                 properties: Dict[str, Any] = None):
        """
        初始化网关设备
        
        Args:
            device_id: 设备ID
            edgex_id: EdgeX设备ID
            tb_device_info: ThingsBoard设备信息
            tb_credentials: ThingsBoard设备凭证
            edgex_connector: EdgeX连接器实例
            thingsboard_connector: ThingsBoard连接器实例
            properties: 设备属性
        """
        super().__init__(device_id, edgex_id, tb_device_info, tb_credentials,
                        edgex_connector, thingsboard_connector, properties)
        
        # 网关特有属性
        self.max_connected_devices = self.properties.get("max_connected_devices", 20)
        self.init_connected_devices = self.properties.get("init_connected_devices", 5)
        
        # 网关状态
        self.state.update({
            "connected_devices": self.init_connected_devices,
            "cpu_usage": 10.0,
            "memory_usage": 25.0,
            "network_throughput": 5.0,
            "uptime": 0
        })
        
        self.logger.info(f"网关设备 {device_id} 已初始化")
    
    def generate_telemetry(self) -> Dict[str, Any]:
        """
        生成网关遥测数据
        
        Returns:
            Dict[str, Any]: 遥测数据字典
        """
        # 更新网关状态
        self.state["uptime"] = self.state.get("uptime", 0) + self.telemetry_interval
        
        # 随机变化连接设备数
        if random.random() < 0.1:  # 10%概率变化连接设备数
            change = random.choice([-1, 1])
            self.state["connected_devices"] = max(0, min(
                self.state["connected_devices"] + change,
                self.max_connected_devices
            ))
        
        # 随机变化CPU使用率 (5%-50%)
        self.state["cpu_usage"] = min(50.0, max(5.0, 
            self.state["cpu_usage"] + random.uniform(-2.0, 2.0)
        ))
        
        # 随机变化内存使用率 (20%-60%)
        self.state["memory_usage"] = min(60.0, max(20.0, 
            self.state["memory_usage"] + random.uniform(-1.0, 1.0)
        ))
        
        # 随机变化网络吞吐量 (1-20 Mbps)
        self.state["network_throughput"] = min(20.0, max(1.0, 
            self.state["network_throughput"] + random.uniform(-0.5, 0.5)
        ))
        
        # 返回遥测数据
        return {
            "connected_devices": self.state["connected_devices"],
            "cpu_usage": round(self.state["cpu_usage"], 2),
            "memory_usage": round(self.state["memory_usage"], 2),
            "network_throughput": round(self.state["network_throughput"], 2),
            "uptime_seconds": self.state["uptime"]
        }
    
    def handle_command(self, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理网关命令
        
        Args:
            command: 命令名称
            params: 命令参数
        
        Returns:
            Dict[str, Any]: 命令执行结果
        """
        params = params or {}
        result = {"success": False, "message": "未知命令"}
        
        if command == "reboot":
            # 模拟重启网关
            self.logger.info(f"网关 {self.device_id} 执行重启命令")
            self.state["uptime"] = 0
            result = {"success": True, "message": "网关已重启"}
        
        elif command == "factory_reset":
            # 模拟恢复出厂设置
            self.logger.info(f"网关 {self.device_id} 执行恢复出厂设置命令")
            self.state["connected_devices"] = self.init_connected_devices
            self.state["uptime"] = 0
            result = {"success": True, "message": "网关已恢复出厂设置"}
        
        elif command == "update_firmware":
            # 模拟固件更新
            version = params.get("version", "unknown")
            self.logger.info(f"网关 {self.device_id} 更新固件到版本 {version}")
            result = {"success": True, "message": f"固件已更新到版本 {version}"}
        
        return result