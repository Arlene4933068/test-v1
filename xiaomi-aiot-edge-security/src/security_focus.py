#!/usr/bin/env python3
# 小米AIoT边缘安全防护研究平台 - 安全防护研究专注版
# 此版本减少遥测数据发送频率，专注于安全仿真和防护研究

import os
import sys
import time
import logging
import yaml
import random
import json
import threading
import queue
import traceback
from typing import Dict, List, Any

def setup_logging():
    """设置日志系统"""
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, f"security_{time.strftime('%Y%m%d')}.log")
    
    # 创建格式器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 创建文件处理器
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    # 创建控制台处理器 - 仅显示警告和错误
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.WARNING)
    
    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # 为ThingsBoard日志设置更高的级别，减少输出
    tb_logger = logging.getLogger("ThingsBoard")
    tb_logger.setLevel(logging.WARNING)
    
    # 返回主日志记录器
    return logging.getLogger("SecurityFocus")

def create_config():
    """创建默认配置文件"""
    logger = logging.getLogger("Config")
    config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    config_file = os.path.join(config_dir, "security_focus.yaml")
    if not os.path.exists(config_file):
        default_config = {
            "platform": {
                "edgex": {
                    "host": "localhost",
                    "port": 59880
                },
                "thingsboard": {
                    "host": "localhost",
                    "port": 8080
                }
            },
            "security": {
                # 提高安全事件发生的频率
                "scan_interval": 5,  # 扫描间隔，秒
                "detection_threshold": 0.6,  # 降低检测阈值，增加事件数量
                "enable_attack_simulation": True,
                "simulation_probability": 0.2,  # 提高攻击概率
                "attack_complexity": "high"  # 低/中/高复杂度攻击
            },
            "devices": {
                # 模拟设备配置
                "device_count": 4,  # 默认设备数量
                "telemetry_interval": 60,  # 增加到60秒，减少遥测频率
                "telemetry_enabled": False  # 默认关闭遥测发送
            },
            "edge_protection": {
                "protection_level": "high",  # 增加防护级别
                "enable_firewall": True,
                "enable_ids": True,
                "enable_data_protection": True,
                "detection_sensitivity": "high",  # 高检测灵敏度
                "proactive_defense": True,  # 主动防御
                "device_whitelist": [
                    "xiaomi_gateway_01",
                    "xiaomi_router_01",
                    "xiaomi_speaker_01",
                    "xiaomi_camera_01"
                ],
                "threat_intelligence": {
                    "enabled": True,
                    "update_interval": 3600,
                    "sources": ["local", "cloud"]
                },
                "anomaly_detection": {
                    "baseline_period": 24,  # 小时
                    "statistical_methods": ["z-score", "moving-average"],
                    "machine_learning": False
                }
            },
            "analytics": {
                "output_dir": "output",
                "report_interval": 300,  # 5分钟生成一次报告
                "save_alerts": True,
                "visualization_enabled": False
            }
        }
        
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        logger.info(f"已创建安全专注配置文件: {config_file}")
    
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
        self.protection_level = config.get('protection_level', 'high')
        self.enable_firewall = config.get('enable_firewall', True)
        self.enable_ids = config.get('enable_ids', True)
        self.enable_data_protection = config.get('enable_data_protection', True)
        
        # 增加额外安全设置
        self.detection_sensitivity = config.get('detection_sensitivity', 'high')
        self.proactive_defense = config.get('proactive_defense', True)
        
        # 状态变量
        self.running = False
        self.protection_thread = None
        
        # 保护事件队列
        self.event_queue = queue.Queue()
        
        # 设备白名单
        self.device_whitelist = set(config.get('device_whitelist', []))
        
        # 被阻止的IP集合
        self.blocked_ips = set()
        
        # 检测到的威胁
        self.detected_threats = []
        self.threat_count_by_type = {}
        
        # 注册回调函数
        self.on_threat_detected = None
        self.on_protection_activated = None
        
        # 威胁情报
        self.threat_intelligence = self._initialize_threat_intelligence(
            config.get('threat_intelligence', {})
        )
        
        # 异常检测配置
        self.anomaly_config = config.get('anomaly_detection', {})
    
    def _initialize_threat_intelligence(self, ti_config):
        """初始化威胁情报数据库"""
        ti_enabled = ti_config.get('enabled', True)
        if not ti_enabled:
            return {}
            
        # 实际项目中，这里应该从外部源加载威胁情报数据
        # 为了演示，我们使用一组预定义的威胁情报
        return {
            "malicious_ips": [
                f"192.168.{i}.{j}" 
                for i in range(1, 5) 
                for j in range(1, 10) 
                if random.random() < 0.1
            ],
            "attack_signatures": [
                "syn_flood_pattern_1",
                "dns_exfiltration_pattern",
                "sql_injection_pattern",
                "command_injection_pattern"
            ],
            "vulnerability_hashes": [
                "cve-2023-12345",
                "cve-2024-67890"
            ],
            "last_updated": time.time()
        }
    
    def start(self):
        """启动防护"""
        if self.running:
            return
        
        self.running = True
        self.protection_thread = threading.Thread(target=self._protection_loop)
        self.protection_thread.daemon = True
        self.protection_thread.start()
        
        self.logger.info(f"边缘计算安全防护已启动，防护级别: {self.protection_level}, 检测灵敏度: {self.detection_sensitivity}")
        if self.proactive_defense:
            self.logger.info("启用主动防御模式")
        
        # 显示初始化防护状态
        self.logger.info(f"防火墙状态: {'启用' if self.enable_firewall else '禁用'}")
        self.logger.info(f"入侵检测系统(IDS)状态: {'启用' if self.enable_ids else '禁用'}")
        self.logger.info(f"数据保护状态: {'启用' if self.enable_data_protection else '禁用'}")
    
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
        
        # 显示防护统计信息
        self._show_protection_statistics()
        
        self.logger.info("边缘计算安全防护已停止")
    
    def _show_protection_statistics(self):
        """显示防护统计信息"""
        self.logger.info("==== 边缘计算安全防护统计 ====")
        self.logger.info(f"总检测到的威胁数量: {len(self.detected_threats)}")
        
        # 按类型统计威胁
        if self.threat_count_by_type:
            self.logger.info("威胁类型统计:")
            for threat_type, count in self.threat_count_by_type.items():
                self.logger.info(f"  - {threat_type}: {count}次")
        
        # 统计阻止的IP数量
        self.logger.info(f"已阻止的恶意IP数量: {len(self.blocked_ips)}")
        
        # 防护效果评估
        if len(self.detected_threats) > 0:
            mitigated = sum(1 for threat in self.detected_threats if threat.get('mitigated', False))
            mitigation_rate = (mitigated / len(self.detected_threats)) * 100
            self.logger.info(f"威胁缓解率: {mitigation_rate:.1f}%")
    
    def register_protection_callback(self, callback):
        """注册保护激活回调函数"""
        self.on_protection_activated = callback
    
    def register_threat_callback(self, callback):
        """注册威胁检测回调函数"""
        self.on_threat_detected = callback
    
    def _protection_loop(self):
        """防护主循环"""
        activity_counter = 0
        
        while self.running:
            try:
                # 处理保护事件队列
                self._process_event_queue()
                
                # 每次循环增加活动计数器
                activity_counter += 1
                
                # 检查网络流量异常
                if activity_counter % 3 == 0:  # 每3个循环
                    self._monitor_network_traffic()
                
                # 验证设备完整性
                if activity_counter % 5 == 0:  # 每5个循环
                    self._verify_device_integrity()
                
                # 检查配置安全性
                if activity_counter % 7 == 0:  # 每7个循环
                    self._check_configuration_security()
                
                # 扫描恶意软件
                if activity_counter % 11 == 0:  # 每11个循环
                    self._scan_for_malware()
                    
                # 分析安全事件相关性
                if activity_counter % 13 == 0:  # 每13个循环
                    self._analyze_security_correlations()
                
                # 更新威胁情报
                if activity_counter % 60 == 0:  # 大约每分钟
                    self._update_threat_intelligence()
                
                # 防御状态自检
                if activity_counter % 30 == 0:  # 每半分钟
                    self._self_check_defense_status()
                
                # 重置计数器，防止过大
                if activity_counter >= 120:
                    activity_counter = 0
                
                # 等待一段时间
                time.sleep(1.0)
            except Exception as e:
                self.logger.error(f"防护循环执行异常: {str(e)}")
                time.sleep(5.0)
    
    def _process_event_queue(self):
        """处理保护事件队列"""
        try:
            # 获取队列中的所有事件（非阻塞）
            events = []
            while not self.event_queue.empty():
                try:
                    event = self.event_queue.get_nowait()
                    events.append(event)
                    self.event_queue.task_done()
                except queue.Empty:
                    break
            
            # 如果有事件，处理它们
            if events:
                for event in events:
                    self._handle_security_event(event)
        except Exception as e:
            self.logger.error(f"处理事件队列时出错: {str(e)}")
    
    def _handle_security_event(self, event):
        """处理安全事件"""
        try:
            event_type = event.get('type')
            details = event.get('details', {})
            timestamp = event.get('timestamp', time.time())
            
            # 添加到已检测威胁列表
            threat_record = {
                'type': event_type,
                'details': details,
                'timestamp': timestamp,
                'mitigated': False
            }
            
            self.detected_threats.append(threat_record)
            
            # 更新威胁类型计数
            if event_type in self.threat_count_by_type:
                self.threat_count_by_type[event_type] += 1
            else:
                self.threat_count_by_type[event_type] = 1
            
            # 根据威胁类型采取不同的应对措施
            if event_type == 'network_anomaly':
                mitigated = self._handle_network_anomaly(details)
                threat_record['mitigated'] = mitigated
            elif event_type == 'device_tampering':
                mitigated = self._handle_device_tampering(details)
                threat_record['mitigated'] = mitigated
            elif event_type == 'malware_detected':
                mitigated = self._handle_malware_detection(details)
                threat_record['mitigated'] = mitigated
            elif event_type == 'config_vulnerability':
                mitigated = self._handle_config_vulnerability(details)
                threat_record['mitigated'] = mitigated
            else:
                self.logger.warning(f"未知的安全事件类型: {event_type}")
            
            # 触发回调
            if self.on_threat_detected:
                self.on_threat_detected({
                    'type': event_type,
                    'details': details,
                    'timestamp': timestamp
                })
        except Exception as e:
            self.logger.error(f"处理安全事件时出错: {str(e)}")
    
    def add_security_event(self, event_type, details):
        """添加安全事件到队列"""
        try:
            event = {
                'type': event_type,
                'details': details,
                'timestamp': time.time()
            }
            self.event_queue.put(event)
        except Exception as e:
            self.logger.error(f"添加安全事件到队列时出错: {str(e)}")
    
    def _handle_network_anomaly(self, details):
        """处理网络异常"""
        anomaly_type = details.get('anomaly_type', '')
        source_ip = details.get('source_ip', '')
        confidence = details.get('confidence', 0.0)
        
        # 记录处理
        self.logger.warning(f"处理网络异常: {anomaly_type} 来自 {source_ip} (置信度: {confidence:.2f})")
        
        # 获取安全等级阈值 - 根据灵敏度调整
        threshold = 0.8  # 默认
        if self.detection_sensitivity == 'high':
            threshold = 0.7
        elif self.detection_sensitivity == 'medium':
            threshold = 0.8
        elif self.detection_sensitivity == 'low':
            threshold = 0.9
        
        # 确定是否阻止IP
        if confidence >= threshold:
            self.logger.warning(f"阻止可疑IP: {source_ip} (原因: {anomaly_type}, 置信度: {confidence:.2f})")
            self.blocked_ips.add(source_ip)
            
            # 触发防护措施
            if self.on_protection_activated:
                self.on_protection_activated({
                    'action': 'block_ip',
                    'details': {
                        'ip': source_ip,
                        'reason': anomaly_type,
                        'confidence': confidence
                    },
                    'timestamp': time.time()
                })
            
            return True
        else:
            self.logger.info(f"监控可疑IP: {source_ip} (置信度低于阈值: {confidence:.2f} < {threshold})")
            return False
    
    def _handle_device_tampering(self, details):
        """处理设备篡改"""
        device_id = details.get('device_id', '')
        tampering_type = details.get('tampering_type', '')
        severity = details.get('severity', 'medium')
        
        # 记录处理
        self.logger.warning(f"处理设备篡改: {tampering_type} 在设备 {device_id} (严重度: {severity})")
        
        # 根据严重程度决定措施
        if severity in ('high', 'critical'):
            # 高严重级别 - 断开设备、隔离、通知
            self.logger.warning(f"⛔ 断开并隔离设备: {device_id}")
            
            # 触发防护措施
            if self.on_protection_activated:
                self.on_protection_activated({
                    'action': 'isolate_device',
                    'details': {
                        'device_id': device_id,
                        'tampering_type': tampering_type,
                        'severity': severity
                    },
                    'timestamp': time.time()
                })
            
            return True
        else:
            # 中低严重级别 - 监控设备
            self.logger.info(f"增强监控设备: {device_id}")
            
            # 触发防护措施
            if self.on_protection_activated:
                self.on_protection_activated({
                    'action': 'enhance_monitoring',
                    'details': {
                        'device_id': device_id,
                        'tampering_type': tampering_type,
                        'severity': severity
                    },
                    'timestamp': time.time()
                })
            
            return False
    
    def _handle_malware_detection(self, details):
        """处理恶意软件检测"""
        malware_type = details.get('malware_type', '')
        file_path = details.get('file_path', '')
        threat_level = details.get('threat_level', 'medium')
        
        # 记录处理
        self.logger.warning(f"处理恶意软件: {malware_type} 在 {file_path} (威胁等级: {threat_level})")
        
        # 根据威胁等级决定措施
        if threat_level in ('high', 'critical'):
            # 高威胁级别 - 隔离文件
            self.logger.warning(f"隔离恶意文件: {file_path}")
            
            # 触发防护措施
            if self.on_protection_activated:
                self.on_protection_activated({
                    'action': 'quarantine_file',
                    'details': {
                        'file_path': file_path,
                        'malware_type': malware_type,
                        'threat_level': threat_level
                    },
                    'timestamp': time.time()
                })
            
            return True
        else:
            # 中低威胁级别 - 标记文件
            self.logger.info(f"标记可疑文件: {file_path}")
            
            # 触发防护措施
            if self.on_protection_activated:
                self.on_protection_activated({
                    'action': 'flag_file',
                    'details': {
                        'file_path': file_path,
                        'malware_type': malware_type,
                        'threat_level': threat_level
                    },
                    'timestamp': time.time()
                })
            
            return False
    
    def _handle_config_vulnerability(self, details):
        """处理配置漏洞"""
        config_file = details.get('config_file', '')
        vulnerability_type = details.get('vulnerability_type', '')
        risk_level = details.get('risk_level', 'medium')
        
        # 记录处理
        self.logger.warning(f"处理配置漏洞: {vulnerability_type} 在 {config_file} (风险等级: {risk_level})")
        
        # 根据风险等级决定措施
        if risk_level in ('high', 'critical'):
            # 高风险级别 - 修复配置
            self.logger.warning(f"修复配置漏洞: {config_file}")
            
            # 触发防护措施
            if self.on_protection_activated:
                self.on_protection_activated({
                    'action': 'fix_vulnerability',
                    'details': {
                        'config_file': config_file,
                        'vulnerability_type': vulnerability_type,
                        'risk_level': risk_level
                    },
                    'timestamp': time.time()
                })
            
            return True
        else:
            # 中低风险级别 - 记录漏洞
            self.logger.info(f"记录配置漏洞: {config_file}")
            
            # 触发防护措施
            if self.on_protection_activated:
                self.on_protection_activated({
                    'action': 'log_vulnerability',
                    'details': {
                        'config_file': config_file,
                        'vulnerability_type': vulnerability_type,
                        'risk_level': risk_level
                    },
                    'timestamp': time.time()
                })
            
            return False
    
    def _monitor_network_traffic(self):
        """监控网络流量异常"""
        # 提高检测几率，使安全研究更集中
        if random.random() < 0.15:  # 15%的几率检测到异常
            # 生成模拟异常
            anomaly_types = [
                'port_scan', 'syn_flood', 'dns_tunneling', 
                'unusual_protocol', 'data_exfiltration',
                'brute_force', 'command_and_control',
                'lateral_movement', 'crypto_mining'
            ]
            
            # 检查是否应该基于威胁情报生成IP
            use_threat_intel = False
            if random.random() < 0.4 and self.threat_intelligence.get('malicious_ips'):
                source_ip = random.choice(self.threat_intelligence['malicious_ips'])
                use_threat_intel = True
            else:
                source_ip = f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"
            
            anomaly_type = random.choice(anomaly_types)
            
            # 根据是否使用威胁情报调整置信度
            confidence_base = 0.7 if use_threat_intel else 0.5
            confidence = round(random.uniform(confidence_base, 0.98), 2)
            
            # 构建完整异常详情
            anomaly = {
                'anomaly_type': anomaly_type,
                'source_ip': source_ip,
                'destination_ip': f"10.0.{random.randint(1, 254)}.{random.randint(1, 254)}",
                'confidence': confidence,
                'packet_count': random.randint(100, 10000),
                'duration': random.randint(10, 300),  # 持续时间（秒）
                'ports': [random.randint(1, 65535) for _ in range(random.randint(1, 5))],
                'protocol': random.choice(['TCP', 'UDP', 'ICMP', 'HTTP', 'DNS'])
            }
            
            # 将异常添加到事件队列
            self.add_security_event('network_anomaly', anomaly)
    
    def _verify_device_integrity(self):
        """验证设备完整性"""
        if random.random() < 0.08:  # 8%的几率检测到篡改
            # 生成模拟篡改事件
            tampering_types = [
                'firmware_modified', 'configuration_changed', 
                'unauthorized_access', 'hardware_tampering',
                'bootloader_compromised', 'root_access_detected',
                'certificate_invalid', 'secure_boot_failure'
            ]
            
            device_id = f"xiaomi_device_{random.randint(1, 10)}"
            tampering_type = random.choice(tampering_types)
            
            # 根据篡改类型调整严重性
            if tampering_type in ['bootloader_compromised', 'root_access_detected', 'secure_boot_failure']:
                severity = random.choice(['high', 'critical'])
            else:
                severity = random.choice(['low', 'medium', 'high'])
            
            # 构建完整篡改详情
            tampering = {
                'device_id': device_id,
                'tampering_type': tampering_type,
                'severity': severity,
                'detected_at': time.time(),
                'detection_method': random.choice([
                    'checksum_verification', 'behavioral_analysis',
                    'log_analysis', 'signature_check'
                ]),
                'affected_components': random.sample([
                    'firmware', 'bootloader', 'os', 'application',
                    'configuration', 'certificates'
                ], k=random.randint(1, 3))
            }
            
            # 将篡改事件添加到事件队列
            self.add_security_event('device_tampering', tampering)
    
    def _check_configuration_security(self):
        """检查配置安全性"""
        if random.random() < 0.1:  # 10%的几率检测到配置漏洞
            # 生成模拟配置漏洞事件
            vulnerability_types = [
                'weak_password', 'open_port', 'insecure_protocol', 
                'default_credential', 'missing_encryption',
                'excessive_permissions', 'debug_enabled',
                'outdated_component', 'insecure_api_key'
            ]
            
            vulnerability_type = random.choice(vulnerability_types)
            
            # 根据漏洞类型调整风险等级
            if vulnerability_type in ['default_credential', 'missing_encryption', 'weak_password']:
                risk_level = random.choice(['high', 'critical'])
            else:
                risk_level = random.choice(['low', 'medium', 'high'])
            
            # 构建完整漏洞详情
            vulnerability = {
                'config_file': f"/etc/xiaomi/device{random.randint(1, 20)}.{random.choice(['yaml', 'json', 'conf'])}",
                'vulnerability_type': vulnerability_type,
                'risk_level': risk_level,
                'recommended_fix': "Update configuration with secure settings",
                'cve_id': f"CVE-202{random.randint(0, 4)}-{random.randint(10000, 99999)}",
                'discovery_method': random.choice([
                    'static_analysis', 'dynamic_testing',
                    'security_scan', 'code_review'
                ])
            }
            
            # 将漏洞事件添加到事件队列
            self.add_security_event('config_vulnerability', vulnerability)
    
    def _scan_for_malware(self):
        """扫描恶意代码"""
        if random.random() < 0.06:  # 6%的几率检测到恶意软件
            # 生成模拟恶意软件事件
            malware_types = [
                'trojan', 'ransomware', 'rootkit', 'botnet_client', 
                'backdoor', 'spyware', 'worm', 'keylogger',
                'cryptominer', 'fileless_malware'
            ]
            
            malware_type = random.choice(malware_types)
            
            # 根据恶意软件类型调整威胁等级
            if malware_type in ['ransomware', 'rootkit', 'backdoor']:
                threat_level = random.choice(['high', 'critical'])
            else:
                threat_level = random.choice(['low', 'medium', 'high'])
            
            # 构建完整恶意软件详情
            malware = {
                'malware_type': malware_type,
                'file_path': f"/tmp/suspect_file_{random.randint(1000, 9999)}.{random.choice(['bin', 'elf', 'so', 'dat'])}",
                'threat_level': threat_level,
                'signature_matched': f"SIG_{random.randint(10000, 99999)}",
                'file_hash': ''.join(random.choices('0123456789abcdef', k=64)),
                'infection_vector': random.choice([
                    'usb_device', 'network_download',
                    'email_attachment', 'software_update'
                ])
            }
            
            # 将恶意软件事件添加到事件队列
            self.add_security_event('malware_detected', malware)
    
    def _analyze_security_correlations(self):
        """分析安全事件相关性"""
        # 此功能需要多个安全事件作为输入
        # 简化版本：偶尔生成关联分析事件
        if len(self.detected_threats) >= 3 and random.random() < 0.2:
            # 从最近的威胁中选择样本
            recent_threats = self.detected_threats[-10:]
            sample_threats = random.sample(recent_threats, min(3, len(recent_threats)))
            
            # 计算事件关联性
            correlation_types = [
                'temporal_sequence', 'common_attacker',
                'attack_campaign', 'attack_chain'
            ]
            
            correlation = {
                'correlation_type': random.choice(correlation_types),
                'confidence': round(random.uniform(0.7, 0.95), 2),
                'related_event_count': len(sample_threats),
                'attacker_profile': {
                    'sophistication': random.choice(['low', 'medium', 'high']),
                    'motivation': random.choice(['financial', 'espionage', 'disruption']),
                    'persistence': random.choice(['transient', 'persistent'])
                },
                'summary': "Multiple related security events detected"
            }
            
            # 记录关联分析结果
            self.logger.warning(f"安全事件关联分析: 检测到{correlation['correlation_type']}关联模式，涉及{correlation['related_event_count']}个安全事件")
            
            # 触发回调
            if self.on_threat_detected:
                self.on_threat_detected({
                    'type': 'security_correlation',
                    'details': correlation,
                    'timestamp': time.time()
                })
    
    def _update_threat_intelligence(self):
        """更新威胁情报"""
        # 实际系统中，这里应该从外部源获取最新的威胁情报
        # 为了演示，我们只是随机更新一些条目
        if random.random() < 0.3:  # 30%的几率更新威胁情报
            # 更新恶意IP列表
            new_ips = [
                f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}"
                for _ in range(random.randint(1, 5))
            ]
            
            if 'malicious_ips' in self.threat_intelligence:
                # 添加新IP，同时保持列表长度合理
                self.threat_intelligence['malicious_ips'].extend(new_ips)
                if len(self.threat_intelligence['malicious_ips']) > 50:
                    self.threat_intelligence['malicious_ips'] = self.threat_intelligence['malicious_ips'][-50:]
            
            # 更新最后更新时间
            self.threat_intelligence['last_updated'] = time.time()
            
            self.logger.info(f"已更新威胁情报数据库，新增{len(new_ips)}个恶意IP")
    
    def _self_check_defense_status(self):
        """防御状态自检"""
        # 检查防御系统各组件的状态和有效性
        if random.random() < 0.05:  # 5%的几率发现防御系统问题
            defense_components = ['firewall', 'ids', 'data_protection', 'threat_intelligence']
            problem_component = random.choice(defense_components)
            
            self.logger.info(f"防御系统自检: {problem_component}组件需要优化")
            
            # 对于主动防御模式，自动"修复"问题
            if self.proactive_defense:
                self.logger.info(f"主动防御: 优化{problem_component}组件配置")

