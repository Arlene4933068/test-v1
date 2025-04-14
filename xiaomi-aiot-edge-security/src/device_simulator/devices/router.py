#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路由器设备模拟器
模拟AIoT边缘路由器设备
"""

import logging
import time
import random
from typing import Dict, Any, List, Optional
from .device_base import DeviceBase

class Router(DeviceBase):
    """路由器设备模拟器类"""
    
    def __init__(self, device_id: str, edgex_id: Optional[str] = None,
                 tb_device_info: Optional[Dict[str, Any]] = None,
                 tb_credentials: Optional[Dict[str, Any]] = None,
                 edgex_connector=None, thingsboard_connector=None,
                 properties: Dict[str, Any] = None):
        """
        初始化路由器设备
        
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
        
        # 路由器特有属性
        self.max_bandwidth = self.properties.get("max_bandwidth", 1000)  # Mbps
        self.wifi_channels = self.properties.get("wifi_channels", ["2.4GHz", "5GHz"])
        
        # 路由器状态
        self.state.update({
            "connected_clients": random.randint(1, 10),
            "signal_strength": random.randint(-70, -30),  # dBm
            "bandwidth_usage": random.uniform(10.0, 30.0),  # %
            "active_channel": random.choice(self.wifi_channels),
            "uptime": 0
        })
        
        self.logger.info(f"路由器设备 {device_id} 已初始化")
    
    def generate_telemetry(self) -> Dict[str, Any]:
        """
        生成路由器遥测数据
        
        Returns:
            Dict[str, Any]: 遥测数据字典
        """
        # 更新路由器状态
        self.state["uptime"] = self.state.get("uptime", 0) + self.telemetry_interval
        
        # 随机变化连接客户端数
        if random.random() < 0.2:  # 20%概率变化连接客户端数
            change = random.choice([-1, 0, 0, 1])
            self.state["connected_clients"] = max(0, self.state["connected_clients"] + change)
        
        # 随机变化信号强度 (-30~-70dBm)
        self.state["signal_strength"] = min(-30, max(-70, 
            self.state["signal_strength"] + random.randint(-2, 2)
        ))
        
        # 随机变化带宽使用率 (5%-80%)
        self.state["bandwidth_usage"] = min(80.0, max(5.0, 
            self.state["bandwidth_usage"] + random.uniform(-3.0, 3.0)
        ))
        
        # 偶尔切换WiFi频道
        if random.random() < 0.05:  # 5%概率切换频道
            self.state["active_channel"] = random.choice(self.wifi_channels)
        
        # 返回遥测数据
        return {
            "connected_clients": self.state["connected_clients"],
            "signal_strength": self.state["signal_strength"],
            "bandwidth_usage": round(self.state["bandwidth_usage"], 2),
            "active_channel": self.state["active_channel"],
            "uptime_seconds": self.state["uptime"]
        }
    
    def handle_command(self, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理路由器命令
        
        Args:
            command: 命令名称
            params: 命令参数
        
        Returns:
            Dict[str, Any]: 命令执行结果
        """
        params = params or {}
        result = {"success": False, "message": "未知命令"}
        
        if command == "reboot":
            # 模拟重启路由器
            self.logger.info(f"路由器 {self.device_id} 执行重启命令")
            self.state["uptime"] = 0
            result = {"success": True, "message": "路由器已重启"}
        
        elif command == "change_channel":
            # 模拟切换WiFi频道
            channel = params.get("channel")
            if channel and channel in self.wifi_channels:
                self.logger.info(f"路由器 {self.device_id} 切换频道到 {channel}")
                self.state["active_channel"] = channel
                result = {"success": True, "message": f"已切换到频道 {channel}"}
            else:
                result = {"success": False, "message": "无效的频道"}
        
        elif command == "disconnect_client":
            # 模拟断开客户端连接
            client_id = params.get("client_id")
            self.logger.info(f"路由器 {self.device_id} 断开客户端 {client_id}")
            if self.state["connected_clients"] > 0:
                self.state["connected_clients"] -= 1
            result = {"success": True, "message": f"已断开客户端 {client_id}"}
        
        return result