#!/usr/bin/env python3
# 直接启动小米AIoT边缘安全防护研究平台

import os
import sys
import time
import logging
import yaml
import platform
import shutil
import traceback
import importlib.util
import random
import json
import threading
import queue
from typing import Dict, List, Any

def setup_logging():
    """设置日志系统"""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, f"platform_{time.strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("DirectStart")

def create_config():
    """创建默认配置文件"""
    logger = logging.getLogger("Config")
    config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    config_file = os.path.join(config_dir, "platform.yaml")
    if not os.path.exists(config_file):
        default_config = {
            "platform": {
                "edgex": {
                    "host": "localhost",
                    "port": 59880,
                    "metadata_port": 59881,
                    "core_command_port": 59882,
                    "api_version": "v2",
                    "device_service_name": "xiaomi-device-service"
                },
                "thingsboard": {
                    "host": "localhost",
                    "port": 8080,
                    "username": "yy3205543808@gmail.com",
                    "password": "wlsxcdh52jy.L"
                }
            },
            "security": {
                "scan_interval": 10,
                "detection_threshold": 0.7,
                "enable_attack_simulation": True,
                "simulation_probability": 0.1
            },
            "analytics": {
                "output_dir": "output",
                "report_interval": 3600
            },
            "edge_protection": {
                "protection_level": "medium",
                "enable_firewall": True,
                "enable_ids": True,
                "enable_data_protection": True,
                "device_whitelist": [
                    "xiaomi_gateway_01",
                    "xiaomi_router_01",
                    "xiaomi_speaker_01",
                    "xiaomi_camera_01"
                ]
            }
        }
        
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        logger.info(f"已创建默认配置文件: {config_file}")
    
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logger.error(f"加载配置文件失败: {str(e)}")
        return None

class EdgeSecurityProtector:
    """边缘计算安全防护器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化边缘计算安全防护器"""
        self.logger = logging.getLogger("EdgeProtector")
        self.config = config
        
        # 基础配置
        self.protection_level = config.get('protection_level', 'medium')  # low, medium, high
        self.enable_firewall = config.get('enable_firewall', True)
        self.enable_ids = config.get('enable_ids', True)
        self.enable_data_protection = config.get('enable_data_protection', True)
        
        # 状态变量
        self.running = False
        self.protection_thread = None
        
        # 保护事件队列
        self.event_queue = queue.Queue()
        
        # 设备白名单
        self.device_whitelist = set(config.get('device_whitelist', []))
        
        # 被阻止的IP集合
        self.blocked_ips = set()
        
        # 注册回调函数
        self.on_threat_detected = None
        self.on_protection_activated = None
    
    def start(self):
        """启动防护"""
        if self.running:
            return
        
        self.running = True
        self.protection_thread = threading.Thread(target=self._protection_loop)
        self.protection_thread.daemon = True
        self.protection_thread.start()
        
        self.logger.info(f"边缘计算安全防护已启动，防护级别: {self.protection_level}")
    
    def stop(self):
        """停止防护"""
        if not self.running:
            return
        
        self.logger.info("正在停止边缘计算安全防护...")
        self.running = False
        
        if self.protection_thread and self.protection_thread.is_alive():
            try:
                self.protection_thread.join(timeout=3.0)
            except Exception as e:
                self.logger.warning(f"等待防护线程结束时出现异常: {str(e)}")
        
        self.logger.info("边缘计算安全防护已停止")
    
    def register_protection_callback(self, callback):
        """注册保护激活回调函数"""
        self.on_protection_activated = callback
    
    def _protection_loop(self):
        """防护主循环"""
        while self.running:
            try:
                # 检查网络流量异常
                self._monitor_network_traffic()
                
                # 验证设备完整性
                self._verify_device_integrity()
                
                # 等待一段时间
                time.sleep(2.0)
            except Exception as e:
                self.logger.error(f"防护循环执行异常: {str(e)}")
                time.sleep(5.0)
    
    def _monitor_network_traffic(self):
        """模拟监控网络流量"""
        if random.random() < 0.05:  # 5%的概率检测到异常
            anomaly_types = ['port_scan', 'syn_flood', 'dns_tunneling', 'unusual_protocol']
            anomaly = {
                'anomaly_type': random.choice(anomaly_types),
                'source_ip': f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}",
                'destination_ip': f"10.0.{random.randint(1, 254)}.{random.randint(1, 254)}",
                'confidence': round(random.uniform(0.5, 0.95), 2)
            }
            
            self.logger.warning(f"检测到网络异常: {anomaly['anomaly_type']} 从 {anomaly['source_ip']} 到 {anomaly['destination_ip']} (置信度: {anomaly['confidence']})")
            if self.on_protection_activated:
                self.on_protection_activated({
                    'action': 'network_anomaly_detected',
                    'details': anomaly
                })
    
    def _verify_device_integrity(self):
        """模拟验证设备完整性"""
        if random.random() < 0.03:  # 3%的概率检测到篡改
            tampering_types = ['firmware_modified', 'configuration_changed', 'unauthorized_access']
            device_event = {
                'device_id': f"xiaomi_device_{random.randint(1, 10)}",
                'tampering_type': random.choice(tampering_types),
                'severity': random.choice(['low', 'medium', 'high'])
            }
            
            self.logger.warning(f"设备安全警告: {device_event['tampering_type']} 检测到于设备 {device_event['device_id']} (严重度: {device_event['severity']})")
            if self.on_protection_activated:
                self.on_protection_activated({
                    'action': 'device_tampering_detected',
                    'details': device_event
                })

