#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网关设备模拟器
模拟小米AIoT边缘网关设备
"""

import random
import time
import json
import threading
from datetime import datetime

from .simulator_base import DeviceSimulator
from ..utils.crypto import generate_random_key

class GatewaySimulator(DeviceSimulator):
    """网关设备模拟器类"""
    
    def __init__(self, config_path=None):
        """
        初始化网关模拟器
        
        Args:
            config_path (str, optional): 配置文件路径. 默认为None.
        """
        super().__init__("gateway", config_path)
        
        # 网关特有属性
        self.connected_devices = []
        self.max_devices = self.device_config.get("max_devices", 50)
        self.gateway_model = self.device_config.get("model", "Xiaomi AIoT Gateway Pro")
        self.firmware_version = self.device_config.get("firmware_version", "3.2.1")
        self.network_interfaces = self.device_config.get("network_interfaces", {
            "wifi": {"enabled": True, "ssid": "Xiaomi_Gateway", "security": "WPA2", "frequency": "2.4GHz"},
            "ethernet": {"enabled": True, "speed": "1000Mbps", "duplex": "full"},
            "zigbee": {"enabled": True, "version": "3.0", "channel": 15},
            "bluetooth": {"enabled": True, "version": "5.0", "mode": "BLE"},
            "thread": {"enabled": False}
        })
        
        # 网关处理能力
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.disk_usage = 0.0
        self.bandwidth_usage = 0.0
        
        # 网关安全状态
        self.firewall_enabled = self.security_settings.get("firewall_enabled", True)
        self.security_level = self.security_settings.get("security_level", "high")
        self.security_updates = self.security_settings.get("auto_update", True)
        self.access_token = generate_random_key(32) if self.firewall_enabled else None
        
        # 网关功能
        self.edge_computing = self.features.get("edge_computing", True)
        self.local_storage = self.features.get("local_storage", True)
        self.remote_management = self.features.get("remote_management", True)
        
        # 模拟连接设备管理
        self.device_management_thread = None
        self.logger.info(f"网关设备 {self.device_id} 初始化完成, 型号: {self.gateway_model}")
    
    def connect(self):
        """连接网关设备并启动设备管理"""
        super().connect()
        
        if self.connected:
            # 启动设备管理线程
            self.device_management_thread = threading.Thread(
                target=self._manage_connected_devices,
                name=f"{self.device_id}_device_management"
            )
            self.device_management_thread.daemon = True
            self.device_management_thread.start()
            self.logger.info(f"网关 {self.device_id} 设备管理系统已启动")
    
    def disconnect(self):
        """断开网关设备连接"""
        # 通知所有连接的设备断开连接
        for device in self.connected_devices:
            device_id = device.get("id", "unknown")
            self.logger.info(f"网关 {self.device_id} 断开与设备 {device_id} 的连接")
        
        self.connected_devices = []
        super().disconnect()
    
    def generate_telemetry(self):
        """
        生成网关遥测数据
        
        Returns:
            dict: 网关遥测数据
        """
        # 更新资源使用情况
        if self.behavior_mode == "normal":
            # 正常模式下的资源使用
            self.cpu_usage = random.uniform(10, 40)
            self.memory_usage = random.uniform(20, 50)
            self.disk_usage = random.uniform(30, 60)
            self.bandwidth_usage = random.uniform(100, 500)  # KB/s
        elif self.behavior_mode == "anomaly":
            # 异常模式 - 资源使用偏高但不至于攻击
            self.cpu_usage = random.uniform(50, 75)
            self.memory_usage = random.uniform(60, 85)
            self.disk_usage = random.uniform(70, 90)
            self.bandwidth_usage = random.uniform(800, 2000)  # KB/s
        elif self.behavior_mode == "attack":
            # 攻击模式 - 资源使用极高
            self.cpu_usage = random.uniform(85, 100)
            self.memory_usage = random.uniform(90, 100)
            self.disk_usage = random.uniform(95, 100)
            self.bandwidth_usage = random.uniform(3000, 10000)  # KB/s
        
        telemetry = {
            "cpu_usage": round(self.cpu_usage, 2),
            "memory_usage": round(self.memory_usage, 2),
            "disk_usage": round(self.disk_usage, 2),
            "bandwidth_usage": round(self.bandwidth_usage, 2),
            "connected_device_count": len(self.connected_devices),
            "uptime": int(time.time() - self.created_time.timestamp()),
            "firewall_enabled": self.firewall_enabled,
            "security_level": self.security_level,
            "last_security_update": (datetime.now() - self.created_time).days
        }
        
        # 网络接口状态
        network_status = {}
        for interface, config in self.network_interfaces.items():
            if config.get("enabled", False):
                # 模拟接口连接质量
                quality = random.uniform(0.7, 1.0)
                if self.behavior_mode == "anomaly":
                    quality = random.uniform(0.3, 0.7)
                elif self.behavior_mode == "attack":
                    quality = random.uniform(0.0, 0.3)
                
                network_status[interface] = {
                    "connected": quality > 0.2,  # 低于0.2时断开
                    "signal_strength": int(quality * 100) if interface in ["wifi", "zigbee", "bluetooth"] else None,
                    "data_rate": round(quality * float(config.get("speed", "100").replace("Mbps", "")), 2) 
                        if interface == "ethernet" else None
                }
        
        telemetry["network_status"] = network_status
        
        # 异常或攻击时可能会有额外的指标
        if self.behavior_mode in ["anomaly", "attack"]:
            telemetry["unusual_packets"] = random.randint(10, 1000)
            telemetry["failed_auth_attempts"] = random.randint(5, 50)
            telemetry["blocked_connections"] = random.randint(3, 30)
        
        return telemetry
    
    def device_behavior(self):
        """网关设备特定行为"""
        # 定期检查安全更新
        if self.security_updates and random.random() < 0.05:  # 5%的几率执行更新检查
            self.logger.info(f"网关 {self.device_id} 正在检查安全更新")
            # 模拟更新过程
            if random.random() < 0.3:  # 30%的几率有新更新
                self.firmware_version = f"3.{random.randint(2, 9)}.{random.randint(1, 9)}"
                self.logger.info(f"网关 {self.device_id} 更新固件到版本 {self.firmware_version}")
                
                # 发送更新通知
                update_info = {
                    "event": "firmware_update",
                    "previous_version": self.device_config.get("firmware_version", "3.2.1"),
                    "new_version": self.firmware_version,
                    "update_time": datetime.now().isoformat()
                }
                self._send_telemetry(update_info)
                
                # 更新配置中的版本信息
                self.device_config["firmware_version"] = self.firmware_version
        
        # 模拟网关执行边缘计算任务
        if self.edge_computing and random.random() < 0.1:  # 10%的几率执行边缘计算
            self.logger.debug(f"网关 {self.device_id} 正在执行边缘计算任务")
            # 模拟计算资源消耗
            self.cpu_usage += random.uniform(5, 15)
            self.memory_usage += random.uniform(5, 10)
            self.cpu_usage = min(self.cpu_usage, 100)
            self.memory_usage = min(self.memory_usage, 100)
            
            # 模拟计算结果
            compute_result = {
                "event": "edge_compute",
                "task_id": f"task_{int(time.time())}",
                "execution_time_ms": random.randint(50, 500),
                "success": random.random() < 0.95,  # 95%成功率
                "resource_usage": {
                    "cpu": round(self.cpu_usage, 2),
                    "memory": round(self.memory_usage, 2)
                }
            }
            
            # 仅记录日志而不发送，避免过多数据
            self.logger.debug(f"边缘计算结果: {compute_result}")
    
    def _manage_connected_devices(self):
        """管理与网关连接的设备"""
        while self.connected and not self.should_stop.is_set():
            try:
                # 模拟设备连接/断开
                current_device_count = len(self.connected_devices)
                
                # 随机增加设备
                if current_device_count < self.max_devices and random.random() < 0.1:  # 10%几率添加设备
                    new_device = self._generate_random_device()
                    self.connected_devices.append(new_device)
                    self.logger.info(f"新设备 {new_device['id']} 连接到网关 {self.device_id}")
                    
                    # 发送设备连接事件
                    connect_event = {
                        "event": "device_connected",
                        "device_id": new_device["id"],
                        "device_type": new_device["type"],
                        "connection_time": datetime.now().isoformat()
                    }
                    self._send_telemetry(connect_event)
                
                # 随机移除设备
                if current_device_count > 0 and random.random() < 0.05:  # 5%几率移除设备
                    removed_device = random.choice(self.connected_devices)
                    self.connected_devices.remove(removed_device)
                    self.logger.info(f"设备 {removed_device['id']} 从网关 {self.device_id} 断开连接")
                    
                    # 发送设备断开事件
                    disconnect_event = {
                        "event": "device_disconnected",
                        "device_id": removed_device["id"],
                        "device_type": removed_device["type"],
                        "disconnection_time": datetime.now().isoformat(),
                        "reason": random.choice(["user_initiated", "timeout", "signal_lost", "power_off"])
                    }
                    self._send_telemetry(disconnect_event)
                
                # 模拟设备通信活动
                self._simulate_device_activities()
                
                # 间隔等待
                time.sleep(random.uniform(3, 8))
                
            except Exception as e:
                self.logger.error(f"设备管理异常: {str(e)}")
                time.sleep(1)
    
    def _generate_random_device(self):
        """生成随机连接设备信息"""
        device_types = ["light", "switch", "sensor", "lock", "thermostat", "speaker", "camera"]
        device_type = random.choice(device_types)
        device_id = f"{device_type}_{int(time.time())}_{random.randint(1000, 9999)}"
        
        return {
            "id": device_id,
            "type": device_type,
            "name": f"Xiaomi {device_type.capitalize()} {random.randint(1, 99)}",
            "protocol": random.choice(["zigbee", "bluetooth", "wifi"]),
            "connected_since": datetime.now().isoformat(),
            "firmware_version": f"1.{random.randint(0, 9)}.{random.randint(0, 9)}",
            "battery_level": random.randint(10, 100) if random.random() < 0.7 else None,  # 70%是电池设备
            "last_activity": datetime.now().isoformat()
        }
    
    def _simulate_device_activities(self):
        """模拟设备通信活动"""
        # 只对一部分设备进行活动模拟以避免过多数据
        active_device_count = min(len(self.connected_devices), 3)
        if active_device_count <= 0:
            return
            
        for _ in range(active_device_count):
            if len(self.connected_devices) > 0:
                device = random.choice(self.connected_devices)
                
                # 更新最后活动时间
                device["last_activity"] = datetime.now().isoformat()
                
                # 模拟设备数据传输
                if device["type"] == "sensor":
                    # 传感器数据
                    data = {
                        "event": "device_data",
                        "device_id": device["id"],
                        "data_type": random.choice(["temperature", "humidity", "motion", "light", "pressure"]),
                        "value": round(random.uniform(0, 100), 2),
                        "unit": random.choice(["°C", "%", "lux", "hPa", "boolean"]),
                        "timestamp": datetime.now().isoformat()
                    }
                elif device["type"] in ["camera", "speaker"]:
                    # 摄像头或音箱的流量较大
                    data = {
                        "event": "device_stream",
                        "device_id": device["id"],
                        "stream_type": "video" if device["type"] == "camera" else "audio",
                        "bitrate": random.randint(500, 5000),  # Kbps
                        "duration": random.randint(10, 60),  # 秒
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    # 其他设备的状态变化
                    data = {
                        "event": "device_state_change",
                        "device_id": device["id"],
                        "state": random.choice(["on", "off", "idle", "active", "error"]),
                        "timestamp": datetime.now().isoformat()
                    }
                
                # 仅记录日志而不发送，避免过多数据
                self.logger.debug(f"设备活动: {data}")
                
                # 如果是攻击模式，有机会注入恶意指令
                if self.behavior_mode == "attack" and random.random() < 0.2:
                    data["malicious_payload"] = {
                        "command": random.choice(["extract_credentials", "scan_network", "upload_data"]),
                        "target": "cloud_server" if random.random() < 0.5 else "local_network"
                    }
                    self.logger.debug(f"注入恶意指令: {data['malicious_payload']}")
    
    def add_device(self, device_info):
        """手动添加设备到网关"""
        if len(self.connected_devices) >= self.max_devices:
            self.logger.warning(f"网关 {self.device_id} 已达到最大设备数量 {self.max_devices}")
            return False
        
        self.connected_devices.append(device_info)
        self.logger.info(f"手动添加设备 {device_info['id']} 到网关 {self.device_id}")
        
        # 发送设备连接事件
        connect_event = {
            "event": "device_connected",
            "device_id": device_info["id"],
            "device_type": device_info["type"],
            "connection_time": datetime.now().isoformat(),
            "manual_add": True
        }
        self._send_telemetry(connect_event)
        return True
    
    def remove_device(self, device_id):
        """手动移除设备"""
        for device in self.connected_devices:
            if device["id"] == device_id:
                self.connected_devices.remove(device)
                self.logger.info(f"手动移除设备 {device_id} 从网关 {self.device_id}")
                
                # 发送设备断开事件
                disconnect_event = {
                    "event": "device_disconnected",
                    "device_id": device_id,
                    "device_type": device["type"],
                    "disconnection_time": datetime.now().isoformat(),
                    "reason": "user_initiated",
                    "manual_remove": True
                }
                self._send_telemetry(disconnect_event)
                return True
        
        self.logger.warning(f"设备 {device_id} 未连接到网关 {self.device_id}")
        return False
    
    def get_connected_devices(self):
        """获取所有连接的设备"""
        return self.connected_devices
    
    def update_security_settings(self, settings):
        """更新安全设置"""
        if "firewall_enabled" in settings:
            self.firewall_enabled = settings["firewall_enabled"]
        
        if "security_level" in settings:
            self.security_level = settings["security_level"]
        
        if "auto_update" in settings:
            self.security_updates = settings["auto_update"]
        
        self.logger.info(f"网关 {self.device_id} 安全设置已更新")
        
        # 如果防火墙状态改变，则重新生成访问令牌
        if "firewall_enabled" in settings:
            if self.firewall_enabled:
                self.access_token = generate_random_key(32)
            else:
                self.access_token = None
            
            # 发送安全设置更新事件
            security_event = {
                "event": "security_settings_updated",
                "firewall_enabled": self.firewall_enabled,
                "security_level": self.security_level,
                "auto_update": self.security_updates,
                "update_time": datetime.now().isoformat()
            }
            self._send_telemetry(security_event)
        
        return True