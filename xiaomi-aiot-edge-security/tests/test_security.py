#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全模块测试
用于测试攻击检测器、防护引擎和安全规则的功能
"""

import os
import sys
import unittest
import json
import time
import threading
from unittest.mock import MagicMock, patch, Mock
import queue

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.security.attack_detector import AttackDetector
from src.security.protection_engine import ProtectionEngine
from src.security.security_logger import SecurityLogger
from src.security.rules.ddos_rules import DDOSRules
from src.security.rules.mitm_rules import MITMRules
from src.security.rules.firmware_rules import FirmwareRules
from src.security.rules.credential_rules import CredentialRules
from src.utils.config import load_config


class TestAttackDetector(unittest.TestCase):
    """测试攻击检测器"""
    
    def setUp(self):
        """在每个测试之前设置"""
        # 模拟安全日志记录器
        self.mock_logger = MagicMock(spec=SecurityLogger)
        
        # 模拟配置
        self.config = {
            "monitoring_interval": 1.0,
            "alert_threshold": 80,
            "rules": {
                "ddos": {"enabled": True, "threshold": 100},
                "mitm": {"enabled": True, "threshold": 80},
                "firmware": {"enabled": True, "threshold": 70},
                "credential": {"enabled": True, "threshold": 90}
            }
        }
        
        # 创建攻击检测器实例
        self.detector = AttackDetector(self.config, self.mock_logger)
    
    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.detector.config, self.config)
        self.assertEqual(self.detector.monitoring_interval, 1.0)
        self.assertEqual(self.detector.alert_threshold, 80)
        self.assertFalse(self.detector.monitoring_active)
        self.assertIsNone(self.detector.monitoring_thread)
        
        # 检查规则是否已初始化
        self.assertEqual(len(self.detector.rules), 4)
        self.assertIsInstance(self.detector.rules[0], DDOSRules)
        self.assertIsInstance(self.detector.rules[1], MITMRules)
        self.assertIsInstance(self.detector.rules[2], FirmwareRules)
        self.assertIsInstance(self.detector.rules[3], CredentialRules)
    
    def test_start_stop_monitoring(self):
        """测试启动和停止监控"""
        # 模拟线程
        with patch('threading.Thread') as mock_thread:
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance
            
            # 测试启动监控
            result = self.detector.start_monitoring()
            self.assertTrue(result)
            self.assertTrue(self.detector.monitoring_active)
            
            # 线程应该已启动
            mock_thread_instance.start.assert_called_once()
            
            # 测试停止监控
            result = self.detector.stop_monitoring()
            self.assertTrue(result)
            self.assertFalse(self.detector.monitoring_active)
    
    def test_analyze_traffic(self):
        """测试流量分析"""
        # 模拟正常流量数据
        normal_traffic = {
            "source_ip": "192.168.1.100",
            "destination_ip": "192.168.1.1",
            "protocol": "TCP",
            "port": 80,
            "packet_count": 10,
            "byte_count": 1500,
            "timestamp": int(time.time())
        }
        
        # 测试分析正常流量
        threats = self.detector.analyze_traffic(normal_traffic)
        self.assertEqual(len(threats), 0)
        
        # 模拟DDoS攻击流量
        ddos_traffic = {
            "source_ip": "192.168.1.100",
            "destination_ip": "192.168.1.1",
            "protocol": "TCP",
            "port": 80,
            "packet_count": 10000,
            "byte_count": 1500000,
            "timestamp": int(time.time())
        }
        
        # 修改DDoS规则检测阈值
        for rule in self.detector.rules:
            if isinstance(rule, DDOSRules):
                rule.packet_threshold = 1000
                break
        
        # 测试分析DDoS攻击流量
        threats = self.detector.analyze_traffic(ddos_traffic)
        self.assertGreater(len(threats), 0)
        
        # 检查威胁信息
        threat = threats[0]
        self.assertEqual(threat["type"], "ddos")
        self.assertGreaterEqual(threat["confidence"], 0)
        self.assertLessEqual(threat["confidence"], 100)
        
        # 日志记录器应该记录威胁
        self.mock_logger.log_threat.assert_called()
    
    def test_analyze_device_activity(self):
        """测试设备活动分析"""
        # 模拟正常设备活动
        normal_activity = {
            "device_id": "test-device",
            "device_type": "gateway",
            "action": "telemetry_update",
            "data": {"temperature": 25.5},
            "timestamp": int(time.time())
        }
        
        # 测试分析正常设备活动
        threats = self.detector.analyze_device_activity(normal_activity)
        self.assertEqual(len(threats), 0)
        
        # 模拟可疑固件更新
        suspicious_firmware = {
            "device_id": "test-device",
            "device_type": "gateway",
            "action": "firmware_update",
            "data": {
                "version": "1.0.0",
                "url": "http://malicious-site.com/firmware.bin",
                "checksum": "invalid-checksum"
            },
            "timestamp": int(time.time())
        }
        
        # 模拟固件规则检测
        for rule in self.detector.rules:
            if isinstance(rule, FirmwareRules):
                rule.suspicious_domains = ["malicious-site.com"]
                break
        
        # 测试分析可疑固件更新
        threats = self.detector.analyze_device_activity(suspicious_firmware)
        self.assertGreater(len(threats), 0)
        
        # 检查威胁信息
        threat = threats[0]
        self.assertEqual(threat["type"], "firmware")
        self.assertGreaterEqual(threat["confidence"], 0)
        self.assertLessEqual(threat["confidence"], 100)
        
        # 日志记录器应该记录威胁
        self.mock_logger.log_threat.assert_called()


class TestProtectionEngine(unittest.TestCase):
    """测试防护引擎"""
    
    def setUp(self):
        """在每个测试之前设置"""
        # 模拟安全日志记录器
        self.mock_logger = MagicMock(spec=SecurityLogger)
        
        # 模拟配置
        self.config = {
            "auto_protection": True,
            "protection_levels": {
                "low": {"threshold": 30, "actions": ["log"]},
                "medium": {"threshold": 60, "actions": ["log", "alert"]},
                "high": {"threshold": 80, "actions": ["log", "alert", "block"]}
            },
            "notification_endpoints": ["admin@example.com"]
        }
        
        # 创建防护引擎实例
        self.engine = ProtectionEngine(self.config, self.mock_logger)
        
        # 创建一个队列用于测试
        self.alert_queue = queue.Queue()
        self.engine.alert_queue = self.alert_queue
    
    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.engine.config, self.config)
        self.assertTrue(self.engine.auto_protection)
        self.assertFalse(self.engine.processing_active)
        self.assertIsNone(self.engine.processing_thread)
    
    def test_start_stop_processing(self):
        """测试启动和停止处理"""
        # 模拟线程
        with patch('threading.Thread') as mock_thread:
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance
            
            # 测试启动处理
            result = self.engine.start_processing()
            self.assertTrue(result)
            self.assertTrue(self.engine.processing_active)
            
            # 线程应该已启动
            mock_thread_instance.start.assert_called_once()
            
            # 测试停止处理
            result = self.engine.stop_processing()
            self.assertTrue(result)
            self.assertFalse(self.engine.processing_active)
    
    def test_handle_threat(self):
        """测试威胁处理"""
        # 创建低威胁
        low_threat = {
            "id": "threat-1",
            "type": "ddos",
            "confidence": 20,
            "source": "192.168.1.100",
            "target": "192.168.1.1",
            "timestamp": int(time.time()),
            "details": {
                "packet_count": 500,
                "duration": 10
            }
        }
        
        # 测试处理低威胁
        actions = self.engine.handle_threat(low_threat)
        self.assertEqual(actions, ["log"])
        
        # 日志记录器应该记录防护操作
        self.mock_logger.log_protection.assert_called_once()
        
        # 重置模拟
        self.mock_logger.reset_mock()
        
        # 创建高威胁
        high_threat = {
            "id": "threat-2",
            "type": "mitm",
            "confidence": 90,
            "source": "192.168.1.200",
            "target": "192.168.1.1",
            "timestamp": int(time.time()),
            "details": {
                "arp_spoofing": True,
                "duration": 30
            }
        }
        
        # 模拟阻止方法
        self.engine._block_source = MagicMock(return_value=True)
        
        # 测试处理高威胁
        actions = self.engine.handle_threat(high_threat)
        self.assertEqual(set(actions), set(["log", "alert", "block"]))
        
        # 日志记录器应该记录防护操作
        self.mock_logger.log_protection.assert_called_once()
        
        # 阻止方法应该被调用
        self.engine._block_source.assert_called_with(high_threat["source"])
    
    def test_process_alerts(self):
        """测试警报处理"""
        # 启动处理
        with patch('threading.Thread') as mock_thread:
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance
            self.engine.start_processing()
        
        # 添加威胁到队列
        threat = {
            "id": "threat-3",
            "type": "credential",
            "confidence": 85,
            "source": "192.168.1.150",
            "target": "test-device",
            "timestamp": int(time.time()),
            "details": {
                "login_attempts": 10,
                "duration": 5
            }
        }
        self.alert_queue.put(threat)
        
        # 模拟处理方法
        self.engine.handle_threat = MagicMock(return_value=["log", "alert", "block"])
        
        # 调用处理方法
        self.engine._process_alert_queue()
        
        # 处理方法应该被调用
        self.engine.handle_threat.assert_called_with(threat)


class TestSecurityRules(unittest.TestCase):
    """测试安全规则"""
    
    def test_ddos_rules(self):
        """测试DDoS防护规则"""
        # 创建规则实例
        config = {"threshold": 1000, "time_window": 60}
        rules = DDOSRules(config)
        
        # 测试正常流量
        normal_traffic = {
            "source_ip": "192.168.1.100",
            "destination_ip": "192.168.1.1",
            "protocol": "TCP",
            "port": 80,
            "packet_count": 100,
            "byte_count": 15000,
            "timestamp": int(time.time())
        }
        
        result = rules.analyze(normal_traffic)
        self.assertEqual(result["detected"], False)
        self.assertEqual(result["confidence"], 0)
        
        # 测试DDoS攻击流量
        ddos_traffic = {
            "source_ip": "192.168.1.100",
            "destination_ip": "192.168.1.1",
            "protocol": "TCP",
            "port": 80,
            "packet_count": 5000,
            "byte_count": 750000,
            "timestamp": int(time.time())
        }
        
        result = rules.analyze(ddos_traffic)
        self.assertEqual(result["detected"], True)
        self.assertGreater(result["confidence"], 50)
    
    def test_mitm_rules(self):
        """测试中间人攻击防护规则"""
        # 创建规则实例
        config = {"threshold": 80, "arp_cache_expiry": 300}
        rules = MITMRules(config)
        
        # 测试正常ARP数据
        normal_arp = {
            "source_ip": "192.168.1.100",
            "source_mac": "00:11:22:33:44:55",
            "operation": "request",
            "timestamp": int(time.time())
        }
        
        result = rules.analyze(normal_arp)
        self.assertEqual(result["detected"], False)
        self.assertEqual(result["confidence"], 0)
        
        # 测试ARP欺骗攻击
        # 首先缓存正常的MAC地址
        rules.arp_cache["192.168.1.100"] = {
            "mac": "AA:BB:CC:DD:EE:FF",
            "timestamp": int(time.time()) - 10
        }
        
        spoofed_arp = {
            "source_ip": "192.168.1.100",
            "source_mac": "00:11:22:33:44:55",  # 与缓存中的不同
            "operation": "reply",
            "timestamp": int(time.time())
        }
        
        result = rules.analyze(spoofed_arp)
        self.assertEqual(result["detected"], True)
        self.assertGreater(result["confidence"], 50)
    
    def test_firmware_rules(self):
        """测试固件攻击防护规则"""
        # 创建规则实例
        config = {
            "threshold": 70,
            "trusted_domains": ["xiaomi.com", "mi.com"],
            "suspicious_domains": ["malware.com", "hack.xyz"]
        }
        rules = FirmwareRules(config)
        
        # 测试正常固件更新
        normal_update = {
            "device_id": "test-device",
            "device_type": "gateway",
            "action": "firmware_update",
            "data": {
                "version": "1.0.0",
                "url": "https://update.xiaomi.com/firmware.bin",
                "checksum": "valid-checksum"
            },
            "timestamp": int(time.time())
        }
        
        result = rules.analyze(normal_update)
        self.assertEqual(result["detected"], False)
        self.assertEqual(result["confidence"], 0)
        
        # 测试可疑固件更新
        suspicious_update = {
            "device_id": "test-device",
            "device_type": "gateway",
            "action": "firmware_update",
            "data": {
                "version": "1.0.0",
                "url": "http://malware.com/firmware.bin",
                "checksum": "invalid-checksum"
            },
            "timestamp": int(time.time())
        }
        
        result = rules.analyze(suspicious_update)
        self.assertEqual(result["detected"], True)
        self.assertGreater(result["confidence"], 50)
    
    def test_credential_rules(self):
        """测试凭证攻击防护规则"""
        # 创建规则实例
        config = {
            "threshold": 90,
            "max_login_attempts": 5,
            "time_window": 300
        }
        rules = CredentialRules(config)
        
        # 测试正常登录
        normal_login = {
            "device_id": "test-device",
            "device_type": "gateway",
            "action": "login",
            "data": {
                "username": "admin",
                "success": True
            },
            "timestamp": int(time.time())
        }
        
        result = rules.analyze(normal_login)
        self.assertEqual(result["detected"], False)
        self.assertEqual(result["confidence"], 0)
        
        # 测试多次失败登录
        for _ in range(6):
            failed_login = {
                "device_id": "test-device",
                "device_type": "gateway",
                "action": "login",
                "data": {
                    "username": "admin",
                    "success": False
                },
                "timestamp": int(time.time())
            }
            rules.analyze(failed_login)
        
        # 再次尝试登录，应该被检测为凭证攻击
        result = rules.analyze(failed_login)
        self.assertEqual(result["detected"], True)
        self.assertGreater(result["confidence"], 50)


class TestIntegration(unittest.TestCase):
    """安全模块集成测试"""
    
    def setUp(self):
        """在每个测试之前设置"""
        # 创建一个实际的安全日志记录器
        self.logger = SecurityLogger({
            "log_file": "test_security.log",
            "log_level": "INFO",
            "max_size": 10485760,  # 10MB
            "backup_count": 3
        })
        
        # 加载安全配置
        try:
            self.security_config = load_config('../config/security.yaml')
        except Exception:
            # 如果配置文件不存在，使用默认配置
            self.security_config = {
                "detector": {
                    "monitoring_interval": 1.0,
                    "alert_threshold": 80,
                    "rules": {
                        "ddos": {"enabled": True, "threshold": 100},
                        "mitm": {"enabled": True, "threshold": 80},
                        "firmware": {"enabled": True, "threshold": 70},
                        "credential": {"enabled": True, "threshold": 90}
                    }
                },
                "protection": {
                    "auto_protection": True,
                    "protection_levels": {
                        "low": {"threshold": 30, "actions": ["log"]},
                        "medium": {"threshold": 60, "actions": ["log", "alert"]},
                        "high": {"threshold": 80, "actions": ["log", "alert", "block"]}
                    },
                    "notification_endpoints": ["admin@example.com"]
                }
            }
    
    def tearDown(self):
        """在每个测试之后清理"""
        # 移除测试日志文件
        if os.path.exists("test_security.log"):
            os.remove("test_security.log")
    
    @unittest.skip("长时间运行的集成测试")
    def test_security_integration(self):
        """测试安全检测和防护的集成"""
        # 创建攻击检测器
        detector = AttackDetector(self.security_config["detector"], self.logger)
        
        # 创建防护引擎
        engine = ProtectionEngine(self.security_config["protection"], self.logger)
        
        # 将防护引擎连接到检测器
        detector.set_alert_callback(engine.add_threat)
        
        # 启动监控和处理
        detector.start_monitoring()
        engine.start_processing()
        
        try:
            # 模拟DDoS攻击流量
            ddos_traffic = {
                "source_ip": "192.168.1.100",
                "destination_ip": "192.168.1.1",
                "protocol": "TCP",
                "port": 80,
                "packet_count": 10000,
                "byte_count": 1500000,
                "timestamp": int(time.time())
            }
            
            # 分析流量
            threats = detector.analyze_traffic(ddos_traffic)
            self.assertGreater(len(threats), 0)
            
            # 等待处理完成
            time.sleep(1.0)
            
            # 检查日志文件是否存在
            self.assertTrue(os.path.exists("test_security.log"))
            
            # 读取日志并检查
            with open("test_security.log", "r") as f:
                log_content = f.read()
                self.assertIn("THREAT", log_content)
                self.assertIn("PROTECTION", log_content)
        
        finally:
            # 停止监控和处理
            detector.stop_monitoring()
            engine.stop_processing()


if __name__ == '__main__':
    unittest.main()