class ThingsboardConnector:
    """ThingsBoard 连接器"""
    
    def __init__(self, config):
        """初始化ThingsBoard连接器"""
        self.logger = logging.getLogger("ThingsBoard")
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 8080)
        self.username = config.get('username', '')
        self.password = config.get('password', '')
        self.jwt_token = None
    
    def connect(self):
        """连接到ThingsBoard"""
        try:
            self.logger.info(f"尝试连接到ThingsBoard: http://{self.host}:{self.port}/api/auth/login")
            
            # 模拟连接成功
            self.jwt_token = "mock-jwt-token"
            self.logger.info("成功连接到ThingsBoard Edge实例")
            return True
        except Exception as e:
            self.logger.error(f"连接到ThingsBoard时出错: {str(e)}")
            return False
    
    def create_device(self, device_name, device_type):
        """创建设备"""
        try:
            self.logger.info(f"成功创建设备: {device_name}")
            return f"mock-token-mock-{device_name}-{device_type}"
        except Exception as e:
            self.logger.error(f"创建设备时出错: {str(e)}")
            return None
    
    def send_telemetry(self, access_token, telemetry_data):
        """发送设备遥测数据"""
        try:
            self.logger.info(f"模拟发送遥测数据，访问令牌: {access_token}")
            
            # 保存到本地备份
            backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "telemetry_backup")
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            token_short = access_token[-10:] if len(access_token) > 10 else access_token
            backup_file = os.path.join(backup_dir, f"telemetry_{token_short}_{timestamp}.json")
            
            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump({
                    "token": access_token, 
                    "timestamp": time.time(), 
                    "data": telemetry_data
                }, f, indent=2)
            
            return True
        except Exception as e:
            self.logger.error(f"发送遥测数据时出错: {str(e)}")
            return False

