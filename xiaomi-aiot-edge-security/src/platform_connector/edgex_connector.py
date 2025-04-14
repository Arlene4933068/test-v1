#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EdgeX Foundry 连接器
提供与Docker中部署的EdgeX Foundry实例的连接和交互功能
"""

import requests
import json
import logging
from typing import Dict, List, Any, Optional
from .connector_base import ConnectorBase

class EdgeXConnector(ConnectorBase):
    """EdgeX Foundry 平台连接器"""
    
def __init__(self, config: Dict[str, Any]):
    """
    初始化EdgeX连接器
    
    Args:
        config: 包含连接配置的字典
            - host: EdgeX主机地址 (默认为 'localhost')
            - port: EdgeX数据服务端口 (默认为 59880)
            - metadata_port: EdgeX元数据服务端口 (默认为 59881)
            - core_command_port: EdgeX核心命令服务端口 (默认为 59882)
            - token: 认证令牌 (可选)
    """
    super().__init__(config)
    self.logger = logging.getLogger(__name__)
    
    # 设置连接参数
    self.host = config.get('host', 'localhost')
    self.port = config.get('port', 59880)  # 修改为您环境中的core-data端口
    self.metadata_port = config.get('metadata_port', 59881)  # 修改为您环境中的metadata端口
    self.core_command_port = config.get('core_command_port', 59882)  # 修改为您环境中的command端口
    self.token = config.get('token', None)
    
    # 设置基础URL
    self.core_data_url = f"http://{self.host}:{self.port}"
    self.metadata_url = f"http://{self.host}:{self.metadata_port}"
    self.command_url = f"http://{self.host}:{self.core_command_port}"
    
    # 设置请求头
    self.headers = {"Content-Type": "application/json"}
    if self.token:
        self.headers["Authorization"] = f"Bearer {self.token}"
    
def connect(self) -> bool:
    """
    连接到EdgeX Foundry实例
    
    Returns:
        bool: 连接成功返回True，否则返回False
    """
    try:
        # 尝试获取ping请求来验证连接 - 使用core-data的ping端点
        response = requests.get(f"{self.core_data_url}/api/v2/ping", headers=self.headers)
        if response.status_code == 200:
            self.logger.info("成功连接到EdgeX Foundry实例")
            return True
        else:
            self.logger.error(f"无法连接到EdgeX Foundry实例，状态码: {response.status_code}")
            return False
    except Exception as e:
        self.logger.error(f"连接EdgeX Foundry实例时发生错误: {str(e)}")
        return False
    
def disconnect(self) -> bool:
    """
    断开与EdgeX Foundry的连接
    
    Returns:
        bool: 断开连接成功返回True，否则返回False
    """
    # EdgeX REST API无需显式断开连接
    return True

def create_device_profile(self, profile_data: Dict[str, Any]) -> str:
    """
    创建设备配置文件
    
    Args:
        profile_data: 设备配置文件数据
    
    Returns:
        str: 创建的设备配置文件ID，失败时返回空字符串
    """
    try:
        response = requests.post(
            f"{self.metadata_url}/api/v2/deviceprofile",
            headers=self.headers,
            json=profile_data
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            self.logger.info(f"成功创建设备配置文件: {profile_data.get('name')}")
            return result.get('id', '')
        else:
            self.logger.error(f"创建设备配置文件失败: {response.status_code}, {response.text}")
            return ""
    except Exception as e:
        self.logger.error(f"创建设备配置文件时发生错误: {str(e)}")
        return ""

def create_device_service(self, service_data: Dict[str, Any]) -> str:
    """
    创建设备服务
    
    Args:
        service_data: 设备服务数据
    
    Returns:
        str: 创建的设备服务ID，失败时返回空字符串
    """
    try:
        response = requests.post(
            f"{self.metadata_url}/api/v2/deviceservice",
            headers=self.headers,
            json=service_data
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            self.logger.info(f"成功创建设备服务: {service_data.get('name')}")
            return result.get('id', '')
        else:
            self.logger.error(f"创建设备服务失败: {response.status_code}, {response.text}")
            return ""
    except Exception as e:
        self.logger.error(f"创建设备服务时发生错误: {str(e)}")
        return ""

def create_device(self, device_data: Dict[str, Any]) -> str:
    """
    创建设备
    
    Args:
        device_data: 设备数据
    
    Returns:
        str: 创建的设备ID，失败时返回空字符串
    """
    try:
        response = requests.post(
            f"{self.metadata_url}/api/v2/device",
            headers=self.headers,
            json=device_data
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            self.logger.info(f"成功创建设备: {device_data.get('name')}")
            return result.get('id', '')
        else:
            self.logger.error(f"创建设备失败: {response.status_code}, {response.text}")
            return ""
    except Exception as e:
        self.logger.error(f"创建设备时发生错误: {str(e)}")
        return ""

def send_device_data(self, device_name: str, readings: List[Dict[str, Any]]) -> bool:
    """
    发送设备数据到EdgeX Foundry
    
    Args:
        device_name: 设备名称
        readings: 读数列表，每个读数为包含resourceName、value等字段的字典
    
    Returns:
        bool: 发送成功返回True，否则返回False
    """
    try:
        # 构建事件数据
        event_data = {
            "apiVersion": "v2",
            "deviceName": device_name,
            "readings": readings
        }
        
        response = requests.post(
            f"{self.core_data_url}/api/v2/event",
            headers=self.headers,
            json=event_data
        )
        
        if response.status_code in [200, 201]:
            self.logger.debug(f"成功发送设备{device_name}的数据")
            return True
        else:
            self.logger.error(f"发送设备数据失败: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        self.logger.error(f"发送设备数据时发生错误: {str(e)}")
        return False

def get_device_readings(self, device_name: str, count: int = 10) -> List[Dict[str, Any]]:
    """
    获取设备的最新读数
    
    Args:
        device_name: 设备名称
        count: 要获取的最大读数数量
    
    Returns:
        List[Dict[str, Any]]: 设备读数列表
    """
    try:
        response = requests.get(
            f"{self.core_data_url}/api/v2/reading/device/name/{device_name}/all?limit={count}",
            headers=self.headers
        )
        
        if response.status_code == 200:
            result = response.json()
            self.logger.debug(f"成功获取设备{device_name}的读数")
            return result.get('readings', [])
        else:
            self.logger.error(f"获取设备读数失败: {response.status_code}, {response.text}")
            return []
    except Exception as e:
        self.logger.error(f"获取设备读数时发生错误: {str(e)}")
        return []

def execute_device_command(self, device_name: str, command_name: str, method: str = "get", payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    执行设备命令
    
    Args:
        device_name: 设备名称
        command_name: 命令名称
        method: 请求方法，'get'或'put'
        payload: PUT请求的有效载荷
    
    Returns:
        Dict[str, Any]: API响应结果
    """
    try:
        url = f"{self.command_url}/api/v2/device/name/{device_name}/{command_name}"
        
        if method.lower() == "get":
            response = requests.get(url, headers=self.headers)
        elif method.lower() == "put":
            response = requests.put(url, headers=self.headers, json=payload or {})
        else:
            self.logger.error(f"不支持的请求方法: {method}")
            return {"error": "不支持的请求方法"}
        
        if response.status_code in [200, 201]:
            self.logger.debug(f"成功执行设备命令: {device_name}/{command_name}")
            return response.json()
        else:
            self.logger.error(f"执行设备命令失败: {response.status_code}, {response.text}")
            return {"error": response.text}
    except Exception as e:
        self.logger.error(f"执行设备命令时发生错误: {str(e)}")
        return {"error": str(e)}