class AttackSimulator:
    """攻击模拟器 - 增强版"""
    
    def __init__(self, config):
        """初始化攻击模拟器"""
        self.logger = logging.getLogger("AttackSimulator")
        self.config = config
        self.enable_simulation = config.get('enable_attack_simulation', True)
        self.simulation_probability = config.get('simulation_probability', 0.2)
        self.attack_complexity = config.get('attack_complexity', 'medium')
        self.running = False
        self.simulator_thread = None
        
        # 攻击统计
        self.attack_statistics = {
            'total_attacks': 0,
            'by_type': {},
            'by_target': {},
            'complex_attack_chains': 0
        }
        
        # 当前活动攻击
        self.active_attacks = {}
        
        # 攻击历史
        self.attack_history = []
        
        # 最大历史记录
        self.max_history = 100
    
    def start(self):
        """启动攻击模拟器"""
        if self.running or not self.enable_simulation:
            return
        
        self.running = True
        self.simulator_thread = threading.Thread(target=self._simulation_loop)
        self.simulator_thread.daemon = True
        self.simulator_thread.start()
        
        self.logger.info(f"攻击模拟已启动，复杂度: {self.attack_complexity}")
    
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
        
        # 显示攻击统计
        self._show_attack_statistics()
        
        self.logger.info("攻击模拟已停止")
    
    def _show_attack_statistics(self):
        """显示攻击统计"""
        self.logger.info("==== 攻击模拟统计 ====")
        self.logger.info(f"总模拟攻击数量: {self.attack_statistics['total_attacks']}")
        
        # 按类型统计
        if self.attack_statistics['by_type']:
            self.logger.info("攻击类型统计:")
            for attack_type, count in self.attack_statistics['by_type'].items():
                self.logger.info(f"  - {attack_type}: {count}次")
        
        # 复杂攻击链
        self.logger.info(f"复杂攻击链数量: {self.attack_statistics['complex_attack_chains']}")
    
    def _simulation_loop(self):
        """攻击模拟循环"""
        # 定义攻击类型和场景
        attack_types = {
            "reconnaissance": ["port_scan", "dns_enumeration", "vulnerability_scan"],
            "initial_access": ["phishing", "credential_stuffing", "supply_chain"],
            "execution": ["command_injection", "script_execution", "malicious_file"],
            "persistence": ["backdoor", "startup_modification", "cron_job"],
            "lateral_movement": ["network_sniffing", "pass_the_hash", "internal_scan"],
            "data_exfiltration": ["dns_tunneling", "encrypted_channel", "steganography"]
        }
        
        # 根据复杂度调整攻击参数
        attack_chance = self.simulation_probability
        if self.attack_complexity == 'low':
            chain_chance = 0.1
            max_chain_length = 2
        elif self.attack_complexity == 'medium':
            chain_chance = 0.3
            max_chain_length = 3
        else:  # high
            chain_chance = 0.5
            max_chain_length = 5
            attack_chance *= 1.2  # 提高攻击频率
        
        while self.running:
            try:
                # 检查是否应该开始一次攻击
                if random.random() < attack_chance:
                    # 决定是单一攻击还是攻击链
                    if random.random() < chain_chance:
                        # 生成攻击链
                        self._generate_attack_chain(attack_types, max_chain_length)
                    else:
                        # 生成单一攻击
                        self._generate_single_attack(attack_types)
                
                # 更新活动攻击状态
                self._update_active_attacks()
                
                # 等待
                time.sleep(random.uniform(4.0, 8.0))
            except Exception as e:
                self.logger.error(f"模拟攻击时出错: {str(e)}")
                time.sleep(5.0)
    
    def _generate_single_attack(self, attack_types):
        """生成单一攻击"""
        # 随机选择攻击类型和子类型
        attack_category = random.choice(list(attack_types.keys()))
        attack_subtype = random.choice(attack_types[attack_category])
        
        # 生成目标设备
        device_types = ["gateway", "router", "camera", "speaker", "sensor"]
        target_type = random.choice(device_types)
        target_id = f"{target_type}_{random.randint(1, 20)}"
        
        # 生成攻击详情
        attack_id = f"ATTACK_{random.randint(10000, 99999)}"
        attack = {
            "id": attack_id,
            "category": attack_category,
            "subtype": attack_subtype,
            "target": target_id,
            "intensity": random.choice(["low", "medium", "high"]),
            "start_time": time.time(),
            "duration": random.randint(15, 60),  # 持续15-60秒
            "status": "active"
        }
        
        # 添加到活动攻击
        self.active_attacks[attack_id] = attack
        
        # 更新统计
        self.attack_statistics["total_attacks"] += 1
        if attack_category in self.attack_statistics["by_type"]:
            self.attack_statistics["by_type"][attack_category] += 1
        else:
            self.attack_statistics["by_type"][attack_category] = 1
        
        if target_id in self.attack_statistics["by_target"]:
            self.attack_statistics["by_target"][target_id] += 1
        else:
            self.attack_statistics["by_target"][target_id] = 1
        
        # 记录日志
        self.logger.warning(f"模拟攻击: {attack_category}/{attack_subtype} 针对 {target_id}, 强度: {attack['intensity']}")
        
        # 添加到历史记录
        self.attack_history.append(attack)
        if len(self.attack_history) > self.max_history:
            self.attack_history = self.attack_history[-self.max_history:]
    
    def _generate_attack_chain(self, attack_types, max_length):
        """生成攻击链"""
        # 确定攻击链长度
        chain_length = random.randint(2, max_length)
        
        # 选择目标
        device_types = ["gateway", "router", "camera", "speaker", "sensor"]
        target_type = random.choice(device_types)
        target_id = f"{target_type}_{random.randint(1, 20)}"
        
        # 创建攻击链ID
        chain_id = f"CHAIN_{random.randint(10000, 99999)}"
        
        # 确定攻击步骤 - 根据MITRE ATT&CK模型的战术顺序
        possible_steps = [
            "reconnaissance", "initial_access", "execution", 
            "persistence", "lateral_movement", "data_exfiltration"
        ]
        
        # 选择攻击链中的步骤
        selected_steps = []
        if chain_length >= len(possible_steps):
            selected_steps = possible_steps
        else:
            # 确保第一步是侦察
            selected_steps.append("reconnaissance")
            chain_length -= 1
            
            # 从剩余步骤中选择
            remaining_steps = possible_steps[1:]
            selected_additional = random.sample(remaining_steps, min(chain_length, len(remaining_steps)))
            selected_steps.extend(selected_additional)
        
        # 生成每个步骤的攻击
        for step_idx, step in enumerate(selected_steps):
            # 选择攻击子类型
            attack_subtype = random.choice(attack_types[step])
            
            # 生成攻击详情
            attack_id = f"{chain_id}_STEP{step_idx+1}"
            attack = {
                "id": attack_id,
                "chain_id": chain_id,
                "step": step_idx + 1,
                "category": step,
                "subtype": attack_subtype,
                "target": target_id,
                "intensity": random.choice(["low", "medium", "high"]),
                "start_time": time.time() + step_idx * random.randint(10, 30),  # 逐步开始
                "duration": random.randint(20, 90),  # 持续20-90秒
                "status": "pending" if step_idx > 0 else "active"
            }
            
            # 添加到活动攻击
            self.active_attacks[attack_id] = attack
            
            # 更新统计
            self.attack_statistics["total_attacks"] += 1
            if step in self.attack_statistics["by_type"]:
                self.attack_statistics["by_type"][step] += 1
            else:
                self.attack_statistics["by_type"][step] = 1
        
        # 更新复杂攻击链计数
        self.attack_statistics["complex_attack_chains"] += 1
        
        # 记录日志
        self.logger.warning(f"模拟攻击链: {chain_id} 包含{len(selected_steps)}个步骤，目标: {target_id}")
        
        # 记录第一步的详情
        first_attack = self.active_attacks[f"{chain_id}_STEP1"]
        self.logger.warning(f"攻击链第1步: {first_attack['category']}/{first_attack['subtype']} 开始执行")
    
    def _update_active_attacks(self):
        """更新活动攻击状态"""
        current_time = time.time()
        completed_attacks = []
        
        # 检查需要开始的攻击步骤
        pending_attacks = [a for a in self.active_attacks.values() if a["status"] == "pending"]
        for attack in pending_attacks:
            if current_time >= attack["start_time"]:
                attack["status"] = "active"
                self.logger.warning(f"攻击链第{attack['step']}步: {attack['category']}/{attack['subtype']} 开始执行")
        
        # 检查需要结束的攻击
        for attack_id, attack in self.active_attacks.items():
            if attack["status"] == "active" and current_time >= attack["start_time"] + attack["duration"]:
                attack["status"] = "completed"
                attack["end_time"] = current_time
                
                # 检查这是否是攻击链中的一步
                if "chain_id" in attack:
                    chain_id = attack["chain_id"]
                    step = attack["step"]
                    self.logger.info(f"攻击链 {chain_id} 第{step}步已完成: {attack['category']}/{attack['subtype']}")
                    
                    # 检查是否是攻击链的最后一步
                    last_step = True
                    for other_attack in self.active_attacks.values():
                        if "chain_id" in other_attack and other_attack["chain_id"] == chain_id and other_attack["step"] > step:
                            last_step = False
                            break
                    
                    if last_step:
                        self.logger.warning(f"攻击链 {chain_id} 已完整执行完毕")
                else:
                    self.logger.info(f"攻击已完成: {attack['category']}/{attack['subtype']} 针对 {attack['target']}")
                
                completed_attacks.append(attack_id)
        
        # 从活动攻击中移除已完成的攻击
        for attack_id in completed_attacks:
            if attack_id in self.active_attacks:
                attack = self.active_attacks.pop(attack_id)
                
                # 添加到历史记录
                self.attack_history.append(attack)
                if len(self.attack_history) > self.max_history:
                    self.attack_history = self.attack_history[-self.max_history:]