class DeviceSimulator:
    """设备模拟器"""
    
    def __init__(self, config):
        """初始化设备模拟器"""
        self.logger = logging.getLogger("DeviceSimulator")
        self.config = config
        self.devices = {}
        self.running = False
        self.simulator_thread = None
    
    def start(self, tb_connector):
        """启动设备模拟器"""
        if self.running:
            return
        
        try:
            # 创建设备
            device_types = [
                ("xiaomi_gateway_01", "gateway"),
                ("xiaomi_router_01", "router"),
                ("xiaomi_speaker_01", "smart_speaker"),
                ("xiaomi_camera_01", "camera")
            ]
            
            for device_name, device_type in device_types:
                # 创建设备
                access_token = tb_connector.create_device(device_name, device_type)
                
                if access_token:
                    self.devices[device_name] = {
                        "name": device_name,
                        "type": device_type,
                        "token": access_token,
                        "status": "active"
                    }
                    self.logger.info(f"成功创建{device_type}设备: {device_name}")
                else:
                    self.logger.error(f"创建设备失败: {device_name}")
            
            # 启动模拟线程
            self.running = True
            self.simulator_thread = threading.Thread(target=self._simulation_loop, args=(tb_connector,))
            self.simulator_thread.daemon = True
            self.simulator_thread.start()
            
            self.logger.info(f"成功创建 {len(self.devices)} 个设备")
        except Exception as e:
            self.logger.error(f"启动设备模拟器时出错: {str(e)}")
    
    def stop(self):
        """停止设备模拟器"""
        if not self.running:
            return
        
        self.running = False
        
        if self.simulator_thread and self.simulator_thread.is_alive():
            try:
                self.simulator_thread.join(timeout=5.0)
            except Exception as e:
                self.logger.warning(f"等待模拟线程结束时出现异常: {str(e)}")
        
        # 停止所有设备
        for device_name in self.devices:
            self.logger.info(f"设备{device_name}已停止")
        
        self.logger.info(f"已停止 {len(self.devices)}/{len(self.devices)} 个设备")
    
    def _simulation_loop(self, tb_connector):
        """设备模拟循环"""
        while self.running:
            try:
                # 为每个设备生成模拟数据
                for device_name, device in self.devices.items():
                    try:
                        # 生成随机遥测数据
                        telemetry = self._generate_telemetry(device["type"])
                        
                        # 发送数据到ThingsBoard
                        tb_connector.send_telemetry(device["token"], telemetry)
                    except Exception as e:
                        self.logger.error(f"为设备 {device_name} 生成数据时出错: {str(e)}")
                
                # 随机设备事件
                self._generate_random_events()
                
                # 等待
                time.sleep(random.uniform(5.0, 8.0))
            except Exception as e:
                self.logger.error(f"模拟循环执行异常: {str(e)}")
                time.sleep(5.0)
    
    def _generate_telemetry(self, device_type):
        """为不同设备类型生成遥测数据"""
        if device_type == "gateway":
            return {
                "temperature": round(random.uniform(25, 45), 1),
                "humidity": round(random.uniform(30, 70), 1),
                "connected_devices": random.randint(3, 15),
                "uptime": random.randint(3600, 864000),
                "cpu_usage": round(random.uniform(10, 80), 1),
                "memory_usage": round(random.uniform(20, 70), 1)
            }
        elif device_type == "router":
            return {
                "temperature": round(random.uniform(30, 55), 1),
                "bandwidth_usage": round(random.uniform(1, 100), 2),
                "connected_clients": random.randint(1, 20),
                "tx_bytes": random.randint(1000000, 100000000),
                "rx_bytes": random.randint(1000000, 100000000),
                "signal_strength": random.randint(-90, -30)
            }
        elif device_type == "smart_speaker":
            return {
                "volume": random.randint(0, 100),
                "playing_status": random.choice(["playing", "paused", "stopped"]),
                "active_timers": random.randint(0, 3),
                "temperature": round(random.uniform(25, 40), 1),
                "last_command": random.choice([
                    "设置闹钟", "播放音乐", "查询天气", 
                    "调整音量", "关闭灯光", "查询时间"
                ])
            }
        elif device_type == "camera":
            return {
                "resolution": random.choice(["720p", "1080p", "4K"]),
                "recording_status": random.choice(["recording", "standby"]),
                "motion_detected": random.choice([True, False]),
                "storage_usage": round(random.uniform(10, 95), 1),
                "battery_level": random.randint(10, 100),
                "night_mode": random.choice([True, False])
            }
        else:
            return {
                "status": "online",
                "last_seen": int(time.time())
            }
    
    def _generate_random_events(self):
        """生成随机设备事件"""
        try:
            # 随机智能音箱语音命令
            if "xiaomi_speaker_01" in self.devices and random.random() < 0.1:
                command = random.choice(["设置闹钟", "播放音乐", "调整音量", "天气查询", "新闻播报"])
                self.logger.info(f"小爱音箱 xiaomi_speaker_01 接收语音命令: {command}")
            
            # 随机摄像头动作检测
            if "xiaomi_camera_01" in self.devices and random.random() < 0.08:
                motion_id = f"MOTION_{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))}_{int(time.time())}"
                self.logger.info(f"摄像头 xiaomi_camera_01 检测到移动: {motion_id}")
        except Exception as e:
            self.logger.error(f"生成随机事件时出错: {str(e)}")

