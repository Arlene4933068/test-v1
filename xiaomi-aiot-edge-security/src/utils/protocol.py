#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
协议处理工具模块
提供与IoT设备通信所需的各种协议支持，包括MQTT、CoAP、HTTP等
"""

import json
import logging
import requests
import paho.mqtt.client as mqtt
from typing import Dict, Any, Callable, Optional, Union
import aiocoap
import asyncio

from .logger import get_logger

logger = get_logger(__name__)

class ProtocolHandler:
    """协议处理基类"""
    
    def __init__(self, protocol_type: str):
        """
        初始化协议处理器
        
        Args:
            protocol_type: 协议类型，如 "mqtt", "coap", "http"
        """
        self.protocol_type = protocol_type
        self.logger = logging.getLogger(f"protocol.{protocol_type}")
    
    def validate_message(self, message: Dict[str, Any]) -> bool:
        """
        验证消息格式是否有效
        
        Args:
            message: 要验证的消息
            
        Returns:
            bool: 消息是否有效
        """
        if not isinstance(message, dict):
            self.logger.warning(f"Invalid message format: {message}")
            return False
        
        # 基本消息格式验证
        required_fields = ['device_id', 'timestamp', 'data']
        return all(field in message for field in required_fields)


class MQTTHandler(ProtocolHandler):
    """MQTT协议处理器"""
    
    def __init__(self, broker_host: str = "localhost", broker_port: int = 1883, 
                 username: Optional[str] = None, password: Optional[str] = None):
        """
        初始化MQTT协议处理器
        
        Args:
            broker_host: MQTT代理主机
            broker_port: MQTT代理端口
            username: 认证用户名 (可选)
            password: 认证密码 (可选)
        """
        super().__init__("mqtt")
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = mqtt.Client()
        
        if username and password:
            self.client.username_pw_set(username, password)
            
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        
        self.subscriptions = {}
        self.is_connected = False
        
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT连接回调"""
        if rc == 0:
            self.logger.info(f"Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
            self.is_connected = True
            
            # 重新订阅所有话题
            for topic, callback in self.subscriptions.items():
                self.client.subscribe(topic)
                self.logger.debug(f"Re-subscribed to topic: {topic}")
        else:
            self.logger.error(f"Failed to connect to MQTT broker, return code: {rc}")
            self.is_connected = False
    
    def _on_message(self, client, userdata, msg):
        """MQTT消息回调"""
        topic = msg.topic
        
        try:
            payload = json.loads(msg.payload.decode())
            
            if topic in self.subscriptions and callable(self.subscriptions[topic]):
                if self.validate_message(payload):
                    self.subscriptions[topic](payload)
                else:
                    self.logger.warning(f"Received invalid message format on topic {topic}")
        except json.JSONDecodeError:
            self.logger.warning(f"Received non-JSON message on topic {topic}")
        except Exception as e:
            self.logger.error(f"Error processing message on topic {topic}: {e}")
    
    def _on_disconnect(self, client, userdata, rc):
        """MQTT断开连接回调"""
        self.logger.warning(f"Disconnected from MQTT broker with code: {rc}")
        self.is_connected = False
    
    def connect(self):
        """连接到MQTT代理"""
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            self.logger.error(f"Error connecting to MQTT broker: {e}")
            return False
    
    def disconnect(self):
        """断开与MQTT代理的连接"""
        if self.is_connected:
            self.client.loop_stop()
            self.client.disconnect()
            self.is_connected = False
            self.logger.info("Disconnected from MQTT broker")
    
    def subscribe(self, topic: str, callback: Callable[[Dict[str, Any]], None]):
        """
        订阅MQTT主题
        
        Args:
            topic: 要订阅的MQTT主题
            callback: 接收消息时要调用的回调函数
        """
        if not self.is_connected:
            if not self.connect():
                self.logger.error(f"Cannot subscribe to {topic}: not connected")
                return False
        
        self.subscriptions[topic] = callback
        result, _ = self.client.subscribe(topic)
        
        if result == mqtt.MQTT_ERR_SUCCESS:
            self.logger.info(f"Subscribed to topic: {topic}")
            return True
        else:
            self.logger.error(f"Failed to subscribe to topic: {topic}")
            return False
    
    def publish(self, topic: str, message: Dict[str, Any], qos: int = 0) -> bool:
        """
        发布MQTT消息
        
        Args:
            topic: 要发布的MQTT主题
            message: 要发布的消息 (字典格式)
            qos: 服务质量 (0, 1, 或 2)
            
        Returns:
            bool: 发布是否成功
        """
        if not self.is_connected:
            if not self.connect():
                self.logger.error(f"Cannot publish to {topic}: not connected")
                return False
        
        if not isinstance(message, dict):
            self.logger.error(f"Message must be a dictionary, got {type(message)}")
            return False
            
        try:
            payload = json.dumps(message)
            result = self.client.publish(topic, payload, qos)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.logger.debug(f"Published message to {topic}")
                return True
            else:
                self.logger.error(f"Failed to publish message to {topic}, error code: {result.rc}")
                return False
        except Exception as e:
            self.logger.error(f"Error publishing message to {topic}: {e}")
            return False


class HTTPHandler(ProtocolHandler):
    """HTTP协议处理器"""
    
    def __init__(self, base_url: str = "", headers: Optional[Dict[str, str]] = None):
        """
        初始化HTTP协议处理器
        
        Args:
            base_url: 基础URL
            headers: 要包含在所有请求中的HTTP头
        """
        super().__init__("http")
        self.base_url = base_url
        self.headers = headers or {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        发送HTTP GET请求
        
        Args:
            endpoint: API端点
            params: 查询参数
            
        Returns:
            Dict: 响应数据
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"HTTP GET error: {e}")
            return {"error": str(e)}
    
    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送HTTP POST请求
        
        Args:
            endpoint: API端点
            data: 请求数据
            
        Returns:
            Dict: 响应数据
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"HTTP POST error: {e}")
            return {"error": str(e)}
    
    def put(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送HTTP PUT请求
        
        Args:
            endpoint: API端点
            data: 请求数据
            
        Returns:
            Dict: 响应数据
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.put(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"HTTP PUT error: {e}")
            return {"error": str(e)}
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """
        发送HTTP DELETE请求
        
        Args:
            endpoint: API端点
            
        Returns:
            Dict: 响应数据
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.delete(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"HTTP DELETE error: {e}")
            return {"error": str(e)}


class CoAPHandler(ProtocolHandler):
    """CoAP协议处理器"""
    
    def __init__(self, server_host: str = "localhost", server_port: int = 5683):
        """
        初始化CoAP协议处理器
        
        Args:
            server_host: CoAP服务器主机
            server_port: CoAP服务器端口
        """
        super().__init__("coap")
        self.server_host = server_host
        self.server_port = server_port
        self.loop = asyncio.new_event_loop()
        
    async def _request(self, method: str, path: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        发送CoAP请求
        
        Args:
            method: 请求方法 (GET, POST, PUT, DELETE)
            path: 资源路径
            payload: 请求负载
            
        Returns:
            Dict: 响应数据
        """
        protocol = await aiocoap.Context.create_client_context()
        
        request = aiocoap.Message(code=method)
        request.set_request_uri(f"coap://{self.server_host}:{self.server_port}/{path}")
        
        if payload:
            request.payload = json.dumps(payload).encode('utf-8')
            request.opt.content_format = 50  # application/json
        
        try:
            response = await protocol.request(request).response
            if response.payload:
                return json.loads(response.payload.decode('utf-8'))
            return {"status": "success"}
        except Exception as e:
            self.logger.error(f"CoAP request error: {e}")
            return {"error": str(e)}
        finally:
            await protocol.shutdown()
    
    def get(self, path: str) -> Dict[str, Any]:
        """
        发送CoAP GET请求
        
        Args:
            path: 资源路径
            
        Returns:
            Dict: 响应数据
        """
        return self.loop.run_until_complete(self._request('GET', path))
    
    def post(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送CoAP POST请求
        
        Args:
            path: 资源路径
            data: 请求数据
            
        Returns:
            Dict: 响应数据
        """
        return self.loop.run_until_complete(self._request('POST', path, data))
    
    def put(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送CoAP PUT请求
        
        Args:
            path: 资源路径
            data: 请求数据
            
        Returns:
            Dict: 响应数据
        """
        return self.loop.run_until_complete(self._request('PUT', path, data))
    
    def delete(self, path: str) -> Dict[str, Any]:
        """
        发送CoAP DELETE请求
        
        Args:
            path: 资源路径
            
        Returns:
            Dict: 响应数据
        """
        return self.loop.run_until_complete(self._request('DELETE', path))


def create_protocol_handler(protocol: str, **kwargs) -> Union[MQTTHandler, HTTPHandler, CoAPHandler]:
    """
    创建协议处理器工厂函数
    
    Args:
        protocol: 协议类型，支持 "mqtt", "http", "coap"
        **kwargs: 传递给相应协议处理器的参数
        
    Returns:
        协议处理器实例
        
    Raises:
        ValueError: 如果指定了不支持的协议
    """
    protocol = protocol.lower()
    if protocol == "mqtt":
        return MQTTHandler(**kwargs)
    elif protocol == "http":
        return HTTPHandler(**kwargs)
    elif protocol == "coap":
        return CoAPHandler(**kwargs)
    else:
        raise ValueError(f"Unsupported protocol: {protocol}")