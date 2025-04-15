#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小爱音箱模拟器
模拟小爱音箱（蓝牙网关）设备
"""

import logging
import time
import random
from typing import Dict, Any, List, Optional
from .device_base import DeviceBase

class SmartSpeaker(DeviceBase):
    """小爱音箱设备模拟器类"""
    
    def __init__(self, device_id: str, edgex_id: Optional[str] = None,
                 tb_device_info: Optional[Dict[str, Any]] = None,
                 tb_credentials: Optional[Dict[str, Any]] = None,
                 edgex_connector=None, thingsboard_connector=None,
                 properties: Dict[str, Any] = None):
        """
        初始化小爱音箱设备
        
        Args:
            device_id: 设备ID
            edgex_id: EdgeX设备ID
            tb_device_info: ThingsBoard设备信息
            tb_credentials: ThingsBoard设备凭证
            edgex_connector: EdgeX连接器实例
            thingsboard_connector: ThingsBoard连接器实例
            properties: 设备属性
        """
        super().__init__(device_id, edgex_id, tb_device_info, tb_credentials,
                        edgex_connector, thingsboard_connector, properties)
        
        # 小爱音箱特有属性
        self.max_volume = self.properties.get("max_volume", 100)
        self.max_bluetooth_devices = self.properties.get("max_bluetooth_devices", 5)
        
        # 可用的语音命令列表
        self.available_commands = [
            "播放音乐", "设置闹钟", "查询天气", "控制智能家居", "讲个笑话"
        ]
        
        # 小爱音箱状态
        self.state.update({
            "volume": random.randint(20, 50),
            "bluetooth_status": random.choice([True, False]),
            "connected_bluetooth_devices": 0 if not random.choice([True, False]) else random.randint(1, 3),
            "playing_status": "idle",  # idle, playing, paused
            "last_command": "",
            "uptime": 0
        })
        
        self.logger.info(f"小爱音箱设备 {device_id} 已初始化")
    
    def generate_telemetry(self) -> Dict[str, Any]:
        """
        生成小爱音箱遥测数据
        
        Returns:
            Dict[str, Any]: 遥测数据字典
        """
        # 更新小爱音箱状态
        self.state["uptime"] = self.state.get("uptime", 0) + self.telemetry_interval
        
        # 随机变化播放状态
        if random.random() < 0.1:  # 10%概率变化播放状态
            self.state["playing_status"] = random.choice(["idle", "playing", "paused"])
        
        # 随机变化蓝牙状态
        if random.random() < 0.05:  # 5%概率变化蓝牙状态
            self.state["bluetooth_status"] = not self.state["bluetooth_status"]
            # 如果蓝牙关闭，连接的蓝牙设备为0
            if not self.state["bluetooth_status"]:
                self.state["connected_bluetooth_devices"] = 0
        
        # 如果蓝牙开启，随机变化连接的蓝牙设备数
        if self.state["bluetooth_status"] and random.random() < 0.1:  # 10%概率变化连接设备数
            change = random.choice([-1, 0, 0, 1])
            self.state["connected_bluetooth_devices"] = max(0, min(
                self.state["connected_bluetooth_devices"] + change,
                self.max_bluetooth_devices
            ))
        
        # 随机模拟接收语音命令
        if random.random() < 0.05:  # 5%概率接收语音命令
            self.state["last_command"] = random.choice(self.available_commands)
            self.logger.info(f"小爱音箱 {self.device_id} 接收语音命令: {self.state['last_command']}")
        
        # 返回遥测数据
        return {
            "volume": self.state["volume"],
            "bluetooth_status": self.state["bluetooth_status"],
            "connected_bluetooth_devices": self.state["connected_bluetooth_devices"],
            "playing_status": self.state["playing_status"],
            "last_command": self.state["last_command"],
            "uptime_seconds": self.state["uptime"]
        }
    
    def handle_command(self, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理小爱音箱命令
        
        Args:
            command: 命令名称
            params: 命令参数
        
        Returns:
            Dict[str, Any]: 命令执行结果
        """
        params = params or {}
        result = {"success": False, "message": "未知命令"}
        
        if command == "set_volume":
            # 设置音量
            volume = params.get("volume")
            if isinstance(volume, (int, float)) and 0 <= volume <= self.max_volume:
                self.logger.info(f"小爱音箱 {self.device_id} 设置音量为 {volume}")
                self.state["volume"] = int(volume)
                result = {"success": True, "message": f"音量已设置为 {volume}"}
            else:
                result = {"success": False, "message": f"无效的音量值，范围应为0-{self.max_volume}"}
        
        elif command == "toggle_bluetooth":
            # 切换蓝牙状态
            self.state["bluetooth_status"] = not self.state["bluetooth_status"]
            status = "开启" if self.state["bluetooth_status"] else "关闭"
            self.logger.info(f"小爱音箱 {self.device_id} {status}蓝牙")
            
            # 如果关闭蓝牙，断开所有蓝牙设备
            if not self.state["bluetooth_status"]:
                self.state["connected_bluetooth_devices"] = 0
            
            result = {"success": True, "message": f"蓝牙已{status}"}
        
        elif command == "play_control":
            # 播放控制（播放、暂停、停止）
            action = params.get("action", "")
            if action in ["play", "pause", "stop"]:
                if action == "play":
                    self.state["playing_status"] = "playing"
                    status_text = "播放"
                elif action == "pause":
                    self.state["playing_status"] = "paused"
                    status_text = "暂停"
                else:  # stop
                    self.state["playing_status"] = "idle"
                    status_text = "停止"
                
                self.logger.info(f"小爱音箱 {self.device_id} {status_text}音乐")
                result = {"success": True, "message": f"已{status_text}"}
            else:
                result = {"success": False, "message": "无效的播放控制命令"}
        
        elif command == "voice_command":
            # 处理语音命令
            voice_text = params.get("text", "")
            self.logger.info(f"小爱音箱 {self.device_id} 接收语音命令: {voice_text}")
            self.state["last_command"] = voice_text
            result = {"success": True, "message": f"已处理语音命令: {voice_text}"}
        
        return result