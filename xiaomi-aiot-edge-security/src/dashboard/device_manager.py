# src/dashboard/device_manager.py
import uuid
import time
from ..utils.logger import get_logger
from ..platform_connector.edgex_connector import EdgeXConnector
from ..platform_connector.thingsboard_connector import ThingsBoardConnector

class DeviceManager:
    """设备管理器：管理边缘设备的创建、删除和监控"""
    
    def __init__(self, config=None):
        self.logger = get_logger("DeviceManager")
        self.config = config
        self.edgex_connector = EdgeXConnector(config)
        self.thingsboard_connector = ThingsBoardConnector(config)
        self.devices = {}  # 本地设备缓存
        self.logger.info("设备管理器初始化完成")
    
    def add_device(self, device_type, name, platform, properties=None):
        """添加设备
        
        Args:
            device_type: 设备类型 (gateway, router, speaker, camera)
            name: 设备名称
            platform: 平台 (edgex, thingsboard)
            properties: 设备属性
            
        Returns:
            dict: 添加结果
        """
        properties = properties or {}
        device_id = str(uuid.uuid4())
        
        try:
            # 根据平台类型选择连接器
            if platform.lower() == "edgex":
                result = self.edgex_connector.add_device(
                    device_id=device_id,
                    device_type=device_type,
                    name=name,
                    properties=properties
                )
            elif platform.lower() == "thingsboard":
                result = self.thingsboard_connector.add_device(
                    device_id=device_id,
                    device_type=device_type,
                    name=name,
                    properties=properties
                )
            else:
                raise ValueError(f"不支持的平台类型: {platform}")
            
            # 缓存设备信息
            if result.get("success"):
                self.devices[device_id] = {
                    "id": device_id,
                    "type": device_type,
                    "name": name,
                    "platform": platform,
                    "properties": properties,
                    "status": "active",
                    "created_at": time.time()
                }
                self.logger.info(f"设备添加成功: {name} ({device_type}) on {platform}")
                return {
                    "device_id": device_id,
                    "platform": platform,
                    "name": name,
                    "type": device_type
                }
            else:
                self.logger.error(f"设备添加失败: {result.get('message')}")
                raise Exception(result.get("message", "添加设备失败"))
                
        except Exception as e:
            self.logger.error(f"添加设备出错: {str(e)}")
            raise
    
    def remove_device(self, device_id, platform):
        """移除设备
        
        Args:
            device_id: 设备ID
            platform: 平台 (edgex, thingsboard)
            
        Returns:
            dict: 移除结果
        """
        try:
            # 根据平台类型选择连接器
            if platform.lower() == "edgex":
                result = self.edgex_connector.remove_device(device_id)
            elif platform.lower() == "thingsboard":
                result = self.thingsboard_connector.remove_device(device_id)
            else:
                raise ValueError(f"不支持的平台类型: {platform}")
            
            # 从缓存中移除设备
            if result.get("success") and device_id in self.devices:
                device_name = self.devices[device_id]["name"]
                device_type = self.devices[device_id]["type"]
                del self.devices[device_id]
                self.logger.info(f"设备移除成功: {device_name} ({device_type}) from {platform}")
                return {
                    "device_id": device_id,
                    "platform": platform
                }
            elif device_id not in self.devices:
                self.logger.warning(f"设备 {device_id} 不在本地缓存中")
                return {
                    "device_id": device_id,
                    "platform": platform
                }
            else:
                self.logger.error(f"设备移除失败: {result.get('message')}")
                raise Exception(result.get("message", "移除设备失败"))
                
        except Exception as e:
            self.logger.error(f"移除设备出错: {str(e)}")
            raise
    
    def get_device(self, device_id):
        """获取设备信息
        
        Args:
            device_id: 设备ID
            
        Returns:
            dict: 设备信息
        """
        device = self.devices.get(device_id)
        if not device:
            self.logger.warning(f"设备不存在: {device_id}")
            return None
            
        # 获取实时状态
        try:
            if device["platform"].lower() == "edgex":
                status = self.edgex_connector.get_device_status(device_id)
            elif device["platform"].lower() == "thingsboard":
                status = self.thingsboard_connector.get_device_status(device_id)
            else:
                status = {"status": "unknown"}
                
            device.update(status)
            return device
        except Exception as e:
            self.logger.error(f"获取设备状态出错: {str(e)}")
            device["status"] = "error"
            device["error"] = str(e)
            return device
    
    def get_all_devices(self):
        """获取所有设备列表
        
        Returns:
            list: 设备列表
        """
        return list(self.devices.values())
    
    def get_all_device_status(self):
        """获取所有设备状态
        
        Returns:
            dict: 设备状态信息
        """
        status = {
            "total": len(self.devices),
            "active": 0,
            "inactive": 0,
            "error": 0,
            "by_type": {},
            "by_platform": {}
        }
        
        for device in self.devices.values():
            # 获取实时状态
            try:
                if device["platform"].lower() == "edgex":
                    device_status = self.edgex_connector.get_device_status(device["id"])
                elif device["platform"].lower() == "thingsboard":
                    device_status = self.thingsboard_connector.get_device_status(device["id"])
                else:
                    device_status = {"status": "unknown"}
                
                device_state = device_status.get("status", "unknown")
            except Exception as e:
                self.logger.error(f"获取设备 {device['name']} 状态出错: {str(e)}")
                device_state = "error"
            
            # 更新计数
            if device_state == "active":
                status["active"] += 1
            elif device_state == "error":
                status["error"] += 1
            else:
                status["inactive"] += 1
            
            # 按类型统计
            device_type = device["type"]
            if device_type not in status["by_type"]:
                status["by_type"][device_type] = {
                    "total": 0, "active": 0, "inactive": 0, "error": 0
                }
            
            status["by_type"][device_type]["total"] += 1
            if device_state == "active":
                status["by_type"][device_type]["active"] += 1
            elif device_state == "error":
                status["by_type"][device_type]["error"] += 1
            else:
                status["by_type"][device_type]["inactive"] += 1
            
            # 按平台统计
            platform = device["platform"]
            if platform not in status["by_platform"]:
                status["by_platform"][platform] = {
                    "total": 0, "active": 0, "inactive": 0, "error": 0
                }
            
            status["by_platform"][platform]["total"] += 1
            if device_state == "active":
                status["by_platform"][platform]["active"] += 1
            elif device_state == "error":
                status["by_platform"][platform]["error"] += 1
            else:
                status["by_platform"][platform]["inactive"] += 1
        
        return status
    
    def sync_devices(self):
        """同步设备信息，从平台获取最新设备列表
        
        Returns:
            dict: 同步结果
        """
        try:
            # 从EdgeX同步
            edgex_devices = self.edgex_connector.get_all_devices()
            
            # 从ThingsBoard同步
            thingsboard_devices = self.thingsboard_connector.get_all_devices()
            
            # 合并设备列表
            all_devices = {}
            
            for device in edgex_devices:
                all_devices[device["id"]] = {
                    **device,
                    "platform": "edgex"
                }
            
            for device in thingsboard_devices:
                all_devices[device["id"]] = {
                    **device,
                    "platform": "thingsboard"
                }
            
            # 更新本地缓存
            self.devices = all_devices
            
            self.logger.info(f"设备同步完成，共 {len(self.devices)} 个设备")
            return {
                "success": True,
                "count": len(self.devices),
                "by_platform": {
                    "edgex": len(edgex_devices),
                    "thingsboard": len(thingsboard_devices)
                }
            }
        except Exception as e:
            self.logger.error(f"同步设备出错: {str(e)}")
            raise