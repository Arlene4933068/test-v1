"""小米AIoT边缘安全防护研究平台 - 攻击仿真模块
负责模拟各种攻击场景，生成攻击数据"""

import logging
import random
import time
from typing import Dict, Any, List
from scapy.all import sniff, wrpcap, IP, TCP, UDP, Raw
from .security_logger import SecurityLogger
from .attack_detector import AttackDetector
from .protection_engine import ProtectionEngine
from .packet_visualizer import PacketVisualizer
import yaml
import os
import threading

class AttackSimulator:
    """攻击仿真器，用于模拟各种攻击场景"""
    
    def __init__(self, config_path: str = "config/security.yaml"):
        """初始化攻击仿真器
        
        Args:
            config_path: 安全配置文件路径
        """
        self.logger = logging.getLogger("security.attack_simulator")
        
        # 加载配置文件
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"加载安全配置文件失败: {str(e)}")
            self.config = {}
        
        # 初始化组件
        self.security_logger = SecurityLogger(config_path)
        self.detector = AttackDetector(self.config)
        self.protection_engine = ProtectionEngine(config_path)
        
        # 注册检测器的告警回调
        self.detector.add_alert_callback(self.protection_engine.handle_alert)
        
        # 初始化抓包配置
        self.capture_dir = os.path.join(os.path.dirname(config_path), 'captures')
        os.makedirs(self.capture_dir, exist_ok=True)
        self.packet_buffer = []
        self.max_packets = 1000
        
        # 初始化可视化器
        self.visualizer = PacketVisualizer(self.capture_dir)
        self.vis_thread = None
    
    def simulate_ddos_attack(self, target_device_id: str, duration: int = 60, request_rate: int = 1000):
        """模拟DDoS攻击
        
        Args:
            target_device_id: 目标设备ID
            duration: 攻击持续时间（秒）
            request_rate: 每秒请求数
        """
        self.logger.info(f"开始模拟DDoS攻击 - 目标设备: {target_device_id}")
        
        start_time = time.time()
        attack_count = 0
        
        while time.time() - start_time < duration:
            # 生成大量请求
            for _ in range(request_rate):
                attack_data = {
                    "type": "ddos",
                    "device_id": target_device_id,
                    "timestamp": time.time(),
                    "request": {
                        "method": "POST",
                        "path": "/api/device/data",
                        "payload": {"value": random.randint(1, 1000)}
                    }
                }
                
                # 记录攻击事件
                self.security_logger.log_event(
                    "ddos_attack",
                    target_device_id,
                    attack_data,
                    severity="critical"
                )
                
                attack_count += 1
            
            # 检测攻击
            self.detector.detect_attacks({
                "device_id": target_device_id,
                "type": "ddos",
                "request_count": request_rate,
                "time_window": 1
            })
            
            time.sleep(1)
        
        self.logger.info(f"DDoS攻击模拟完成 - 总请求数: {attack_count}")
    
    def simulate_mitm_attack(self, target_device_id: str, duration: int = 300):
        """模拟中间人攻击
        
        Args:
            target_device_id: 目标设备ID
            duration: 攻击持续时间（秒）
        """
        self.logger.info(f"开始模拟中间人攻击 - 目标设备: {target_device_id}")
        
        start_time = time.time()
        intercepted_count = 0
        
        while time.time() - start_time < duration:
            # 模拟数据包拦截和篡改
            original_data = {
                "temperature": random.uniform(20, 30),
                "humidity": random.uniform(40, 60)
            }
            
            modified_data = {
                "temperature": original_data["temperature"] + random.uniform(5, 10),
                "humidity": original_data["humidity"] + random.uniform(-10, 10)
            }
            
            attack_data = {
                "type": "mitm",
                "device_id": target_device_id,
                "timestamp": time.time(),
                "original_data": original_data,
                "modified_data": modified_data
            }
            
            # 记录攻击事件
            self.security_logger.log_event(
                "mitm_attack",
                target_device_id,
                attack_data,
                severity="high"
            )
            
            intercepted_count += 1
            
            # 检测攻击
            self.detector.detect_attacks({
                "device_id": target_device_id,
                "type": "mitm",
                "data_integrity": "compromised",
                "original_data": original_data,
                "received_data": modified_data
            })
            
            time.sleep(random.uniform(1, 5))
        
        self.logger.info(f"中间人攻击模拟完成 - 拦截次数: {intercepted_count}")
    
    def simulate_credential_attack(self, target_device_id: str, attempts: int = 100):
        """模拟凭证攻击
        
        Args:
            target_device_id: 目标设备ID
            attempts: 尝试次数
        """
        self.logger.info(f"开始模拟凭证攻击 - 目标设备: {target_device_id}")
        
        for i in range(attempts):
            # 生成随机凭证
            username = f"user_{random.randint(1, 1000)}"
            password = f"pass_{random.randint(1000, 9999)}"
            
            attack_data = {
                "type": "credential",
                "device_id": target_device_id,
                "timestamp": time.time(),
                "attempt": {
                    "username": username,
                    "password": password,
                    "attempt_number": i + 1
                }
            }
            
            # 记录攻击事件
            self.security_logger.log_event(
                "credential_attack",
                target_device_id,
                attack_data,
                severity="high"
            )
            
            # 检测攻击
            self.detector.detect_attacks({
                "device_id": target_device_id,
                "type": "credential",
                "failed_attempts": i + 1,
                "time_window": 300
            })
            
            time.sleep(random.uniform(0.1, 0.5))
        
        self.logger.info(f"凭证攻击模拟完成 - 总尝试次数: {attempts}")
    
    def simulate_firmware_attack(self, target_device_id: str):
        """模拟固件攻击
        
        Args:
            target_device_id: 目标设备ID
        """
        self.logger.info(f"开始模拟固件攻击 - 目标设备: {target_device_id}")
        
        # 模拟固件篡改
        attack_data = {
            "type": "firmware",
            "device_id": target_device_id,
            "timestamp": time.time(),
            "details": {
                "original_version": "1.0.0",
                "modified_version": "1.0.0_malicious",
                "modification_type": "binary_patching"
            }
        }
        
        # 记录攻击事件
        self.security_logger.log_event(
            "firmware_attack",
            target_device_id,
            attack_data,
            severity="critical"
        )
        
        # 检测攻击
        self.detector.detect_attacks({
            "device_id": target_device_id,
            "type": "firmware",
            "firmware_integrity": "compromised",
            "version_mismatch": True
        })
        
        self.logger.info("固件攻击模拟完成")
    
    def capture_packets(self, interface: str = None, filter: str = None, duration: int = 60, visualize: bool = True):
        """捕获网络数据包
        
        Args:
            interface: 网络接口名称
            filter: BPF过滤器表达式
            duration: 捕获持续时间（秒）
        """
        self.logger.info(f"开始捕获网络数据包 - 接口: {interface or '默认'} 过滤器: {filter or '无'}")
        
        def packet_callback(packet):
            if IP in packet:
                packet_info = {
                    'timestamp': time.time(),
                    'src_ip': packet[IP].src,
                    'dst_ip': packet[IP].dst,
                    'protocol': packet[IP].proto
                }
                
                if TCP in packet:
                    packet_info.update({
                        'src_port': packet[TCP].sport,
                        'dst_port': packet[TCP].dport,
                        'tcp_flags': packet[TCP].flags
                    })
                elif UDP in packet:
                    packet_info.update({
                        'src_port': packet[UDP].sport,
                        'dst_port': packet[UDP].dport
                    })
                
                if Raw in packet:
                    packet_info['payload'] = str(packet[Raw].load)
                
                self.packet_buffer.append(packet_info)
                
                # 分析数据包是否存在异常
                self.analyze_packet(packet_info)
                
                # 更新可视化数据
                self.visualizer.update_data(packet_info)
                
                # 保存到PCAP文件
                if len(self.packet_buffer) >= self.max_packets:
                    self.save_capture()
        
        try:
            # 启动可视化服务
            if visualize and not self.vis_thread:
                self.vis_thread = threading.Thread(target=self.visualizer.start)
                self.vis_thread.daemon = True
                self.vis_thread.start()
                self.logger.info("可视化服务已启动 - http://localhost:8050")
            
            sniff(iface=interface, filter=filter, prn=packet_callback, timeout=duration)
            self.save_capture()
            self.logger.info("数据包捕获完成")
        except Exception as e:
            self.logger.error(f"数据包捕获失败: {str(e)}")
    
    def analyze_packet(self, packet_info: Dict):
        """分析数据包是否存在异常
        
        Args:
            packet_info: 数据包信息
        """
        # 检测可疑端口
        suspicious_ports = [22, 23, 3389, 445]
        if packet_info.get('dst_port') in suspicious_ports:
            self.security_logger.log_alert(
                'suspicious_port_access',
                'network',
                {
                    'src_ip': packet_info['src_ip'],
                    'dst_ip': packet_info['dst_ip'],
                    'dst_port': packet_info['dst_port']
                },
                confidence=0.8,
                severity='high'
            )
        
        # 检测大量TCP SYN包（可能是SYN洪水攻击）
        if TCP in packet_info and packet_info['tcp_flags'] == 2:  # SYN flag
            self.detector.detect_attacks({
                'type': 'syn_flood',
                'src_ip': packet_info['src_ip'],
                'timestamp': packet_info['timestamp']
            })
    
    def save_capture(self):
        """保存捕获的数据包到PCAP文件"""
        if self.packet_buffer:
            timestamp = int(time.time())
            filename = os.path.join(self.capture_dir, f'capture_{timestamp}.pcap')
            wrpcap(filename, self.packet_buffer)
            self.packet_buffer = []
            self.logger.info(f"数据包已保存到: {filename}")
    
    def run_attack_simulation(self, target_device_id: str):
        """运行完整的攻击仿真
        
        Args:
            target_device_id: 目标设备ID
        """
        self.logger.info(f"开始运行攻击仿真 - 目标设备: {target_device_id}")
        
        # 模拟DDoS攻击
        self.simulate_ddos_attack(target_device_id, duration=30, request_rate=500)
        
        # 等待一段时间
        time.sleep(10)
        
        # 模拟中间人攻击
        self.simulate_mitm_attack(target_device_id, duration=60)
        
        # 等待一段时间
        time.sleep(10)
        
        # 模拟凭证攻击
        self.simulate_credential_attack(target_device_id, attempts=50)
        
        # 等待一段时间
        time.sleep(10)
        
        # 模拟固件攻击
        self.simulate_firmware_attack(target_device_id)
        
        self.logger.info("攻击仿真完成")