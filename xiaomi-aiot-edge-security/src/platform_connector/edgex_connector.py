"""
EdgeX Foundry 连接器 - 通过REST API与EdgeX Foundry通信
"""
import json
import time
import uuid
import logging
from typing import Dict, Any, List, Optional
import requests
from requests.exceptions import RequestException

from . import connector_base

class EdgeXConnector(connector_base.ConnectorBase):
    """
    EdgeX Foundry连接器，通过REST API与EdgeX Foundry通信
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化EdgeX Foundry连接器
        
        Args:
            config: 连接配置信息，必须包含:
                - url: EdgeX Foundry API的基础URL
                - service_name: 设备服务名称
                - profile_name: 设备配置文件名称
        """
        super().__init__()
        self.config = config
        self.base_url = config.get('url', 'http://localhost:48080')
        self.core_metadata_url = config.get('core_metadata_url', 'http://localhost:48081') 
        self.core_data_url = config.get('core_data_url', 'http://localhost:48080')
        self.core_command_url = config.get('core_command_url', 'http://localhost:48082')
        self.service_name = config.get('service_name', 'xiaomi-aiot-device-service')
        self.profile_name = config.get('profile_name', 'xiaomi-aiot-device-profile')
        self.device_cache = {}  # 缓存已创建的设备信息
        self.logger = logging.getLogger(__name__)
        
    def connect(self) -> bool:
        """
        连接到EdgeX Foundry
        
        Returns:
            连接是否成功
        """
        try:
            # 检查Core Metadata服务是否可访问
            response = requests.get(f"{self.core_metadata_url}/api/v1/ping")
            if response.status_code == 200:
                self.is_connected = True
                self.logger.info("成功连接到EdgeX Foundry")
                
                # 确保设备服务存在
                self._ensure_device_service_exists()
                
                # 确保设备配置文件存在
                self._ensure_device_profile_exists()
                
                return True
            else:
                self.logger.error(f"无法连接到EdgeX Foundry: HTTP {response.status_code}")
                return False
        except RequestException as e:
            self.logger.error(f"连接EdgeX Foundry失败: {str(e)}")
            return False
    
    def disconnect(self) -> bool:
        """
        断开与EdgeX Foundry的连接
        
        Returns:
            断开连接是否成功
        """
        self.is_connected = False
        self.logger.info("已断开与EdgeX Foundry的连接")
        return True
    
    def create_device(self, device_info: Dict[str, Any]) -> str:
        """
        在EdgeX中创建设备
        
        Args:
            device_info: 设备信息，应包含:
                - name: 设备名称
                - description: 设备描述
                - labels: 设备标签
                - protocols: 设备协议配置
                
        Returns:
            创建的设备ID
        """
        if not self.is_connected:
            self.logger.error("未连接到EdgeX Foundry，无法创建设备")
            return ""
        
        # 生成唯一设备名称（如果未提供）
        if 'name' not in device_info:
            device_info['name'] = f"xiaomi-aiot-{device_info.get('type', 'device')}-{str(uuid.uuid4())[:8]}"
        
        # 准备设备创建请求
        device_data = {
            "name": device_info['name'],
            "description": device_info.get('description', '小米AIoT模拟设备'),
            "adminState": "UNLOCKED",
            "operatingState": "ENABLED",
            "labels": device_info.get('labels', ["xiaomi", "aiot", "simulation"]),
            "service": {"name": self.service_name},
            "profile": {"name": self.profile_name},
            "protocols": device_info.get('protocols', {
                "HTTP": {
                    "host": "localhost",
                    "port": "8080",
                    "path": f"/api/devices/{device_info['name']}"
                }
            })
        }
        
        try:
            # 创建设备
            response = requests.post(
                f"{self.core_metadata_url}/api/v1/device",
                json=device_data
            )
            
            if response.status_code == 200:
                # EdgeX创建设备成功后，会返回设备ID
                device_id = response.json()['id']
                self.logger.info(f"成功在EdgeX创建设备: {device_info['name']}, ID: {device_id}")
                
                # 缓存设备信息
                self.device_cache[device_id] = {
                    "name": device_info['name'],
                    "type": device_info.get('type', 'generic')
                }
                
                return device_id
            else:
                self.logger.error(f"创建设备失败: HTTP {response.status_code}, {response.text}")
                return ""
        except RequestException as e:
            self.logger.error(f"创建设备请求异常: {str(e)}")
            return ""
    
    def delete_device(self, device_id: str) -> bool:
        """
        删除EdgeX中的设备
        
        Args:
            device_id: 设备ID
            
        Returns:
            删除是否成功
        """
        if not self.is_connected:
            self.logger.error("未连接到EdgeX Foundry，无法删除设备")
            return False
        
        try:
            # EdgeX通过设备ID删除设备
            response = requests.delete(f"{self.core_metadata_url}/api/v1/device/id/{device_id}")
            
            if response.status_code == 200:
                self.logger.info(f"成功删除设备: {device_id}")
                # 从缓存中移除设备
                if device_id in self.device_cache:
                    del self.device_cache[device_id]
                return True
            else:
                self.logger.error(f"删除设备失败: HTTP {response.status_code}, {response.text}")
                return False
        except RequestException as e:
            self.logger.error(f"删除设备请求异常: {str(e)}")
            return False
    
    def send_telemetry(self, device_id: str, data: Dict[str, Any]) -> bool:
        """
        发送设备遥测数据到EdgeX
        
        Args:
            device_id: 设备ID
            data: 遥测数据，键值对形式
            
        Returns:
            发送是否成功
        """
        if not self.is_connected:
            self.logger.error("未连接到EdgeX Foundry，无法发送遥测数据")
            return False
        
        if device_id not in self.device_cache:
            self.logger.error(f"设备ID {device_id} 未在缓存中找到")
            return False
        
        device_name = self.device_cache[device_id]["name"]
        
        # 准备事件数据
        current_time = int(time.time() * 1000)  # 毫秒时间戳
        readings = []
        
        for key, value in data.items():
            # 根据值类型确定读数类型
            if isinstance(value, int):
                reading_type = "Int64"
            elif isinstance(value, float):
                reading_type = "Float64"
            elif isinstance(value, bool):
                reading_type = "Bool"
                value = str(value).lower()  # "true" 或 "false"
            else:
                reading_type = "String"
                value = str(value)
            
            readings.append({
                "name": key,
                "value": value,
                "valueType": reading_type,
                "origin": current_time
            })
        
        event_data = {
            "device": device_name,
            "origin": current_time,
            "readings": readings
        }
        
        try:
            # 发送事件数据
            response = requests.post(
                f"{self.core_data_url}/api/v1/event",
                json=event_data
            )
            
            if response.status_code == 200:
                self.logger.debug(f"成功发送遥测数据: {device_name}")
                return True
            else:
                self.logger.error(f"发送遥测数据失败: HTTP {response.status_code}, {response.text}")
                return False
        except RequestException as e:
            self.logger.error(f"发送遥测数据请求异常: {str(e)}")
            return False
    
    def get_commands(self, device_id: str) -> List[Dict[str, Any]]:
        """
        获取发送给设备的命令
        
        Args:
            device_id: 设备ID
            
        Returns:
            命令列表
        """
        if not self.is_connected:
            self.logger.error("未连接到EdgeX Foundry，无法获取命令")
            return []
        
        if device_id not in self.device_cache:
            self.logger.error(f"设备ID {device_id} 未在缓存中找到")
            return []
        
        device_name = self.device_cache[device_id]["name"]
        
        try:
            # 获取设备的可用命令
            response = requests.get(f"{self.core_command_url}/api/v1/device/name/{device_name}")
            
            if response.status_code == 200:
                # 解析命令信息
                command_data = response.json()
                commands = []
                
                if "commands" in command_data:
                    for cmd in command_data["commands"]:
                        if "get" in cmd:  # 仅处理GET命令作为示例
                            commands.append({
                                "id": cmd.get("id", ""),
                                "name": cmd.get("name", ""),
                                "url": cmd.get("get", {}).get("url", ""),
                                "parameters": []  # EdgeX不直接提供参数，可以从URL解析
                            })
                
                return commands
            else:
                self.logger.error(f"获取命令失败: HTTP {response.status_code}, {response.text}")
                return []
        except RequestException as e:
            self.logger.error(f"获取命令请求异常: {str(e)}")
            return []
    
    def send_command_response(self, device_id: str, command_id: str, response: Dict[str, Any]) -> bool:
        """
        发送命令执行结果
        
        Args:
            device_id: 设备ID
            command_id: 命令ID
            response: 命令执行结果
            
        Returns:
            发送是否成功
        """
        # EdgeX通常不需要显式发送命令响应，因为它是通过REST API直接响应的
        # 这里提供一个简单的实现，仅记录日志
        self.logger.info(f"命令执行结果 - 设备: {device_id}, 命令: {command_id}, 响应: {response}")
        return True
    
    def _ensure_device_service_exists(self):
        """确保设备服务存在，如果不存在则创建"""
        try:
            # 检查设备服务是否存在
            response = requests.get(f"{self.core_metadata_url}/api/v1/deviceservice/name/{self.service_name}")
            
            if response.status_code == 200:
                self.logger.info(f"设备服务已存在: {self.service_name}")
            elif response.status_code == 404:
                # 创建设备服务
                service_data = {
                    "name": self.service_name,
                    "description": "小米AIoT设备仿真服务",
                    "adminState": "UNLOCKED",
                    "operatingState": "ENABLED",
                    "labels": ["xiaomi", "aiot", "simulation"],
                    "addressable": {
                        "name": f"{self.service_name}-addressable",
                        "protocol": "HTTP",
                        "address": "localhost",
                        "port": 8080,
                        "path": "/api"
                    }
                }
                
                create_response = requests.post(
                    f"{self.core_metadata_url}/api/v1/deviceservice",
                    json=service_data
                )
                
                if create_response.status_code == 200:
                    self.logger.info(f"成功创建设备服务: {self.service_name}")
                else:
                    self.logger.error(f"创建设备服务失败: HTTP {create_response.status_code}, {create_response.text}")
            else:
                self.logger.error(f"检查设备服务失败: HTTP {response.status_code}, {response.text}")
        except RequestException as e:
            self.logger.error(f"设备服务检查异常: {str(e)}")
    
    def _ensure_device_profile_exists(self):
        """确保设备配置文件存在，如果不存在则创建"""
        try:
            # 检查设备配置文件是否存在
            response = requests.get(f"{self.core_metadata_url}/api/v1/deviceprofile/name/{self.profile_name}")
            
            if response.status_code == 200:
                self.logger.info(f"设备配置文件已存在: {self.profile_name}")
            elif response.status_code == 404:
                # 创建基本的设备配置文件
                # 注意：实际应用中应从YAML文件加载完整的设备配置文件
                profile_data = {
                    "name": self.profile_name,
                    "manufacturer": "Xiaomi",
                    "model": "AIoT-Simulation",
                    "labels": ["xiaomi", "aiot", "simulation"],
                    "description": "小米AIoT设备模拟配置文件",
                    "deviceResources": [
                        {
                            "name": "temperature",
                            "description": "温度传感器",
                            "properties": {
                                "valueType": "Float64",
                                "readWrite": "R",
                                "units": "度"
                            }
                        },
                        {
                            "name": "humidity",
                            "description": "湿度传感器",
                            "properties": {
                                "valueType": "Float64",
                                "readWrite": "R",
                                "units": "%"
                            }
                        },
                        {
                            "name": "status",
                            "description": "设备状态",
                            "properties": {
                                "valueType": "String",
                                "readWrite": "RW"
                            }
                        }
                    ]
                }
                
                create_response = requests.post(
                    f"{self.core_metadata_url}/api/v1/deviceprofile",
                    json=profile_data
                )
                
                if create_response.status_code == 200:
                    self.logger.info(f"成功创建设备配置文件: {self.profile_name}")
                else:
                    self.logger.error(f"创建设备配置文件失败: HTTP {create_response.status_code}, {create_response.text}")
            else:
                self.logger.error(f"检查设备配置文件失败: HTTP {response.status_code}, {response.text}")
        except RequestException as e:
            self.logger.error(f"设备配置文件检查异常: {str(e)}")