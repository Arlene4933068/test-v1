#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
边缘设备模拟器基类
提供所有边缘设备模拟器的通用功能
"""

import uuid
import time
import random
import logging
import threading
import json
from abc import ABC, abstractmethod
from datetime import datetime

# 导入工具模块
from .utils.config import ConfigManager
from .utils.logger import setup_logger
from .utils.crypto import encrypt_data, decrypt_data
from .utils.protocol import Protocol

class DeviceSimulator(ABC):
    """边缘设备模拟器基类"""
    
    def __init__(self, device_type, config_path=None):
        """
        初始化设备模拟器
        
        Args:
            device_type (str): 设备类型标识
            config_path (str, optional): 配置文件路径. 默认为None.
        """
        # 设备基本信息
        self.device_type = device_type
        self.device_id = f"{device_type}_{uuid.uuid4().hex[:8]}"
        self.name = f"{device_type}_{int(time.time())}"
        self.status = "offline"
        self.created_time = datetime.now()
        self.last_online_time = None
        
        # 加载配置
        self.config_manager = ConfigManager()
        if config_path:
            self.config = self.config_manager.load_config(config_path)
        else:
            self.config = self.config_manager.load_config("config/simulator.yaml")
        
        # 设备特定配置
        self.device_config = self.config.get(device_type, {})
        
        # 设置日志
        self.logger = setup_logger(f"simulator.{device_type}", self.config.get("logging", {}))
        
        # 通信协议
        self.protocol = Protocol(self.config.get("protocol", {}).get(device_type, "mqtt"))
        
        # 设备特性
        self.features = self.device_config.get("features", {})
        
        # 遥测数据点
        self.telemetry_points = self.device_config.get("telemetry", {})
        
        # 安全参数
        self.security_settings = self.device_config.get("security", {})
        
        # 连接状态
        self.connected = False
        self.connection_thread = None
        self.should_stop = threading.Event()
        
        # 行为模式
        self.behavior_mode = self.device_config.get("behavior", "normal")
        
        self.logger.info(f"初始化设备模拟器: {self.device_id}, 类型: {self.device_type}")
    
        # 新增基础资源监控属性初始化
        self.cpu_usage = 0.0
        self.memory_usage = 0.0 
        self.uptime = 0
        self.network_usage = {"up": 0.0, "down": 0.0}
        
        # 新增设备状态标志初始化
        self._is_active = False
        self._operation_mode = "normal"
    
    def connect(self):
        """连接到平台"""
        if self.connected:
            self.logger.warning(f"设备 {self.device_id} 已经连接")
            return
        
        try:
            self.connection_thread = threading.Thread(target=self._run, name=f"{self.device_type}_thread")
            self.connection_thread.daemon = True
            self.should_stop.clear()
            self.connection_thread.start()
            self.connected = True
            self.status = "online"
            self.last_online_time = datetime.now()
            self.logger.info(f"设备 {self.device_id} 已连接")
        except Exception as e:
            self.logger.error(f"设备 {self.device_id} 连接失败: {str(e)}")
    
    def disconnect(self):
        """断开与平台的连接"""
        if not self.connected:
            return
        
        try:
            self.should_stop.set()
            if self.connection_thread:
                self.connection_thread.join(timeout=2.0)
            self.connected = False
            self.status = "offline"
            self.logger.info(f"设备 {self.device_id} 已断开连接")
        except Exception as e:
            self.logger.error(f"设备 {self.device_id} 断开连接失败: {str(e)}")
    
    def _run(self):
        """运行设备模拟行为（在线程中）"""
        self.logger.info(f"设备 {self.device_id} 开始运行")
        
        # 初始设备注册
        self._register_device()
        
        # 定时生成遥测数据
        telemetry_interval = self.device_config.get("telemetry_interval", 10)
        
        while not self.should_stop.is_set():
            try:
                # 生成并发送遥测数据
                telemetry_data = self.generate_telemetry()
                self._send_telemetry(telemetry_data)
                
                # 设备特定行为
                self.device_behavior()
                
                # 根据当前模式可能触发异常行为
                if self.behavior_mode == "attack":
                    self._simulate_attack()
                elif self.behavior_mode == "anomaly":
                    self._simulate_anomaly()
                
                # 等待下一个间隔
                self.should_stop.wait(telemetry_interval)
            except Exception as e:
                self.logger.error(f"设备 {self.device_id} 运行时错误: {str(e)}")
                # 短暂等待后继续
                self.should_stop.wait(1)
        
        self.logger.info(f"设备 {self.device_id} 停止运行")
    
    def _register_device(self):
        """向平台注册设备"""
        device_info = {
            "id": self.device_id,
            "name": self.name,
            "type": self.device_type,
            "model": self.device_config.get("model", "generic"),
            "manufacturer": "Xiaomi",
            "firmware_version": self.device_config.get("firmware_version", "1.0.0"),
            "features": self.features,
            "created_time": self.created_time.isoformat()
        }
        
        # 如果有安全凭证，则添加
        if "credentials" in self.security_settings:
            device_info["credentials"] = self.security_settings.get("credentials")
        
        # 修改为安全访问方式
        device_info.update({
            "auto_update": self.security_settings.get("auto_update", True),
            "encryption_enabled": self.security_settings.get("encrypt_telemetry", False),
            "auth_mode": self.security_settings.get("auth_mode", "basic")
        })
        self.logger.info(f"正在注册设备 {self.device_id}")
        # 这里应该调用平台连接器的注册方法
        # 在子类中实现具体的注册逻辑
    
    def _send_telemetry(self, telemetry_data):
        """
        发送遥测数据到平台
        
        Args:
            telemetry_data (dict): 遥测数据
        """
        if not self.connected:
            self.logger.warning(f"设备 {self.device_id} 未连接，无法发送遥测数据")
            return
        
        # 添加时间戳
        telemetry_data["timestamp"] = int(time.time() * 1000)
        
        # 根据安全设置加密数据
        if self.security_settings.get("encrypt_telemetry", False):
            encrypted_data = encrypt_data(json.dumps(telemetry_data), 
                                         self.security_settings.get("encryption_key", "default_key"))
            payload = {"encrypted": True, "data": encrypted_data}
        else:
            payload = telemetry_data
        
        self.logger.debug(f"设备 {self.device_id} 发送遥测数据: {telemetry_data}")
        # 具体的发送逻辑在子类中实现
    
    def _simulate_attack(self):
        """模拟攻击行为"""
        attack_type = random.choice(["ddos", "mitm", "firmware", "credential"])
        self.logger.debug(f"设备 {self.device_id} 模拟攻击行为: {attack_type}")
        
        if attack_type == "ddos":
            # 模拟DDoS攻击 - 高频率发送大量数据
            for _ in range(random.randint(5, 20)):
                spam_data = {"spam": "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=500))}
                self._send_telemetry(spam_data)
                time.sleep(0.1)
        
        elif attack_type == "mitm":
            # 模拟中间人攻击 - 发送伪造的认证信息
            fake_auth = {
                "token": "fake_token_" + uuid.uuid4().hex,
                "command": "admin_access",
                "params": {"action": "escalate_privileges"}
            }
            self._send_telemetry(fake_auth)
        
        elif attack_type == "firmware":
            # 模拟固件篡改
            firmware_attack = {
                "firmware_update": True,
                "version": "malicious_1.0",
                "url": "http://malicious-server.com/update.bin"
            }
            self._send_telemetry(firmware_attack)
        
        elif attack_type == "credential":
            # 模拟凭证盗取攻击
            brute_force = {
                "auth_attempt": True,
                "credentials": [
                    {"username": "admin", "password": "password123"},
                    {"username": "root", "password": "toor"},
                    {"username": "user", "password": "123456"}
                ]
            }
            self._send_telemetry(brute_force)
    
    def _simulate_anomaly(self):
        """模拟异常行为（不一定是攻击，但不符合正常模式）"""
        anomaly_type = random.choice(["data_spike", "connection_issue", "config_change"])
        self.logger.debug(f"设备 {self.device_id} 模拟异常行为: {anomaly_type}")
        
        if anomaly_type == "data_spike":
            # 模拟数据异常峰值
            spike_data = {}
            for key in self.telemetry_points:
                # 生成正常值的10-50倍
                normal_value = self.telemetry_points[key].get("normal_value", 1)
                spike_data[key] = normal_value * random.uniform(10, 50)
            self._send_telemetry(spike_data)
            
        elif anomaly_type == "connection_issue":
            # 模拟连接异常 - 短暂断开然后重连
            self.logger.info(f"设备 {self.device_id} 模拟连接异常")
            self.status = "unstable"
            time.sleep(random.uniform(0.5, 2.0))
            self.status = "online"
            
        elif anomaly_type == "config_change":
            # 模拟配置异常变更
            config_change = {
                "config_update": True,
                "changes": {
                    "remote_access": True,
                    "telemetry_frequency": 0.1,  # 异常高频率
                    "debug_mode": True
                }
            }
            self._send_telemetry(config_change)
    
    def set_behavior_mode(self, mode):
        """
        设置设备行为模式
        
        Args:
            mode (str): 行为模式 - normal, attack, anomaly
        """
        if mode not in ["normal", "attack", "anomaly"]:
            self.logger.warning(f"无效的行为模式: {mode}, 使用 'normal'")
            mode = "normal"
        
        self.behavior_mode = mode
        self.logger.info(f"设备 {self.device_id} 行为模式设置为: {mode}")
    
    def get_device_info(self):
        """获取设备信息"""
        return {
            "id": self.device_id,
            "name": self.name,
            "type": self.device_type,
            "status": self.status,
            "created_time": self.created_time.isoformat(),
            "last_online_time": self.last_online_time.isoformat() if self.last_online_time else None,
            "features": self.features,
            "behavior_mode": self.behavior_mode
        }
    
    @abstractmethod
    def generate_telemetry(self):
        """
        生成设备遥测数据（由子类实现）
        
        Returns:
            dict: 遥测数据
        """
        pass
    
    @abstractmethod
    def device_behavior(self):
        """
        设备特定行为（由子类实现）
        """
        pass
    
    def _update_resource_usage(self):
        """更新设备资源使用情况（基类实现）"""
        # 基础资源模拟
        self.cpu_usage = max(0.0, min(100.0, 
            self.cpu_usage + random.uniform(-5.0, 5.0)))
        self.memory_usage = max(0.0, min(100.0,
            self.memory_usage + random.uniform(-3.0, 3.0)))
        self.uptime += 1
        
        # 网络流量模拟
        self.network_usage["up"] = random.expovariate(1/50)
        self.network_usage["down"] = random.expovariate(1/100)
        
        return {
            "cpu": self.cpu_usage,
            "memory": self.memory_usage,
            "uptime": self.uptime,
            "network": self.network_usage
        }

@property
def is_active(self):
    """设备是否处于活动状态"""
    return self._is_active

    @is_active.setter
    def is_active(self, value):
        old_state = self._is_active
        self._is_active = bool(value)
        if old_state != self._is_active:
            event = "activated" if self._is_active else "deactivated"
            self.logger.info(f"设备 {self.device_id} {event}")
