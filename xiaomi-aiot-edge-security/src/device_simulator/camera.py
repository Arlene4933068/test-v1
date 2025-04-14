#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
摄像头设备模拟器
模拟小米AIoT摄像头设备
"""

import random
import time
import uuid
import math
from datetime import datetime, timedelta

from .simulator_base import DeviceSimulator

class CameraSimulator(DeviceSimulator):
    """摄像头设备模拟器类"""
    
    def __init__(self, config_path=None):
        """
        初始化摄像头模拟器
        
        Args:
            config_path (str, optional): 配置文件路径. 默认为None.
        """
        super().__init__("camera", config_path)
        
        # 摄像头特有属性
        self.camera_model = self.device_config.get("model", "Xiaomi AIoT Camera Pro")
        self.firmware_version = self.device_config.get("firmware_version", "2.3.7")
        
        # 视频参数
        self.resolution = self.device_config.get("resolution", "1080p")  # 分辨率
        self.fps = self.device_config.get("fps", 30)  # 帧率
        self.bitrate = self.device_config.get("bitrate", 2000)  # Kbps
        self.encoding = self.device_config.get("encoding", "H.264")  # 编码格式
        self.night_vision = self.device_config.get("night_vision", True)  # 夜视功能
        self.wide_dynamic_range = self.device_config.get("wide_dynamic_range", True)  # 宽动态范围
        
        # 当前状态
        self.is_streaming = False  # 是否正在流式传输
        self.is_recording = False  # 是否正在录制
        self.recording_start_time = None  # 录制开始时间
        self.ptz_enabled = self.device_config.get("ptz_enabled", False)  # 是否支持云台
        self.current_position = {
            "pan": 0,  # 水平旋转角度 (-180 到 180)
            "tilt": 0,  # 垂直旋转角度 (-90 到 90)
            "zoom": 1.0  # 缩放比例 (1.0 到 10.0)
        } if self.ptz_enabled else None
        
        # 连接和存储
        self.wifi_connected = True
        self.wifi_signal_strength = random.randint(70, 100)  # 0-100
        self.storage_total = self.device_config.get("storage", 32) * 1024  # MB
        self.storage_used = 0  # MB
        
        # 事件检测
        self.motion_detection = self.device_config.get("motion_detection", True)
        self.face_recognition = self.device_config.get("face_recognition", False)
        self.object_detection = self.device_config.get("object_detection", False)
        self.detected_events = []
        
        # 流量统计
        self.bandwidth_usage = 0.0  # Kbps
        self.total_data_sent = 0.0  # MB
        self.total_data_received = 0.0  # MB
        
        # 性能指标
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.temperature = random.uniform(35.0, 45.0)  # 摄像头往往会发热
        self.uptime = 0
        
        # 电源状态
        self.power_source = self.device_config.get("power_source", "AC")  # AC或Battery
        self.battery_level = 100 if self.power_source == "Battery" else None
        
        # 安全设置
        self.encryption_enabled = self.security_settings.get("encryption_enabled", True)
        self.auth_required = self.security_settings.get("auth_required", True)
        self.access_token = self.security_settings.get("access_token", str(uuid.uuid4()))
        
        # 初始化存储
        self._initialize_storage()
        
        self.logger.info(f"摄像头设备 {self.device_id} 初始化完成, 型号: {self.camera_model}")
    
    def _initialize_storage(self):
        """初始化模拟存储"""
        self.storage_used = random.uniform(0.1, 0.4) * self.storage_total
        num_recordings = random.randint(5, 20)
        
        for i in range(num_recordings):
            # 生成随机录制时间
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            
            record_time = datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
            duration = random.randint(10, 300)  # 10秒到5分钟
            file_size = (self.bitrate * duration) / 8000  # MB
            
            # 生成事件类型
            event_types = ["motion", "person", "vehicle", "animal", "package", "face", "sound"]
            event_weights = [0.5, 0.2, 0.1, 0.1, 0.05, 0.03, 0.02]  # 权重
            event_type = random.choices(event_types, weights=event_weights, k=1)[0]
            
            # 创建录制记录
            recording = {
                "id": f"rec_{record_time.strftime('%Y%m%d%H%M%S')}",
                "start_time": record_time.isoformat(),
                "end_time": (record_time + timedelta(seconds=duration)).isoformat(),
                "duration": duration,
                "file_size": round(file_size, 2),
                "resolution": self.resolution,
                "fps": self.fps,
                "encoding": self.encoding,
                "trigger": event_type,
                "thumbnail": f"thumbnail_{i}.jpg"
            }
            
            # 创建对应的事件记录
            event = {
                "id": f"evt_{record_time.strftime('%Y%m%d%H%M%S')}",
                "type": event_type,
                "time": record_time.isoformat(),
                "confidence": round(random.uniform(0.7, 0.99), 2),
                "recording_id": recording["id"],
                "details": self._generate_event_details(event_type)
            }
            
            # 添加到事件列表
            self.detected_events.append(event)
    
    def _generate_event_details(self, event_type):
        """根据事件类型生成详细信息"""
        if event_type == "motion":
            return {
                "motion_area": f"{random.randint(10, 50)}%",
                "motion_intensity": round(random.uniform(0.1, 1.0), 2),
                "direction": random.choice(["left", "right", "up", "down", "center"])
            }
        elif event_type == "person":
            return {
                "person_count": random.randint(1, 3),
                "height": random.randint(160, 190),
                "position": {
                    "x": random.randint(0, 100),
                    "y": random.randint(0, 100),
                    "width": random.randint(10, 30),
                    "height": random.randint(20, 60)
                },
                "recognized": random.random() < 0.3  # 30%概率是认识的人
            }
        elif event_type == "vehicle":
            return {
                "vehicle_type": random.choice(["car", "motorcycle", "truck", "bicycle"]),
                "color": random.choice(["black", "white", "red", "blue", "silver", "gray"]),
                "license_plate": random.random() < 0.4  # 40%概率识别到车牌
            }
        elif event_type == "animal":
            return {
                "animal_type": random.choice(["cat", "dog", "bird", "unknown"]),
                "size": random.choice(["small", "medium", "large"])
            }
        elif event_type == "package":
            return {
                "size": random.choice(["small", "medium", "large"]),
                "placed": random.random() < 0.7,  # 70%概率是放下包裹，30%是取走
                "carrier": random.choice(["courier", "person"])
            }
        elif event_type == "face":
            return {
                "familiar": random.random() < 0.5,  # 50%概率是熟悉的人脸
                "age_estimate": random.randint(18, 65),
                "gender": random.choice(["male", "female"]),
                "expression": random.choice(["neutral", "happy", "serious"])
            }
        elif event_type == "sound":
            return {
                "sound_type": random.choice(["talk", "yell", "crash", "alarm", "doorbell"]),
                "volume": round(random.uniform(0.3, 1.0), 2),
                "duration": random.randint(1, 10)
            }
        else:
            return {}
    
    def generate_telemetry(self):
        """
        生成摄像头遥测数据
        
        Returns:
            dict: 摄像头遥测数据
        """
        # 更新动态状态
        self._update_camera_state()
        
        # 基础遥测数据
        telemetry = {
            "cpu_usage": round(self.cpu_usage, 2),
            "memory_usage": round(self.memory_usage, 2),
            "temperature": round(self.temperature, 1),
            "uptime": self.uptime,
            "storage": {
                "total": round(self.storage_total, 2),
                "used": round(self.storage_used, 2),
                "free": round(self.storage_total - self.storage_used, 2),
                "usage_percent": round((self.storage_used / self.storage_total) * 100, 1)
            },
            "power": {
                "source": self.power_source,
                "battery_level": self.battery_level if self.power_source == "Battery" else None
            },
            "network": {
                "wifi_connected": self.wifi_connected,
                "signal_strength": self.wifi_signal_strength if self.wifi_connected else 0,
                "bandwidth": {
                    "upload": round(self.bandwidth_usage, 2),
                    "download": round(self.bandwidth_usage * 0.1, 2)  # 下载通常远小于上传
                },
                "data_usage": {
                    "sent": round(self.total_data_sent, 2),
                    "received": round(self.total_data_received, 2)
                }
            },
            "video": {
                "streaming": self.is_streaming,
                "recording": self.is_recording,
                "resolution": self.resolution,
                "fps": self.fps,
                "bitrate": self.bitrate,
                "encoding": self.encoding,
                "night_vision": self.night_vision,
                "wide_dynamic_range": self.wide_dynamic_range
            },
            "detection": {
                "motion_detection": self.motion_detection,
                "face_recognition": self.face_recognition,
                "object_detection": self.object_detection,
                "recent_events_count": len([e for e in self.detected_events 
                                          if datetime.fromisoformat(e["time"]) > 
                                             datetime.now() - timedelta(hours=24)])
            },
            "firmware_version": self.firmware_version,
        }
        
        # 如果支持云台，添加当前位置
        if self.ptz_enabled:
            telemetry["ptz"] = self.current_position
        
        return telemetry
    
    def device_behavior(self):
        """摄像头设备特定行为"""
        # 更新资源使用情况
        self._update_resource_usage()
        
        # 更新网络连接和带宽使用
        self._update_network_usage()
        
        # 更新存储使用情况
        self._update_storage_usage()
        
        # 检测事件
        if random.random() < 0.2:  # 20%概率检测到事件
            self._detect_event()
        
        # 根据行为模式执行特定操作
        if self.behavior_mode == "anomaly":
            self._simulate_anomaly_behavior()
        elif self.behavior_mode == "attack":
            self._simulate_attack_behavior()
    
    def _update_camera_state(self):
        """更新摄像头状态"""
        # 更新温度
        if self.is_streaming or self.is_recording:
            temp_increase = random.uniform(0.05, 0.2)
        else:
            temp_increase = random.uniform(-0.2, 0.05)
        
        self.temperature = max(30.0, min(65.0, self.temperature + temp_increase))
        
        # 如果是电池供电，更新电池电量
        if self.power_source == "Battery" and self.battery_level is not None:
            # 耗电量取决于工作模式
            if self.is_streaming and self.is_recording:
                battery_drain = random.uniform(0.03, 0.06)
            elif self.is_streaming or self.is_recording:
                battery_drain = random.uniform(0.01, 0.03)
            else:
                battery_drain = random.uniform(0.001, 0.005)
            
            self.battery_level = max(0, self.battery_level - battery_drain)
            
            # 如果电池电量过低，停止流/录制
            if self.battery_level < 5 and (self.is_streaming or self.is_recording):
                self.is_streaming = False
                if self.is_recording:
                    self._stop_recording()
                self.logger.warning(f"设备 {self.device_id} 电池电量低，已停止视频流和录制")
        
        # 更新云台位置（如果启用）
        if self.ptz_enabled and random.random() < 0.1:  # 10%概率移动云台
            self._update_ptz_position()
    
    def _update_resource_usage(self):
        """更新资源使用情况"""
        # 基础CPU和内存使用
        base_cpu = 10.0  # 基础占用
        base_memory = 15.0  # 基础占用
        
        # 根据活动状态增加资源占用
        if self.is_streaming:
            base_cpu += 20.0
            base_memory += 10.0
            
            # 高分辨率和帧率增加CPU使用
            if self.resolution in ["1080p", "2K", "4K"]:
                base_cpu += 10.0
            if self.fps > 25:
                base_cpu += 5.0
        
        if self.is_recording:
            base_cpu += 15.0
            base_memory += 5.0
        
        if self.motion_detection:
            base_cpu += 5.0
            base_memory += 3.0
        
        if self.face_recognition:
            base_cpu += 10.0
            base_memory += 7.0
        
        if self.object_detection:
            base_cpu += 15.0
            base_memory += 10.0
        
        if self.night_vision and self._is_night_time():
            base_cpu += 3.0
            base_memory += 2.0
        
        # 根据模式调整资源使用波动
        if self.behavior_mode == "normal":
            cpu_variation = random.uniform(-5, 5)
            memory_variation = random.uniform(-3, 3)
        elif self.behavior_mode == "anomaly":
            cpu_variation = random.uniform(-10, 20)
            memory_variation = random.uniform(-5, 15)
        elif self.behavior_mode == "attack":
            cpu_variation = random.uniform(15, 50)
            memory_variation = random.uniform(10, 40)
        
        # 更新最终值
        self.cpu_usage = max(0, min(100, base_cpu + cpu_variation))
        self.memory_usage = max(0, min(100, base_memory + memory_variation))
        
        # 更新运行时间
        self.uptime += random.randint(5, 15)
    
    def _update_network_usage(self):
        """更新网络使用情况"""
        if not self.wifi_connected:
            # 随机尝试重新连接WiFi
            if random.random() < 0.2:  # 20%概率尝试重连
                self.wifi_connected = True
                self.wifi_signal_strength = random.randint(30, 70)
                self.logger.info(f"设备 {self.device_id} 重新连接到WiFi")
            return
        
        # 更新WiFi信号强度
        if self.behavior_mode == "normal":
            self.wifi_signal_strength = max(10, min(100, self.wifi_signal_strength + random.uniform(-3, 3)))
        elif self.behavior_mode == "anomaly":
            self.wifi_signal_strength = max(10, min(100, self.wifi_signal_strength + random.uniform(-10, 5)))
        elif self.behavior_mode == "attack":
            self.wifi_signal_strength = max(5, min(60, self.wifi_signal_strength + random.uniform(-15, 5)))
            
            # 攻击模式可能导致WiFi断开
            if random.random() < 0.1:  # 10%概率断开
                self.wifi_connected = False
                self.logger.warning(f"设备 {self.device_id} WiFi连接中断")
                return
        
        # 计算带宽使用
        base_bandwidth = 0.0
        
        if self.is_streaming:
            # 基础流带宽
            resolution_factor = {
                "480p": 0.5,
                "720p": 1.0,
                "1080p": 2.0,
                "2K": 4.0,
                "4K": 8.0
            }.get(self.resolution, 1.0)
            
            fps_factor = self.fps / 30.0
            encoding_factor = 1.0 if self.encoding == "H.264" else (0.7 if self.encoding == "H.265" else 1.3)
            
            stream_bandwidth = self.bitrate * resolution_factor * fps_factor * encoding_factor
            base_bandwidth += stream_bandwidth
        
        if self.is_recording:
            # 录制通常只消耗少量额外带宽用于状态更新
            base_bandwidth += 10.0
        
        # 添加随机波动
        bandwidth_variation = random.uniform(-50, 50) if base_bandwidth > 0 else 0
        self.bandwidth_usage = max(0, base_bandwidth + bandwidth_variation)
        
        # 累计流量
        interval = random.uniform(5, 15) / 3600  # 转换为小时
        data_sent = self.bandwidth_usage * interval * 1024 / 8000  # Kbps转MB
        data_received = data_sent * 0.1  # 下载通常远小于上传
        
        self.total_data_sent += data_sent
        self.total_data_received += data_received
    
    def _update_storage_usage(self):
        """更新存储使用情况"""
        if self.is_recording:
            # 计算录制使用的存储空间
            interval = random.uniform(5, 15)  # 秒
            storage_usage = (self.bitrate * interval) / 8000  # MB
            
            self.storage_used += storage_usage
            
            # 如果存储接近满，停止录制
            storage_percent = (self.storage_used / self.storage_total) * 100
            if storage_percent > 95:
                self._stop_recording()
                self.logger.warning(f"设备 {self.device_id} 存储空间不足，已停止录制")
    
    def _detect_event(self):
        """检测事件"""
        # 如果相关检测功能关闭，不检测事件
        if not (self.motion_detection or self.face_recognition or self.object_detection):
            return
        
        # 确定事件类型
        available_events = []
        
        if self.motion_detection:
            available_events.extend(["motion"])
        
        if self.face_recognition:
            available_events.extend(["face"])
        
        if self.object_detection:
            available_events.extend(["person", "vehicle", "animal", "package"])
        
        # 如果没有可用事件类型，返回
        if not available_events:
            return
        
        # 选择事件类型
        event_type = random.choice(available_events)
        
        # 生成事件ID
        event_id = f"evt_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 创建事件记录
        event = {
            "id": event_id,
            "type": event_type,
            "time": datetime.now().isoformat(),
            "confidence": round(random.uniform(0.7, 0.99), 2),
            "recording_id": None,  # 如果开始录制，将会更新
            "details": self._generate_event_details(event_type)
        }
        
        # 添加到事件列表
        self.detected_events.append(event)
        self.logger.info(f"设备 {self.device_id} 检测到{event_type}事件")
        
        # 根据事件类型决定是否开始录制
        if not self.is_recording and random.random() < 0.7:  # 70%概率开始录制
            self._start_recording(event_id)
        
        # 发送事件遥测
        event_telemetry = {
            "event": "detection",
            "type": event_type,
            "time": event["time"],
            "details": event["details"]
        }
        self._send_telemetry(event_telemetry)
    
    def _start_recording(self, event_id=None):
        """开始录制"""
        if self.is_recording:
            self.logger.warning(f"设备 {self.device_id} 已经在录制中")
            return False
    
    def toggle_detection_features(self, motion=None, face=None, object_detection=None):
        """切换检测功能"""
        changes = []
        
        # 更新运动检测
        if motion is not None:
            if isinstance(motion, bool):
                old_motion = self.motion_detection
                self.motion_detection = motion
                changes.append(f"运动检测: {'开启' if motion else '关闭'}")
            else:
                self.logger.warning(f"设备 {self.device_id} 无效的运动检测值: {motion}")
        
        # 更新人脸识别
        if face is not None:
            if isinstance(face, bool):
                old_face = self.face_recognition
                self.face_recognition = face
                changes.append(f"人脸识别: {'开启' if face else '关闭'}")
            else:
                self.logger.warning(f"设备 {self.device_id} 无效的人脸识别值: {face}")
        
        # 更新物体检测
        if object_detection is not None:
            if isinstance(object_detection, bool):
                old_object = self.object_detection
                self.object_detection = object_detection
                changes.append(f"物体检测: {'开启' if object_detection else '关闭'}")
            else:
                self.logger.warning(f"设备 {self.device_id} 无效的物体检测值: {object_detection}")
        
        if changes:
            self.logger.info(f"设备 {self.device_id} 检测功能已更新: {', '.join(changes)}")
            return True
        
        return False
    
    def get_detected_events(self, limit=10, event_type=None, start_time=None, end_time=None):
        """获取检测到的事件"""
        # 过滤事件
        filtered_events = self.detected_events
        
        # 按事件类型过滤
        if event_type:
            filtered_events = [e for e in filtered_events if e["type"] == event_type]
        
        # 按时间范围过滤
        if start_time:
            start_dt = datetime.fromisoformat(start_time) if isinstance(start_time, str) else start_time
            filtered_events = [e for e in filtered_events if datetime.fromisoformat(e["time"]) >= start_dt]
        
        if end_time:
            end_dt = datetime.fromisoformat(end_time) if isinstance(end_time, str) else end_time
            filtered_events = [e for e in filtered_events if datetime.fromisoformat(e["time"]) <= end_dt]
        
        # 排序（最新的在前）
        sorted_events = sorted(filtered_events, key=lambda e: e["time"], reverse=True)
        
        # 限制数量
        return sorted_events[:limit]
    
    def get_network_stats(self):
        """获取网络统计信息"""
        return {
            "wifi_connected": self.wifi_connected,
            "signal_strength": self.wifi_signal_strength if self.wifi_connected else 0,
            "bandwidth": {
                "upload": round(self.bandwidth_usage, 2),
                "download": round(self.bandwidth_usage * 0.1, 2)
            },
            "data_usage": {
                "sent": round(self.total_data_sent, 2),
                "received": round(self.total_data_received, 2)
            }
        }
    
    def toggle_night_vision(self, enabled=None):
        """切换夜视功能"""
        if enabled is None:
            # 切换当前状态
            self.night_vision = not self.night_vision
        else:
            self.night_vision = enabled
        
        self.logger.info(f"设备 {self.device_id} 夜视功能: {'开启' if self.night_vision else '关闭'}")
        return self.night_vision
        
    def _send_telemetry(self, data):
        """发送遥测数据（需要在子类中实现）"""
        # 这个方法应该在继承类中被实现，用于发送遥测数据到服务器
        pass
        
        # 检查存储空间
        storage_percent = (self.storage_used / self.storage_total) * 100
        if storage_percent > 95:
            self.logger.warning(f"设备 {self.device_id} 存储空间不足，无法开始录制")
            return False
        
        # 检查电池电量（如果是电池供电）
        if self.power_source == "Battery" and self.battery_level < 10:
            self.logger.warning(f"设备 {self.device_id} 电池电量低，无法开始录制")
            return False
        
        # 开始录制
        self.is_recording = True
        self.recording_start_time = datetime.now()
        
        # 如果是由事件触发，更新事件记录
        if event_id:
            for event in self.detected_events:
                if event["id"] == event_id:
                    recording_id = f"rec_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    event["recording_id"] = recording_id
                    break
        
        self.logger.info(f"设备 {self.device_id} 开始录制")
        return True
    
    def _stop_recording(self):
        """停止录制"""
        if not self.is_recording:
            self.logger.warning(f"设备 {self.device_id} 没有在录制中")
            return False
        
        # 停止录制
        self.is_recording = False
        end_time = datetime.now()
        
        # 计算录制时长和文件大小
        if self.recording_start_time:
            duration = (end_time - self.recording_start_time).total_seconds()
            file_size = (self.bitrate * duration) / 8000  # MB
            
            # 创建录制记录
            recording_id = f"rec_{self.recording_start_time.strftime('%Y%m%d%H%M%S')}"
            recording = {
                "id": recording_id,
                "start_time": self.recording_start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration": duration,
                "file_size": round(file_size, 2),
                "resolution": self.resolution,
                "fps": self.fps,
                "encoding": self.encoding,
                "trigger": "manual",  # 可能会被事件更新
                "thumbnail": f"thumbnail_{int(time.time())}.jpg"
            }
            
            # 更新与此录制相关的事件
            for event in self.detected_events:
                if event["recording_id"] == recording_id:
                    recording["trigger"] = event["type"]
                    break
            
            self.logger.info(f"设备 {self.device_id} 停止录制，时长: {duration:.1f}秒, 大小: {file_size:.2f}MB")
            
            # 重置录制时间
            self.recording_start_time = None
            
            return True
        else:
            self.logger.warning(f"设备 {self.device_id} 录制开始时间未记录")
            self.recording_start_time = None
            return False
    
    def _update_ptz_position(self):
        """更新云台位置"""
        if not self.ptz_enabled or not self.current_position:
            return
        
        # 随机更新云台位置
        if self.behavior_mode == "normal":
            # 小幅度的随机移动
            pan_change = random.uniform(-5, 5)
            tilt_change = random.uniform(-3, 3)
            zoom_change = random.uniform(-0.1, 0.1)
        elif self.behavior_mode == "anomaly":
            # 较大幅度的随机移动
            pan_change = random.uniform(-20, 20)
            tilt_change = random.uniform(-10, 10)
            zoom_change = random.uniform(-0.5, 0.5)
        elif self.behavior_mode == "attack":
            # 可能出现剧烈或异常的移动
            pan_change = random.uniform(-45, 45)
            tilt_change = random.uniform(-20, 20)
            zoom_change = random.uniform(-1.0, 1.0)
        
        # 更新位置，保持在有效范围内
        self.current_position["pan"] = max(-180, min(180, self.current_position["pan"] + pan_change))
        self.current_position["tilt"] = max(-90, min(90, self.current_position["tilt"] + tilt_change))
        self.current_position["zoom"] = max(1.0, min(10.0, self.current_position["zoom"] + zoom_change))
    
    def _is_night_time(self):
        """判断当前是否是夜间"""
        hour = datetime.now().hour
        return hour < 6 or hour > 18
    
    def _simulate_anomaly_behavior(self):
        """模拟异常行为"""
        anomaly_type = random.choice([
            "video_glitch", "storage_error", "recording_failure", 
            "detection_malfunction", "connection_instability", "ptz_error"
        ])
        
        self.logger.warning(f"设备 {self.device_id} 模拟异常行为: {anomaly_type}")
        
        if anomaly_type == "video_glitch":
            # 模拟视频故障
            if self.is_streaming:
                # 随机改变视频参数
                if random.random() < 0.5:
                    old_resolution = self.resolution
                    self.resolution = random.choice(["480p", "720p", "1080p"])
                    self.logger.warning(f"设备 {self.device_id} 视频故障，分辨率从 {old_resolution} 变为 {self.resolution}")
                
                if random.random() < 0.3:
                    old_fps = self.fps
                    self.fps = random.choice([15, 20, 25, 30])
                    self.logger.warning(f"设备 {self.device_id} 视频故障，帧率从 {old_fps} 变为 {self.fps}")
            
        elif anomaly_type == "storage_error":
            # 模拟存储错误
            error_type = random.choice(["read_error", "write_error", "corruption"])
            self.logger.warning(f"设备 {self.device_id} 存储错误: {error_type}")
            
            if self.is_recording and random.random() < 0.7:
                self._stop_recording()
                self.logger.warning(f"设备 {self.device_id} 由于存储错误停止录制")
            
        elif anomaly_type == "recording_failure":
            # 模拟录制失败
            if self.is_recording:
                self._stop_recording()
                self.logger.warning(f"设备 {self.device_id} 录制失败")
            
        elif anomaly_type == "detection_malfunction":
            # 模拟检测功能故障
            if self.motion_detection or self.face_recognition or self.object_detection:
                # 生成错误检测事件
                false_event_type = random.choice(["motion", "person", "vehicle", "face"])
                
                event = {
                    "id": f"evt_false_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "type": false_event_type,
                    "time": datetime.now().isoformat(),
                    "confidence": round(random.uniform(0.5, 0.7), 2),  # 较低的置信度
                    "recording_id": None,
                    "details": self._generate_event_details(false_event_type),
                    "is_false_positive": True
                }
                
                self.detected_events.append(event)
                self.logger.warning(f"设备 {self.device_id} 检测故障，产生虚假{false_event_type}事件")
            
        elif anomaly_type == "connection_instability":
            # 模拟连接不稳定
            if self.wifi_connected:
                self.wifi_signal_strength = max(10, min(100, self.wifi_signal_strength - random.uniform(10, 30)))
                
                if random.random() < 0.4:  # 40%概率断开
                    self.wifi_connected = False
                    self.logger.warning(f"设备 {self.device_id} WiFi连接中断")
                    
                    if self.is_streaming:
                        self.is_streaming = False
                        self.logger.warning(f"设备 {self.device_id} 由于连接中断停止视频流")
            
        elif anomaly_type == "ptz_error":
            # 模拟云台错误
            if self.ptz_enabled and self.current_position:
                # 云台卡住或跳动
                if random.random() < 0.5:
                    # 卡住 - 不再响应移动
                    self.logger.warning(f"设备 {self.device_id} 云台卡住")
                else:
                    # 跳动 - 剧烈的随机移动
                    self.current_position["pan"] = random.uniform(-180, 180)
                    self.current_position["tilt"] = random.uniform(-90, 90)
                    self.logger.warning(f"设备 {self.device_id} 云台跳动")
    
    def _simulate_attack_behavior(self):
        """模拟攻击行为"""
        attack_type = random.choice([
            "unauthorized_access", "data_exfiltration", "stream_hijacking",
            "credential_theft", "firmware_attack", "privacy_violation"
        ])
        
        self.logger.warning(f"设备 {self.device_id} 模拟攻击行为: {attack_type}")
        
        if attack_type == "unauthorized_access":
            # 模拟未授权访问
            self.logger.warning(f"设备 {self.device_id} 检测到未授权访问尝试")
            
            # 模拟高CPU使用和异常连接
            self.cpu_usage = min(100, self.cpu_usage + random.uniform(30, 60))
            
            # 生成可疑登录事件
            login_event = {
                "event": "security_breach",
                "type": "unauthorized_login",
                "time": datetime.now().isoformat(),
                "source_ip": f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}",
                "attempt_count": random.randint(3, 20),
                "success": random.random() < 0.3  # 30%概率成功
            }
            self._send_telemetry(login_event)
        
        elif attack_type == "data_exfiltration":
            # 模拟数据窃取
            self.logger.warning(f"设备 {self.device_id} 检测到可疑数据传输")
            
            # 异常带宽使用
            old_bandwidth = self.bandwidth_usage
            self.bandwidth_usage += random.uniform(500, 2000)
            self.total_data_sent += random.uniform(50, 200)  # 额外数据传输
            
            # 生成可疑数据包
            exfiltration_event = {
                "event": "suspicious_data_transfer",
                "destination_ip": f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}",
                "data_size": round(random.uniform(50, 200), 2),  # MB
                "protocol": random.choice(["HTTP", "HTTPS", "FTP", "MQTT"]),
                "timestamp": datetime.now().isoformat()
            }
            self._send_telemetry(exfiltration_event)
        
        elif attack_type == "stream_hijacking":
            # 模拟视频流劫持
            self.logger.warning(f"设备 {self.device_id} 检测到视频流劫持尝试")
            
            if self.is_streaming:
                # 模拟视频参数突然变化
                old_resolution = self.resolution
                old_bitrate = self.bitrate
                
                self.resolution = random.choice(["480p", "720p", "1080p", "2K", "4K"])
                self.bitrate = random.randint(500, 8000)
                
                self.logger.warning(f"设备 {self.device_id} 视频参数异常变化: 分辨率 {old_resolution} → {self.resolution}, 比特率 {old_bitrate} → {self.bitrate}")
            
            # 生成流劫持事件
            hijack_event = {
                "event": "stream_hijacking",
                "time": datetime.now().isoformat(),
                "unauthorized_viewer": f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}",
                "stream_redirect": random.random() < 0.5  # 50%概率重定向流
            }
            self._send_telemetry(hijack_event)
        
        elif attack_type == "credential_theft":
            # 模拟凭证窃取
            self.logger.warning(f"设备 {self.device_id} 检测到凭证窃取尝试")
            
            # 模拟暴力破解或凭证泄露
            brute_force = {
                "event": "credential_attack",
                "time": datetime.now().isoformat(),
                "attack_type": random.choice(["brute_force", "dictionary", "credential_stuffing"]),
                "attempts": random.randint(10, 1000),
                "source_ips": [f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}" 
                              for _ in range(random.randint(1, 5))],
                "compromised": random.random() < 0.2  # 20%概率凭证被窃取
            }
            self._send_telemetry(brute_force)
            
            # 如果凭证被窃取，可能改变安全状态
            if brute_force["compromised"]:
                self.auth_required = random.random() < 0.7  # 70%概率保持认证，30%概率被关闭
                self.access_token = str(uuid.uuid4()) if self.auth_required else None
                self.logger.warning(f"设备 {self.device_id} 凭证可能已被窃取，认证状态: {'已保持' if self.auth_required else '已禁用'}")
        
        elif attack_type == "firmware_attack":
            # 模拟固件攻击
            self.logger.warning(f"设备 {self.device_id} 检测到可疑固件修改尝试")
            
            # 模拟固件篡改
            firmware_event = {
                "event": "firmware_attack",
                "time": datetime.now().isoformat(),
                "attack_type": random.choice(["unauthorized_update", "downgrade_attack", "modified_firmware"]),
                "source": f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}",
                "previous_version": self.firmware_version,
                "malicious_version": f"{random.randint(1, 5)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
                "success": random.random() < 0.3  # 30%概率成功
            }
            self._send_telemetry(firmware_event)
            
            # 如果攻击成功，可能改变固件版本
            if firmware_event["success"]:
                self.firmware_version = firmware_event["malicious_version"]
                self.logger.warning(f"设备 {self.device_id} 固件可能已被篡改，版本变为: {self.firmware_version}")
        
        elif attack_type == "privacy_violation":
            # 模拟隐私侵犯
            self.logger.warning(f"设备 {self.device_id} 检测到隐私侵犯尝试")
            
            # 模拟未授权的视频/音频访问
            privacy_event = {
                "event": "privacy_violation",
                "time": datetime.now().isoformat(),
                "violation_type": random.choice(["unauthorized_recording", "silent_streaming", "data_access"]),
                "duration": random.randint(10, 300),  # 秒
                "accessed_data": random.choice(["video", "audio", "stored_recordings", "events", "settings"]),
                "source": f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
            }
            self._send_telemetry(privacy_event)
            
            # 可能触发未授权录制
            if not self.is_recording and privacy_event["violation_type"] == "unauthorized_recording":
                self.is_recording = True
                self.recording_start_time = datetime.now()
                self.logger.warning(f"设备 {self.device_id} 可能被触发未授权录制")
    
    def start_streaming(self):
        """开始视频流"""
        if self.is_streaming:
            self.logger.warning(f"设备 {self.device_id} 已经在流式传输中")
            return False
        
        # 检查网络连接
        if not self.wifi_connected:
            self.logger.warning(f"设备 {self.device_id} 网络未连接，无法开始流式传输")
            return False
        
        # 检查电池电量（如果是电池供电）
        if self.power_source == "Battery" and self.battery_level < 15:
            self.logger.warning(f"设备 {self.device_id} 电池电量低，无法开始流式传输")
            return False
        
        # 开始流式传输
        self.is_streaming = True
        self.logger.info(f"设备 {self.device_id} 开始视频流，分辨率: {self.resolution}, 帧率: {self.fps}, 比特率: {self.bitrate}Kbps")
        return True
    
    def stop_streaming(self):
        """停止视频流"""
        if not self.is_streaming:
            self.logger.warning(f"设备 {self.device_id} 没有进行流式传输")
            return False
        
        # 停止流式传输
        self.is_streaming = False
        self.logger.info(f"设备 {self.device_id} 停止视频流")
        return True
    
    def start_recording(self):
        """手动开始录制"""
        return self._start_recording()
    
    def stop_recording(self):
        """手动停止录制"""
        return self._stop_recording()
    
    def set_ptz_position(self, pan, tilt, zoom=None):
        """设置云台位置"""
        if not self.ptz_enabled:
            self.logger.warning(f"设备 {self.device_id} 不支持云台控制")
            return False
        
        # 检查参数范围
        if not (-180 <= pan <= 180):
            self.logger.warning(f"设备 {self.device_id} 无效的水平角度: {pan}，应在-180到180之间")
            return False
            
        if not (-90 <= tilt <= 90):
            self.logger.warning(f"设备 {self.device_id} 无效的垂直角度: {tilt}，应在-90到90之间")
            return False
            
        if zoom is not None and not (1.0 <= zoom <= 10.0):
            self.logger.warning(f"设备 {self.device_id} 无效的缩放比例: {zoom}，应在1.0到10.0之间")
            return False
        
        # 更新位置
        self.current_position["pan"] = pan
        self.current_position["tilt"] = tilt
        if zoom is not None:
            self.current_position["zoom"] = zoom
        
        self.logger.info(f"设备 {self.device_id} 云台位置设置为 pan: {pan}, tilt: {tilt}" + 
                         (f", zoom: {zoom}" if zoom is not None else ""))
        return True
    
    def set_video_parameters(self, resolution=None, fps=None, bitrate=None, encoding=None):
        """设置视频参数"""
        changes = []
        
        # 更新分辨率
        if resolution is not None:
            if resolution in ["480p", "720p", "1080p", "2K", "4K"]:
                old_resolution = self.resolution
                self.resolution = resolution
                changes.append(f"分辨率: {old_resolution} → {resolution}")
            else:
                self.logger.warning(f"设备 {self.device_id} 无效的分辨率: {resolution}")
        
        # 更新帧率
        if fps is not None:
            if 5 <= fps <= 60:
                old_fps = self.fps
                self.fps = fps
                changes.append(f"帧率: {old_fps} → {fps}")
            else:
                self.logger.warning(f"设备 {self.device_id} 无效的帧率: {fps}，应在5到60之间")
        
        # 更新比特率
        if bitrate is not None:
            if 100 <= bitrate <= 10000:
                old_bitrate = self.bitrate
                self.bitrate = bitrate
                changes.append(f"比特率: {old_bitrate} → {bitrate}Kbps")
            else:
                self.logger.warning(f"设备 {self.device_id} 无效的比特率: {bitrate}，应在100到10000之间")
        
        # 更新编码
        if encoding is not None:
            if encoding in ["H.264", "H.265", "MJPEG"]:
                old_encoding = self.encoding
                self.encoding = encoding
                changes.append(f"编码: {old_encoding} → {encoding}")
            else:
                self.logger.warning(f"设备 {self.device_id} 无效的编码: {encoding}")
        
        if changes:
            self.logger.info(f"设备 {self.device_id} 视频参数已更新: {', '.join(changes)}")
            
            # 如果正在流式传输，重新启动以应用新参数
            if self.is_streaming:
                self.is_streaming = False
                self.logger.info(f"设备 {self.device_id} 重新启动视频流以应用新参数")
                self.is_streaming = True
            
            return True
        
        return False