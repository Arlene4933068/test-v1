#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟器测试模块
用于测试各种边缘设备模拟器的功能
"""

import os
import sys
import unittest
import json
import time
from unittest.mock import MagicMock, patch
import threading

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.device_simulator.simulator_base import DeviceSimulator
from src.device_simulator.gateway import GatewaySimulator
from src.device_simulator.router import RouterSimulator
from src.device_simulator.speaker import SpeakerSimulator
from src.device_simulator.camera import CameraSimulator
from src.utils.config import load_config

class MockMQTTClient:
    """MQTT客户端模拟类"""
    
    def __init__(self):
        self.connected = False
        self.subscriptions = {}
        self.published_messages = []
        
    def connect(self, host, port, keepalive=60):
        self.connected = True
        return 0
        
    def disconnect(self):
        self.connected = False
        return 0
        
    def loop_start(self):
        pass
        
    def loop_stop(self):
        pass
        
    def subscribe(self, topic):
        self.subscriptions[topic] = True
        return [0, 0]
        
    def publish(self, topic, payload, qos=0):
        message = {
            'topic': topic,
            'payload': json.loads(payload) if isinstance(payload, str) else payload,
            'qos': qos
        }
        self.published_messages.append(message)
        
        class Result:
            rc = 0
        return Result()


class TestDeviceSimulatorBase(unittest.TestCase):
    """测试设备模拟器基类"""
    
    def setUp(self):
        """在每个测试之前设置"""
        # 创建一个具体的设备模拟器实例用于测试
        self.mock_protocol_handler = MagicMock()
        
        with patch('src.device_simulator.simulator_base.create_protocol_handler') as mock_create:
            mock_create.return_value = self.mock_protocol_handler
            
            class ConcreteDeviceSimulator(DeviceSimulator):
                def _init_attributes(self):
                    return {"firmware": "1.0.0", "model": "test-model"}
                    
                def _init_telemetry(self):
                    return {"temperature": 25.0, "humidity": 60.0}
                    
                def generate_telemetry(self):
                    telemetry = self._init_telemetry()
                    telemetry["temperature"] += 0.1
                    return telemetry
            
            self.device = ConcreteDeviceSimulator("test-device")
    
    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.device.device_type, "test-device")
        self.assertTrue(self.device.device_id.startswith("test-device_"))
        self.assertEqual(self.device.status, "offline")
        self.assertFalse(self.device.connected)
        self.assertFalse(self.device.running)
        self.assertEqual(self.device.data_generation_interval, 5.0)
        
        # 检查属性和遥测数据初始化
        self.assertEqual(self.device.attributes, {"firmware": "1.0.0", "model": "test-model"})
        self.assertEqual(self.device.telemetry, {"temperature": 25.0, "humidity": 60.0})
    
    def test_connect_disconnect(self):
        """测试连接和断开操作"""
        # 测试连接
        result = self.device.connect()
        self.assertTrue(result)
        self.assertTrue(self.device.connected)
        self.assertEqual(self.device.status, "online")
        
        # 模拟协议处理器应该被用于发送状态更新
        self.mock_protocol_handler.publish.assert_called()
        
        # 重置模拟
        self.mock_protocol_handler.reset_mock()
        
        # 测试断开连接
        result = self.device.disconnect()
        self.assertTrue(result)
        self.assertFalse(self.device.connected)
        self.assertEqual(self.device.status, "offline")
        
        # 模拟协议处理器应该被用于发送状态更新
        self.mock_protocol_handler.publish.assert_called()
    
    def test_start_stop(self):
        """测试启动和停止数据生成"""
        # 测试启动
        self.device.connect = MagicMock(return_value=True)
        
        with patch('threading.Thread') as mock_thread:
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance
            
            result = self.device.start(interval=1.0)
            self.assertTrue(result)
            self.assertTrue(self.device.running)
            self.assertEqual(self.device.data_generation_interval, 1.0)
            
            # 线程应该已启动
            mock_thread_instance.start.assert_called_once()
            
            # 测试停止
            self.device.stop()
            self.assertFalse(self.device.running)
    
    def test_send_telemetry(self):
        """测试发送遥测数据"""
        # 设置设备为已连接状态
        self.device.connected = True
        
        # 测试发送遥测数据
        telemetry = {"temperature": 26.0, "humidity": 65.0}
        result = self.device.send_telemetry(telemetry)
        
        # 应该调用协议处理器的publish方法
        self.mock_protocol_handler.publish.assert_called_once()
        
        # 检查发送的数据格式
        args, kwargs = self.mock_protocol_handler.publish.call_args
        topic, message = args
        
        self.assertEqual(topic, "v1/devices/me/telemetry")
        self.assertEqual(message["device_id"], self.device.device_id)
        self.assertEqual(message["device_type"], "test-device")
        self.assertEqual(message["data"], telemetry)
        self.assertIn("timestamp", message)


class TestGatewaySimulator(unittest.TestCase):
    """测试网关设备模拟器"""
    
    @patch('src.utils.protocol.MQTTHandler')
    def test_gateway_simulator(self, mock_mqtt_handler):
        """测试网关模拟器的特定功能"""
        # 设置模拟的MQTT处理器
        mock_instance = MagicMock()
        mock_mqtt_handler.return_value = mock_instance
        
        # 创建网关模拟器实例
        gateway = GatewaySimulator(device_id="test_gateway")
        
        # 测试属性初始化
        self.assertEqual(gateway.device_type, "gateway")
        self.assertEqual(gateway.device_id, "test_gateway")
        
        # 测试遥测数据生成
        telemetry = gateway.generate_telemetry()
        self.assertIn("connected_devices", telemetry)
        self.assertIn("data_throughput", telemetry)
        self.assertIn("cpu_usage", telemetry)
        self.assertIn("memory_usage", telemetry)
        
        # 测试设备管理功能
        if hasattr(gateway, "add_connected_device"):
            result = gateway.add_connected_device("test_device")
            self.assertTrue(result)
            self.assertIn("test_device", gateway.connected_devices)
            
            telemetry = gateway.generate_telemetry()
            self.assertEqual(telemetry["connected_devices"], 1)


class TestRouterSimulator(unittest.TestCase):
    """测试路由器模拟器"""
    
    @patch('src.utils.protocol.MQTTHandler')
    def test_router_simulator(self, mock_mqtt_handler):
        """测试路由器模拟器的特定功能"""
        # 设置模拟的MQTT处理器
        mock_instance = MagicMock()
        mock_mqtt_handler.return_value = mock_instance
        
        # 创建路由器模拟器实例
        router = RouterSimulator(device_id="test_router")
        
        # 测试属性初始化
        self.assertEqual(router.device_type, "router")
        self.assertEqual(router.device_id, "test_router")
        
        # 测试遥测数据生成
        telemetry = router.generate_telemetry()
        self.assertIn("network_traffic", telemetry)
        self.assertIn("connected_clients", telemetry)
        self.assertIn("signal_strength", telemetry)
        self.assertIn("bandwidth_usage", telemetry)


class TestSpeakerSimulator(unittest.TestCase):
    """测试小爱音箱模拟器"""
    
    @patch('src.utils.protocol.MQTTHandler')
    def test_speaker_simulator(self, mock_mqtt_handler):
        """测试音箱模拟器的特定功能"""
        # 设置模拟的MQTT处理器
        mock_instance = MagicMock()
        mock_mqtt_handler.return_value = mock_instance
        
        # 创建音箱模拟器实例
        speaker = SpeakerSimulator(device_id="test_speaker")
        
        # 测试属性初始化
        self.assertEqual(speaker.device_type, "speaker")
        self.assertEqual(speaker.device_id, "test_speaker")
        
        # 测试遥测数据生成
        telemetry = speaker.generate_telemetry()
        self.assertIn("volume", telemetry)
        self.assertIn("playing_status", telemetry)
        self.assertIn("bluetooth_connections", telemetry)
        self.assertIn("voice_commands_count", telemetry)


class TestCameraSimulator(unittest.TestCase):
    """测试摄像头模拟器"""
    
    @patch('src.utils.protocol.MQTTHandler')
    def test_camera_simulator(self, mock_mqtt_handler):
        """测试摄像头模拟器的特定功能"""
        # 设置模拟的MQTT处理器
        mock_instance = MagicMock()
        mock_mqtt_handler.return_value = mock_instance
        
        # 创建摄像头模拟器实例
        camera = CameraSimulator(device_id="test_camera")
        
        # 测试属性初始化
        self.assertEqual(camera.device_type, "camera")
        self.assertEqual(camera.device_id, "test_camera")
        
        # 测试遥测数据生成
        telemetry = camera.generate_telemetry()
        self.assertIn("resolution", telemetry)
        self.assertIn("frame_rate", telemetry)
        self.assertIn("motion_detected", telemetry)
        self.assertIn("storage_usage", telemetry)


class TestIntegration(unittest.TestCase):
    """设备模拟器集成测试"""
    
    def setUp(self):
        """在每个测试之前设置"""
        # 加载配置
        try:
            self.config = load_config('../config/simulator.yaml')
        except Exception:
            # 如果配置文件不存在，使用默认配置
            self.config = {
                "mqtt": {
                    "broker_host": "localhost",
                    "broker_port": 1883
                }
            }
        
        # 清理现有设备列表
        self.devices = []
    
    def tearDown(self):
        """在每个测试之后清理"""
        # 停止并断开所有设备
        for device in self.devices:
            if device.running:
                device.stop()
            if device.connected:
                device.disconnect()
    
    @unittest.skip("需要实际的MQTT代理")
    def test_multiple_devices(self):
        """测试多个设备同时运行"""
        # 创建多个不同类型的设备
        gateway = GatewaySimulator()
        router = RouterSimulator()
        speaker = SpeakerSimulator()
        camera = CameraSimulator()
        
        self.devices = [gateway, router, speaker, camera]
        
        # 连接并启动所有设备
        for device in self.devices:
            success = device.connect()
            self.assertTrue(success)
            
            success = device.start(interval=1.0)
            self.assertTrue(success)
        
        # 让设备运行一段时间
        time.sleep(5.0)
        
        # 验证所有设备都在运行
        for device in self.devices:
            self.assertTrue(device.running)
            self.assertTrue(device.connected)
        
        # 停止所有设备
        for device in self.devices:
            success = device.stop()
            self.assertTrue(success)
            self.assertFalse(device.running)


if __name__ == '__main__':
    unittest.main()