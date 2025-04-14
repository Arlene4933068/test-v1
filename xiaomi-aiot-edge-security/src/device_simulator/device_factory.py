#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备工厂模块
用于自动创建和注册各类边缘节点，包括网关、路由器、小爱音箱和摄像头
"""

import logging
import uuid
from typing import Dict, Any, List, Optional
from ..platform_connector.edgex_connector import EdgeXConnector
from ..platform_connector.thingsboard_connector import ThingsBoardConnector
from .devices.device_base import DeviceBase
from .devices.gateway import Gateway
from .devices.router import Router
from .devices.smart_speaker import SmartSpeaker
from .devices.camera import Camera

class DeviceFactory:
    """设备工厂类，用于创建和管理各种模拟设备"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化设备工厂
        
        Args:
            config: 包含设备工厂配置的字典
                - edgex: EdgeX Foundry连接配置
                - thingsboard: ThingsBoard连接配置
                - devices: 设备配置
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # 连接器实例
        self.edgex = None
        if 'edgex' in config:
            self.edgex = EdgeXConnector(config['edgex'])
        
        self.thingsboard = None
        if 'thingsboard' in config:
            self.thingsboard = ThingsBoardConnector(config['thingsboard'])
        
        # 存储已创建的设备
        self.devices = {}
    
    def initialize(self) -> bool:
        """
        初始化工厂，连接到平台
        
        Returns:
            bool: 初始化成功返回True，否则返回False
        """
        success = True
        
        # 连接EdgeX Foundry
        if self.edgex:
            if not self.edgex.connect():
                self.logger.error("连接EdgeX Foundry失败")
                success = False
        
        # 连接ThingsBoard
        if self.thingsboard:
            if not self.thingsboard.connect():
                self.logger.error("连接ThingsBoard Edge失败")
                success = False
        
        return success
    
    def create_all_devices(self) -> Dict[str, DeviceBase]:
        """
        创建配置中定义的所有设备
        
        Returns:
            Dict[str, DeviceBase]: 创建的设备字典
        """
        created_devices = {}
        
        if 'devices' not in self.config:
            self.logger.warning("配置中未找到设备定义")
            return created_devices
        
        # 创建每个设备
        for device_config in self.config['devices']:
            device = self.create_device(device_config)
            if device:
                created_devices[device.device_id] = device
        
        return created_devices
    
    def create_device(self, device_config: Dict[str, Any]) -> Optional[DeviceBase]:
        """
        根据配置创建单个设备
        
        Args:
            device_config: 设备配置
                - type: 设备类型 ('gateway', 'router', 'smart_speaker', 'camera')
                - name: 设备名称
                - platform: 平台类型 ('edgex', 'thingsboard', 'both')
                - properties: 设备特定属性
        
        Returns:
            Optional[DeviceBase]: 创建的设备实例，失败时返回None
        """
        device_type = device_config.get('type')
        device_name = device_config.get('name', f"{device_type}_{str(uuid.uuid4())[:8]}")
        platform = device_config.get('platform', 'both')
        properties = device_config.get('properties', {})
        
        if not device_type:
            self.logger.error("设备配置缺少'type'字段")
            return None
        
        # 在平台上注册设备
        edgex_id = None
        tb_device_info = None
        tb_credentials = None
        
        if platform in ['edgex', 'both'] and self.edgex:
            edgex_id = self._register_device_on_edgex(device_type, device_name, properties)
            if not edgex_id:
                self.logger.error(f"在EdgeX Foundry上注册设备'{device_name}'失败")
                if platform == 'edgex':  # 如果仅针对EdgeX，则失败返回None
                    return None
        
        if platform in ['thingsboard', 'both'] and self.thingsboard:
            tb_device_info = self._register_device_on_thingsboard(device_type, device_name, properties)
            if tb_device_info:
                device_id = tb_device_info.get('id', {}).get('id')
                if device_id:
                    tb_credentials = self.thingsboard.get_device_credentials(device_id)
            
            if not tb_device_info or not tb_credentials:
                self.logger.error(f"在ThingsBoard上注册设备'{device_name}'失败")
                if platform == 'thingsboard':  # 如果仅针对ThingsBoard，则失败返回None
                    return None
        
        # 创建相应类型的设备实例
        device = None
        if device_type == 'gateway':
            device = Gateway(
                device_id=device_name,
                edgex_id=edgex_id,
                tb_device_info=tb_device_info,
                tb_credentials=tb_credentials,
                edgex_connector=self.edgex,
                thingsboard_connector=self.thingsboard,
                properties=properties
            )
        elif device_type == 'router':
            device = Router(
                device_id=device_name,
                edgex_id=edgex_id,
                tb_device_info=tb_device_info,
                tb_credentials=tb_credentials,
                edgex_connector=self.edgex,
                thingsboard_connector=self.thingsboard,
                properties=properties
            )
        elif device_type == 'smart_speaker':
            device = SmartSpeaker(
                device_id=device_name,
                edgex_id=edgex_id,
                tb_device_info=tb_device_info,
                tb_credentials=tb_credentials,
                edgex_connector=self.edgex,
                thingsboard_connector=self.thingsboard,
                properties=properties
            )
        elif device_type == 'camera':
            device = Camera(
                device_id=device_name,
                edgex_id=edgex_id,
                tb_device_info=tb_device_info,
                tb_credentials=tb_credentials,
                edgex_connector=self.edgex,
                thingsboard_connector=self.thingsboard,
                properties=properties
            )
        else:
            self.logger.error(f"不支持的设备类型: {device_type}")
            return None
        
        self.logger.info(f"成功创建{device_type}设备: {device_name}")
        self.devices[device_name] = device
        return device
    
    def _register_device_on_edgex(self, device_type: str, device_name: str, properties: Dict[str, Any]) -> str:
        """
        在EdgeX Foundry上注册设备
        
        Args:
            device_type: 设备类型
            device_name: 设备名称
            properties: 设备属性
        
        Returns:
            str: 设备ID，失败时返回空字符串
        """
        try:
            # 设备配置文件数据
            profile_name = f"{device_type}_profile"
            profile_data = self._get_device_profile_data(device_type, profile_name)
            
            # 检查配置文件是否已存在，如果不存在则创建
            # 注：实际实现中可能需要先检查EdgeX中是否已有此配置文件
            profile_id = self.edgex.create_device_profile(profile_data)
            
            # 设备服务数据（假设服务已存在，如果没有，需要先创建）
            service_name = "xiaomi-device-service"
            # 这里可以添加创建服务的代码，如果服务不存在
            
            # 创建设备
            device_data = {
                "name": device_name,
                "description": f"小米AIoT {device_type}设备模拟器",
                "adminState": "UNLOCKED",
                "operatingState": "UP",
                "labels": ["simulated", "xiaomi", device_type],
                "serviceName": service_name,
                "profileName": profile_name
            }
            
            device_id = self.edgex.create_device(device_data)
            return device_id
        except Exception as e:
            self.logger.error(f"在EdgeX Foundry上注册设备时发生错误: {str(e)}")
            return ""
    
    def _register_device_on_thingsboard(self, device_type: str, device_name: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        在ThingsBoard上注册设备
        
        Args:
            device_type: 设备类型
            device_name: 设备名称
            properties: 设备属性
        
        Returns:
            Dict[str, Any]: 设备信息，失败时返回空字典
        """
        try:
            # 创建设备
            label = f"小米AIoT {device_type}设备模拟器"
            device_info = self.thingsboard.create_device(device_name, device_type, label)
            
            return device_info
        except Exception as e:
            self.logger.error(f"在ThingsBoard上注册设备时发生错误: {str(e)}")
            return {}
    
    def _get_device_profile_data(self, device_type: str, profile_name: str) -> Dict[str, Any]:
        """
        根据设备类型获取设备配置文件数据
        
        Args:
            device_type: 设备类型
            profile_name: 配置文件名称
        
        Returns:
            Dict[str, Any]: 设备配置文件数据
        """
        # 基础配置文件结构
        profile_data = {
            "name": profile_name,
            "description": f"小米AIoT {device_type}设备配置文件",
            "manufacturer": "Xiaomi",
            "model": f"Simulated-{device_type}",
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