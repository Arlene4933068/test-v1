#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路由器设备模拟器
模拟小米AIoT路由器设备
"""

import random
import time
import uuid
import ipaddress
from datetime import datetime, timedelta

from .simulator_base import DeviceSimulator

class RouterSimulator(DeviceSimulator):
    """路由器设备模拟器类"""
    
    def __init__(self, config_path=None):
        """
        初始化路由器模拟器
        
        Args:
            config_path (str, optional): 配置文件路径. 默认为None.
        """
        super().__init__("router", config_path)
        
        # 路由器特有属性
        self.router_model = self.device_config.get("model", "Xiaomi AIoT Router Pro")
        self.firmware_version = self.device_config.get("firmware_version", "2.5.3")
        
        # 网络参数
        self.wan_ip = self.device_config.get("wan_ip", "192.168.1.1")
        self.lan_ip = self.device_config.get("lan_ip", "192.168.31.1")
        self.subnet_mask = self.device_config.get("subnet_mask", "255.255.255.0")
        self.dns_servers = self.device_config.get("dns_servers", ["8.8.8.8", "114.114.114.114"])
        self.dhcp_enabled = self.device_config.get("dhcp_enabled", True)
        self.dhcp_range = self.device_config.get("dhcp_range", {
            "start": "192.168.31.100",
            "end": "192.168.31.200"
        })
        
        # 无线网络
        self.wifi_networks = self.device_config.get("wifi_networks", [
            {
                "ssid": "Xiaomi_AIoT",
                "band": "2.4GHz",
                "channel": 6,
                "bandwidth": "20MHz",
                "security": "WPA2-PSK",
                "enabled": True,
                "hidden": False,
                "client_limit": 32
            },
            {
                "ssid": "Xiaomi_AIoT_5G",
                "band": "5GHz",
                "channel": 36,
                "bandwidth": "80MHz",
                "security": "WPA2-PSK",
                "enabled": True,
                "hidden": False,
                "client_limit": 32
            }
        ])
        
        # 路由表
        self.routing_table = []
        self._initialize_routing_table()
        
        # 连接的客户端
        self.connected_clients = []
        self._initialize_connected_clients()
        
        # 性能指标
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.uptime = 0
        
        # 网络流量统计
        self.upload_bandwidth = 0.0  # Mbps
        self.download_bandwidth = 0.0  # Mbps
        self.total_upload = 0.0  # MB
        self.total_download = 0.0  # MB
        self.bandwidth_history = []
        
        # 安全状态
        self.firewall_enabled = self.security_settings.get("firewall_enabled", True)
        self.firewall_rules = self.security_settings.get("firewall_rules", [
            {"action": "block", "source": "any", "destination": "lan", "port": 23},  # Block Telnet
            {"action": "block", "source": "wan", "destination": "lan", "port": 22},  # Block SSH from WAN
            {"action": "allow", "source": "lan", "destination": "any", "port": "any"}  # Allow all outbound
        ])
        self.intrusion_detection = self.security_settings.get("intrusion_detection", True)
        self.blocked_ips = []
        
        self.logger.info(f"路由器设备 {self.device_id} 初始化完成, 型号: {self.router_model}")
    
    def _initialize_routing_table(self):
        """初始化路由表"""
        # 添加基础路由
        self.routing_table = [
            {"destination": "0.0.0.0/0", "gateway": self.wan_ip, "interface": "wan0", "metric": 0},
            {"destination": f"{self.lan_ip}/24", "gateway": "0.0.0.0", "interface": "lan0", "metric": 0},
            {"destination": "127.0.0.0/8", "gateway": "0.0.0.0", "interface": "lo", "metric": 0}
        ]
        
        # 添加一些随机路由
        for _ in range(random.randint(2, 5)):
            self.routing_table.append({
                "destination": f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.0/24",
                "gateway": f"192.168.31.{random.randint(2, 99)}",
                "interface": "lan0",
                "metric": random.randint(1, 10)
            })
    
    def _initialize_connected_clients(self):
        """初始化连接的客户端"""
        num_clients = random.randint(5, 15)
        
        for i in range(num_clients):
            # 分配一个IP
            ip = f"192.168.31.{100 + i}"
            
            # 随机生成MAC地址
            mac = ":".join(["{:02x}".format(random.randint(0, 255)) for _ in range(6)])
            
            # 随机设备类型
            device_types = ["smartphone", "laptop", "tablet", "desktop", "iot_device", "tv", "gaming_console"]
            device_type = random.choice(device_types)
            
            # 随机设备名称
            device_names = {
                "smartphone": ["iPhone", "Xiaomi", "Samsung", "Huawei", "OPPO"],
                "laptop": ["MacBook", "ThinkPad", "XPS", "Surface", "MiNotebook"],
                "tablet": ["iPad", "Galaxy Tab", "MiPad", "Surface"],
                "desktop": ["iMac", "HP", "Dell", "Lenovo"],
                "iot_device": ["Smart Bulb", "Smart Speaker", "Smart TV", "Smart Lock"],
                "tv": ["Xiaomi TV", "Samsung TV", "LG TV", "Sony TV"],
                "gaming_console": ["PlayStation", "Xbox", "Switch", "Steam Deck"]
            }
            
            brand = random.choice(device_names.get(device_type, ["Unknown"]))
            model = f"{brand} {random.choice(['A', 'B', 'C', 'X', 'Y', 'Z'])}{random.randint(1, 9)}"
            
            # 随机连接方式
            connection_type = random.choice(["2.4GHz", "5GHz", "ethernet"])
            
            # 连接时间
            connected_time = datetime.now() - timedelta(
                hours=random.randint(0, 48), 
                minutes=random.randint(0, 59)
            )
            
            # 添加客户端
            self.connected_clients.append({
                "ip": ip,
                "mac": mac,
                "hostname": f"{brand.lower()}-{mac.replace(':', '')[-4:]}",
                "device_type": device_type,
                "device_name": model,
                "connection_type": connection_type,
                "connected_since": connected_time.isoformat(),
                "bandwidth": {
                    "upload": random.uniform(0.1, 10.0),  # Mbps
                    "download": random.uniform(0.5, 30.0)  # Mbps
                },
                "data_usage": {
                    "upload": random.uniform(10, 500),  # MB
                    "download": random.uniform(50, 2000)  # MB
                },
                "signal_strength": random.randint(30, 90) if connection_type != "ethernet" else None,
                "last_activity": datetime.now().isoformat()
            })
    
    def generate_telemetry(self):
        """
        生成路由器遥测数据
        
        Returns:
            dict: 路由器遥测数据
        """
        # 更新流量统计
        self._update_traffic_stats()
        
        # 基础遥测数据
        telemetry = {
            "cpu_usage": round(self.cpu_usage, 2),
            "memory_usage": round(self.memory_usage, 2),
            "uptime": self.uptime,
            "connected_clients_count": len(self.connected_clients),
            "bandwidth": {
                "upload": round(self.upload_bandwidth, 2),
                "download": round(self.download_bandwidth, 2)
            },
            "data_usage": {
                "upload_total": round(self.total_upload, 2),
                "download_total": round(self.total_download, 2)
            },
            "wifi_status": self._get_wifi_status(),
            "wan_status": self._get_wan_status(),
            "firmware_version": self.firmware_version,
            "security": {
                "firewall_enabled": self.firewall_enabled,
                "intrusion_detection": self.intrusion_detection,
                "blocked_ip_count": len(self.blocked_ips)
            }
        }
        
        # 在异常或攻击模式下添加额外信息
        if self.behavior_mode in ["anomaly", "attack"]:
            threats = self._generate_threat_data()
            telemetry["security"]["threats"] = threats
        
        return telemetry
    
    def device_behavior(self):
        """路由器设备特定行为"""
        # 更新资源使用率
        self._update_resource_usage()
        
        # 更新正常模式连接客户端
        self._update_connected_clients()
        
        # 更新安全状态
        if self.behavior_mode == "normal":
            # 正常模式偶尔会检测到一些威胁
            if random.random() < 0.1:  # 10%的概率
                self._detect_normal_threats()
                
        elif self.behavior_mode == "anomaly":
            # 异常模式检测到更多威胁
            if random.random() < 0.3:  # 30%的概率
                self._detect_anomaly_threats()
                
        elif self.behavior_mode == "attack":
            # 攻击模式下频繁检测到威胁
            if random.random() < 0.6:  # 60%的概率
                self._detect_attack_threats()
        
        # 模拟固件更新检查
        if random.random() < 0.05:  # 5%的概率检查更新
            self._check_firmware_update()
    
    def _update_resource_usage(self):
        """更新资源使用情况"""
        # 更新CPU和内存使用率
        if self.behavior_mode == "normal":
            self.cpu_usage = min(100, max(0, self.cpu_usage * 0.8 + random.uniform(10, 30)))
            self.memory_usage = min(100, max(0, self.memory_usage * 0.9 + random.uniform(5, 15)))
        elif self.behavior_mode == "anomaly":
            self.cpu_usage = min(100, max(0, self.cpu_usage * 0.8 + random.uniform(30, 60)))
            self.memory_usage = min(100, max(0, self.memory_usage * 0.9 + random.uniform(20, 40)))
        elif self.behavior_mode == "attack":
            self.cpu_usage = min(100, max(0, self.cpu_usage * 0.8 + random.uniform(60, 90)))
            self.memory_usage = min(100, max(0, self.memory_usage * 0.9 + random.uniform(50, 80)))
        
        # 更新运行时间
        self.uptime += random.randint(5, 15)
    
    def _update_traffic_stats(self):
        """更新流量统计"""
        # 获取所有客户端的带宽使用
        upload_total = 0
        download_total = 0
        
        for client in self.connected_clients:
            # 随机更新客户端带宽
            if self.behavior_mode == "normal":
                client["bandwidth"]["upload"] = min(100, max(0.1, client["bandwidth"]["upload"] * 0.9 + random.uniform(-1, 1)))
                client["bandwidth"]["download"] = min(200, max(0.5, client["bandwidth"]["download"] * 0.9 + random.uniform(-2, 2)))
            elif self.behavior_mode == "anomaly":
                client["bandwidth"]["upload"] = min(100, max(0.1, client["bandwidth"]["upload"] * 0.9 + random.uniform(-0.5, 5)))
                client["bandwidth"]["download"] = min(200, max(0.5, client["bandwidth"]["download"] * 0.9 + random.uniform(-1, 10)))
            elif self.behavior_mode == "attack":
                # 攻击模式下某些客户端可能会有异常高的带宽
                if random.random() < 0.2:  # 20%的客户端可能参与攻击
                    client["bandwidth"]["upload"] = min(500, max(0.1, client["bandwidth"]["upload"] * 0.9 + random.uniform(10, 50)))
                    client["bandwidth"]["download"] = min(1000, max(0.5, client["bandwidth"]["download"] * 0.9 + random.uniform(20, 100)))
                else:
                    client["bandwidth"]["upload"] = min(100, max(0.1, client["bandwidth"]["upload"] * 0.9 + random.uniform(-1, 1)))
                    client["bandwidth"]["download"] = min(200, max(0.5, client["bandwidth"]["download"] * 0.9 + random.uniform(-2, 2)))
            
            # 更新数据使用量
            interval = random.uniform(5, 15) / 3600  # 转换为小时
            upload_mb = client["bandwidth"]["upload"] * interval * 1024 / 8  # Mbps转MB
            download_mb = client["bandwidth"]["download"] * interval * 1024 / 8  # Mbps转MB
            
            client["data_usage"]["upload"] += upload_mb
            client["data_usage"]["download"] += download_mb
            
            upload_total += client["bandwidth"]["upload"]
            download_total += client["bandwidth"]["download"]
            
            # 更新最后活动时间
            if random.random() < 0.3:  # 30%的概率更新活动时间
                client["last_activity"] = datetime.now().isoformat()
        
        # 更新总带宽
        self.upload_bandwidth = upload_total
        self.download_bandwidth = download_total
        
        # 更新总流量
        interval = random.uniform(5, 15) / 3600  # 转换为小时
        self.total_upload += upload_total * interval * 1024 / 8  # Mbps转MB
        self.total_download += download_total * interval * 1024 / 8  # Mbps转MB
        
        # 添加到历史记录
        self.bandwidth_history.append({
            "timestamp": datetime.now().isoformat(),
            "upload": round(self.upload_bandwidth, 2),
            "download": round(self.download_bandwidth, 2)
        })
        
        # 只保留最近100个记录
        if len(self.bandwidth_history) > 100:
            self.bandwidth_history = self.bandwidth_history[-100:]
    
    def _update_connected_clients(self):
        """更新连接的客户端"""
        # 随机添加客户端
        if len(self.connected_clients) < 30 and random.random() < 0.1:  # 10%的概率添加客户端
            self._add_random_client()
        
        # 随机移除客户端
        if len(self.connected_clients) > 5 and random.random() < 0.05:  # 5%的概率移除客户端
            self._remove_random_client()
    
    def _add_random_client(self):
        """添加随机客户端"""
        # 生成一个未使用的IP
        used_ips = [client["ip"] for client in self.connected_clients]
        ip = None
        for i in range(100, 200):
            test_ip = f"192.168.31.{i}"
            if test_ip not in used_ips:
                ip = test_ip
                break
        
        if not ip:
            self.logger.warning("无法分配IP地址，DHCP池已满")
            return
        
        # 随机生成MAC地址
        mac = ":".join(["{:02x}".format(random.randint(0, 255)) for _ in range(6)])
        
        # 随机设备类型
        device_types = ["smartphone", "laptop", "tablet", "desktop", "iot_device", "tv", "gaming_console"]
        device_type = random.choice(device_types)
        
        # 随机设备名称
        device_names = {
            "smartphone": ["iPhone", "Xiaomi", "Samsung", "Huawei", "OPPO"],
            "laptop": ["MacBook", "ThinkPad", "XPS", "Surface", "MiNotebook"],
            "tablet": ["iPad", "Galaxy Tab", "MiPad", "Surface"],
            "desktop": ["iMac", "HP", "Dell", "Lenovo"],
            "iot_device": ["Smart Bulb", "Smart Speaker", "Smart TV", "Smart Lock"],
            "tv": ["Xiaomi TV", "Samsung TV", "LG TV", "Sony TV"],
            "gaming_console": ["PlayStation", "Xbox", "Switch", "Steam Deck"]
        }
        
        brand = random.choice(device_names.get(device_type, ["Unknown"]))
        model = f"{brand} {random.choice(['A', 'B', 'C', 'X', 'Y', 'Z'])}{random.randint(1, 9)}"
        
        # 随机连接方式
        connection_type = random.choice(["2.4GHz", "5GHz", "ethernet"])
        
        # 添加客户端
        new_client = {
            "ip": ip,
            "mac": mac,
            "hostname": f"{brand.lower()}-{mac.replace(':', '')[-4:]}",
            "device_type": device_type,
            "device_name": model,
            "connection_type": connection_type,
            "connected_since": datetime.now().isoformat(),
            "bandwidth": {
                "upload": random.uniform(0.1, 5.0),  # Mbps
                "download": random.uniform(0.5, 15.0)  # Mbps
            },
            "data_usage": {
                "upload": 0,  # MB
                "download": 0  # MB
            },
            "signal_strength": random.randint(30, 90) if connection_type != "ethernet" else None,
            "last_activity": datetime.now().isoformat()
        }
        
        self.connected_clients.append(new_client)
        self.logger.info(f"新客户端 {new_client['device_name']} ({ip}) 连接到路由器")
        
        # 如果是在攻击模式下，新连接的设备可能是恶意设备
        if self.behavior_mode == "attack" and random.random() < 0.3:
            new_client["suspicious"] = True
            new_client["behavior"] = random.choice(["port_scanning", "data_exfiltration", "botnet_activity"])
            self.logger.warning(f"检测到可疑客户端 {new_client['device_name']} ({ip})")
    
    def _remove_random_client(self):
        """移除随机客户端"""
        if not self.connected_clients:
            return
            
        client = random.choice(self.connected_clients)
        self.connected_clients.remove(client)
        self.logger.info(f"客户端 {client['device_name']} ({client['ip']}) 断开连接")
    
    def _get_wifi_status(self):
        """获取WiFi状态"""
        wifi_status = []
        
        for network in self.wifi_networks:
            # 计算该网络下的客户端数量
            clients_count = sum(1 for client in self.connected_clients 
                               if client["connection_type"] in ["2.4GHz", "5GHz"] and 
                               ((network["band"] == "2.4GHz" and client["connection_type"] == "2.4GHz") or
                                (network["band"] == "5GHz" and client["connection_type"] == "5GHz")))
            
            # 计算信道利用率
            channel_utilization = min(100, clients_count * random.uniform(2, 5) + random.uniform(5, 15))
            
            # 如果是攻击模式，某些网络可能会被干扰
            interference = 0
            if self.behavior_mode == "attack" and random.random() < 0.3:
                interference = random.uniform(30, 80)
                
            # 添加WiFi状态
            wifi_status.append({
                "ssid": network["ssid"],
                "band": network["band"],
                "channel": network["channel"],
                "bandwidth": network["bandwidth"],
                "security": network["security"],
                "enabled": network["enabled"],
                "clients_count": clients_count,
                "channel_utilization": round(channel_utilization, 2),
                "interference": round(interference, 2),
                "signal_quality": round(max(0, 100 - channel_utilization/2 - interference/2), 2)
            })
        
        return wifi_status
    
    def _get_wan_status(self):
        """获取WAN口状态"""
        # 基础连接状态
        wan_status = {
            "ip": self.wan_ip,
            "connected": True,
            "connection_type": random.choice(["pppoe", "dhcp", "static"]),
            "uptime": self.uptime,
            "dns_servers": self.dns_servers,
            "latency": random.uniform(5, 50)  # ms
        }
        
        # 异常或攻击模式可能有连接问题
        if self.behavior_mode == "anomaly":
            if random.random() < 0.2:
                wan_status["connected"] = random.random() < 0.7  # 30%的概率断开
                wan_status["latency"] = random.uniform(50, 200)  # 延迟增加
                
        elif self.behavior_mode == "attack":
            if random.random() < 0.4:
                wan_status["connected"] = random.random() < 0.5  # 50%的概率断开
                wan_status["latency"] = random.uniform(100, 500)  # 延迟严重增加
                wan_status["packet_loss"] = random.uniform(10, 30)  # 添加丢包率
        
        return wan_status
    
    def _detect_normal_threats(self):
        """检测正常模式下的威胁"""
        # 在正常模式下偶尔检测到的低级威胁
        if random.random() < 0.5:  # 50%的概率检测到威胁
            threat_type = random.choice([
                "port_scan_attempt", "suspicious_connection", "web_attack_attempt"
            ])
            
            source_ip = f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
            
            threat = {
                "type": threat_type,
                "severity": "low",
                "source_ip": source_ip,
                "timestamp": datetime.now().isoformat(),
                "details": f"检测到来自 {source_ip} 的{threat_type}",
                "action_taken": "logged"
            }
            
            self.logger.warning(f"检测到安全威胁: {threat['details']}")
            
            # 决定是否阻止IP
            if random.random() < 0.3 and self.firewall_enabled:  # 30%的概率阻止
                self.blocked_ips.append(source_ip)
                threat["action_taken"] = "blocked"
                self.logger.info(f"已阻止IP: {source_ip}")
    
    def _detect_anomaly_threats(self):
        """检测异常模式下的威胁"""
        # 在异常模式下检测到的中级威胁
        threat_types = [
            "brute_force_attempt", "suspicious_download", "malware_communication", 
            "dns_poisoning_attempt", "abnormal_traffic_pattern"
        ]
        
        # 生成1-3个威胁
        threat_count = random.randint(1, 3)
        
        for _ in range(threat_count):
            threat_type = random.choice(threat_types)
            
            # 随机决定源IP是内部还是外部
            if random.random() < 0.4:  # 40%的概率是内部IP
                if self.connected_clients:
                    source_ip = random.choice(self.connected_clients)["ip"]
                else:
                    source_ip = f"192.168.31.{random.randint(100, 200)}"
            else:  # 外部IP
                source_ip = f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
            
            threat = {
                "type": threat_type,
                "severity": "medium",
                "source_ip": source_ip,
                "timestamp": datetime.now().isoformat(),
                "details": f"检测到来自 {source_ip} 的{threat_type}",
                "action_taken": "logged"
            }
            
            self.logger.warning(f"检测到安全威胁: {threat['details']}")
            
            # 决定是否阻止IP
            if random.random() < 0.6 and self.firewall_enabled:  # 60%的概率阻止
                self.blocked_ips.append(source_ip)
                threat["action_taken"] = "blocked"
                self.logger.info(f"已阻止IP: {source_ip}")
    
    def _detect_attack_threats(self):
        """检测攻击模式下的威胁"""
        # 在攻击模式下检测到的高级威胁
        threat_types = [
            "ddos_attack", "ransomware_activity", "data_exfiltration", 
            "backdoor_detected", "encrypted_tunnel", "botnet_command_control"
        ]
        
        # 生成2-5个威胁
        threat_count = random.randint(2, 5)
        
        for _ in range(threat_count):
            threat_type = random.choice(threat_types)
            
            # 随机决定源IP是内部还是外部
            if random.random() < 0.5:  # 50%的概率是内部IP (内部设备被入侵)
                if self.connected_clients:
                    source_ip = random.choice(self.connected_clients)["ip"]
                else:
                    source_ip = f"192.168.31.{random.randint(100, 200)}"
            else:  # 外部IP
                source_ip = f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
            
            # 目标可能是内部或外部
            if random.random() < 0.7:  # 70%的概率是外部目标
                target_ip = f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
            else:  # 内部目标
                target_ip = f"192.168.31.{random.randint(1, 99)}"
            
            threat = {
                "type": threat_type,
                "severity": "high",
                "source_ip": source_ip,
                "target_ip": target_ip,
                "timestamp": datetime.now().isoformat(),
                "details": f"检测到来自 {source_ip} 到 {target_ip} 的{threat_type}",
                "ports": [random.randint(1, 65535) for _ in range(random.randint(1, 3))],
                "action_taken": "logged"
            }
            
            self.logger.warning(f"检测到严重安全威胁: {threat['details']}")
            
            # 决定是否阻止IP
            if random.random() < 0.9 and self.firewall_enabled:  # 90%的概率阻止
                self.blocked_ips.append(source_ip)
                threat["action_taken"] = "blocked"
                self.logger.info(f"已阻止IP: {source_ip}")
    
    def _generate_threat_data(self):
        """生成威胁数据"""
        threats = []
        
        if self.behavior_mode == "anomaly":
            # 生成1-3个中级威胁
            threat_count = random.randint(1, 3)
            
            for _ in range(threat_count):
                threat_type = random.choice([
                    "brute_force_attempt", "suspicious_download", "malware_communication", 
                    "dns_poisoning_attempt", "abnormal_traffic_pattern"
                ])
                
                source_ip = f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
                
                threats.append({
                    "type": threat_type,
                    "severity": "medium",
                    "source_ip": source_ip,
                    "timestamp": datetime.now().isoformat(),
                    "details": f"检测到来自 {source_ip} 的{threat_type}",
                    "action_taken": random.choice(["logged", "blocked"])
                })
        
        elif self.behavior_mode == "attack":
            # 生成2-5个高级威胁
            threat_count = random.randint(2, 5)
            
            for _ in range(threat_count):
                threat_type = random.choice([
                    "ddos_attack", "ransomware_activity", "data_exfiltration", 
                    "backdoor_detected", "encrypted_tunnel", "botnet_command_control"
                ])
                
                source_ip = f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
                target_ip = f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
                
                threats.append({
                    "type": threat_type,
                    "severity": "high",
                    "source_ip": source_ip,
                    "target_ip": target_ip,
                    "timestamp": datetime.now().isoformat(),
                    "details": f"检测到来自 {source_ip} 到 {target_ip} 的{threat_type}",
                    "ports": [random.randint(1, 65535) for _ in range(random.randint(1, 3))],
                    "action_taken": random.choice(["logged", "blocked", "quarantined"])
                })
        
        return threats
    
    def _check_firmware_update(self):
        """检查固件更新"""
        if not self.security_settings.get("auto_update", True):
            return
            
        # 检查更新
        if random.random() < 0.2:  # 20%的概率有更新
            current_version = self.firmware_version.split(".")
            new_version = f"{current_version[0]}.{current_version[1]}.{int(current_version[2]) + 1}"
            
            self.logger.info(f"检测到新的固件版本 {new_version}")
            
            # 更新固件
            if random.random() < 0.8:  # 80%的概率更新成功
                self.firmware_version = new_version
                self.logger.info(f"固件更新到 {new_version} 成功")
                
                # 发送更新成功的遥测
                update_info = {
                    "event": "firmware_update",
                    "previous_version": self.device_config.get("firmware_version"),
                    "new_version": new_version,
                    "update_time": datetime.now().isoformat(),
                    "status": "success"
                }
                self._send_telemetry(update_info)
            else:
                self.logger.warning(f"固件更新到 {new_version} 失败")
                
                # 发送更新失败的遥测
                update_info = {
                    "event": "firmware_update",
                    "previous_version": self.device_config.get("firmware_version"),
                    "new_version": new_version,
                    "update_time": datetime.now().isoformat(),
                    "status": "failed",
                    "reason": random.choice([
                        "connection_error", "verification_failed", "installation_error", "insufficient_space"
                    ])
                }
                self._send_telemetry(update_info)
    
    def get_bandwidth_history(self):
        """获取带宽历史记录"""
        return self.bandwidth_history
    
    def get_connected_clients(self):
        """获取连接的客户端列表"""
        return self.connected_clients
    
    def get_security_status(self):
        """获取安全状态"""
        return {
            "firewall_enabled": self.firewall_enabled,
            "intrusion_detection": self.intrusion_detection,
            "blocked_ips": self.blocked_ips,
            "security_level": self.security_settings.get("security_level", "medium"),
            "auto_update": self.security_settings.get("auto_update", True),
            "last_update_check": datetime.now().isoformat()
        }
    
    def update_security_settings(self, settings):
        """更新安全设置"""
        if "firewall_enabled" in settings:
            self.firewall_enabled = settings["firewall_enabled"]
        
        if "intrusion_detection" in settings:
            self.intrusion_detection = settings["intrusion_detection"]
        
        if "security_level" in settings:
            self.security_settings["security_level"] = settings["security_level"]
        
        if "auto_update" in settings:
            self.security_settings["auto_update"] = settings["auto_update"]
        
        if "firewall_rules" in settings:
            self.firewall_rules = settings["firewall_rules"]
        
        self.logger.info(f"路由器 {self.device_id} 安全设置已更新")
        
        # 发送安全设置更新事件
        security_event = {
            "event": "security_settings_updated",
            "firewall_enabled": self.firewall_enabled,
            "intrusion_detection": self.intrusion_detection,
            "security_level": self.security_settings.get("security_level"),
            "auto_update": self.security_settings.get("auto_update"),
            "update_time": datetime.now().isoformat()
        }
        self._send_telemetry(security_event)
        
        return True
    
    def block_ip(self, ip_address):
        """阻止指定IP地址"""
        if ip_address not in self.blocked_ips:
            self.blocked_ips.append(ip_address)
            self.logger.info(f"已手动阻止IP: {ip_address}")
            
            # 发送IP阻止事件
            block_event = {
                "event": "ip_blocked",
                "ip_address": ip_address,
                "block_time": datetime.now().isoformat(),
                "block_type": "manual"
            }
            self._send_telemetry(block_event)
            return True
        else:
            self.logger.warning(f"IP {ip_address} 已在阻止列表中")
            return False
    
    def unblock_ip(self, ip_address):
        """解除对指定IP地址的阻止"""
        if ip_address in self.blocked_ips:
            self.blocked_ips.remove(ip_address)
            self.logger.info(f"已解除对IP的阻止: {ip_address}")
            
            # 发送IP解除阻止事件
            unblock_event = {
                "event": "ip_unblocked",
                "ip_address": ip_address,
                "unblock_time": datetime.now().isoformat(),
                "unblock_type": "manual"
            }
            self._send_telemetry(unblock_event)
            return True
        else:
            self.logger.warning(f"IP {ip_address} 不在阻止列表中")
            return False