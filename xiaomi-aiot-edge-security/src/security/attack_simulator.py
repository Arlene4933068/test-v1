#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
攻击模拟器模块
提供多种典型攻击场景的模拟功能
"""

import logging
import random
import time
import threading
import json
import socket
import requests
from typing import Dict, Any, List, Optional, Callable
import scapy.all as scapy
from ..utils.logger import get_logger

class AttackSimulator:
    """攻击模拟器类，用于模拟各种攻击场景"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化攻击模拟器
        
        Args:
            config: 配置参数
        """
        self.logger = get_logger(__name__)
        self.config = config or {}
        
        # 获取攻击配置
        self.attacks_enabled = self.config.get("attacks_enabled", {
            "ddos": True,
            "mitm": True,
            "credential": True,
            "firmware": True,
            "protocol": True,
            "data_exfiltration": True,
            "iot_botnet": True,
            "physical_tampering": True
        })
        
        # 模拟设置
        self.simulation_interval = self.config.get("simulation_interval", 5)  # 秒
        self.intensity = self.config.get("intensity", "medium")  # low, medium, high
        
        # 攻击状态
        self.attack_status = {}
        
        # 回调函数
        self.callbacks = []
        
        # 攻击模拟线程
        self.simulation_threads = {}
        self._stop_event = threading.Event()
    
    def add_callback(self, callback: Callable):
        """
        添加攻击事件的回调函数
        
        Args:
            callback: 回调函数，接受攻击事件数据作为参数
        """
        if callback not in self.callbacks:
            self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable):
        """
        移除回调函数
        
        Args:
            callback: 要移除的回调函数
        """
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def _trigger_callbacks(self, event_data: Dict[str, Any]):
        """
        触发所有回调函数
        
        Args:
            event_data: 攻击事件数据
        """
        for callback in self.callbacks:
            try:
                callback(event_data)
            except Exception as e:
                self.logger.error(f"回调函数执行错误: {str(e)}")
    
    def start_simulation(self):
        """启动自动攻击模拟"""
        if self._stop_event.is_set():
            self._stop_event.clear()
        
        # 启动各类攻击模拟线程
        if self.attacks_enabled.get("ddos", True):
            self.simulation_threads["ddos"] = threading.Thread(target=self._ddos_simulation_loop)
            self.simulation_threads["ddos"].daemon = True
            self.simulation_threads["ddos"].start()
        
        if self.attacks_enabled.get("mitm", True):
            self.simulation_threads["mitm"] = threading.Thread(target=self._mitm_simulation_loop)
            self.simulation_threads["mitm"].daemon = True
            self.simulation_threads["mitm"].start()
        
        if self.attacks_enabled.get("credential", True):
            self.simulation_threads["credential"] = threading.Thread(target=self._credential_simulation_loop)
            self.simulation_threads["credential"].daemon = True
            self.simulation_threads["credential"].start()
        
        if self.attacks_enabled.get("firmware", True):
            self.simulation_threads["firmware"] = threading.Thread(target=self._firmware_simulation_loop)
            self.simulation_threads["firmware"].daemon = True
            self.simulation_threads["firmware"].start()
        
        if self.attacks_enabled.get("protocol", True):
            self.simulation_threads["protocol"] = threading.Thread(target=self._protocol_simulation_loop)
            self.simulation_threads["protocol"].daemon = True
            self.simulation_threads["protocol"].start()
        
        if self.attacks_enabled.get("data_exfiltration", True):
            self.simulation_threads["data_exfiltration"] = threading.Thread(target=self._data_exfiltration_simulation_loop)
            self.simulation_threads["data_exfiltration"].daemon = True
            self.simulation_threads["data_exfiltration"].start()
        
        if self.attacks_enabled.get("iot_botnet", True):
            self.simulation_threads["iot_botnet"] = threading.Thread(target=self._iot_botnet_simulation_loop)
            self.simulation_threads["iot_botnet"].daemon = True
            self.simulation_threads["iot_botnet"].start()
        
        if self.attacks_enabled.get("physical_tampering", True):
            self.simulation_threads["physical_tampering"] = threading.Thread(target=self._physical_tampering_simulation_loop)
            self.simulation_threads["physical_tampering"].daemon = True
            self.simulation_threads["physical_tampering"].start()
        
        self.logger.info("攻击模拟已启动")
    
    def stop_simulation(self):
        """停止自动攻击模拟"""
        self._stop_event.set()
        
        # 等待所有线程结束
        for name, thread in self.simulation_threads.items():
            if thread.is_alive():
                thread.join(timeout=2.0)
        
        self.simulation_threads = {}
        self.logger.info("攻击模拟已停止")
    
    def simulate_ddos_attack(self, target_device_id: str = None, intensity: str = None):
        """
        模拟DDoS攻击
        
        Args:
            target_device_id: 目标设备ID
            intensity: 攻击强度 (low, medium, high)
        """
        intensity = intensity or self.intensity
        target_device_id = target_device_id or f"device_{random.randint(1, 100)}"
        
        # 根据强度设置参数
        if intensity == "low":
            packet_count = random.randint(100, 500)
            duration = random.randint(5, 10)
        elif intensity == "medium":
            packet_count = random.randint(500, 2000)
            duration = random.randint(10, 20)
        else:  # high
            packet_count = random.randint(2000, 10000)
            duration = random.randint(20, 60)
        
        # 随机选择DDoS类型
        attack_type = random.choice(["syn_flood", "udp_flood", "icmp_flood", "http_flood"])
        
        # 生成随机源IP
        source_ips = []
        for _ in range(min(10, packet_count // 50)):
            source_ips.append(f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}")
        
        # 创建攻击事件数据
        attack_data = {
            "type": "ddos",
            "subtype": attack_type,
            "target_id": target_device_id,
            "source_ips": source_ips,
            "packet_count": packet_count,
            "duration": duration,
            "timestamp": time.time(),
            "intensity": intensity
        }
        
        # 更新攻击状态
        self.attack_status["ddos"] = {
            "active": True,
            "target_id": target_device_id,
            "start_time": time.time(),
            "duration": duration,
            "details": attack_data
        }
        
        self.logger.info(f"模拟DDoS攻击: {attack_type} 针对设备 {target_device_id}, 强度: {intensity}")
        
        # 触发回调
        self._trigger_callbacks(attack_data)
        
        # 设置定时器来"结束"攻击
        def end_attack():
            if "ddos" in self.attack_status:
                self.attack_status["ddos"]["active"] = False
                self.logger.info(f"DDoS攻击结束: {attack_type} 针对设备 {target_device_id}")
        
        threading.Timer(duration, end_attack).start()
        
        return attack_data
    
    def _ddos_simulation_loop(self):
        """DDoS攻击模拟循环"""
        while not self._stop_event.is_set():
            try:
                # 随机决定是否发起攻击
                if random.random() < 0.2:  # 20%概率
                    # 如果没有活跃的DDoS攻击，则模拟一次
                    if "ddos" not in self.attack_status or not self.attack_status["ddos"].get("active", False):
                        self.simulate_ddos_attack()
                
                # 等待下一个循环
                wait_time = self.simulation_interval * random.uniform(0.8, 1.2)
                self._stop_event.wait(wait_time)
            except Exception as e:
                self.logger.error(f"DDoS模拟循环错误: {str(e)}")
                self._stop_event.wait(5.0)
    
    def simulate_mitm_attack(self, target_device_id: str = None, gateway_id: str = None):
        """
        模拟中间人攻击
        
        Args:
            target_device_id: 目标设备ID
            gateway_id: 网关ID
        """
        target_device_id = target_device_id or f"device_{random.randint(1, 100)}"
        gateway_id = gateway_id or f"gateway_{random.randint(1, 10)}"
        
        # 随机选择中间人攻击类型
        attack_type = random.choice(["arp_spoofing", "dns_spoofing", "ssl_stripping", "proxy_hijacking"])
        
        # 生成攻击者IP
        attacker_ip = f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"
        
        # 创建攻击事件数据
        attack_data = {
            "type": "mitm",
            "subtype": attack_type,
            "target_id": target_device_id,
            "gateway_id": gateway_id,
            "attacker_ip": attacker_ip,
            "intercepted_traffic": random.randint(1, 100),  # 模拟拦截的流量(MB)
            "timestamp": time.time(),
            "intensity": self.intensity
        }
        
        # 更新攻击状态
        self.attack_status["mitm"] = {
            "active": True,
            "target_id": target_device_id,
            "gateway_id": gateway_id,
            "start_time": time.time(),
            "details": attack_data
        }
        
        self.logger.info(f"模拟中间人攻击: {attack_type} 针对设备 {target_device_id}, 通过网关 {gateway_id}")
        
        # 触发回调
        self._trigger_callbacks(attack_data)
        
        # 随机持续时间
        duration = random.randint(30, 120)  # 30s-2min
        
        # 设置定时器来"结束"攻击
        def end_attack():
            if "mitm" in self.attack_status:
                self.attack_status["mitm"]["active"] = False
                self.logger.info(f"中间人攻击结束: {attack_type} 针对设备 {target_device_id}")
        
        threading.Timer(duration, end_attack).start()
        
        return attack_data
    
    def _mitm_simulation_loop(self):
        """中间人攻击模拟循环"""
        while not self._stop_event.is_set():
            try:
                # 随机决定是否发起攻击
                if random.random() < 0.15:  # 15%概率
                    # 如果没有活跃的中间人攻击，则模拟一次
                    if "mitm" not in self.attack_status or not self.attack_status["mitm"].get("active", False):
                        self.simulate_mitm_attack()
                    # 如果没有活跃的中间人攻击，则模拟一次
                    if "mitm" not in self.attack_status or not self.attack_status["mitm"].get("active", False):
                        self.simulate_mitm_attack()
                
                # 等待下一个循环
                wait_time = self.simulation_interval * random.uniform(0.8, 1.2) * 5  # 中间人攻击间隔更长
                self._stop_event.wait(wait_time)
            except Exception as e:
                self.logger.error(f"中间人攻击模拟循环错误: {str(e)}")
                self._stop_event.wait(5.0)
    
    def simulate_credential_attack(self, target_device_id: str = None, credentials_type: str = None):
        """
        模拟凭证攻击
        
        Args:
            target_device_id: 目标设备ID
            credentials_type: 凭证类型
        """
        target_device_id = target_device_id or f"device_{random.randint(1, 100)}"
        credentials_type = credentials_type or random.choice(["password", "token", "certificate", "api_key"])
        
        # 随机选择凭证攻击类型
        attack_type = random.choice(["brute_force", "dictionary", "credential_stuffing", "phishing"])
        
        # 攻击参数
        attempts = random.randint(10, 5000)
        success = random.random() < 0.1  # 10%概率成功
        
        # 创建攻击事件数据
        attack_data = {
            "type": "credential",
            "subtype": attack_type,
            "target_id": target_device_id,
            "credentials_type": credentials_type,
            "attempts": attempts,
            "success": success,
            "attacker_ip": f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}",
            "timestamp": time.time(),
            "intensity": self.intensity
        }
        
        # 更新攻击状态
        self.attack_status["credential"] = {
            "active": True,
            "target_id": target_device_id,
            "start_time": time.time(),
            "details": attack_data
        }
        
        self.logger.info(f"模拟凭证攻击: {attack_type} ({credentials_type}) 针对设备 {target_device_id}, 成功: {success}")
        
        # 触发回调
        self._trigger_callbacks(attack_data)
        
        # 随机持续时间
        duration = random.randint(10, 60)  # 10s-1min
        
        # 设置定时器来"结束"攻击
        def end_attack():
            if "credential" in self.attack_status:
                self.attack_status["credential"]["active"] = False
                self.logger.info(f"凭证攻击结束: {attack_type} 针对设备 {target_device_id}")
        
        threading.Timer(duration, end_attack).start()
        
        return attack_data
    
    def _credential_simulation_loop(self):
        """凭证攻击模拟循环"""
        while not self._stop_event.is_set():
            try:
                # 随机决定是否发起攻击
                if random.random() < 0.1:  # 10%概率
                    # 如果没有活跃的凭证攻击，则模拟一次
                    if "credential" not in self.attack_status or not self.attack_status["credential"].get("active", False):
                        self.simulate_credential_attack()
                
                # 等待下一个循环
                wait_time = self.simulation_interval * random.uniform(0.8, 1.2) * 3  # 凭证攻击间隔适中
                self._stop_event.wait(wait_time)
            except Exception as e:
                self.logger.error(f"凭证攻击模拟循环错误: {str(e)}")
                self._stop_event.wait(5.0)
    
    def simulate_firmware_attack(self, target_device_id: str = None, firmware_type: str = None):
        """
        模拟固件攻击
        
        Args:
            target_device_id: 目标设备ID
            firmware_type: 固件类型
        """
        target_device_id = target_device_id or f"device_{random.randint(1, 100)}"
        firmware_type = firmware_type or random.choice(["gateway", "router", "speaker", "camera"])
        
        # 随机选择固件攻击类型
        attack_type = random.choice(["backdoor", "trojan", "corrupt_update", "rollback"])
        
        # 创建攻击事件数据
        attack_data = {
            "type": "firmware",
            "subtype": attack_type,
            "target_id": target_device_id,
            "firmware_type": firmware_type,
            "fake_version": f"{random.randint(1, 10)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
            "original_version": f"{random.randint(1, 10)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
            "timestamp": time.time(),
            "intensity": self.intensity
        }
        
        # 更新攻击状态
        self.attack_status["firmware"] = {
            "active": True,
            "target_id": target_device_id,
            "start_time": time.time(),
            "details": attack_data
        }
        
        self.logger.info(f"模拟固件攻击: {attack_type} 针对设备 {target_device_id} ({firmware_type})")
        
        # 触发回调
        self._trigger_callbacks(attack_data)
        
        # 随机持续时间
        duration = random.randint(60, 300)  # 1-5分钟
        
        # 设置定时器来"结束"攻击
        def end_attack():
            if "firmware" in self.attack_status:
                self.attack_status["firmware"]["active"] = False
                self.logger.info(f"固件攻击结束: {attack_type} 针对设备 {target_device_id}")
        
        threading.Timer(duration, end_attack).start()
        
        return attack_data
    
    def _firmware_simulation_loop(self):
        """固件攻击模拟循环"""
        while not self._stop_event.is_set():
            try:
                # 随机决定是否发起攻击
                if random.random() < 0.05:  # 5%概率
                    # 如果没有活跃的固件攻击，则模拟一次
                    if "firmware" not in self.attack_status or not self.attack_status["firmware"].get("active", False):
                        self.simulate_firmware_attack()
                
                # 等待下一个循环
                wait_time = self.simulation_interval * random.uniform(0.8, 1.2) * 10  # 固件攻击间隔较长
                self._stop_event.wait(wait_time)
            except Exception as e:
                self.logger.error(f"固件攻击模拟循环错误: {str(e)}")
                self._stop_event.wait(5.0)
    
    def simulate_protocol_attack(self, target_device_id: str = None, protocol: str = None):
        """
        模拟协议漏洞攻击
        
        Args:
            target_device_id: 目标设备ID
            protocol: 协议类型
        """
        target_device_id = target_device_id or f"device_{random.randint(1, 100)}"
        protocol = protocol or random.choice(["mqtt", "coap", "zigbee", "bluetooth", "z-wave"])
        
        # 随机选择协议攻击类型
        attack_type = random.choice(["replay", "fuzzing", "overflow", "injection"])
        
        # 创建攻击事件数据
        attack_data = {
            "type": "protocol",
            "subtype": attack_type,
            "target_id": target_device_id,
            "protocol": protocol,
            "payload_size": random.randint(100, 10000),
            "timestamp": time.time(),
            "intensity": self.intensity
        }
        
        # 更新攻击状态
        self.attack_status["protocol"] = {
            "active": True,
            "target_id": target_device_id,
            "start_time": time.time(),
            "details": attack_data
        }
        
        self.logger.info(f"模拟协议攻击: {attack_type} 针对设备 {target_device_id} ({protocol}协议)")
        
        # 触发回调
        self._trigger_callbacks(attack_data)
        
        # 随机持续时间
        duration = random.randint(20, 120)  # 20s-2min
        
        # 设置定时器来"结束"攻击
        def end_attack():
            if "protocol" in self.attack_status:
                self.attack_status["protocol"]["active"] = False
                self.logger.info(f"协议攻击结束: {attack_type} 针对设备 {target_device_id}")
        
        threading.Timer(duration, end_attack).start()
        
        return attack_data
    
    def _protocol_simulation_loop(self):
        """协议攻击模拟循环"""
        while not self._stop_event.is_set():
            try:
                # 随机决定是否发起攻击
                if random.random() < 0.08:  # 8%概率
                    # 如果没有活跃的协议攻击，则模拟一次
                    if "protocol" not in self.attack_status or not self.attack_status["protocol"].get("active", False):
                        self.simulate_protocol_attack()
                
                # 等待下一个循环
                wait_time = self.simulation_interval * random.uniform(0.8, 1.2) * 6  # 协议攻击间隔较长
                self._stop_event.wait(wait_time)
            except Exception as e:
                self.logger.error(f"协议攻击模拟循环错误: {str(e)}")
                self._stop_event.wait(5.0)
    
    def simulate_data_exfiltration(self, target_device_id: str = None, data_type: str = None):
        """
        模拟数据窃取/泄露攻击
        
        Args:
            target_device_id: 目标设备ID
            data_type: 数据类型
        """
        target_device_id = target_device_id or f"device_{random.randint(1, 100)}"
        data_type = data_type or random.choice(["user_data", "credentials", "metadata", "sensor_readings", "audio", "video"])
        
        # 随机选择数据窃取类型
        attack_type = random.choice(["covert_channel", "steganography", "direct_transfer", "dns_tunneling"])
        
        # 创建攻击事件数据
        data_size = random.randint(1, 1000)  # KB
        attack_data = {
            "type": "data_exfiltration",
            "subtype": attack_type,
            "target_id": target_device_id,
            "data_type": data_type,
            "data_size": data_size,
            "destination_ip": f"{random.randint(1, 220)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}",
            "timestamp": time.time(),
            "intensity": self.intensity
        }
        
        # 更新攻击状态
        self.attack_status["data_exfiltration"] = {
            "active": True,
            "target_id": target_device_id,
            "start_time": time.time(),
            "details": attack_data
        }
        
        self.logger.info(f"模拟数据窃取攻击: {attack_type} 针对设备 {target_device_id}, 数据类型: {data_type}, 大小: {data_size}KB")
        
        # 触发回调
        self._trigger_callbacks(attack_data)
        
        # 随机持续时间
        duration = random.randint(30, 180)  # 30s-3min
        
        # 设置定时器来"结束"攻击
        def end_attack():
            if "data_exfiltration" in self.attack_status:
                self.attack_status["data_exfiltration"]["active"] = False
                self.logger.info(f"数据窃取攻击结束: {attack_type} 针对设备 {target_device_id}")
        
        threading.Timer(duration, end_attack).start()
        
        return attack_data
    
    def _data_exfiltration_simulation_loop(self):
        """数据窃取攻击模拟循环"""
        while not self._stop_event.is_set():
            try:
                # 随机决定是否发起攻击
                if random.random() < 0.07:  # 7%概率
                    # 如果没有活跃的数据窃取攻击，则模拟一次
                    if "data_exfiltration" not in self.attack_status or not self.attack_status["data_exfiltration"].get("active", False):
                        self.simulate_data_exfiltration()
                
                # 等待下一个循环
                wait_time = self.simulation_interval * random.uniform(0.8, 1.2) * 7  # 数据窃取攻击间隔较长
                self._stop_event.wait(wait_time)
            except Exception as e:
                self.logger.error(f"数据窃取攻击模拟循环错误: {str(e)}")
                self._stop_event.wait(5.0)
    
    def simulate_iot_botnet(self, target_devices: List[str] = None, botnet_type: str = None):
        """
        模拟IoT僵尸网络攻击
        
        Args:
            target_devices: 目标设备ID列表
            botnet_type: 僵尸网络类型
        """
        if not target_devices:
            # 随机生成被感染设备列表
            infected_count = random.randint(2, 10)
            target_devices = [f"device_{random.randint(1, 100)}" for _ in range(infected_count)]
        
        botnet_type = botnet_type or random.choice(["mirai", "bashlight", "torii", "emotet", "gafgyt"])
        
        # 随机选择僵尸网络攻击目标类型
        attack_target_type = random.choice(["ddos", "crypto_mining", "spam", "proxy", "data_theft"])
        
        # 创建攻击事件数据
        command_server = f"{random.randint(1, 220)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"
        attack_data = {
            "type": "iot_botnet",
            "subtype": botnet_type,
            "infected_devices": target_devices,
            "device_count": len(target_devices),
            "command_server": command_server,
            "attack_target_type": attack_target_type,
            "bandwidth_usage": random.randint(10, 100),  # Mbps
            "timestamp": time.time(),
            "intensity": self.intensity
        }
        
        # 更新攻击状态
        self.attack_status["iot_botnet"] = {
            "active": True,
            "target_devices": target_devices,
            "start_time": time.time(),
            "details": attack_data
        }
        
        self.logger.info(f"模拟IoT僵尸网络攻击: {botnet_type} 感染 {len(target_devices)} 个设备, 类型: {attack_target_type}")
        
        # 触发回调
        self._trigger_callbacks(attack_data)
        
        # 随机持续时间
        duration = random.randint(300, 1800)  # 5-30分钟
        
        # 设置定时器来"结束"攻击
        def end_attack():
            if "iot_botnet" in self.attack_status:
                self.attack_status["iot_botnet"]["active"] = False
                self.logger.info(f"IoT僵尸网络攻击结束: {botnet_type}")
        
        threading.Timer(duration, end_attack).start()
        
        return attack_data
    
    def _iot_botnet_simulation_loop(self):
        """IoT僵尸网络攻击模拟循环"""
        while not self._stop_event.is_set():
            try:
                # 随机决定是否发起攻击
                if random.random() < 0.03:  # 3%概率
                    # 如果没有活跃的僵尸网络攻击，则模拟一次
                    if "iot_botnet" not in self.attack_status or not self.attack_status["iot_botnet"].get("active", False):
                        self.simulate_iot_botnet()
                
                # 等待下一个循环
                wait_time = self.simulation_interval * random.uniform(0.8, 1.2) * 15  # 僵尸网络攻击间隔很长
                self._stop_event.wait(wait_time)
            except Exception as e:
                self.logger.error(f"僵尸网络攻击模拟循环错误: {str(e)}")
                self._stop_event.wait(5.0)
    
    def simulate_physical_tampering(self, target_device_id: str = None, tampering_type: str = None):
        """
        模拟物理篡改攻击
        
        Args:
            target_device_id: 目标设备ID
            tampering_type: 物理篡改类型
        """
        target_device_id = target_device_id or f"device_{random.randint(1, 100)}"
        tampering_type = tampering_type or random.choice(["reset", "sensor_manipulation", "port_access", "hardware_trojan", "side_channel"])
        
        # 创建攻击事件数据
        attack_data = {
            "type": "physical_tampering",
            "subtype": tampering_type,
            "target_id": target_device_id,
            "location": random.choice(["front_panel", "side_port", "internal_component", "power_supply", "network_interface"]),
            "detection_confidence": random.randint(60, 95),
            "timestamp": time.time(),
            "intensity": self.intensity
        }
        
        # 更新攻击状态
        self.attack_status["physical_tampering"] = {
            "active": True,
            "target_id": target_device_id,
            "start_time": time.time(),
            "details": attack_data
        }
        
        self.logger.info(f"模拟物理篡改攻击: {tampering_type} 针对设备 {target_device_id}")
        
        # 触发回调
        self._trigger_callbacks(attack_data)
        
        # 随机持续时间
        duration = random.randint(60, 300)  # 1-5分钟
        
        # 设置定时器来"结束"攻击
        def end_attack():
            if "physical_tampering" in self.attack_status:
                self.attack_status["physical_tampering"]["active"] = False
                self.logger.info(f"物理篡改攻击结束: {tampering_type} 针对设备 {target_device_id}")
        
        threading.Timer(duration, end_attack).start()
        
        return attack_data
    
    def _physical_tampering_simulation_loop(self):
        """物理篡改攻击模拟循环"""
        while not self._stop_event.is_set():
            try:
                # 随机决定是否发起攻击
                if random.random() < 0.02:  # 2%概率
                    # 如果没有活跃的物理篡改攻击，则模拟一次
                    if "physical_tampering" not in self.attack_status or not self.attack_status["physical_tampering"].get("active", False):
                        self.simulate_physical_tampering()
                
                # 等待下一个循环
                wait_time = self.simulation_interval * random.uniform(0.8, 1.2) * 20  # 物理篡改攻击间隔很长
                self._stop_event.wait(wait_time)
            except Exception as e:
                self.logger.error(f"物理篡改攻击模拟循环错误: {str(e)}")
                self._stop_event.wait(5.0)
    
    def get_attack_status(self) -> Dict[str, Any]:
        """
        获取当前攻击状态
        
        Returns:
            Dict[str, Any]: 当前攻击状态
        """
        # 清理已结束的攻击
        current_time = time.time()
        for attack_type in list(self.attack_status.keys()):
            if not self.attack_status[attack_type].get("active", False):
                # 保留最后10个已结束的攻击记录
                if "history" not in self.attack_status:
                    self.attack_status["history"] = []
                
                # 添加到历史记录
                self.attack_status["history"].append({
                    "type": attack_type,
                    "details": self.attack_status[attack_type]["details"],
                    "start_time": self.attack_status[attack_type]["start_time"],
                    "end_time": current_time
                })
                
                # 只保留最后10个记录
                if len(self.attack_status["history"]) > 10:
                    self.attack_status["history"] = self.attack_status["history"][-10:]
                
                # 从活跃状态中删除
                if attack_type != "history":
                    del self.attack_status[attack_type]
        
        return self.attack_status