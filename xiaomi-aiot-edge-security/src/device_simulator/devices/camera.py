#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
摄像头设备模拟器
模拟AIoT边缘摄像头设备
"""

import logging
import time
import random
import string
from typing import Dict, Any, List, Optional
from .device_base import DeviceBase

class Camera(DeviceBase):
    """摄像头设备模拟器类"""
    
    def __init__(self, device_id: str, edgex_id: Optional[str] = None,
                 tb_device_info: Optional[Dict[str, Any]] = None,
                 tb_credentials: Optional[Dict[str, Any]] = None,
                 edgex_connector=None, thingsboard_connector=None,
                 properties: Dict[str, Any] = None):
        """
        初始化摄像头设备
        
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
        
        # 摄像头特有属性
        self.available_resolutions = self.properties.get("available_resolutions", 
                                                        ["640x480", "1280x720", "1920x1080"])
        self.night_vision = self.properties.get("night_vision", True)
        self.motion_detection = self.properties.get("motion_detection", True)
        
        # 摄像头状态
        self.state.update({
            "status": "streaming",  # streaming, standby, off
            "resolution": random.choice(self.available_resolutions),
            "motion_detected": False,
            "fps": random.uniform(15.0, 30.0),
            "streaming_bitrate": random.uniform(1.0, 5.0),  # Mbps
            "night_vision_active": False,
            "last_event_id": "",
            "uptime": 0
        })
        
        self.logger.info(f"摄像头设备 {device_id} 已初始化")
    
    def generate_telemetry(self) -> Dict[str, Any]:
        """
        生成摄像头遥测数据
        
        Returns:
            Dict[str, Any]: 遥测数据字典
        """
        # 更新摄像头状态
        self.state["uptime"] = self.state.get("uptime", 0) + self.telemetry_interval
        
        # 随机变化FPS (15-30)
        self.state["fps"] = min(30.0, max(15.0, 
            self.state["fps"] + random.uniform(-1.0, 1.0)
        ))
        
        # 随机变化码率 (1-5 Mbps)
        self.state["streaming_bitrate"] = min(5.0, max(1.0, 
            self.state["streaming_bitrate"] + random.uniform(-0.2, 0.2)
        ))
        
        # 随机检测移动
        motion_prob = 0.1  # 10%概率检测到移动
        prev_motion = self.state["motion_detected"]
        self.state["motion_detected"] = random.random() < motion_prob
        
        # 如果检测到移动，生成事件ID
        if self.state["motion_detected"] and not prev_motion:
            event_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            self.state["last_event_id"] = f"MOTION_{event_id}_{int(time.time())}"
            self.logger.info(f"摄像头 {self.device_id} 检测到移动: {self.state['last_event_id']}")
        
        # 根据时间自动切换夜视模式(假设晚上6点到早上6点开启夜视)
        current_hour = time.localtime().tm_hour
        night_time = current_hour < 6 or current_hour >= 18
        if self.night_vision:
            self.state["night_vision_active"] = night_time
        
        # 返回遥测数据
        return {
            "status": self.state["status"],
            "resolution": self.state["resolution"],
            "motion_detected": self.state["motion_detected"],
            "fps": round(self.state["fps"], 2),
            "streaming_bitrate": round(self.state["streaming_bitrate"], 2),
            "night_vision_active": self.state["night_vision_active"],
            "last_event_id": self.state["last_event_id"],
            "uptime_seconds": self.state["uptime"]
        }
    
    def handle_command(self, command: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        处理摄像头命令
        
        Args:
            command: 命令名称
            params: 命令参数
        
        Returns:
            Dict[str, Any]: 命令执行结果
        """
        params = params or {}
        result = {"success": False, "message": "未知命令"}
        
        if command == "change_status":
            # 切换摄像头状态
            status = params.get("status")
            if status in ["streaming", "standby", "off"]:
                self.logger.info(f"摄像头 {self.device_id} 切换状态到 {status}")
                self.state["status"] = status
                result = {"success": True, "message": f"摄像头状态已切换到 {status}"}
            else:
                result = {"success": False, "message": "无效的状态"}
        
        elif command == "change_resolution":
            # 切换分辨率
            resolution = params.get("resolution")
            if resolution in self.available_resolutions:
                self.logger.info(f"摄像头 {self.device_id} 切换分辨率到 {resolution}")
                self.state["resolution"] = resolution
                result = {"success": True, "message": f"分辨率已设置为 {resolution}"}
            else:
                result = {"success": False, "message": "无效的分辨率"}
        
        elif command == "toggle_night_vision":
            # 切换夜视模式
            if self.night_vision:
                night_vision_active = params.get("active", not self.state["night_vision_active"])
                self.state["night_vision_active"] = night_vision_active
                status = "开启" if night_vision_active else "关闭"
                self.logger.info(f"摄像头 {self.device_id} {status}夜视模式")
                result = {"success": True, "message": f"夜视模式已{status}"}
            else:
                result = {"success": False, "message": "该摄像头不支持夜视模式"}
        
        elif command == "capture_snapshot":
            # 模拟拍摄快照
            snapshot_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            timestamp = int(time.time())
            snapshot_url = f"https://example.com/snapshots/{self.device_id}/{snapshot_id}_{timestamp}.jpg"
            self.logger.info(f"摄像头 {self.device_id} 拍摄快照: {snapshot_id}")
            result = {
                "success": True, 
                "message": "快照已拍摄", 
                "snapshot_id": snapshot_id,
                "url": snapshot_url
            }
        
        return result