class SecurityAnalytics:
    """安全分析模块"""
    
    def __init__(self, config):
        """初始化安全分析模块"""
        self.logger = logging.getLogger("SecurityAnalytics")
        self.config = config
        self.output_dir = config.get('output_dir', 'output')
        self.report_interval = config.get('report_interval', 300)  # 默认5分钟
        self.save_alerts = config.get('save_alerts', True)
        
        # 确保输出目录存在
        self.output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.output_dir)
        os.makedirs(self.output_path, exist_ok=True)
        
        # 安全事件存储
        self.security_events = []
        self.max_events = 1000  # 最大事件存储数量
        
        # 状态变量
        self.running = False
        self.analytics_thread = None
        
        # 上次报告时间
        self.last_report_time = time.time()
    
    def start(self):
        """启动安全分析"""
        if self.running:
            return
        
        self.running = True
        self.analytics_thread = threading.Thread(target=self._analytics_loop)
        self.analytics_thread.daemon = True
        self.analytics_thread.start()
        
        self.logger.info(f"安全分析模块已启动，报告间隔: {self.report_interval}秒")
    
    def stop(self):
        """停止安全分析"""
        if not self.running:
            return
        
        self.running = False
        
        if self.analytics_thread and self.analytics_thread.is_alive():
            try:
                self.analytics_thread.join(timeout=5.0)
            except Exception as e:
                self.logger.warning(f"等待分析线程结束时出现异常: {str(e)}")
        
        # 生成最终报告
        self._generate_security_report()
        
        self.logger.info("安全分析模块已停止")
    
    def add_security_event(self, event):
        """添加安全事件"""
        try:
            # 添加事件
            self.security_events.append(event)
            
            # 如果超过最大数量，删除最旧的事件
            if len(self.security_events) > self.max_events:
                self.security_events = self.security_events[-self.max_events:]
            
            # 根据是否保存警报决定是否写入文件
            if self.save_alerts:
                self._save_alert_to_file(event)
        except Exception as e:
            self.logger.error(f"添加安全事件时出错: {str(e)}")
    
    def _save_alert_to_file(self, event):
        """将警报保存到文件"""
        try:
            alerts_dir = os.path.join(self.output_path, "alerts")
            os.makedirs(alerts_dir, exist_ok=True)
            
            # 生成时间戳字符串
            timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime(event.get('timestamp', time.time())))
            event_type = event.get('type', 'unknown')
            
            # 创建文件名
            filename = f"{timestamp}_{event_type}.json"
            filepath = os.path.join(alerts_dir, filename)
            
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(event, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"保存警报到文件时出错: {str(e)}")
    
    def _analytics_loop(self):
        """分析循环"""
        while self.running:
            try:
                current_time = time.time()
                
                # 检查是否应该生成报告
                if current_time - self.last_report_time >= self.report_interval:
                    self._generate_security_report()
                    self.last_report_time = current_time
                
                # 等待
                time.sleep(10.0)
            except Exception as e:
                self.logger.error(f"安全分析循环执行异常: {str(e)}")
                time.sleep(30.0)
    
    def _generate_security_report(self):
        """生成安全报告"""
        try:
            # 如果没有安全事件，不生成报告
            if not self.security_events:
                return
            
            # 创建报告目录
            reports_dir = os.path.join(self.output_path, "reports")
            os.makedirs(reports_dir, exist_ok=True)
            
            # 生成报告文件名
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            report_file = os.path.join(reports_dir, f"security_report_{timestamp}.json")
            
            # 分析期间
            start_time = self.security_events[0].get('timestamp', 0)
            end_time = self.security_events[-1].get('timestamp', time.time())
            duration = end_time - start_time
            
            # 统计不同类型的事件
            event_types = {}
            severity_counts = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
            
            for event in self.security_events:
                event_type = event.get('type', 'unknown')
                if event_type in event_types:
                    event_types[event_type] += 1
                else:
                    event_types[event_type] = 1
                
                # 计算严重性
                details = event.get('details', {})
                
                # 根据不同事件类型获取严重性
                severity = None
                if 'severity' in details:
                    severity = details['severity']
                elif 'risk_level' in details:
                    severity = details['risk_level']
                elif 'threat_level' in details:
                    severity = details['threat_level']
                elif 'confidence' in details:
                    conf = details['confidence']
                    if conf >= 0.9:
                        severity = 'critical'
                    elif conf >= 0.7:
                        severity = 'high'
                    elif conf >= 0.5:
                        severity = 'medium'
                    else:
                        severity = 'low'
                
                if severity in severity_counts:
                    severity_counts[severity] += 1
            
            # 计算总事件数
            total_events = len(self.security_events)
            
            # 创建报告内容
            report = {
                'timestamp': time.time(),
                'report_id': f"REPORT_{timestamp}",
                'period': {
                    'start': start_time,
                    'end': end_time,
                    'duration_seconds': duration
                },
                'summary': {
                    'total_events': total_events,
                    'event_rate': total_events / (duration / 3600) if duration > 0 else 0,  # 每小时事件数
                    'event_types': event_types,
                    'severity_distribution': severity_counts,
                    'high_critical_percentage': ((severity_counts['high'] + severity_counts['critical']) / total_events * 100) if total_events > 0 else 0
                },
                'top_events': self._get_top_events(5),
                'recommendations': self._generate_recommendations(event_types, severity_counts)
            }
            
            # 写入报告
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"已生成安全报告: {report_file}")
            
            # 显示简要报告信息
            self.logger.info(f"报告摘要: {total_events}个安全事件，"
                            f"{severity_counts['high'] + severity_counts['critical']}个高危/严重事件")
            
            # 清理旧事件数据
            self._clean_old_events()
        except Exception as e:
            self.logger.error(f"生成安全报告时出错: {str(e)}")
    
    def _get_top_events(self, count):
        """获取最高优先级事件"""
        # 优先考虑高严重性事件
        prioritized_events = []
        
        for event in self.security_events:
            details = event.get('details', {})
            priority_score = 0
            
            # 根据不同类型的严重性字段计算优先级
            if 'severity' in details:
                severity = details['severity']
                if severity == 'critical':
                    priority_score = 4
                elif severity == 'high':
                    priority_score = 3
                elif severity == 'medium':
                    priority_score = 2
                else:
                    priority_score = 1
            elif 'risk_level' in details:
                risk = details['risk_level']
                if risk == 'critical':
                    priority_score = 4
                elif risk == 'high':
                    priority_score = 3
                elif risk == 'medium':
                    priority_score = 2
                else:
                    priority_score = 1
            elif 'threat_level' in details:
                threat = details['threat_level']
                if threat == 'critical':
                    priority_score = 4
                elif threat == 'high':
                    priority_score = 3
                elif threat == 'medium':
                    priority_score = 2
                else:
                    priority_score = 1
            elif 'confidence' in details:
                conf = details['confidence']
                if conf >= 0.9:
                    priority_score = 4
                elif conf >= 0.7:
                    priority_score = 3
                elif conf >= 0.5:
                    priority_score = 2
                else:
                    priority_score = 1
            
            # 保留事件的副本并添加优先级分数
            event_copy = event.copy()
            event_copy['priority_score'] = priority_score
            prioritized_events.append(event_copy)
        
        # 按优先级排序
        prioritized_events.sort(key=lambda x: x['priority_score'], reverse=True)
        
        # 返回前N个事件，并移除临时的优先级分数字段
        top_events = prioritized_events[:count]
        for event in top_events:
            if 'priority_score' in event:
                del event['priority_score']
        
        return top_events
    
    def _generate_recommendations(self, event_types, severity_counts):
        """生成安全建议"""
        recommendations = []
        
        # 根据事件类型生成建议
        if 'network_anomaly' in event_types and event_types['network_anomaly'] > 0:
            recommendations.append({
                'target': 'network',
                'action': '增强网络监控和过滤',
                'description': '建议加强网络流量分析，实施更严格的入站流量过滤，并考虑设置异常流量阈值报警。',
                'priority': 'high' if event_types['network_anomaly'] >= 3 else 'medium'
            })
        
        if 'device_tampering' in event_types and event_types['device_tampering'] > 0:
            recommendations.append({
                'target': 'devices',
                'action': '增强设备完整性验证',
                'description': '定期验证设备固件和配置的完整性，实施设备访问控制，并考虑部署设备行为基线监控系统。',
                'priority': 'high'
            })
        
        if 'malware_detected' in event_types and event_types['malware_detected'] > 0:
            recommendations.append({
                'target': 'malware',
                'action': '部署边缘恶意软件防护',
                'description': '在边缘设备上部署轻量级恶意软件检测工具，定期更新恶意代码特征库，并隔离可疑文件。',
                'priority': 'high' if event_types['malware_detected'] >= 2 else 'medium'
            })
        
        if 'config_vulnerability' in event_types and event_types['config_vulnerability'] > 0:
            recommendations.append({
                'target': 'configuration',
                'action': '实施配置管理和审计',
                'description': '建立配置基线并定期审计，实施自动配置检查机制，防止配置漂移和安全设置被削弱。',
                'priority': 'medium'
            })
        
        # 根据严重性分布生成通用建议
        high_critical = severity_counts['high'] + severity_counts['critical']
        total = sum(severity_counts.values())
        
        if total > 0 and high_critical / total >= 0.3:  # 如果高危/严重事件占比超过30%
            recommendations.append({
                'target': 'general',
                'action': '升级安全态势管理',
                'description': '高危安全事件比例较高，建议升级安全监控策略，增加安全人员审查频率，并考虑部署主动防御系统。',
                'priority': 'high'
            })
        
        # 如果建议列表为空，添加一个一般性建议
        if not recommendations:
            recommendations.append({
                'target': 'general',
                'action': '维持当前安全措施',
                'description': '当前未检测到需要特别注意的安全问题，建议继续执行定期安全评估和更新。',
                'priority': 'low'
            })
        
        return recommendations
    
    def _clean_old_events(self):
        """清理旧事件数据，仅保留最近的事件"""
        # 保留最近的500个事件
        retain_count = min(500, self.max_events // 2)
        if len(self.security_events) > retain_count:
            self.security_events = self.security_events[-retain_count:]
            self.logger.debug(f"清理旧安全事件，保留最近{retain_count}个事件")

def main():
    # 设置环境
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 创建必要目录
    dirs_to_create = [
        "logs", "data", "config", "quarantine", "output"
    ]
    
    for directory in dirs_to_create:
        os.makedirs(directory, exist_ok=True)
    
    # 设置日志
    logger = setup_logging()
    
    logger.info("启动小米AIoT边缘安全防护研究平台 - 安全防护研究专注版")
    logger.info(f"Python 版本: {sys.version.split()[0]}")
    logger.info(f"当前工作目录: {os.getcwd()}")
    
    try:
        # 加载配置
        config = create_config()
        if not config:
            logger.error("无法加载配置，程序退出")
            return
        
        # 初始化安全分析模块
        security_config = config.get('security', {})
        edge_protection_config = config.get('edge_protection', {})
        analytics_config = config.get('analytics', {})
        
        # 创建安全分析模块
        security_analytics = SecurityAnalytics(analytics_config)
        
        # 初始化攻击模拟器
        attack_simulator = AttackSimulator(security_config)
        
        # 初始化边缘计算防护
        edge_protector = EdgeSecurityProtector(edge_protection_config)
        
        # 连接各组件
        def on_protection_activated(protection_data):
            action = protection_data.get('action', '')
            details = protection_data.get('details', {})
            logger.warning(f"边缘计算安全防护措施已激活: {action}, 详情: {details}")
        
        def on_threat_detected(threat_data):
            # 将威胁信息发送到安全分析模块
            security_analytics.add_security_event(threat_data)
        
        edge_protector.register_protection_callback(on_protection_activated)
        edge_protector.register_threat_callback(on_threat_detected)
        
        # 启动各组件
        security_analytics.start()
        attack_simulator.start()
        edge_protector.start()
        
        logger.info("所有安全组件已启动")
        logger.info("小米AIoT边缘安全防护研究平台现在运行中...")
        logger.info("按 Ctrl+C 停止程序")
        
        try:
            # 主循环
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("收到停止信号，正在关闭平台...")
        
        # 停止各组件
        edge_protector.stop()
        attack_simulator.stop()
        security_analytics.stop()
        
        logger.info("小米AIoT边缘安全防护研究平台已安全停止")
    
    except Exception as e:
        logger.error(f"运行平台时出现错误: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main()