#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
平台连接器基类
提供连接边缘计算平台的通用功能
"""

import logging
import uuid
import time
import json
import threading
from abc import ABC, abstractmethod

from ..utils.config import ConfigManager
from ..utils.logger import setup_logger

class PlatformConnector(ABC):
    """平台连接器基类"""
    pass

# 为向后兼容保留的别名
ConnectorBase = PlatformConnector

def __init__(self, platform_name, config_path=None):
        """
        初始化平台连接器
        
        Args:
            platform_name (str): 平台名称
            config_path (str, optional): 配置文件路径. 默认为None.
        """
        self.platform_name = platform_name
        self.connector_id = f"{platform_name.lower()}_connector_{uuid.uuid4().hex[:8]}"
        
        # 加载配置
        self.config_manager = ConfigManager()
        if config_path:
            self.config = self.config_manager.load_config(config_path)
        else:
            self.config = self.config_manager.load_config(f"config/{platform_name.lower()}.yaml")
        
        # 设置日志
        self.logger = setup_logger(f"connector.{platform_name.lower()}", self.config.get("logging", {}))
        
        # 连接状态
        self.connected = False
        self.connection_thread = None
        self.should_stop = threading.Event()
        
        # 已注册设备
        self.registered_devices = {}
        
        # 连接信息
        self.host = self.config.get("host", "localhost")
        self.port = self.config.get("port", 8080)
        self.use_ssl = self.config.get("use_ssl", False)
        self.username = self.config.get("username", "")
        self.password = self.config.get("password", "")
        self.api_key = self.config.get("api_key", "")
        self.auth_token = None
        
        # 重试设置
        self.retry_interval = self.config.get("retry_interval", 5)
        self.max_retries = self.config.get("max_retries", 5)
        
        # 回调函数
        self.callbacks = {
            "on_connected": [],
            "on_disconnected": [],
            "on_data_received": [],
            "on_device_registered": [],
            "on_device_removed": [],
            "on_error": []
        }
        
        self.logger.info(f"初始化 {platform_name} 平台连接器")
    
def connect(self):
        """连接到平台"""
        if self.connected:
            self.logger.warning(f"{self.platform_name} 连接器已连接")
            return False
        
        self.logger.info(f"正在连接到 {self.platform_name} 平台 {self.host}:{self.port}")
        
        try:
            # 执行具体平台的连接逻辑
            if self._connect_to_platform():
                self.connected = True
                
                # 启动连接维护线程
                self.connection_thread = threading.Thread(
                    target=self._maintain_connection,
                    name=f"{self.platform_name}_connection_thread"
                )
                self.connection_thread.daemon = True
                self.should_stop.clear()
                self.connection_thread.start()
                
                self.logger.info(f"成功连接到 {self.platform_name} 平台")
                
                # 触发连接回调
                self._trigger_callbacks("on_connected")
                
                return True
            else:
                self.logger.error(f"无法连接到 {self.platform_name} 平台")
                return False
                
        except Exception as e:
            self.logger.error(f"连接 {self.platform_name} 平台时出错: {str(e)}")
            self._trigger_callbacks("on_error", error=str(e), error_type="connection")
            return False
    
def disconnect(self):
        """断开与平台的连接"""
        if not self.connected:
            self.logger.warning(f"{self.platform_name} 连接器未连接")
            return False
        
        self.logger.info(f"正在断开与 {self.platform_name} 平台的连接")
        
        try:
            # 停止连接线程
            self.should_stop.set()
            if self.connection_thread:
                self.connection_thread.join(timeout=2.0)
            
            # 执行具体平台的断开连接逻辑
            if self._disconnect_from_platform():
                self.connected = False
                
                self.logger.info(f"已断开与 {self.platform_name} 平台的连接")
                
                # 触发断开连接回调
                self._trigger_callbacks("on_disconnected")
                
                return True
            else:
                self.logger.error(f"无法正常断开与 {self.platform_name} 平台的连接")
                return False
                
        except Exception as e:
            self.logger.error(f"断开 {self.platform_name} 平台连接时出错: {str(e)}")
            self._trigger_callbacks("on_error", error=str(e), error_type="disconnection")
            
            # 强制标记为未连接
            self.connected = False
            return False
    
def register_device(self, device_info):
        """
        在平台上注册设备
        
        Args:
            device_info (dict): 设备信息
            
        Returns:
            bool: 是否成功注册
        """
        if not self.connected:
            self.logger.warning(f"{self.platform_name} 连接器未连接，无法注册设备")
            return False
        
        device_id = device_info.get("id")
        if not device_id:
            self.logger.error("注册设备失败: 设备ID为空")
            return False
        
        self.logger.info(f"正在 {self.platform_name} 平台上注册设备: {device_id}")
        
        try:
            # 执行具体平台的设备注册逻辑
            result = self._register_device_to_platform(device_info)
            
            if result:
                # 添加到已注册设备
                self.registered_devices[device_id] = device_info
                
                self.logger.info(f"设备 {device_id} 在 {self.platform_name} 平台上注册成功")
                
                # 触发设备注册回调
                self._trigger_callbacks("on_device_registered", device_id=device_id, device_info=device_info)
                
                return True
            else:
                self.logger.error(f"设备 {device_id} 在 {self.platform_name} 平台上注册失败")
                return False
                
        except Exception as e:
            self.logger.error(f"注册设备 {device_id} 时出错: {str(e)}")
            self._trigger_callbacks("on_error", error=str(e), error_type="device_registration", device_id=device_id)
            return False
    
def remove_device(self, device_id):
        """
        从平台上移除设备
        
        Args:
            device_id (str): 设备ID
            
        Returns:
            bool: 是否成功移除
        """
        if not self.connected:
            self.logger.warning(f"{self.platform_name} 连接器未连接，无法移除设备")
            return False
        
        if device_id not in self.registered_devices:
            self.logger.warning(f"设备 {device_id} 未在 {self.platform_name} 平台上注册")
            return False
        
        self.logger.info(f"正在从 {self.platform_name} 平台上移除设备: {device_id}")
        
        try:
            # 执行具体平台的设备移除逻辑
            result = self._remove_device_from_platform(device_id)
            
            if result:
                # 从已注册设备中移除
                device_info = self.registered_devices.pop(device_id, None)
                
                self.logger.info(f"设备 {device_id} 从 {self.platform_name} 平台上移除成功")
                
                # 触发设备移除回调
                self._trigger_callbacks("on_device_removed", device_id=device_id, device_info=device_info)
                
                return True
            else:
                self.logger.error(f"设备 {device_id} 从 {self.platform_name} 平台上移除失败")
                return False
                
        except Exception as e:
            self.logger.error(f"移除设备 {device_id} 时出错: {str(e)}")
            self._trigger_callbacks("on_error", error=str(e), error_type="device_removal", device_id=device_id)
            return False
    
def send_telemetry(self, device_id, telemetry_data):
        """
        发送设备遥测数据到平台
        
        Args:
            device_id (str): 设备ID
            telemetry_data (dict): 遥测数据
            
        Returns:
            bool: 是否成功发送
        """
        if not self.connected:
            self.logger.warning(f"{self.platform_name} 连接器未连接，无法发送遥测数据")
            return False
        
        if device_id not in self.registered_devices:
            self.logger.warning(f"设备 {device_id} 未在 {self.platform_name} 平台上注册，无法发送遥测数据")
            return False
        
        try:
            # 执行具体平台的遥测数据发送逻辑
            result = self._send_telemetry_to_platform(device_id, telemetry_data)
            
            if result:
                self.logger.debug(f"设备 {device_id} 遥测数据发送到 {self.platform_name} 平台成功")
                return True
            else:
                self.logger.warning(f"设备 {device_id} 遥测数据发送到 {self.platform_name} 平台失败")
                return False
                
        except Exception as e:
            self.logger.error(f"发送设备 {device_id} 遥测数据时出错: {str(e)}")
            self._trigger_callbacks("on_error", error=str(e), error_type="telemetry_sending", device_id=device_id)
            return False
    
def update_device_attributes(self, device_id, attributes):
        """
        更新设备属性
        
        Args:
            device_id (str): 设备ID
            attributes (dict): 设备属性
            
        Returns:
            bool: 是否成功更新
        """
        if not self.connected:
            self.logger.warning(f"{self.platform_name} 连接器未连接，无法更新设备属性")
            return False
        
        if device_id not in self.registered_devices:
            self.logger.warning(f"设备 {device_id} 未在 {self.platform_name} 平台上注册，无法更新设备属性")
            return False
        
        try:
            # 执行具体平台的属性更新逻辑
            result = self._update_device_attributes_on_platform(device_id, attributes)
            
            if result:
                self.logger.info(f"设备 {device_id} 属性在 {self.platform_name} 平台上更新成功")
                
                # 更新本地存储的设备信息
                for key, value in attributes.items():
                    if key in self.registered_devices[device_id]:
                        self.registered_devices[device_id][key] = value
                
                return True
            else:
                self.logger.warning(f"设备 {device_id} 属性在 {self.platform_name} 平台上更新失败")
                return False
                
        except Exception as e:
            self.logger.error(f"更新设备 {device_id} 属性时出错: {str(e)}")
            self._trigger_callbacks("on_error", error=str(e), error_type="attribute_update", device_id=device_id)
            return False
    
def get_device_commands(self, device_id):
        """
        获取平台发送给设备的命令
        
        Args:
            device_id (str): 设备ID
            
        Returns:
            list: 命令列表
        """
        if not self.connected:
            self.logger.warning(f"{self.platform_name} 连接器未连接，无法获取设备命令")
            return []
        
        if device_id not in self.registered_devices:
            self.logger.warning(f"设备 {device_id} 未在 {self.platform_name} 平台上注册，无法获取设备命令")
            return []
        
        try:
            # 执行具体平台的命令获取逻辑
            commands = self._get_device_commands_from_platform(device_id)
            
            if commands:
                self.logger.debug(f"获取到设备 {device_id} 的 {len(commands)} 条命令")
            
            return commands
                
        except Exception as e:
            self.logger.error(f"获取设备 {device_id} 命令时出错: {str(e)}")
            self._trigger_callbacks("on_error", error=str(e), error_type="command_retrieval", device_id=device_id)
            return []
    
def respond_to_command(self, device_id, command_id, response):
        """
        响应设备命令
        
        Args:
            device_id (str): 设备ID
            command_id (str): 命令ID
            response (dict): 响应数据
            
        Returns:
            bool: 是否成功响应
        """
        if not self.connected:
            self.logger.warning(f"{self.platform_name} 连接器未连接，无法响应设备命令")
            return False
        
        if device_id not in self.registered_devices:
            self.logger.warning(f"设备 {device_id} 未在 {self.platform_name} 平台上注册，无法响应设备命令")
            return False
        
        try:
            # 执行具体平台的命令响应逻辑
            result = self._respond_to_command_on_platform(device_id, command_id, response)
            
            if result:
                self.logger.debug(f"设备 {device_id} 响应命令 {command_id} 成功")
                return True
            else:
                self.logger.warning(f"设备 {device_id} 响应命令 {command_id} 失败")
                return False
                
        except Exception as e:
            self.logger.error(f"响应设备 {device_id} 命令 {command_id} 时出错: {str(e)}")
            self._trigger_callbacks("on_error", error=str(e), error_type="command_response", device_id=device_id)
            return False
    
def is_device_registered(self, device_id):
        """
        检查设备是否已注册
        
        Args:
            device_id (str): 设备ID
            
        Returns:
            bool: 设备是否已注册
        """
        return device_id in self.registered_devices
    
def get_registered_devices(self):
        """
        获取所有已注册设备
        
        Returns:
            dict: 设备ID到设备信息的映射
        """
        return self.registered_devices
    
def add_callback(self, event_type, callback):
        """
        添加回调函数
        
        Args:
            event_type (str): 事件类型
            callback (callable): 回调函数
            
        Returns:
            bool: 是否成功添加
        """
        if event_type not in self.callbacks:
            self.logger.warning(f"未知的事件类型: {event_type}")
            return False
        
        if not callable(callback):
            self.logger.warning(f"回调函数必须是可调用对象")
            return False
        
        self.callbacks[event_type].append(callback)
        return True
    
def remove_callback(self, event_type, callback):
        """
        移除回调函数
        
        Args:
            event_type (str): 事件类型
            callback (callable): 回调函数
            
        Returns:
            bool: 是否成功移除
        """
        if event_type not in self.callbacks:
            self.logger.warning(f"未知的事件类型: {event_type}")
            return False
        
        if callback in self.callbacks[event_type]:
            self.callbacks[event_type].remove(callback)
            return True
        else:
            self.logger.warning(f"未找到指定的回调函数")
            return False
    
def _trigger_callbacks(self, event_type, **kwargs):
        """
        触发回调函数
        
        Args:
            event_type (str): 事件类型
            **kwargs: 传递给回调函数的参数
        """
        if event_type not in self.callbacks:
            return
        
        for callback in self.callbacks[event_type]:
            try:
                callback(platform=self.platform_name, **kwargs)
            except Exception as e:
                self.logger.error(f"执行 {event_type} 回调时出错: {str(e)}")
    
def _maintain_connection(self):
        """维护与平台的连接（在线程中运行）"""
        self.logger.info(f"启动 {self.platform_name} 连接维护线程")
        
        while not self.should_stop.is_set():
            try:
                # 检查连接状态
                if self.connected and not self._check_connection():
                    self.logger.warning(f"{self.platform_name} 连接已断开，尝试重新连接")
                    
                    # 标记为未连接
                    self.connected = False
                    
                    # 触发断开连接回调
                    self._trigger_callbacks("on_disconnected")
                    
                    # 尝试重新连接
                    retry_count = 0
                    while not self.should_stop.is_set() and retry_count < self.max_retries:
                        retry_count += 1
                        self.logger.info(f"尝试重新连接到 {self.platform_name} 平台 (尝试 {retry_count}/{self.max_retries})")
                        
                        if self._connect_to_platform():
                            self.connected = True
                            self.logger.info(f"重新连接到 {self.platform_name} 平台成功")
                            
                            # 触发连接回调
                            self._trigger_callbacks("on_connected")
                            break
                        
                        self.logger.warning(f"重新连接到 {self.platform_name} 平台失败，将在 {self.retry_interval} 秒后重试")
                        
                        # 等待重试间隔，同时检查是否应该停止
                        self.should_stop.wait(self.retry_interval)
                    
                    if not self.connected and not self.should_stop.is_set():
                        self.logger.error(f"无法重新连接到 {self.platform_name} 平台，达到最大重试次数")
                
                # 接收并处理平台数据
                if self.connected:
                    self._receive_platform_data()
                
                # 等待一段时间
                self.should_stop.wait(1.0)
                
            except Exception as e:
                self.logger.error(f"{self.platform_name} 连接维护线程出错: {str(e)}")
                
                # 触发错误回调
                self._trigger_callbacks("on_error", error=str(e), error_type="connection_maintenance")
                
                # 等待一段时间
                self.should_stop.wait(self.retry_interval)
        
        self.logger.info(f"{self.platform_name} 连接维护线程已停止")
    
@abstractmethod
def _connect_to_platform(self):
        """
        连接到具体平台的实现
        
        Returns:
            bool: 是否成功连接
        """
        pass
    
@abstractmethod
def _disconnect_from_platform(self):
    """
    断开与具体平台连接的实现
    
    Returns:
        bool: 是否成功断开连接
    """
    pass
    
@abstractmethod
def _check_connection(self):
        """
        检查与平台的连接状态
        
        Returns:
            bool: 连接是否正常
        """
        pass
    
@abstractmethod
def _receive_platform_data(self):
        """接收并处理平台数据"""
        pass
    
@abstractmethod
def _register_device_to_platform(self, device_info):
        """
        在具体平台上注册设备的实现
        
        Args:
            device_info (dict): 设备信息
            
        Returns:
            bool: 是否成功注册
        """
        pass
    
@abstractmethod
def _remove_device_from_platform(self, device_id):
        """
        从具体平台上移除设备的实现
        
        Args:
            device_id (str): 设备ID
            
        Returns:
            bool: 是否成功移除
        """
        pass
    
@abstractmethod
def _send_telemetry_to_platform(self, device_id, telemetry_data):
        """
        向具体平台发送遥测数据的实现
        
        Args:
            device_id (str): 设备ID
            telemetry_data (dict): 遥测数据
            
        Returns:
            bool: 是否成功发送
        """
        pass
    
@abstractmethod
def _update_device_attributes_on_platform(self, device_id, attributes):
        """
        在具体平台上更新设备属性的实现
        
        Args:
            device_id (str): 设备ID
            attributes (dict): 设备属性
            
        Returns:
            bool: 是否成功更新
        """
        pass
    
@abstractmethod
def _get_device_commands_from_platform(self, device_id):
        """
        从具体平台获取设备命令的实现
        
        Args:
            device_id (str): 设备ID
            
        Returns:
            list: 命令列表
        """
        pass
    
@abstractmethod
def _respond_to_command_on_platform(self, device_id, command_id, response):
        """
        在具体平台上响应设备命令的实现
        
        Args:
            device_id (str): 设备ID
            command_id (str): 命令ID
            response (dict): 响应数据
            
        Returns:
            bool: 是否成功响应
        """
        pass