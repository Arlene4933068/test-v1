#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ThingsBoard Edge 连接器
提供与Docker中部署的ThingsBoard Edge实例的连接和交互功能
"""

import requests
import json
import logging
import time
from typing import Dict, List, Any, Optional
from .connector_base import ConnectorBase
import paho.mqtt.client as mqtt

class ThingsBoardConnector(ConnectorBase):
    """ThingsBoard Edge 平台连接器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化ThingsBoard连接器
        
        Args:
            config: 包含连接配置的字典
                - host: ThingsBoard主机地址 (默认为 'localhost')
                - port: ThingsBoard HTTP端口 (默认为 8080)
                - mqtt_port: ThingsBoard MQTT端口 (默认为 1883)
                - username: 用户名
                - password: 密码
                - tenant_id: 租户ID (可选)
        """
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
        # 设置连接参数
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 8080)  # 与您环境中的ThingsBoard端口一致
        self.mqtt_port = config.get('mqtt_port', 1883)  # 与您环境中的MQTT端口一致
        self.username = config.get('username')
        self.password = config.get('password')
        self.tenant_id = config.get('tenant_id', None)
        
        # 设置基础URL
        self.base_url = f"http://{self.host}:{self.port}/api"
        
        # 认证令牌
        self.auth_token = None
        self.jwt_token = None
        
        # MQTT客户端
        self.mqtt_client = None
    
    def connect(self) -> bool:
        """
        连接到ThingsBoard Edge实例
        
        Returns:
            bool: 连接成功返回True，否则返回False
        """
        try:
            # 登录以获取JWT令牌
            login_payload = {"username": self.username, "password": self.password}
            response = requests.post(
                f"{self.base_url}/auth/login",
                headers={"Content-Type": "application/json", "Accept": "application/json"},
                json=login_payload
            )
            
            if response.status_code == 200:
                self.jwt_token = response.json().get('token')
                self.logger.info("成功连接到ThingsBoard Edge实例")
                return True
            else:
                self.logger.error(f"无法连接到ThingsBoard Edge实例，登录失败: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"连接ThingsBoard Edge实例时发生错误: {str(e)}")
            return False
    
    def disconnect(self) -> bool:
        """
        断开与ThingsBoard Edge的连接
        
        Returns:
            bool: 断开连接成功返回True，否则返回False
        """
        try:
            # 断开MQTT连接（如果存在）
            if self.mqtt_client and self.mqtt_client.is_connected():
                self.mqtt_client.disconnect()
            
            self.jwt_token = None
            self.auth_token = None
            self.logger.info("已断开与ThingsBoard Edge的连接")
            return True
        except Exception as e:
            self.logger.error(f"断开ThingsBoard Edge连接时发生错误: {str(e)}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """
        获取带有JWT令牌的请求头
        
        Returns:
            Dict[str, str]: 请求头字典
        """
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Authorization": f"Bearer {self.jwt_token}"
        }
    
    def create_device(self, name: str, type: str, label: Optional[str] = None) -> Dict[str, Any]:
        """
        在ThingsBoard中创建设备
        
        Args:
            name: 设备名称
            type: 设备类型
            label: 设备标签 (可选)
        
        Returns:
            Dict[str, Any]: 创建的设备信息，失败时返回空字典
        """
        try:
            device_data = {
                "name": name,
                "type": type
            }
            
            if label:
                device_data["label"] = label
            
            response = requests.post(
                f"{self.base_url}/device",
                headers=self._get_headers(),
                json=device_data
            )
            
            if response.status_code in [200, 201]:
                device_info = response.json()
                self.logger.info(f"成功创建设备: {name} (ID: {device_info.get('id', {}).get('id')})")
                return device_info
            else:
                self.logger.error(f"创建设备失败: {response.status_code}, {response.text}")
                return {}
        except Exception as e:
            self.logger.error(f"创建设备时发生错误: {str(e)}")
            return {}
    
    def get_device_credentials(self, device_id: str) -> Dict[str, Any]:
        """
        获取设备凭证
        
        Args:
            device_id: 设备ID
        
        Returns:
            Dict[str, Any]: 设备凭证信息，失败时返回空字典
        """
        try:
            response = requests.get(
                f"{self.base_url}/device/{device_id}/credentials",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                credentials = response.json()
                self.logger.debug(f"成功获取设备凭证: {device_id}")
                return credentials
            else:
                self.logger.error(f"获取设备凭证失败: {response.status_code}, {response.text}")
                return {}
        except Exception as e:
            self.logger.error(f"获取设备凭证时发生错误: {str(e)}")
            return {}
    
    def connect_mqtt_device(self, access_token: str) -> bool:
        """
        使用MQTT连接设备
        
        Args:
            access_token: 设备访问令牌
        
        Returns:
            bool: 连接成功返回True，否则返回False
        """
        try:
            # 创建新的MQTT客户端
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.username_pw_set(access_token)
            
            # 连接回调
            def on_connect(client, userdata, flags, rc):
                if rc == 0:
                    self.logger.info(f"MQTT设备连接成功，访问令牌: {access_token}")
                else:
                    self.logger.error(f"MQTT设备连接失败，访问令牌: {access_token}，返回码: {rc}")
            
            self.mqtt_client.on_connect = on_connect
            
            # 连接到MQTT代理
            self.mqtt_client.connect(self.host, self.mqtt_port, 60)
            self.mqtt_client.loop_start()
            
            # 等待连接确认
            time.sleep(1)
            
            return self.mqtt_client.is_connected()
        except Exception as e:
            self.logger.error(f"MQTT设备连接时发生错误: {str(e)}")
            return False
    
    def send_telemetry(self, access_token: str, telemetry_data: Dict[str, Any]) -> bool:
        """
        发送设备遥测数据
        
        Args:
            access_token: 设备访问令牌
            telemetry_data: 遥测数据
        
        Returns:
            bool: 发送成功返回True，否则返回False
        """
        try:
            # 如果没有现有的MQTT连接或连接已关闭，则创建新连接
            if not self.mqtt_client or not self.mqtt_client.is_connected():
                if not self.connect_mqtt_device(access_token):
                    return False
            
            result = self.mqtt_client.publish("v1/devices/me/telemetry", json.dumps(telemetry_data))
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.debug(f"成功发送遥测数据，访问令牌: {access_token}")
                return True
            else:
                self.logger.error(f"发送遥测数据失败: {result.rc}")
                return False
        except Exception as e:
            self.logger.error(f"发送遥测数据时发生错误: {str(e)}")
            return False
    
    def send_attributes(self, access_token: str, attributes: Dict[str, Any]) -> bool:
        """
        发送设备属性数据
        
        Args:
            access_token: 设备访问令牌
            attributes: 属性数据
        
        Returns:
            bool: 发送成功返回True，否则返回False
        """
        try:
            # 如果没有现有的MQTT连接或连接已关闭，则创建新连接
            if not self.mqtt_client or not self.mqtt_client.is_connected():
                if not self.connect_mqtt_device(access_token):
                    return False
            
            result = self.mqtt_client.publish("v1/devices/me/attributes", json.dumps(attributes))
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.debug(f"成功发送属性数据，访问令牌: {access_token}")
                return True
            else:
                self.logger.error(f"发送属性数据失败: {result.rc}")
                return False
        except Exception as e:
            self.logger.error(f"发送属性数据时发生错误: {str(e)}")
            return False
    
    def create_dashboard(self, title: str, configuration: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建仪表板
        
        Args:
            title: 仪表板标题
            configuration: 仪表板配置
        
        Returns:
            Dict[str, Any]: 创建的仪表板信息，失败时返回空字典
        """
        try:
            dashboard_data = {
                "title": title,
                "configuration": configuration
            }
            
            response = requests.post(
                f"{self.base_url}/dashboard",
                headers=self._get_headers(),
                json=dashboard_data
            )
            
            if response.status_code in [200, 201]:
                dashboard_info = response.json()
                self.logger.info(f"成功创建仪表板: {title}")
                return dashboard_info
            else:
                self.logger.error(f"创建仪表板失败: {response.status_code}, {response.text}")
                return {}
        except Exception as e:
            self.logger.error(f"创建仪表板时发生错误: {str(e)}")
            return {}