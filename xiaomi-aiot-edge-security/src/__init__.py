# 工具包初始化文件#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小米AIoT边缘安全防护研究平台

该包包含以下主要模块:
- device_simulator: 边缘设备模拟器，模拟各种AIoT设备
- platform_connector: 平台连接器，连接EdgeX Foundry和ThingsBoard Edge
- security: 安全防护模块，包括攻击检测和防护
- analytics: 数据分析模块，收集和分析安全数据
- dashboard: 控制面板，提供UI界面进行监控和控制
- utils: 工具类，提供各种通用功能
"""

__version__ = '1.0.0'
__author__ = 'Xiaomi AIoT Edge Security Research Team'

import os
import sys

# 确保可以导入本包中的模块
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))