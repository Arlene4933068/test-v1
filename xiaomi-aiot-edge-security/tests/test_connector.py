#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
平台连接器测试模块
用于测试EdgeX Foundry和ThingsBoard Edge连接器的功能
"""

import os
import sys
import unittest
import json
import time
from unittest.mock import MagicMock, patch, Mock
import requests

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.platform_connector.connector_base import ConnectorBase
from src.platform_connector.edgex_connector import EdgeXConnector
from src.platform_connector.thingsboard_connector import ThingsBoardConnector
from src.utils.config import load_config


class TestConnectorBase(unittest.TestCase):
    """测试连接器基类"""
    
    def setUp(self):
        """在每个测试之前设置"""
        # 创建一个具体的连接器实例用于测试
        class ConcreteConnector(ConnectorBase):
            def connect(self):
                return True
                
            def disconnect(self):
                return True
                
            def register_device(self, device_type, device_id, attributes=None):
                return {"id": "test-id", "success": True}
                
            def update_device(self, device_id, attributes):
                return {"success": True}
                
            def delete_device(self, device_id):
                return {"success": True}
                
            def send_telemetry(self, device_id, telemetry):
                return {"success": True}
        
        self.connector = ConcreteConnector("test-platform", {})
    
    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.connector.platform_name, "test-platform")
        self.assertEqual(self.connector.config, {})
        self.assertFalse(self.connector.connected)
        self.assertEqual(self.connector.devices, {})
    
    def test_device_management(self):
        """测试设备管理功能"""
        # 测试获取设备列表
        self.assertEqual(len(self.connector.get_devices()), 0)
        
        # 测试添加设备
        self.connector.add_device("test-device-1", {"type": "gateway"})
        self.assertEqual(len(self.connector.get_devices()), 1)
        self.assertIn("test-device-1", self.connector.devices)
        
        # 测试获取特定设备
        device = self.connector.get_device("test-device-1")
        self.assertEqual(device, {"type": "gateway"})
        
        # 测试获取不存在的设备
        self.assertIsNone(self.connector.get_device("non-existent"))
        
        # 测试移除设备
        self.connector.remove_device("test-device-1")
        self.assertEqual(len(self.connector.get_devices()), 0)
        self.assertNotIn("test-device-1", self.connector.devices)


class TestEdgeXConnector(unittest.TestCase):
    """测试EdgeX Foundry连接器"""
    
    def setUp(self):
        """在每个测试之前设置"""
        # 加载配置
        try:
            self.config = load_config('../config/edgex.yaml')
        except Exception:
            # 如果配置文件不存在，使用默认配置
            self.config = {
                "url": "http://localhost:48080",
                "username": "admin",
                "password": "admin"
            }
        
        # 模拟requests模块
        self.patcher = patch('src.platform_connector.edgex_connector.requests')
        self.mock_requests = self.patcher.start()
        
        # 设置模拟响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "test-id"}
        self.mock_requests.get.return_value = mock_response
        self.mock_requests.post.return_value = mock_response
        self.mock_requests.put.return_value = mock_response
        self.mock_requests.delete.return_value = mock_response
        
        # 创建连接器实例
        self.connector = EdgeXConnector(self.config)
    
    def tearDown(self):
        """在每个测试之后清理"""
        self.patcher.stop()
    
    def test_connect(self):
        """测试连接功能"""
        # 设置模拟响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"version": "1.0.0"}
        self.mock_requests.get.return_value = mock_response
        
        # 测试连接
        result = self.connector.connect()
        self.assertTrue(result)
        self.assertTrue(self.connector.connected)
        
        # 验证请求
        self.mock_requests.get.assert_called_with(
            f"{self.config['url']}/api/v1/ping",
            headers={"Content-Type": "application/json"},
            auth=(self.config.get('username'), self.config.get('password')),
            timeout=10
        )
    
    def test_connect_failure(self):
        """测试连接失败的情况"""
        # 设置模拟响应
        mock_response = Mock()
        mock_response.status_code = 401
        self.mock_requests.get.return_value = mock_response
        self.mock_requests.get.side_effect = requests.RequestException("Connection error")
        
        # 测试连接
        result = self.connector.connect()
        self.assertFalse(result)
        self.assertFalse(self.connector.connected)
    
    def test_register_device(self):
        """测试设备注册功能"""
        # 先连接
        self.connector.connected = True
        
        # 测试注册设备
        result = self.connector.register_device("gateway", "test-gateway", {"model": "XM-GW1"})
        
        # 验证结果
        self.assertEqual(result, {"id": "test-id"})
        
        # 验证请求
        self.mock_requests.post.assert_called()
        
        # 设备应该被添加到内部列表
        self.assertIn("test-gateway", self.connector.devices)
    
    def test_send_telemetry(self):
        """测试发送遥测数据"""
        # 先连接并注册设备
        self.connector.connected = True
        self.connector.add_device("test-gateway", {"id": "test-id", "type": "gateway"})
        
        # 测试发送遥测数据
        telemetry = {"temperature": 25.5, "humidity": 60}
        result = self.connector.send_telemetry("test-gateway", telemetry)
        
        # 验证结果
        self.assertEqual(result, {"id": "test-id"})
        
        # 验证请求
        self.mock_requests.post.assert_called()


class TestThingsBoardConnector(unittest.TestCase):
    """测试ThingsBoard Edge连接器"""
    
    def setUp(self):
        """在每个测试之前设置"""
        # 加载配置
        try:
            self.config = load_config('../config/thingsboard.yaml')
        except Exception:
            # 如果配置文件不存在，使用默认配置
            self.config = {
                "url": "http://localhost:8080",
                "username": "tenant@thingsboard.org",
                "password": "tenant"
            }
        
        # 模拟requests模块
        self.patcher = patch('src.platform_connector.thingsboard_connector.requests')
        self.mock_requests = self.patcher.start()
        
        # 设置模拟响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"token": "test-token"}
        self.mock_requests.post.return_value = mock_response
        
        # 创建连接器实例
        self.connector = ThingsBoardConnector(self.config)
    
    def tearDown(self):
        """在每个测试之后清理"""
        self.patcher.stop()
    
    def test_connect(self):
        """测试连接功能"""
        # 设置模拟响应
        mock_auth_response = Mock()
        mock_auth_response.status_code = 200
        mock_auth_response.json.return_value = {"token": "test-token", "refreshToken": "test-refresh"}
        
        self.mock_requests.post.return_value = mock_auth_response
        
        # 测试连接
        result = self.connector.connect()
        self.assertTrue(result)
        self.assertTrue(self.connector.connected)
        self.assertEqual(self.connector.auth_token, "test-token")
        
        # 验证请求
        self.mock_requests.post.assert_called_with(
            f"{self.config['url']}/api/auth/login",
            json={
                "username": self.config['username'],
                "password": self.config['password']
            },
            headers={"Content-Type": "application/json"},
            timeout=10
        )
    
    def test_connect_failure(self):
        """测试连接失败的情况"""
        # 设置模拟响应
        self.mock_requests.post.side_effect = requests.RequestException("Connection error")
        
        # 测试连接
        result = self.connector.connect()
        self.assertFalse(result)
        self.assertFalse(self.connector.connected)
        self.assertIsNone(self.connector.auth_token)
    
    def test_register_device(self):
        """测试设备注册功能"""
        # 先连接
        self.connector.connected = True
        self.connector.auth_token = "test-token"
        
        # 设置模拟响应
        mock_device_response = Mock()
        mock_device_response.status_code = 200
        mock_device_response.json.return_value = {
            "id": {"id": "test-device-id"},
            "name": "test-gateway",
            "type": "gateway"
        }
        self.mock_requests.post.return_value = mock_device_response
        
        # 测试注册设备
        result = self.connector.register_device("gateway", "test-gateway", {"model": "XM-GW1"})
        
        # 验证结果
        self.assertEqual(result["id"]["id"], "test-device-id")
        self.assertEqual(result["name"], "test-gateway")
        
        # 验证请求
        self.mock_requests.post.assert_called()
        
        # 设备应该被添加到内部列表
        self.assertIn("test-gateway", self.connector.devices)
    
    def test_send_telemetry(self):
        """测试发送遥测数据"""
        # 先连接并注册设备
        self.connector.connected = True
        self.connector.auth_token = "test-token"
        self.connector.add_device("test-gateway", {"id": {"id": "test-device-id"}, "type": "gateway"})
        
        # 设置模拟响应
        mock_telemetry_response = Mock()
        mock_telemetry_response.status_code = 200
        self.mock_requests.post.return_value = mock_telemetry_response
        
        # 测试发送遥测数据
        telemetry = {"temperature": 25.5, "humidity": 60}
        result = self.connector.send_telemetry("test-gateway", telemetry)
        
        # 验证结果
        self.assertTrue(result["success"])
        
        # 验证请求
        self.mock_requests.post.assert_called_with(
            f"{self.config['url']}/api/plugins/telemetry/DEVICE/test-device-id/telemetry",
            json=telemetry,
            headers={
                "Content-Type": "application/json",
                "X-Authorization": f"Bearer {self.connector.auth_token}"
            },
            timeout=10
        )


class TestIntegration(unittest.TestCase):
    """平台连接器集成测试"""
    
    @unittest.skip("需要实际的EdgeX Foundry和ThingsBoard实例")
    def test_platform_integration(self):
        """测试与实际平台的集成"""
        # 加载EdgeX配置
        edgex_config = load_config('../config/edgex.yaml')
        
        # 创建EdgeX连接器
        edgex = EdgeXConnector(edgex_config)
        
        # 连接到EdgeX
        success = edgex.connect()
        self.assertTrue(success)
        
        # 注册测试设备
        device_id = f"test-device-{int(time.time())}"
        result = edgex.register_device("gateway", device_id, {"model": "XM-GW1"})
        self.assertIn("id", result)
        
        # 发送测试遥测数据
        telemetry = {"temperature": 25.5, "humidity": 60, "timestamp": int(time.time() * 1000)}
        result = edgex.send_telemetry(device_id, telemetry)
        self.assertTrue("id" in result or "success" in result)
        
        # 清理：删除测试设备
        result = edgex.delete_device(device_id)
        self.assertTrue(result.get("success", False))
        
        # 断开连接
        edgex.disconnect()
        self.assertFalse(edgex.connected)
        
        # 加载ThingsBoard配置
        tb_config = load_config('../config/thingsboard.yaml')
        
        # 创建ThingsBoard连接器
        tb = ThingsBoardConnector(tb_config)
        
        # 连接到ThingsBoard
        success = tb.connect()
        self.assertTrue(success)
        
        # 注册测试设备
        device_id = f"test-device-{int(time.time())}"
        result = tb.register_device("gateway", device_id, {"model": "XM-GW1"})
        self.assertIn("id", result)
        
        # 发送测试遥测数据
        telemetry = {"temperature": 25.5, "humidity": 60, "timestamp": int(time.time() * 1000)}
        result = tb.send_telemetry(device_id, telemetry)
        self.assertTrue(result.get("success", False))
        
        # 清理：删除测试设备
        result = tb.delete_device(device_id)
        self.assertTrue(result.get("success", False))
        
        # 断开连接
        tb.disconnect()
        self.assertFalse(tb.connected)


if __name__ == '__main__':
    unittest.main()