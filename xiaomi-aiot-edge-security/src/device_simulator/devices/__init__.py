"""
设备模块初始化文件
"""
from .device_base import DeviceBase
from .gateway import Gateway
from .router import Router
from .smart_speaker import SmartSpeaker
from .camera import Camera

__all__ = [
    'DeviceBase',
    'Gateway',
    'Router',
    'SmartSpeaker',
    'Camera'
]