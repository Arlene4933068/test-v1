"""
ThingsBoard Edge 连接器 - 通过REST API与ThingsBoard Edge通信
"""
import json
import uuid
import time
import logging
import requests
from typing import Dict, Any, List, Optional
from requests.exceptions import RequestException

from . import connector_base

class ThingsBoardConnector(connector_base.ConnectorBase):
    """
    ThingsBoard Edge连接器，通过REST API与ThingsBoard Edge通信
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化ThingsBoard Edge连接器
        
        Args:
            config: 连接配置信息，必须包含:
                - url: ThingsBoard Edge API的基础URL
                - username: 登录用户名
                - password: 登录密码
        """
        super().__init__()
        self.config = config
        self.base_url = config.get('url', 'http://localhost:8080')
        self.username = config.get('username', 'tenant@thingsboard.org')
        self.password = config.get('password', 'tenant')
        self.token = None
        self.device_cache = {}  # 缓存已创建的设备信息
        self.logger = logging.getLogger(__name__)
    
    def connect(self) -> bool:
        """
        连接到ThingsBoard Edge，获取认证令牌
        
        Returns:
            连接是否成功
        """
        try:
            # 登录获取JWT令牌
            login_url = f"{self.base_url}/api/auth/login"
            response = requests.post(
                login_url,
                json={"username": self.username, "password": self.password}
            )
            
            if response.status_code == 200:
                self.token = response.json()['token']
                self.is_connected = True
                self.logger.info("成功连接到ThingsBoard Edge")
                return True
            else:
                self.logger.error(f"ThingsBoard Edge登录失败: HTTP {response.status_code}, {response.text}")
                return False
        except RequestException as e:
            self.logger.error(f"连接ThingsBoard Edge失败: {str(e)}")
            return False
    
    def disconnect(self) -> bool:
        """
        断开与ThingsBoard Edge的连接
        
        Returns:
            断开连接是否成功
        """
        self.token = None
        self.is_connected = False
        self.logger.info("已断开与ThingsBoard Edge的连接")
        return True
    
    def create_device(self, device_info: Dict[str, Any]) -> str:
        """
        在ThingsBoard中创建设备
        
        Args:
            device_info: 设备信息，应包含:
                - name: 设备名称
                - type: 设备类型
                - label: 设备标签
                
        Returns:
            创建的设备ID
        """
        if not self.is_connected or not self.token:
            self.logger.error("未连接到ThingsBoard Edge，无法创建设备")
            return ""
        
        # 生成唯一设备名称（如果未提供）
        if 'name' not in device_info:
            device_info['name'] = f"xiaomi-aiot-{device_info.get('type', 'device')}-{str(uuid.uuid4())[:8]}"
        
        # 准备设备创建请求
        device_data = {
            "name": device_info['name'],
            "type": device_info.get('type', 'default'),
            "label": device_info.get('label', '小米AIoT模拟设备')
        }
        
        headers = {
            "Content-Type": "application/json",
            "X-Authorization": f"Bearer {self.token}"
        }
        
        try:
            # 创建设备
            response = requests.post(
                f"{self.base_url}/api/device",
                headers=headers,
                json=device_data
            )
            
            if response.status_code == 200:
                device_id = response.json()['id']['id']
                self.logger.info(f"成功在ThingsBoard创建设备: {device_info['name']}, ID: {device_id}")
                
                # 缓存设备信息
                self.device_cache[device_id] = {
                    "name": device_info['name'],
                    "type": device_info.get('type', 'default')
                }
                
                # 获取设备访问令牌
                credentials_response = requests.get(
                    f"{self.base_url}/api/device/{device_id}/credentials",
                    headers=headers
                )
                
                if credentials_response.status_code == 200:
                    access_token = credentials_response.json()['credentialsId']
                    self.device_cache[device_id]['access_token'] = access_token
                    self.logger.info(f"获取设备访问令牌: {access_token}")
                else:
                    self.logger.warning(f"获取设备访问令牌失败: HTTP {credentials_response.status_code}")
                
                return device_id
            else:
                self.logger.error(f"创建设备失败: HTTP {response.status_code}, {response.text}")
                return ""
        except RequestException as e:
            self.logger.error(f"创建设备请求异常: {str(e)}")
            return ""
    
    def delete_device(self, device_id: str) -> bool:
        """
        删除ThingsBoard中的设备
        
        Args:
            device_id: 设备ID
            
        Returns:
            删除是否成功
        """
        if not self.is_connected or not self.token:
            self.logger.error("未连接到ThingsBoard Edge，无法删除设备")
            return False
        
        headers = {
            "Content-Type": "application/json",
            "X-Authorization": f"Bearer {self.token}"
        }
        
        try:
            # 删除设备
            response = requests.delete(
                f"{self.base_url}/api/device/{device_id}",
                headers=headers
            )
            
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
        发送设备遥测数据到ThingsBoard
        
        Args:
            device_id: 设备ID
            data: 遥测数据，键值对形式
            
        Returns:
            发送是否成功
        """
        if not self.is_connected:
            self.logger.error("未连接到ThingsBoard Edge，无法发送遥测数据")
            return False
        
        if device_id not in self.device_cache or 'access_token' not in self.device_cache[device_id]:
            self.logger.error(f"设备ID {device_id} 未在缓存中找到或缺少访问令牌")
            return False
        
        access_token = self.device_cache[device_id]['access_token']
        
        try:
            # 发送遥测数据
            response = requests.post(
                f"{self.base_url}/api/v1/{access_token}/telemetry",
                json=data
            )
            
            if response.status_code == 200:
                self.logger.debug(f"成功发送遥测数据: {self.device_cache[device_id]['name']}")
                return True
            else:
                self.logger.error(f"发送遥测数据失败: HTTP {response.status_code}, {response.text}")
                return False
        except RequestException as e:
            self.logger.error(f"发送遥测数据请求异常: {str(e)}")
            return False
    
    def get_commands(self, device_id: str) -> List[Dict[str, Any]]:
        """
        获取发送给设备的RPC命令
        
        Args:
            device_id: 设备ID
            
        Returns:
            命令列表
        """
        # ThingsBoard的设备RPC命令需要通过MQTT或WebSocket订阅获取
        # 这里实现一个模拟的命令列表
        self.logger.info(f"获取设备 {device_id} 的命令")
        
        # 返回模拟的命令列表
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
        if not self.is_connected or not self.token:
            self.logger.error("未连接到ThingsBoard Edge，无法发送命令响应")
            return False
        
        if device_id not in self.device_cache or 'access_token' not in self.device_cache[device_id]:
            self.logger.error(f"设备ID {device_id} 未在缓存中找到或缺少访问令牌")
            return False
        
        access_token = self.device_cache[device_id]['access_token']
        
        try:
            # 发送RPC响应
            response_url = f"{self.base_url}/api/v1/{access_token}/rpc/{command_id}"
            response = requests.post(
                response_url,
                json=response
            )
            
            if response.status_code == 200:
                self.logger.info(f"成功发送命令响应: {command_id}")
                return True
            else:
                self.logger.error(f"发送命令响应失败: HTTP {response.status_code}, {response.text}")
                return False
        except RequestException as e:
            self.logger.error(f"发送命令响应请求异常: {str(e)}")
            return False
    
    def get_device_attributes(self, device_id: str) -> Dict[str, Any]:
        """
        获取设备属性
        
        Args:
            device_id: 设备ID
            
        Returns:
            设备属性字典
        """
        if not self.is_connected or not self.token:
            self.logger.error("未连接到ThingsBoard Edge，无法获取设备属性")
            return {}
        
        headers = {
            "Content-Type": "application/json",
            "X-Authorization": f"Bearer {self.token}"
        }
        
        try:
            # 获取设备属性
            response = requests.get(
                f"{self.base_url}/api/plugins/telemetry/DEVICE/{device_id}/values/attributes",
                headers=headers
            )
            
            if response.status_code == 200:
                attributes = {}
                for attr in response.json():
                    attributes[attr['key']] = attr['value']
                self.logger.debug(f"获取设备属性成功: {device_id}")
                return attributes
            else:
                self.logger.error(f"获取设备属性失败: HTTP {response.status_code}, {response.text}")
                return {}
        except RequestException as e:
            self.logger.error(f"获取设备属性请求异常: {str(e)}")
            return {}
    
    def set_device_attributes(self, device_id: str, attributes: Dict[str, Any]) -> bool:
        """
        设置设备属性
        
        Args:
            device_id: 设备ID
            attributes: 设备属性字典
            
        Returns:
            设置是否成功
        """
        if not self.is_connected or not self.token:
            self.logger.error("未连接到ThingsBoard Edge，无法设置设备属性")
            return False
        
        if device_id not in self.device_cache or 'access_token' not in self.device_cache[device_id]:
            self.logger.error(f"设备ID {device_id} 未在缓存中找到或缺少访问令牌")
            return False
        
        access_token = self.device_cache[device_id]['access_token']
        
        try:
            # 设置客户端属性
            response = requests.post(
                f"{self.base_url}/api/v1/{access_token}/attributes",
                json=attributes
            )
            
            if response.status_code == 200:
                self.logger.debug(f"设置设备属性成功: {device_id}")
                return True
            else:
                self.logger.error(f"设置设备属性失败: HTTP {response.status_code}, {response.text}")
                return False
        except RequestException as e:
            self.logger.error(f"设置设备属性请求异常: {str(e)}")
            return False