class AttackSimulator:
    """攻击模拟器"""
    
    def __init__(self, config):
        """初始化攻击模拟器"""
        self.logger = logging.getLogger("AttackSimulator")
        self.config = config
        self.enable_simulation = config.get('enable_attack_simulation', True)
        self.simulation_probability = config.get('simulation_probability', 0.1)
        self.running = False
        self.simulator_thread = None
    
    def start(self):
        """启动攻击模拟器"""
        if self.running or not self.enable_simulation:
            return
        
        self.running = True
        self.simulator_thread = threading.Thread(target=self._simulation_loop)
        self.simulator_thread.daemon = True
        self.simulator_thread.start()
    
    def stop(self):
        """停止攻击模拟器"""
        if not self.running:
            return
        
        self.running = False
        
        if self.simulator_thread and self.simulator_thread.is_alive():
            try:
                self.simulator_thread.join(timeout=5.0)
            except Exception as e:
                self.logger.warning(f"等待模拟线程结束时出现异常: {str(e)}")
        
        self.logger.info("攻击模拟已停止")
    
    def _simulation_loop(self):
        """攻击模拟循环"""
        attack_types = ["ddos", "mitm", "credential"]
        active_attacks = {}
        
        while self.running:
            try:
                # 随机开始新攻击
                if random.random() < self.simulation_probability:
                    attack_type = random.choice(attack_types)
                    attack_details = self._generate_attack(attack_type)
                    
                    if attack_type not in active_attacks:
                        self.logger.info(f"模拟{attack_details['name']}攻击: {attack_details['subtype']} 针对设备 {attack_details['target']}, 强度: {attack_details['intensity']}")
                        active_attacks[attack_type] = attack_details
                        
                        # 设置攻击持续时间
                        attack_details["end_time"] = time.time() + attack_details["duration"]
                
                # 检查攻击是否结束
                for attack_type in list(active_attacks.keys()):
                    if time.time() >= active_attacks[attack_type]["end_time"]:
                        attack = active_attacks[attack_type]
                        self.logger.info(f"{attack['name']}攻击结束: {attack['subtype']} 针对设备 {attack['target']}")
                        del active_attacks[attack_type]
                
                # 等待
                time.sleep(random.uniform(3.0, 7.0))
            except Exception as e:
                self.logger.error(f"模拟攻击时出错: {str(e)}")
                time.sleep(5.0)
    
    def _generate_attack(self, attack_type):
        """生成攻击详情"""
        if attack_type == "ddos":
            return {
                "name": "DDoS",
                "type": "ddos",
                "subtype": random.choice(["syn_flood", "udp_flood", "http_flood", "ping_flood"]),
                "intensity": random.choice(["low", "medium", "high"]),
                "target": f"device_{random.randint(1, 100)}",
                "duration": random.randint(10, 30)
            }
        elif attack_type == "mitm":
            return {
                "name": "中间人",
                "type": "mitm",
                "subtype": random.choice(["arp_spoofing", "dns_spoofing", "ssl_strip"]),
                "intensity": random.choice(["low", "medium", "high"]),
                "target": f"device_{random.randint(1, 100)}",
                "duration": random.randint(15, 45)
            }
        elif attack_type == "credential":
            return {
                "name": "凭证",
                "type": "credential",
                "subtype": random.choice(["brute_force", "password_spray", "phishing"]),
                "intensity": random.choice(["low", "medium", "high"]),
                "target": f"device_{random.randint(1, 100)}",
                "duration": random.randint(5, 20)
            }
        else:
            return {
                "name": "未知",
                "type": "unknown",
                "subtype": "generic",
                "intensity": "medium",
                "target": f"device_{random.randint(1, 100)}",
                "duration": random.randint(10, 30)
            }

def main():
    # 设置环境
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 创建必要目录
    dirs_to_create = [
        "logs", "data", "config", "quarantine",
        "data_backup", "telemetry_backup", "output"
    ]
    
    for directory in dirs_to_create:
        os.makedirs(directory, exist_ok=True)
    
    # 设置日志
    logger = setup_logging()
    
    logger.info("启动小米AIoT边缘安全防护研究平台...")
    logger.info(f"Python 版本: {sys.version}")
    logger.info(f"操作系统: {platform.system()} {platform.version()}")
    
    try:
        # 加载配置
        config = create_config()
        if not config:
            logger.error("无法加载配置，程序退出")
            return
        
        # 连接ThingsBoard平台
        tb_config = config.get('platform', {}).get('thingsboard', {})
        tb_connector = ThingsboardConnector(tb_config)
        if not tb_connector.connect():
            logger.error("无法连接到ThingsBoard平台，程序将以离线模式运行")
        
        # 初始化设备模拟器
        device_simulator = DeviceSimulator(config)
        device_simulator.start(tb_connector)
        
        # 初始化攻击模拟器
        security_config = config.get('security', {})
        attack_simulator = AttackSimulator(security_config)
        attack_simulator.start()
        
        # 初始化边缘计算防护
        edge_protection_config = config.get('edge_protection', {
            'protection_level': 'medium',
            'enable_firewall': True,
            'enable_ids': True,
            'enable_data_protection': True
        })
        
        edge_protector = EdgeSecurityProtector(edge_protection_config)
        
        def on_protection_activated(protection_data):
            action = protection_data.get('action', '')
            details = protection_data.get('details', {})
            logger.warning(f"边缘计算安全防护措施已激活: {action}, 详情: {details}")
        
        edge_protector.register_protection_callback(on_protection_activated)
        edge_protector.start()
        logger.info("边缘计算安全防护已启动")
        
        # 主循环
        logger.info("小米AIoT边缘安全防护研究平台已启动，按Ctrl+C停止")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("收到停止信号，正在关闭平台...")
        
        # 停止组件
        device_simulator.stop()
        attack_simulator.stop()
        edge_protector.stop()
        
        logger.info("小米AIoT边缘安全防护研究平台已停止")
    
    except Exception as e:
        logger.error(f"运行平台时出现错误: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main()