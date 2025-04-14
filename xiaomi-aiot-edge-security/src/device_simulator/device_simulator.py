#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设备模拟器模块
管理多个设备的模拟
"""

import logging
import time
from typing import List, Dict, Any, Optional
from .devices.device_base import DeviceBase

class DeviceSimulator:
    """设备模拟器类，管理多个设备的模拟"""

    def __init__(self, devices: List[DeviceBase]):
        """
        初始化设备模拟器
        
        Args:
            devices: 设备列表
        """
        self.logger = logging.getLogger(__name__)
        self.devices = devices
        self.active_devices = {}  # 活跃设备字典 {device_id: device}

    def start_device(self, device_id: str) -> bool:
        """
        启动指定设备
        
        Args:
            device_id: 设备ID
        
        Returns:
            bool: 启动成功返回True，否则返回False
        """
        for device in self.devices:
            if device.device_id == device_id:
                success = device.start()
                if success:
                    self.active_devices[device_id] = device
                return success
        
        self.logger.warning(f"未找到设备: {device_id}")
        return False

    def stop_device(self, device_id: str) -> bool:
        """
        停止指定设备
        
        Args:
            device_id: 设备ID
        
        Returns:
            bool: 停止成功返回True，否则返回False
        """
        if device_id in self.active_devices:
            success = self.active_devices[device_id].stop()
            if success:
                del self.active_devices[device_id]
            return success
        
        self.logger.warning(f"未找到活动设备: {device_id}")
        return False

    def start_all(self) -> Dict[str, bool]:
        """
        启动所有设备
        
        Returns:
            Dict[str, bool]: 设备ID与启动结果的字典
        """
        results = {}
        for device in self.devices:
            device_id = device.device_id
            success = device.start()
            if success:
                self.active_devices[device_id] = device
            results[device_id] = success
        
        self.logger.info(f"已启动 {sum(results.values())}/{len(results)} 个设备")
        return results

    def stop_all(self) -> Dict[str, bool]:
        """
        停止所有活跃设备
        
        Returns:
            Dict[str, bool]: 设备ID与停止结果的字典
        """
        results = {}
        
        # 创建设备ID列表的副本，因为我们会在迭代过程中修改字典
        device_ids = list(self.active_devices.keys())
        
        for device_id in device_ids:
            success = self.stop_device(device_id)
            results[device_id] = success
        
        self.logger.info(f"已停止 {sum(results.values())}/{len(results)} 个设备")
        return results

    def get_active_devices(self) -> List[str]:
        """
        获取所有活跃设备ID
        
        Returns:
            List[str]: 活跃设备ID列表
        """
        return list(self.active_devices.keys())

    def get_device_status(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定设备的状态
        
        Args:
            device_id: 设备ID
        
        Returns:
            Optional[Dict[str, Any]]: 设备状态，如果设备不存在则返回None
        """
        for device in self.devices:
            if device.device_id == device_id:
                return device.get_status()
        
        return None

    def get_all_devices_status(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有设备的状态
        
        Returns:
            Dict[str, Dict[str, Any]]: 设备ID与状态的字典
        """
        return {device.device_id: device.get_status() for device in self.devices}