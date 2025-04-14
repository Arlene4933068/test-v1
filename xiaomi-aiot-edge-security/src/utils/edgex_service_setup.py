#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EdgeX设备服务配置工具
用于创建和设置EdgeX设备服务
"""

import os
import json
import yaml
import requests
import logging
from typing import Dict, Any, List, Optional

class EdgeXServiceSetup:
    """EdgeX设备服务配置工具类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化EdgeX服务配置工具
        
        Args:
            config: EdgeX配置
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # 设置API URL
        self.host = config.get('host', 'localhost')
        self.metadata_port = config.get('metadata_port', 59881)
        self.metadata_url = f"http://{self.host}:{self.metadata_port}"
        
        # API版本
        self.api_version = config.get('api_version', 'v2')
        
        # 设备服务名称
        self.device_service_name = config.get('device_service_name', 'xiaomi-device-service')
        
        # 请求头
        self.headers = {"Content-Type": "application/json"}
    
    def check_service_exists(self) -> bool:
        """
        检查设备服务是否存在
        
        Returns:
            bool: 存在返回True，否则返回False
        """
        try:
            response = requests.get(
                f"{self.metadata_url}/api/{self.api_version}/deviceservice/name/{self.device_service_name}",
                headers=self.headers
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"检查设备服务是否存在时出错: {str(e)}")
            return False
    
    def create_device_service(self) -> bool:
        """
        创建设备服务
        
        Returns:
            bool: 创建成功返回True，否则返回False
        """
        if self.check_service_exists():
            self.logger.info(f"设备服务 {self.device_service_name} 已存在")
            return True
        
        try:
            # 设备服务数据
            service_data = {
                "name": self.device_service_name,
                "description": "小米AIoT设备模拟服务",
                "labels": ["xiaomi", "aiot", "simulator"],
                "baseAddress": f"http://{self.host}:59999",  # 模拟地址
                "adminState": "UNLOCKED"
            }
            
            response = requests.post(
                f"{self.metadata_url}/api/{self.api_version}/deviceservice",
                headers=self.headers,
                json=service_data
            )
            
            if response.status_code in [200, 201]:
                self.logger.info(f"成功创建设备服务: {self.device_service_name}")
                return True
            else:
                self.logger.error(f"创建设备服务失败: {response.status_code}, {response.text}")
                return False
        except Exception as e:
            self.logger.error(f"创建设备服务时出错: {str(e)}")
            return False
    
    def generate_device_profile(self, device_type: str, profile_name: str) -> Dict[str, Any]:
        """
        生成设备配置文件数据
        
        Args:
            device_type: 设备类型
            profile_name: 配置文件名称
        
        Returns:
            Dict[str, Any]: 配置文件数据
        """
        # 基础配置文件结构
        profile_data = {
            "apiVersion": "v2",
            "name": profile_name,
            "manufacturer": "Xiaomi",
            "description": f"小米AIoT {device_type}设备配置文件",
            "model": f"Simulated-{device_type}",
            "labels": ["xiaomi", "simulated", device_type],
            "deviceResources": []
        }
        
        # 根据设备类型添加不同的设备资源
        if device_type == 'gateway':
            profile_data["deviceResources"] = [
                {
                    "name": "connected_devices",
                    "description": "连接的设备数量",
                    "properties": {
                        "valueType": "Int32",
                        "readWrite": "R"
                    }
                },
                {
                    "name": "cpu_usage",
                    "description": "CPU使用率",
                    "properties": {
                        "valueType": "Float32",
                        "readWrite": "R",
                        "units": "%"
                    }
                },
                {
                    "name": "memory_usage",
                    "description": "内存使用率",
                    "properties": {
                        "valueType": "Float32",
                        "readWrite": "R",
                        "units": "%"
                    }
                },
                {
                    "name": "network_throughput",
                    "description": "网络吞吐量",
                    "properties": {
                        "valueType": "Float32",
                        "readWrite": "R",
                        "units": "Mbps"
                    }
                }
            ]
        elif device_type == 'router':
            profile_data["deviceResources"] = [
                {
                    "name": "connected_clients",
                    "description": "连接的客户端数量",
                    "properties": {
                        "valueType": "Int32",
                        "readWrite": "R"
                    }
                },
                {
                    "name": "signal_strength",
                    "description": "信号强度",
                    "properties": {
                        "valueType": "Int32",
                        "readWrite": "R",
                        "units": "dBm"
                    }
                },
                {
                    "name": "bandwidth_usage",
                    "description": "带宽使用率",
                    "properties": {
                        "valueType": "Float32",
                        "readWrite": "R",
                        "units": "%"
                    }
                }
            ]
        elif device_type == 'smart_speaker':
            profile_data["deviceResources"] = [
                {
                    "name": "volume",
                    "description": "音量",
                    "properties": {
                        "valueType": "Int32",
                        "readWrite": "RW",
                        "units": "%"
                    }
                },
                {
                    "name": "bluetooth_status",
                    "description": "蓝牙状态",
                    "properties": {
                        "valueType": "Bool",
                        "readWrite": "R"
                    }
                },
                {
                    "name": "connected_bluetooth_devices",
                    "description": "已连接的蓝牙设备数量",
                    "properties": {
                        "valueType": "Int32",
                        "readWrite": "R"
                    }
                }
            ]
        elif device_type == 'camera':
            profile_data["deviceResources"] = [
                {
                    "name": "status",
                    "description": "摄像头状态",
                    "properties": {
                        "valueType": "String",
                        "readWrite": "R"
                    }
                },
                {
                    "name": "resolution",
                    "description": "分辨率",
                    "properties": {
                        "valueType": "String",
                        "readWrite": "RW"
                    }
                },
                {
                    "name": "motion_detected",
                    "description": "是否检测到移动",
                    "properties": {
                        "valueType": "Bool",
                        "readWrite": "R"
                    }
                },
                {
                    "name": "fps",
                    "description": "每秒帧数",
                    "properties": {
                        "valueType": "Float32",
                        "readWrite": "R"
                    }
                }
            ]
        
        return profile_data