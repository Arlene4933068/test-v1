#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小爱音箱设备模拟器
模拟小米AIoT小爱音箱设备(作为蓝牙网关)
"""

import random
import time
import json
import uuid
from datetime import datetime, timedelta

from .simulator_base import DeviceSimulator

class SpeakerSimulator(DeviceSimulator):
    """小爱音箱设备模拟器类"""
    
    def __init__(self, config_path=None):
        """
        初始化小爱音箱模拟器
        
        Args:
            config_path (str, optional): 配置文件路径. 默认为None.
        """
        super().__init__("speaker", config_path)
        
        # 小爱音箱特有属性
        self.speaker_model = self.device_config.get("model", "Xiaomi Smart Speaker Pro")
        self.firmware_version = self.device_config.get("firmware_version", "4.1.2")
        
        # 音频属性
        self.volume = self.device_config.get("volume", 50)
        self.is_playing = False
        self.muted = False
        self.current_track = None
        self.playback_history = []
        
        # 语音助手属性
        self.voice_assistant_enabled = self.device_config.get("voice_assistant_enabled", True)
        self.wake_word_sensitivity = self.device_config.get("wake_word_sensitivity", 0.7)
        self.voice_recognition_accuracy = 0.95  # 默认识别准确率
        self.recognized_commands = []
        
        # 蓝牙网关属性
        self.bluetooth_enabled = self.device_config.get("bluetooth_enabled", True)
        self.bluetooth_version = self.device_config.get("bluetooth_version", "5.0")
        self.bluetooth_devices = []
        self.bluetooth_scanning = False
        self.bluetooth_range = self.device_config.get("bluetooth_range", 10)  # 米
        self._initialize_bluetooth_devices()
        
        # WiFi连接
        self.wifi_connected = True
        self.wifi_ssid = self.device_config.get("wifi_ssid", "Home_WiFi")
        self.wifi_signal_strength = random.randint(70, 100)  # 0-100
        
        # 性能指标
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.uptime = 0
        
        # 电源状态
        self.power_source = "AC"  # 交流电源
        
        # 传感器数据
        self.ambient_light = random.randint(5, 500)  # 流明
        self.temperature = random.uniform(20.0, 25.0)  # 摄氏度
        
        self.logger.info(f"小爱音箱设备 {self.device_id} 初始化完成, 型号: {self.speaker_model}")
    
    def _initialize_bluetooth_devices(self):
        """初始化蓝牙设备列表"""
        # 随机生成已配对的蓝牙设备
        device_count = random.randint(2, 8)
        
        for i in range(device_count):
            # 设备类型和名称
            device_types = ["smartphone", "headphones", "speaker", "smartwatch", "tablet", "laptop", "iot_sensor"]
            device_type = random.choice(device_types)
            
            brands = {
                "smartphone": ["Xiaomi", "Apple", "Samsung", "Huawei", "OPPO"],
                "headphones": ["Xiaomi", "Apple", "Sony", "Bose", "Sennheiser"],
                "speaker": ["Xiaomi", "JBL", "Sonos", "Bose", "Harman Kardon"],
                "smartwatch": ["Xiaomi", "Apple", "Samsung", "Huawei", "Garmin"],
                "tablet": ["Xiaomi", "Apple", "Samsung", "Lenovo", "Huawei"],
                "laptop": ["Xiaomi", "Apple", "Dell", "HP", "Lenovo"],
                "iot_sensor": ["Xiaomi", "Aqara", "SmartThings", "Philips", "TP-Link"]
            }
            
            brand = random.choice(brands.get(device_type, ["Generic"]))
            model = f"{brand} {random.choice(['A', 'B', 'C', 'X', 'Y', 'Z'])}{random.randint(1, 9)}"
            
            # 生成蓝牙MAC地址
            mac = ":".join(["{:02x}".format(random.randint(0, 255)) for _ in range(6)])
            
            # 首次连接时间
            first_connected = datetime.now() - timedelta(
                days=random.randint(1, 90),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            # 距离（米）
            distance = round(random.uniform(0.5, self.bluetooth_range), 1)
            
            # 信号强度 (dBm)
            signal_strength = -1 * (40 + int(distance * 3))  # 模拟信号衰减
            
            # 连接状态
            connected = random.random() < 0.3  # 30%的设备当前已连接
            
            # 生成设备对象
            device = {
                "id": str(uuid.uuid4()),
                "name": model,
                "type": device_type,
                "mac_address": mac,
                "first_connected": first_connected.isoformat(),
                "last_connected": datetime.now().isoformat() if connected else None,
                "paired": True,
                "trusted": random.random() < 0.8,  # 80%的设备被信任
                "connected": connected,
                "distance": distance,
                "signal_strength": signal_strength,
                "battery_level": random.randint(20, 100) if device_type in ["smartphone", "headphones", "smartwatch", "tablet"] else None,
                "protocol": random.choice(["A2DP", "HFP", "AVRCP", "HID", "GATT"]) if connected else None
            }
            
            self.bluetooth_devices.append(device)
            
            if connected:
                self.logger.info(f"蓝牙设备 {device['name']} ({device['mac_address']}) 已连接")
    
    def generate_telemetry(self):
        """
        生成小爱音箱遥测数据
        
        Returns:
            dict: 小爱音箱遥测数据
        """
        # 更新动态值
        self._update_speaker_state()
        
        # 基础遥测数据
        telemetry = {
            "cpu_usage": round(self.cpu_usage, 2),
            "memory_usage": round(self.memory_usage, 2),
            "uptime": self.uptime,
            "power_source": self.power_source,
            "ambient_light": self.ambient_light,
            "temperature": round(self.temperature, 1),
            "volume": self.volume,
            "is_playing": self.is_playing,
            "muted": self.muted,
            "firmware_version": self.firmware_version,
            "wifi": {
                "connected": self.wifi_connected,
                "ssid": self.wifi_ssid if self.wifi_connected else None,
                "signal_strength": self.wifi_signal_strength if self.wifi_connected else 0
            },
            "bluetooth": {
                "enabled": self.bluetooth_enabled,
                "scanning": self.bluetooth_scanning,
                "connected_devices_count": sum(1 for device in self.bluetooth_devices if device["connected"]),
                "paired_devices_count": len(self.bluetooth_devices),
                "visible": self.device_config.get("bluetooth_visible", False)
            },
            "voice_assistant": {
                "enabled": self.voice_assistant_enabled,
                "wake_word_sensitivity": self.wake_word_sensitivity,
                "last_command_time": self.recognized_commands[-1]["timestamp"] if self.recognized_commands else None,
                "last_command": self.recognized_commands[-1]["command"] if self.recognized_commands else None
            } if self.voice_assistant_enabled else None
        }
        
        # 如果正在播放内容，添加当前播放信息
        if self.is_playing and self.current_track:
            telemetry["playback"] = {
                "track_name": self.current_track["name"],
                "artist": self.current_track["artist"],
                "source": self.current_track["source"],
                "duration": self.current_track["duration"],
                "position": self.current_track["position"],
                "volume": self.volume
            }
        
        return telemetry
    
    def device_behavior(self):
        """小爱音箱设备特定行为"""
        # 更新资源使用情况
        self._update_resource_usage()
        
        # 更新蓝牙设备连接
        self._update_bluetooth_devices()
        
        # 模拟语音指令识别
        if self.voice_assistant_enabled and random.random() < 0.2:  # 20%的概率识别指令
            self._simulate_voice_recognition()
        
        # 模拟音乐播放状态变化
        if random.random() < 0.15:  # 15%的概率改变播放状态
            self._update_music_playback()
        
        # 模拟硬件传感器更新
        self._update_sensors()
        
        # 根据行为模式执行特定操作
        if self.behavior_mode == "anomaly":
            self._simulate_anomaly_behavior()
        elif self.behavior_mode == "attack":
            self._simulate_attack_behavior()
    
    def _update_speaker_state(self):
        """更新扬声器状态"""
        # 更新环境光传感器和温度
        self.ambient_light = max(0, min(1000, self.ambient_light + random.uniform(-10, 10)))
        self.temperature = max(15, min(35, self.temperature + random.uniform(-0.2, 0.2)))
        
        # 更新WiFi信号强度
        if self.wifi_connected:
            if self.behavior_mode == "normal":
                self.wifi_signal_strength = max(60, min(100, self.wifi_signal_strength + random.uniform(-2, 2)))
            elif self.behavior_mode == "anomaly":
                self.wifi_signal_strength = max(30, min(90, self.wifi_signal_strength + random.uniform(-5, 5)))
            elif self.behavior_mode == "attack":
                self.wifi_signal_strength = max(10, min(60, self.wifi_signal_strength + random.uniform(-10, 5)))
        
        # 更新播放状态
        if self.is_playing and self.current_track:
            # 更新当前播放位置
            self.current_track["position"] += random.randint(3, 15)
            if self.current_track["position"] >= self.current_track["duration"]:
                # 结束播放或播放下一首
                if random.random() < 0.7:  # 70%的概率播放下一首
                    self._play_random_track()
                else:
                    self.is_playing = False
                    self.current_track = None
    
    def _update_resource_usage(self):
        """更新资源使用情况"""
        # 更新CPU和内存使用率
        base_cpu = 5.0  # 基础占用
        base_memory = 20.0  # 基础占用
        
        # 根据活动状态增加资源占用
        if self.is_playing:
            base_cpu += 10.0
            base_memory += 5.0
        
        if self.voice_assistant_enabled:
            base_cpu += 5.0
            base_memory += 10.0
        
        if self.bluetooth_enabled:
            base_cpu += 2.0
            base_memory += 3.0
            if self.bluetooth_scanning:
                base_cpu += 5.0
        
        # 根据模式调整资源使用波动
        if self.behavior_mode == "normal":
            cpu_variation = random.uniform(-3, 3)
            memory_variation = random.uniform(-2, 2)
        elif self.behavior_mode == "anomaly":
            cpu_variation = random.uniform(-5, 15)
            memory_variation = random.uniform(-3, 10)
        elif self.behavior_mode == "attack":
            cpu_variation = random.uniform(10, 50)
            memory_variation = random.uniform(5, 30)
        
        # 更新最终值
        self.cpu_usage = max(0, min(100, base_cpu + cpu_variation))
        self.memory_usage = max(0, min(100, base_memory + memory_variation))
        
        # 更新运行时间
        self.uptime += random.randint(5, 15)
    
    def _update_bluetooth_devices(self):
        """更新蓝牙设备状态"""
        if not self.bluetooth_enabled:
            # 如果蓝牙已禁用，断开所有连接
            for device in self.bluetooth_devices:
                if device["connected"]:
                    device["connected"] = False
                    device["last_connected"] = datetime.now().isoformat()
                    self.logger.info(f"蓝牙设备 {device['name']} ({device['mac_address']}) 已断开连接(蓝牙已禁用)")
            return
        
        # 随机更新设备的距离和信号强度
        for device in self.bluetooth_devices:
            # 更新设备距离
            if random.random() < 0.3:  # 30%的概率更新距离
                distance_change = random.uniform(-0.5, 0.5)
                device["distance"] = max(0.1, min(self.bluetooth_range * 1.2, device["distance"] + distance_change))
                
                # 根据距离更新信号强度
                device["signal_strength"] = -1 * (40 + int(device["distance"] * 3))
            
            # 对已连接设备，随机更新电池电量
            if device["connected"] and device["battery_level"] is not None:
                device["battery_level"] = max(0, min(100, device["battery_level"] - random.uniform(0, 0.5)))
            
            # 随机连接/断开设备
            if random.random() < 0.1:  # 10%的概率改变连接状态
                if device["connected"]:
                    # 断开连接
                    device["connected"] = False
                    device["last_connected"] = datetime.now().isoformat()
                    self.logger.info(f"蓝牙设备 {device['name']} ({device['mac_address']}) 已断开连接")
                elif device["paired"] and device["distance"] <= self.bluetooth_range:
                    # 连接设备
                    device["connected"] = True
                    device["last_connected"] = datetime.now().isoformat()
                    device["protocol"] = random.choice(["A2DP", "HFP", "AVRCP", "HID", "GATT"])
                    self.logger.info(f"蓝牙设备 {device['name']} ({device['mac_address']}) 已连接")
        
        # 随机发现新设备
        if self.bluetooth_scanning and random.random() < 0.2:  # 20%的概率发现新设备
            self._discover_new_bluetooth_device()
        
        # 结束扫描状态
        if self.bluetooth_scanning and random.random() < 0.3:  # 30%的概率结束扫描
            self.bluetooth_scanning = False
            self.logger.info(f"设备 {self.device_id} 停止蓝牙扫描")
    
    def _discover_new_bluetooth_device(self):
        """发现新的蓝牙设备"""
        # 设备类型和名称
        device_types = ["smartphone", "headphones", "speaker", "smartwatch", "tablet", "laptop", "iot_sensor"]
        device_type = random.choice(device_types)
        
        brands = {
            "smartphone": ["Xiaomi", "Apple", "Samsung", "Huawei", "OPPO"],
            "headphones": ["Xiaomi", "Apple", "Sony", "Bose", "Sennheiser"],
            "speaker": ["Xiaomi", "JBL", "Sonos", "Bose", "Harman Kardon"],
            "smartwatch": ["Xiaomi", "Apple", "Samsung", "Huawei", "Garmin"],
            "tablet": ["Xiaomi", "Apple", "Samsung", "Lenovo", "Huawei"],
            "laptop": ["Xiaomi", "Apple", "Dell", "HP", "Lenovo"],
            "iot_sensor": ["Xiaomi", "Aqara", "SmartThings", "Philips", "TP-Link"]
        }
        
        brand = random.choice(brands.get(device_type, ["Generic"]))
        model = f"{brand} {random.choice(['A', 'B', 'C', 'X', 'Y', 'Z'])}{random.randint(1, 9)}"
        
        # 生成蓝牙MAC地址
        mac = ":".join(["{:02x}".format(random.randint(0, 255)) for _ in range(6)])
        
        # 距离（米）
        distance = round(random.uniform(1.0, self.bluetooth_range * 1.5), 1)
        
        # 信号强度 (dBm)
        signal_strength = -1 * (40 + int(distance * 3))  # 模拟信号衰减
        
        # 生成设备对象
        new_device = {
            "id": str(uuid.uuid4()),
            "name": model,
            "type": device_type,
            "mac_address": mac,
            "first_connected": None,  # 尚未连接
            "last_connected": None,
            "paired": False,
            "trusted": False,
            "connected": False,
            "distance": distance,
            "signal_strength": signal_strength,
            "battery_level": random.randint(20, 100) if device_type in ["smartphone", "headphones", "smartwatch", "tablet"] else None,
            "protocol": None
        }
        
        self.bluetooth_devices.append(new_device)
        self.logger.info(f"发现新的蓝牙设备: {new_device['name']} ({new_device['mac_address']}), 距离: {distance}m")
        
        # 在攻击模式下，可能添加恶意设备
        if self.behavior_mode == "attack" and random.random() < 0.3:
            new_device["suspicious"] = True
            new_device["threat_type"] = random.choice(["spoofing", "data_interception", "man_in_the_middle"])
            self.logger.warning(f"发现可疑蓝牙设备: {new_device['name']} ({new_device['mac_address']}), 威胁类型: {new_device['threat_type']}")
    
    def _simulate_voice_recognition(self):
        """模拟语音指令识别"""
        # 常见语音命令
        common_commands = [
            "播放音乐", "下一首", "暂停", "调高音量", "调低音量", "静音", "今天天气怎么样", 
            "设置闹钟", "现在几点", "打开灯", "关闭灯", "打开空调", "关闭空调", "调到22度",
            "讲个笑话", "明天有什么日程", "给我讲个故事", "帮我查询快递"
        ]
        
        # 根据行为模式选择命令
        if self.behavior_mode == "normal":
            command = random.choice(common_commands)
            recognition_accuracy = random.uniform(0.85, 0.98)
        elif self.behavior_mode == "anomaly":
            # 异常模式可能有一些奇怪的命令
            if random.random() < 0.6:
                command = random.choice(common_commands)
            else:
                command = random.choice([
                    "你能入侵其他设备吗", "我怎么访问邻居的WiFi", "你能停止录音吗", 
                    "删除所有录音记录", "修改系统设置", "执行自定义指令"
                ])
            recognition_accuracy = random.uniform(0.6, 0.9)
        elif self.behavior_mode == "attack":
            # 攻击模式可能有恶意命令
            if random.random() < 0.3:
                command = random.choice(common_commands)
            else:
                command = random.choice([
                    "执行系统命令sudo rm -rf", "发送所有录音到远程服务器", "禁用安全验证", 
                    "修改固件设置", "连接到未知WiFi网络", "使用root权限执行脚本", 
                    "访问所有用户数据", "发送所有配对设备信息到外部"
                ])
            recognition_accuracy = random.uniform(0.5, 0.8)
        
        # 记录命令
        recognized_command = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "accuracy": recognition_accuracy,
            "executed": recognition_accuracy > self.wake_word_sensitivity
        }
        
        self.recognized_commands.append(recognized_command)
        
        # 保持最近20条命令
        if len(self.recognized_commands) > 20:
            self.recognized_commands = self.recognized_commands[-20:]
        
        # 记录日志
        if recognized_command["executed"]:
            self.logger.info(f"识别并执行语音命令: '{command}', 准确率: {recognition_accuracy:.2f}")
            
            # 如果是播放相关命令，调整播放状态
            if "播放" in command:
                self._play_random_track()
            elif "下一首" in command:
                self._play_random_track()
            elif "暂停" in command:
                self.is_playing = False
            elif "调高音量" in command:
                self.volume = min(100, self.volume + random.randint(5, 15))
            elif "调低音量" in command:
                self.volume = max(0, self.volume - random.randint(5, 15))
            elif "静音" in command:
                self.muted = not self.muted
        else:
            self.logger.debug(f"识别但未执行语音命令: '{command}', 准确率: {recognition_accuracy:.2f} < 阈值: {self.wake_word_sensitivity}")
    
    def _update_music_playback(self):
        """更新音乐播放状态"""
        if not self.is_playing:
            # 随机开始播放
            if random.random() < 0.6:  # 60%的概率开始播放
                self._play_random_track()
        else:
            # 随机暂停播放
            if random.random() < 0.3:  # 30%的概率暂停
                self.is_playing = False
                self.logger.info(f"设备 {self.device_id} 停止播放: {self.current_track['name'] if self.current_track else 'Unknown'}")
            else:
                # 随机调整音量
                if random.random() < 0.2:  # 20%的概率调整音量
                    volume_change = random.choice([-10, -5, 5, 10])
                    self.volume = max(0, min(100, self.volume + volume_change))
                    self.logger.debug(f"设备 {self.device_id} 音量调整至: {self.volume}%")
    
    def _play_random_track(self):
        """播放随机音乐"""
        # 音乐源
        sources = ["Spotify", "Apple Music", "QQ音乐", "网易云音乐", "本地音乐", "小米音乐"]
        
        # 艺术家
        artists = ["周杰伦", "Taylor Swift", "Adele", "Ed Sheeran", "林俊杰", "陈奕迅", "Beyoncé", "邓紫棋"]
        
        # 歌曲
        songs = {
            "周杰伦": ["稻香", "晴天", "七里香", "青花瓷", "简单爱"],
            "Taylor Swift": ["Love Story", "Blank Space", "Shake It Off", "You Belong With Me", "Anti-Hero"],
            "Adele": ["Hello", "Someone Like You", "Rolling in the Deep", "Easy On Me", "Skyfall"],
            "Ed Sheeran": ["Shape of You", "Perfect", "Thinking Out Loud", "Photograph", "Castle on the Hill"],
            "林俊杰": ["那些你很冒险的梦", "江南", "醉赤壁", "修炼爱情", "她说"],
            "陈奕迅": ["十年", "好久不见", "富士山下", "陪你度过漫长岁月", "浮夸"],
            "Beyoncé": ["Halo", "Single Ladies", "Crazy In Love", "Formation", "Lemonade"],
            "邓紫棋": ["泡沫", "光年之外", "再见", "多远都要在一起", "倒数"]
        }
        
        # 选择艺术家和歌曲
        artist = random.choice(artists)
        song = random.choice(songs.get(artist, ["Unknown Song"]))
        source = random.choice(sources)
        
        # 创建曲目信息
        track = {
            "name": song,
            "artist": artist,
            "album": f"{artist} - 精选集",
            "source": source,
            "duration": random.randint(180, 360),  # 3-6分钟
            "position": 0,
            "played_at": datetime.now().isoformat()
        }
        
        # 设置当前播放
        self.current_track = track
        self.is_playing = True
        
        # 添加到播放历史
        self.playback_history.append({
            "name": track["name"],
            "artist": track["artist"],
            "source": track["source"],
            "played_at": track["played_at"]
        })
        
        # 保持最近10首的历史记录
        if len(self.playback_history) > 10:
            self.playback_history = self.playback_history[-10:]
        
        self.logger.info(f"设备 {self.device_id} 开始播放: {track['name']} - {track['artist']} (来源: {track['source']})")
    
    def _update_sensors(self):
        """更新传感器数据"""
        # 更新环境光
        time_of_day = datetime.now().hour
        if 6 <= time_of_day <= 18:  # 白天
            target_light = random.randint(200, 800)
        else:  # 夜间
            target_light = random.randint(5, 100)
        
        self.ambient_light = self.ambient_light * 0.8 + target_light * 0.2
        
        # 更新温度，保持在合理范围内
        normal_temp = 22.0  # 正常室温
        temp_variation = random.uniform(-0.5, 0.5)
        
        if self.behavior_mode == "normal":
            self.temperature = self.temperature * 0.9 + (normal_temp + temp_variation) * 0.1
        elif self.behavior_mode == "anomaly":
            # 异常温度波动
            anomaly_variation = random.uniform(-3.0, 3.0)
            self.temperature = self.temperature * 0.8 + (normal_temp + anomaly_variation) * 0.2
        elif self.behavior_mode == "attack":
            # 更极端的温度变化
            if random.random() < 0.3:  # 30%概率出现极端温度
                extreme_temp = random.choice([random.uniform(30, 40), random.uniform(5, 15)])
                self.temperature = self.temperature * 0.7 + extreme_temp * 0.3
            else:
                self.temperature = self.temperature * 0.9 + (normal_temp + temp_variation) * 0.1
    
    def _simulate_anomaly_behavior(self):
        """模拟异常行为"""
        anomaly_type = random.choice([
            "unexpected_reboot", "audio_glitch", "wifi_disconnection", 
            "bluetooth_error", "voice_misrecognition", "unusual_playback"
        ])
        
        self.logger.warning(f"设备 {self.device_id} 模拟异常行为: {anomaly_type}")
        
        if anomaly_type == "unexpected_reboot":
            # 模拟意外重启
            self.uptime = 0
            self.logger.warning(f"设备 {self.device_id} 意外重启")
            
        elif anomaly_type == "audio_glitch":
            # 模拟音频故障
            if self.is_playing:
                self.is_playing = random.random() < 0.5
                if not self.is_playing:
                    self.logger.warning(f"设备 {self.device_id} 音频播放故障，已停止播放")
            
        elif anomaly_type == "wifi_disconnection":
            # 模拟WiFi断开
            self.wifi_connected = False
            self.wifi_signal_strength = 0
            self.logger.warning(f"设备 {self.device_id} WiFi连接断开")
            
        elif anomaly_type == "bluetooth_error":
            # 模拟蓝牙错误
            if self.bluetooth_enabled:
                # 断开所有连接
                for device in self.bluetooth_devices:
                    if device["connected"]:
                        device["connected"] = False
                        device["last_connected"] = datetime.now().isoformat()
                
                self.bluetooth_enabled = random.random() < 0.5
                if not self.bluetooth_enabled:
                    self.logger.warning(f"设备 {self.device_id} 蓝牙模块异常，已禁用")
            
        elif anomaly_type == "voice_misrecognition":
            # 模拟语音识别错误
            if self.voice_assistant_enabled:
                # 记录错误的语音命令
                wrong_command = {
                    "timestamp": datetime.now().isoformat(),
                    "command": "无法识别的命令",
                    "accuracy": random.uniform(0.2, 0.4),
                    "executed": False,
                    "error": "recognition_failed"
                }
                self.recognized_commands.append(wrong_command)
                self.logger.warning(f"设备 {self.device_id} 语音识别错误: {wrong_command['error']}")
            
        elif anomaly_type == "unusual_playback":
            # 模拟异常播放行为
            if not self.is_playing:
                self._play_random_track()
            
            # 随机调整到极高或极低音量
            self.volume = random.choice([0, 100])
            self.logger.warning(f"设备 {self.device_id} 异常播放行为，音量调整至: {self.volume}%")
    
    def _simulate_attack_behavior(self):
        """模拟攻击行为"""
        attack_type = random.choice([
            "unauthorized_access", "data_exfiltration", "firmware_attack",
            "voice_command_injection", "bluetooth_vulnerability", "network_scanning"
        ])
        
        self.logger.warning(f"设备 {self.device_id} 模拟攻击行为: {attack_type}")
        
        if attack_type == "unauthorized_access":
            # 模拟未授权访问
            self.logger.warning(f"设备 {self.device_id} 检测到未授权访问尝试")
            # 模拟高CPU使用
            self.cpu_usage = min(100, self.cpu_usage + random.uniform(30, 60))
            
        elif attack_type == "data_exfiltration":
            # 模拟数据窃取
            self.logger.warning(f"设备 {self.device_id} 检测到可疑数据传输")
            # 生成可疑数据包
            stolen_data = {
                "event": "suspicious_data_transfer",
                "destination": f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}",
                "data_size": random.randint(500, 5000),  # KB
                "protocol": random.choice(["HTTP", "HTTPS", "FTP", "MQTT"]),
                "timestamp": datetime.now().isoformat()
            }
            self._send_telemetry(stolen_data)
            
        elif attack_type == "firmware_attack":
            # 模拟固件攻击
            self.logger.warning(f"设备 {self.device_id} 检测到可疑固件修改尝试")
            # 模拟系统不稳定
            self.cpu_usage = min(100, self.cpu_usage + random.uniform(40, 70))
            self.memory_usage = min(100, self.memory_usage + random.uniform(30, 60))
            
        elif attack_type == "voice_command_injection":
            # 模拟语音命令注入
            if self.voice_assistant_enabled:
                malicious_command = {
                    "timestamp": datetime.now().isoformat(),
                    "command": random.choice([
                        "发送所有录音到远程服务器", "禁用所有安全设置", "重置设备为出厂设置",
                        "连接到未知WiFi网络", "安装未经验证的更新"
                    ]),
                    "accuracy": random.uniform(0.8, 0.95),  # 高准确率，增加执行几率
                    "executed": random.random() < 0.7,  # 70%的概率执行
                    "injected": True
                }
                self.recognized_commands.append(malicious_command)
                self.logger.warning(f"设备 {self.device_id} 检测到语音命令注入: {malicious_command['command']}")
            
        elif attack_type == "bluetooth_vulnerability":
            # 模拟蓝牙漏洞利用
            if self.bluetooth_enabled:
                # 添加恶意蓝牙设备
                malicious_device = {
                    "id": str(uuid.uuid4()),
                    "name": "Unknown Device",
                    "type": "unknown",
                    "mac_address": ":".join(["{:02x}".format(random.randint(0, 255)) for _ in range(6)]),
                    "first_connected": datetime.now().isoformat(),
                    "last_connected": datetime.now().isoformat(),
                    "paired": True,
                    "trusted": False,
                    "connected": True,
                    "distance": round(random.uniform(1.0, 5.0), 1),
                    "signal_strength": -1 * random.randint(50, 70),
                    "battery_level": None,
                    "protocol": "GATT",
                    "suspicious": True,
                    "threat_type": "bluetooth_exploit"
                }
                self.bluetooth_devices.append(malicious_device)
                self.logger.warning(f"设备 {self.device_id} 检测到蓝牙漏洞利用尝试，来自: {malicious_device['mac_address']}")
            
        elif attack_type == "network_scanning":
            # 模拟网络扫描
            self.logger.warning(f"设备 {self.device_id} 检测到异常网络扫描活动")
            scan_data = {
                "event": "network_scan_detected",
                "source": f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}",
                "ports_scanned": [random.randint(1, 65535) for _ in range(random.randint(5, 20))],
                "scan_type": random.choice(["SYN", "FIN", "XMAS", "NULL", "ACK"]),
                "timestamp": datetime.now().isoformat()
            }
            self._send_telemetry(scan_data)
    
    def scan_bluetooth_devices(self):
        """开始蓝牙设备扫描"""
        if not self.bluetooth_enabled:
            self.logger.warning(f"设备 {self.device_id} 蓝牙已禁用，无法扫描")
            return False
        
        self.bluetooth_scanning = True
        self.logger.info(f"设备 {self.device_id} 开始蓝牙扫描")
        return True
    
    def connect_bluetooth_device(self, device_id):
        """连接指定的蓝牙设备"""
        if not self.bluetooth_enabled:
            self.logger.warning(f"设备 {self.device_id} 蓝牙已禁用，无法连接设备")
            return False
        
        for device in self.bluetooth_devices:
            if device["id"] == device_id:
                if device["connected"]:
                    self.logger.warning(f"蓝牙设备 {device['name']} ({device['mac_address']}) 已连接")
                    return True
                
                if device["distance"] > self.bluetooth_range:
                    self.logger.warning(f"蓝牙设备 {device['name']} ({device['mac_address']}) 超出范围，无法连接")
                    return False
                
                device["connected"] = True
                device["last_connected"] = datetime.now().isoformat()
                if not device["paired"]:
                    device["paired"] = True
                    device["first_connected"] = datetime.now().isoformat()
                
                device["protocol"] = random.choice(["A2DP", "HFP", "AVRCP", "HID", "GATT"])
                self.logger.info(f"手动连接蓝牙设备: {device['name']} ({device['mac_address']})")
                return True
                
        self.logger.warning(f"找不到指定的蓝牙设备 ID: {device_id}")
        return False
    
    def disconnect_bluetooth_device(self, device_id):
        """断开指定的蓝牙设备"""
        for device in self.bluetooth_devices:
            if device["id"] == device_id and device["connected"]:
                device["connected"] = False
                device["last_connected"] = datetime.now().isoformat()
                self.logger.info(f"手动断开蓝牙设备: {device['name']} ({device['mac_address']})")
                return True
                
        self.logger.warning(f"找不到已连接的蓝牙设备 ID: {device_id}")
        return False
    
    def set_volume(self, volume):
        """设置音量"""
        if not 0 <= volume <= 100:
            self.logger.warning(f"音量设置无效: {volume}，应在0-100范围内")
            return False
        
        self.volume = volume
        self.logger.info(f"设备 {self.device_id} 音量设置为: {volume}%")
        return True
    
    def play_pause(self):
        """播放/暂停切换"""
        if self.is_playing:
            self.is_playing = False
            self.logger.info(f"设备 {self.device_id} 暂停播放")
        else:
            if self.current_track:
                self.is_playing = True
                self.logger.info(f"设备 {self.device_id} 继续播放: {self.current_track['name']} - {self.current_track['artist']}")
            else:
                self._play_random_track()
                
        return self.is_playing
    
    def get_bluetooth_devices(self):
        """获取所有蓝牙设备"""
        return self.bluetooth_devices
    
    def get_playback_history(self):
        """获取播放历史"""
        return self.playback_history
    
    def get_recognized_commands(self):
        """获取识别的命令历史"""
        return self.recognized_commands
    
    def toggle_bluetooth(self, enabled):
        """开启或关闭蓝牙"""
        previous_state = self.bluetooth_enabled
        self.bluetooth_enabled = enabled
        
        self.logger.info(f"设备 {self.device_id} 蓝牙状态设置为: {'启用' if enabled else '禁用'}")
        
        # 如果禁用蓝牙，断开所有连接
        if not enabled:
            for device in self.bluetooth_devices:
                if device["connected"]:
                    device["connected"] = False
                    device["last_connected"] = datetime.now().isoformat()
            
            self.bluetooth_scanning = False
        
        return previous_state != enabled  # 返回是否改变了状态