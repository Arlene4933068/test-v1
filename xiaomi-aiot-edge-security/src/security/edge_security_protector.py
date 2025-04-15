#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
边缘计算安全防护模块
提供边缘计算环境中的安全防护功能
"""

import os
import sys
import time
import json
import logging
import threading
import hashlib
import random
import socket
try:
    import ipaddress
except ImportError:
    ipaddress = None
from typing import Dict, List, Any, Tuple, Set, Optional
import queue

class EdgeSecurityProtector:
    """边缘计算安全防护器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化边缘计算安全防护器
        
        Args:
            config: 防护配置
        """
        self.logger = logging.getLogger(__name__)
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
        
        # 防火墙规则
        self.firewall_rules = self._load_firewall_rules()
        
        # 入侵检测系统
        self.ids_signatures = self._load_ids_signatures()
        
        # 设备白名单
        self.device_whitelist = set(config.get('device_whitelist', []))
        
        # 被阻止的IP集合
        self.blocked_ips = set()
        
        # 数据保护密钥
        self.encryption_key = self._generate_encryption_key()
        
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
    
    def register_threat_callback(self, callback):
        """
        注册威胁检测回调函数
        
        Args:
            callback: 当检测到威胁时调用的回调函数
        """
        self.on_threat_detected = callback
    
    def register_protection_callback(self, callback):
        """
        注册保护激活回调函数
        
        Args:
            callback: 当保护措施被激活时调用的回调函数
        """
        self.on_protection_activated = callback
    
    def add_protection_event(self, event_type: str, details: Dict[str, Any]):
        """
        添加保护事件到队列
        
        Args:
            event_type: 事件类型
            details: 事件详情
        """
        try:
            event = {
                'type': event_type,
                'timestamp': time.time(),
                'details': details
            }
            self.event_queue.put(event)
        except Exception as e:
            self.logger.error(f"添加保护事件时出错: {str(e)}")
    
    def _protection_loop(self):
        """防护主循环"""
        while self.running:
            try:
                # 处理保护事件
                self._process_protection_events()
                
                # 检查网络流量异常
                self._monitor_network_traffic()
                
                # 验证设备完整性
                self._verify_device_integrity()
                
                # 扫描恶意代码
                self._scan_for_malware()
                
                # 检查配置安全性
                self._check_configuration_security()
                
                # 等待一段时间
                time.sleep(2.0)
            except Exception as e:
                self.logger.error(f"防护循环执行异常: {str(e)}")
                time.sleep(5.0)
    
    def _process_protection_events(self):
        """处理保护事件队列中的事件"""
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
            
            # 处理事件
            for event in events:
                self._handle_protection_event(event)
        except Exception as e:
            self.logger.error(f"处理保护事件时出错: {str(e)}")
    
    def _handle_protection_event(self, event: Dict[str, Any]):
        """
        处理单个保护事件
        
        Args:
            event: 保护事件
        """
        try:
            event_type = event.get('type', '')
            details = event.get('details', {})
            
            self.logger.info(f"处理保护事件: {event_type}, 详情: {details}")
            
            # 根据事件类型采取不同的防护措施
            if event_type == 'network_anomaly':
                self._handle_network_anomaly(details)
            elif event_type == 'malware_detected':
                self._handle_malware_detection(details)
            elif event_type == 'device_tampering':
                self._handle_device_tampering(details)
            elif event_type == 'config_vulnerability':
                self._handle_config_vulnerability(details)
            elif event_type == 'data_breach':
                self._handle_data_breach(details)
            else:
                self.logger.warning(f"未知的保护事件类型: {event_type}")
            
            # 调用威胁检测回调（如果已注册）
            if self.on_threat_detected:
                self.on_threat_detected(event)
        except Exception as e:
            self.logger.error(f"处理保护事件时出错: {str(e)}")
    
    def _handle_network_anomaly(self, details: Dict[str, Any]):
        """
        处理网络异常
        
        Args:
            details: 异常详情
        """
        try:
            anomaly_type = details.get('anomaly_type', '')
            source_ip = details.get('source_ip', '')
            confidence = details.get('confidence', 0.0)
            
            # 根据异常类型和置信度采取措施
            if confidence >= 0.8:
                # 高置信度异常，立即阻止IP
                if source_ip and self._is_valid_ip(source_ip):
                    self._block_ip(source_ip)
                    
                    # 记录并通知
                    self.logger.warning(f"已阻止可疑IP: {source_ip}, 异常类型: {anomaly_type}, 置信度: {confidence}")
                    
                    # 触发保护回调
                    self._trigger_protection_callback('ip_blocked', {
                        'ip': source_ip,
                        'reason': anomaly_type,
                        'confidence': confidence,
                        'duration': 'permanent'  # 永久阻止
                    })
            elif confidence >= 0.6:
                # 中等置信度，临时阻止
                if source_ip and self._is_valid_ip(source_ip):
                    self._block_ip(source_ip, temporary=True)
                    
                    # 记录并通知
                    self.logger.info(f"已临时阻止可疑IP: {source_ip}, 异常类型: {anomaly_type}, 置信度: {confidence}")
                    
                    # 触发保护回调
                    self._trigger_protection_callback('ip_blocked', {
                        'ip': source_ip,
                        'reason': anomaly_type,
                        'confidence': confidence,
                        'duration': 'temporary'  # 临时阻止
                    })
            else:
                # 低置信度，只记录不采取措施
                self.logger.info(f"监测到低置信度网络异常，IP: {source_ip}, 类型: {anomaly_type}, 置信度: {confidence}")
        except Exception as e:
            self.logger.error(f"处理网络异常时出错: {str(e)}")
    
    def _handle_malware_detection(self, details: Dict[str, Any]):
        """
        处理恶意软件检测
        
        Args:
            details: 检测详情
        """
        try:
            malware_type = details.get('malware_type', '')
            file_path = details.get('file_path', '')
            threat_level = details.get('threat_level', 'medium')
            
            # 根据威胁级别采取措施
            if threat_level == 'critical' or threat_level == 'high':
                # 高危威胁，尝试隔离文件
                if file_path and os.path.exists(file_path):
                    self._quarantine_file(file_path)
                    
                    # 记录并通知
                    self.logger.warning(f"已隔离恶意文件: {file_path}, 类型: {malware_type}, 威胁级别: {threat_level}")
                    
                    # 触发保护回调
                    self._trigger_protection_callback('file_quarantined', {
                        'file_path': file_path,
                        'malware_type': malware_type,
                        'threat_level': threat_level
                    })
            else:
                # 中低危威胁，记录并标记
                self.logger.info(f"检测到可能的恶意文件: {file_path}, 类型: {malware_type}, 威胁级别: {threat_level}")
                
                # 触发保护回调
                self._trigger_protection_callback('malware_flagged', {
                    'file_path': file_path,
                    'malware_type': malware_type,
                    'threat_level': threat_level
                })
        except Exception as e:
            self.logger.error(f"处理恶意软件检测时出错: {str(e)}")
    
    def _handle_device_tampering(self, details: Dict[str, Any]):
        """
        处理设备篡改
        
        Args:
            details: 篡改详情
        """
        try:
            device_id = details.get('device_id', '')
            tampering_type = details.get('tampering_type', '')
            severity = details.get('severity', 'medium')
            
            # 根据严重程度采取措施
            if severity == 'critical' or severity == 'high':
                # 高严重度，断开设备连接
                self._disconnect_compromised_device(device_id)
                
                # 记录并通知
                self.logger.warning(f"已断开被篡改设备: {device_id}, 篡改类型: {tampering_type}, 严重程度: {severity}")
                
                # 触发保护回调
                self._trigger_protection_callback('device_disconnected', {
                    'device_id': device_id,
                    'tampering_type': tampering_type,
                    'severity': severity
                })
            else:
                # 中低严重度，增加监控
                self.logger.info(f"检测到设备篡改迹象: {device_id}, 类型: {tampering_type}, 严重程度: {severity}")
                
                # 触发保护回调
                self._trigger_protection_callback('device_monitoring_increased', {
                    'device_id': device_id,
                    'tampering_type': tampering_type,
                    'severity': severity
                })
        except Exception as e:
            self.logger.error(f"处理设备篡改时出错: {str(e)}")
    
    def _handle_config_vulnerability(self, details: Dict[str, Any]):
        """
        处理配置漏洞
        
        Args:
            details: 漏洞详情
        """
        try:
            config_file = details.get('config_file', '')
            vulnerability_type = details.get('vulnerability_type', '')
            risk_level = details.get('risk_level', 'medium')
            
            # 根据风险级别采取措施
            if risk_level == 'critical' or risk_level == 'high':
                # 高风险，尝试自动修复配置
                fixed = self._fix_config_vulnerability(config_file, vulnerability_type)
                
                if fixed:
                    # 记录修复成功
                    self.logger.info(f"已修复配置漏洞: {config_file}, 类型: {vulnerability_type}")
                    
                    # 触发保护回调
                    self._trigger_protection_callback('config_fixed', {
                        'config_file': config_file,
                        'vulnerability_type': vulnerability_type,
                        'risk_level': risk_level
                    })
                else:
                    # 记录修复失败
                    self.logger.warning(f"无法自动修复配置漏洞: {config_file}, 类型: {vulnerability_type}")
                    
                    # 触发保护回调
                    self._trigger_protection_callback('config_fix_failed', {
                        'config_file': config_file,
                        'vulnerability_type': vulnerability_type,
                        'risk_level': risk_level
                    })
            else:
                # 中低风险，记录并提醒
                self.logger.info(f"检测到配置漏洞: {config_file}, 类型: {vulnerability_type}, 风险级别: {risk_level}")
                
                # 触发保护回调
                self._trigger_protection_callback('config_vulnerability_flagged', {
                    'config_file': config_file,
                    'vulnerability_type': vulnerability_type,
                    'risk_level': risk_level
                })
        except Exception as e:
            self.logger.error(f"处理配置漏洞时出错: {str(e)}")
    
    def _handle_data_breach(self, details: Dict[str, Any]):
        """
        处理数据泄露
        
        Args:
            details: 泄露详情
        """
        try:
            data_type = details.get('data_type', '')
            source = details.get('source', '')
            destination = details.get('destination', '')
            sensitivity = details.get('sensitivity', 'medium')
            
            # 根据数据敏感度采取措施
            if sensitivity == 'critical' or sensitivity == 'high':
                # 高敏感数据，立即阻止传输
                blocked = self._block_data_transmission(source, destination)
                
                if blocked:
                    # 记录阻止成功
                    self.logger.warning(f"已阻止敏感数据传输: {data_type}, 来源: {source}, 目的地: {destination}")
                    
                    # 触发保护回调
                    self._trigger_protection_callback('data_transmission_blocked', {
                        'data_type': data_type,
                        'source': source,
                        'destination': destination,
                        'sensitivity': sensitivity
                    })
                else:
                    # 记录阻止失败
                    self.logger.error(f"无法阻止敏感数据传输: {data_type}, 来源: {source}, 目的地: {destination}")
            else:
                # 中低敏感数据，记录并监控
                self.logger.info(f"检测到数据传输: {data_type}, 来源: {source}, 目的地: {destination}, 敏感度: {sensitivity}")
                
                # 触发保护回调
                self._trigger_protection_callback('data_transmission_monitored', {
                    'data_type': data_type,
                    'source': source,
                    'destination': destination,
                    'sensitivity': sensitivity
                })
        except Exception as e:
            self.logger.error(f"处理数据泄露时出错: {str(e)}")
    
    def _trigger_protection_callback(self, action: str, details: Dict[str, Any]):
        """
        触发保护回调函数
        
        Args:
            action: 保护措施动作
            details: 详情
        """
        if self.on_protection_activated:
            try:
                callback_data = {
                    'action': action,
                    'timestamp': time.time(),
                    'details': details
                }
                self.on_protection_activated(callback_data)
            except Exception as e:
                self.logger.error(f"调用保护回调函数时出错: {str(e)}")
    
    def _monitor_network_traffic(self):
        """监控网络流量异常"""
        # 此处应实现真实的网络流量监控逻辑
        # 为了演示，我们使用模拟数据
        
        if random.random() < 0.05:  # 5%的概率检测到异常
            # 生成模拟异常
            anomaly_types = ['port_scan', 'syn_flood', 'dns_tunneling', 'unusual_protocol']
            anomaly = {
                'anomaly_type': random.choice(anomaly_types),
                'source_ip': f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}",
                'destination_ip': f"10.0.{random.randint(1, 254)}.{random.randint(1, 254)}",
                'confidence': round(random.uniform(0.5, 0.95), 2),
                'packet_count': random.randint(100, 10000)
            }
            
            # 添加到保护事件队列
            self.add_protection_event('network_anomaly', anomaly)
    
    def _verify_device_integrity(self):
        """验证设备完整性"""
        # 此处应实现真实的设备完整性验证逻辑
        # 为了演示，我们使用模拟数据
        
        if random.random() < 0.03:  # 3%的概率检测到篡改
            # 生成模拟篡改事件
            tampering_types = ['firmware_modified', 'configuration_changed', 'unauthorized_access', 'hardware_tampering']
            device_event = {
                'device_id': f"xiaomi_device_{random.randint(1, 10)}",
                'tampering_type': random.choice(tampering_types),
                'severity': random.choice(['low', 'medium', 'high', 'critical']),
                'detected_at': time.time()
            }
            
            # 添加到保护事件队列
            self.add_protection_event('device_tampering', device_event)
    
    def _scan_for_malware(self):
        """扫描恶意代码"""
        # 此处应实现真实的恶意软件扫描逻辑
        # 为了演示，我们使用模拟数据
        
        if random.random() < 0.02:  # 2%的概率检测到恶意软件
            # 生成模拟恶意软件事件
            malware_types = ['trojan', 'ransomware', 'rootkit', 'botnet_client', 'backdoor']
            malware_event = {
                'malware_type': random.choice(malware_types),
                'file_path': f"/tmp/suspect_file_{random.randint(1000, 9999)}.bin",
                'threat_level': random.choice(['low', 'medium', 'high', 'critical']),
                'signature_matched': f"SIG_{random.randint(10000, 99999)}"
            }
            
            # 添加到保护事件队列
            self.add_protection_event('malware_detected', malware_event)
    
    def _check_configuration_security(self):
        """检查配置安全性"""
        # 此处应实现真实的配置安全检查逻辑
        # 为了演示，我们使用模拟数据
        
        if random.random() < 0.04:  # 4%的概率检测到配置漏洞
            # 生成模拟配置漏洞事件
            vulnerability_types = ['weak_password', 'open_port', 'insecure_protocol', 'default_credential', 'missing_encryption']
            config_event = {
                'config_file': f"/etc/device/config_{random.randint(1, 20)}.yaml",
                'vulnerability_type': random.choice(vulnerability_types),
                'risk_level': random.choice(['low', 'medium', 'high', 'critical']),
                'recommended_fix': "Update configuration with secure settings"
            }
            
            # 添加到保护事件队列
            self.add_protection_event('config_vulnerability', config_event)
    
    def _block_ip(self, ip: str, temporary: bool = False):
        """
        阻止IP地址
        
        Args:
            ip: 要阻止的IP地址
            temporary: 是否为临时阻止
        """
        # 此处应实现真实的IP阻止逻辑（如操作iptables或防火墙规则）
        # 为了演示，我们只是记录阻止操作
        
        if ip not in self.blocked_ips:
            self.blocked_ips.add(ip)
            duration = "临时" if temporary else "永久"
            self.logger.info(f"{duration}阻止IP: {ip}")
            
            # 如果是临时阻止，设置自动解除的定时器
            if temporary:
                unblock_thread = threading.Timer(
                    interval=300.0,  # 5分钟后解除
                    function=self._unblock_ip,
                    args=[ip]
                )
                unblock_thread.daemon = True
                unblock_thread.start()
    
    def _unblock_ip(self, ip: str):
        """
        解除IP地址阻止
        
        Args:
            ip: 要解除阻止的IP地址
        """
        # 此处应实现真实的解除阻止逻辑
        # 为了演示，我们只是记录解除操作
        
        if ip in self.blocked_ips:
            self.blocked_ips.remove(ip)
            self.logger.info(f"已解除IP阻止: {ip}")
    
    def _quarantine_file(self, file_path: str) -> bool:
        """
        隔离可疑文件
        
        Args:
            file_path: 文件路径
        
        Returns:
            bool: 操作成功返回True，否则返回False
        """
        # 此处应实现真实的文件隔离逻辑
        # 为了演示，我们只是记录操作
        
        try:
            quarantine_dir = os.path.join(os.getcwd(), "quarantine")
            os.makedirs(quarantine_dir, exist_ok=True)
            
            file_name = os.path.basename(file_path)
            quarantine_path = os.path.join(quarantine_dir, file_name)
            
            self.logger.info(f"已将文件 {file_path} 隔离到 {quarantine_path}")
            return True
        except Exception as e:
            self.logger.error(f"隔离文件时出错: {str(e)}")
            return False
    
    def _disconnect_compromised_device(self, device_id: str) -> bool:
        """
        断开被入侵的设备连接
        
        Args:
            device_id: 设备ID
        
        Returns:
            bool: 操作成功返回True，否则返回False
        """
        # 此处应实现真实的设备断开逻辑
        # 为了演示，我们只是记录操作
        
        try:
            self.logger.info(f"已断开被入侵的设备: {device_id}")
            return True
        except Exception as e:
            self.logger.error(f"断开设备连接时出错: {str(e)}")
            return False
    
    def _fix_config_vulnerability(self, config_file: str, vulnerability_type: str) -> bool:
        """
        修复配置漏洞
        
        Args:
            config_file: 配置文件路径
            vulnerability_type: 漏洞类型
        
        Returns:
            bool: 操作成功返回True，否则返回False
        """
        # 此处应实现真实的配置修复逻辑
        # 为了演示，我们只是记录操作
        
        try:
            self.logger.info(f"已修复配置文件 {config_file} 中的 {vulnerability_type} 漏洞")
            return True
        except Exception as e:
            self.logger.error(f"修复配置漏洞时出错: {str(e)}")
            return False
    
    def _block_data_transmission(self, source: str, destination: str) -> bool:
        """
        阻止数据传输
        
        Args:
            source: 来源
            destination: 目的地
        
        Returns:
            bool: 操作成功返回True，否则返回False
        """
        # 此处应实现真实的数据传输阻止逻辑
        # 为了演示，我们只是记录操作
        
        try:
            self.logger.info(f"已阻止从 {source} 到 {destination} 的数据传输")
            return True
        except Exception as e:
            self.logger.error(f"阻止数据传输时出错: {str(e)}")
            return False
    
    def _is_valid_ip(self, ip: str) -> bool:
        """
        检查是否为有效的IP地址
        
        Args:
            ip: IP地址字符串
        
        Returns:
            bool: 有效返回True，否则返回False
        """
        if ipaddress is None:
            # 简单检查
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            for part in parts:
                try:
                    num = int(part)
                    if num < 0 or num > 255:
                        return False
                except:
                    return False
            return True
        else:
            try:
                ipaddress.ip_address(ip)
                return True
            except ValueError:
                return False
    
    def _load_firewall_rules(self) -> List[Dict[str, Any]]:
        """
        加载防火墙规则
        
        Returns:
            List[Dict[str, Any]]: 防火墙规则列表
        """
        # 此处应从配置文件或数据库加载规则
        # 为了演示，我们使用一些默认规则
        
        return [
            {
                'rule_id': 'fw_rule_001',
                'protocol': 'tcp',
                'port': 22,
                'action': 'allow',
                'source': 'any',
                'description': 'Allow SSH access'
            },
            {
                'rule_id': 'fw_rule_002',
                'protocol': 'tcp',
                'port': 80,
                'action': 'allow',
                'source': 'any',
                'description': 'Allow HTTP access'
            },
            {
                'rule_id': 'fw_rule_003',
                'protocol': 'tcp',
                'port': 443,
                'action': 'allow',
                'source': 'any',
                'description': 'Allow HTTPS access'
            },
            {
                'rule_id': 'fw_rule_004',
                'protocol': 'icmp',
                'action': 'allow',
                'source': 'any',
                'description': 'Allow ICMP (ping)'
            },
            {
                'rule_id': 'fw_rule_999',
                'action': 'deny',
                'source': 'any',
                'description': 'Default deny rule'
            }
        ]
    
    def _load_ids_signatures(self) -> List[Dict[str, Any]]:
        """
        加载入侵检测系统签名
        
        Returns:
            List[Dict[str, Any]]: 签名列表
        """
        # 此处应从规则库加载IDS签名
        # 为了演示，我们使用一些常见签名
        
        return [
            {
                'signature_id': 'ids_001',
                'pattern': 'SQL injection attempt',
                'severity': 'high',
                'description': 'SQL injection attempt detected'
            },
            {
                'signature_id': 'ids_002',
                'pattern': 'XSS attempt',
                'severity': 'medium',
                'description': 'Cross-site scripting attempt detected'
            },
            {
                'signature_id': 'ids_003',
                'pattern': 'Directory traversal',
                'severity': 'high',
                'description': 'Directory traversal attempt detected'
            },
            {
                'signature_id': 'ids_004',
                'pattern': 'Command injection',
                'severity': 'critical',
                'description': 'Command injection attempt detected'
            },
            {
                'signature_id': 'ids_005',
                'pattern': 'Brute force attack',
                'severity': 'medium',
                'description': 'Brute force authentication attempt detected'
            }
        ]
    
    def _generate_encryption_key(self) -> bytes:
        """
        生成加密密钥
        
        Returns:
            bytes: 加密密钥
        """
        # 从配置中获取密钥，如果没有则生成新密钥
        key_str = self.config.get('encryption_key', None)
        
        if key_str:
            # 使用提供的密钥
            try:
                return key_str.encode('utf-8')
            except Exception:
                self.logger.warning("配置中的加密密钥无效，将生成新密钥")
        
        # 生成新密钥
        try:
            return os.urandom(32)  # 256位密钥
        except Exception as e:
            self.logger.error(f"生成加密密钥时出错: {str(e)}")
            # 回退到简单但安全性较低的密钥生成方法
            random_str = str(time.time()) + str(random.randint(10000, 99999))
            return hashlib.sha256(random_str.encode('utf-8')).digest()
    
    def encrypt_data(self, data: bytes) -> bytes:
        """
        加密数据
        
        Args:
            data: 要加密的数据
        
        Returns:
            bytes: 加密后的数据
        """
        # 此处应实现真实的加密逻辑
        # 为了演示，我们使用简单的XOR加密
        try:
            key_length = len(self.encryption_key)
            encrypted = bytearray(len(data))
            
            for i in range(len(data)):
                encrypted[i] = data[i] ^ self.encryption_key[i % key_length]
            
            return bytes(encrypted)
        except Exception as e:
            self.logger.error(f"加密数据时出错: {str(e)}")
            return data  # 失败时返回原始数据
    
    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """
        解密数据
        
        Args:
            encrypted_data: 加密的数据
        
        Returns:
            bytes: 解密后的数据
        """
        # XOR加密是对称的，解密过程与加密相同
        return self.encrypt_data(encrypted_data)
    
    def get_protection_status(self) -> Dict[str, Any]:
        """
        获取防护状态信息
        
        Returns:
            Dict[str, Any]: 防护状态
        """
        return {
            'running': self.running,
            'protection_level': self.protection_level,
            'firewall_enabled': self.enable_firewall,
            'ids_enabled': self.enable_ids,
            'data_protection_enabled': self.enable_data_protection,
            'blocked_ips_count': len(self.blocked_ips),
            'device_whitelist_count': len(self.device_whitelist),
            'last_update_time': time.time()
        }
