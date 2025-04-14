#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备基类模块
定义所有模拟设备的基本接口和功能
"""

import logging
import time
import threading
import uuid
from typing import Dict, Any, List, Optional, Callable
from abc import ABC, abstractmethod

class DeviceBase(ABC):
    """设备基类，定义所有模拟设备的基本接口"""
    
    def __init__(self, device_id: str, edgex_id: Optional[str] = None,
                 tb_device_info: Optional[Dict[str, Any]] = None,
                 tb_credentials: Optional[Dict[str, Any]] = None,
                 edgex_connector=None, thingsboard_connector=None,
                 properties: Dict[str, Any] = None):
        """
        初始化设备基类
        
        Args:
            device_id: 设备ID
            edgex_id: EdgeX设备ID
            tb_device_info: ThingsBoard设备信息
            tb_credentials: ThingsBoard设备凭证
            edgex_connector: EdgeX连接器实例
            thingsboard_connector: ThingsBoard连接器实例
            properties: 设备属性
        """
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.device_id = device_id
        self.edgex_id = edgex_id
        self.tb_device_info = tb_device_info
        self.tb_credentials = tb_credentials
        self.edgex_connector = edgex_connector
        self.thingsboard_connector = thingsboard_connector
        self.properties = properties or {}
        
        # 遥测数据发送间隔（秒）
        self.telemetry_interval = self.properties.get("telemetry_interval", 5)
        
        # 设备状态和遥测数据
        self.state = {
            "status": "offline",  # 设备状态：offline, online
            "last_updated": time.time()
        }
        
        # 遥测数据发送线程
        self._telemetry_thread = None
        self._telemetry_stop_event = threading.Event()
    
    def start(self) -> bool:
        """
        启动设备模拟
        
        Returns:
            bool: 启动成功返回True，否则返回False
        """
        try:
            # 更新设备状态为在线
            self.state["status"] = "online"
            self.state["last_updated"] = time.time()
            
            # 启动遥测线程
            self._telemetry_stop_event.clear()
            self._telemetry_thread = threading.Thread(target=self._telemetry_loop)
            self._telemetry_thread.daemon = True
            self._telemetry_thread.start()
            
            self.logger.info(f"设备{self.device_id}已启动")
            return True
        except Exception as e:
            self.logger.error(f"启动设备{self.device_id}失败: {str(e)}")
            return False
    
    def stop(self) -> bool:
        """
        停止设备模拟
        
        Returns:
            bool: 停止成功返回True，否则返回False
        """
        try:
            # 停止遥测线程
            if self._telemetry_thread and self._telemetry_thread.is_alive():
                self._telemetry_stop_event.set()
                self._telemetry_thread.join(timeout=5.0)
            
            # 更新设备状态为离线
            self.state["status"] = "offline"
            self.state["last_updated"] = time.time()
            
            self.logger.info(f"设备{self.device_id}已停止")
            return True
        except Exception as e:
            self.logger.error(f"停止设备{self.device_id}失败: {str(e)}")
            return False
    
    def _telemetry_loop(self):
        """遥测数据发送循环"""
        while not self._telemetry_stop_event.is_set():
            try:
                # 生成遥测数据
                telemetry = self.generate_telemetry()
                
                # 发送数据到EdgeX
                if self.edgex_id and self.edgex_connector:
                    readings = []
                    for key, value in telemetry.items():
                        readings.append({
                            "resourceName": key,
                            "value": str(value)
                        })
                    
                    self.edgex_connector.send_device_data(self.device_id, readings)
                
                # 发送数据到ThingsBoard
                if (self.tb_device_info and self.tb_credentials and 
                    self.thingsboard_connector and "credentialsId" in self.tb_credentials):
                    access_token = self.tb_credentials.get("credentialsId")
                    self.thingsboard_connector.send_telemetry(access_token, telemetry)
                
                # 更新最后更新时间
                self.state["last_updated"] = time.time()
            
            except Exception as e:
                self.logger.error(f"发送遥测数据失败: {str(e)}")
            
            # 等待下一个发送间隔
            self._telemetry_stop_event.wait(self.telemetry_interval)
    
    @abstractmethod
    def generate_telemetry(self) -> Dict[str, Any]:
        """
        生成设备遥测数据
        
        Returns:
            Dict[str, Any]: 遥测数据字典
        """
        pass
    
    @abstractmethod
    def handle_command(self, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理设备命令
        
        Args:
            command: 命令名称
            params: 命令参数
        
        Returns:
            Dict[str, Any]: 命令执行结果
        """
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取设备状态
        
        Returns:
            Dict[str, Any]: 设备状态信息
        """
        status = {
            "device_id": self.device_id,
            "type": self.__class__.__name__,
            "status": self.state["status"],
            "last_updated": self.state["last_updated"]
        }
        
        # 添加平台特定信息
        if self.edgex_id:
            status["edgex_id"] = self.edgex_id
        
        if self.tb_device_info and "id" in self.tb_device_info:
            status["tb_id"] = self.tb_device_info["id"].get("id", "")
        
        return status