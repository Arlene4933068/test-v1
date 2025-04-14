#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小米AIoT边缘安全防护研究平台 - 主入口
"""

import os
import sys
import time
import yaml
import logging
import argparse
import threading
from typing import Dict, Any

# 确保可以导入本项目模块
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.utils.logger import setup_logger, get_logger
from src.device_simulator import DeviceFactory, DeviceSimulator
from src.platform_connector import EdgeXConnector, ThingsBoardConnector
from src.security import SecurityNode, AttackSimulator
from src.analytics import StatisticalAnalyzer, DataCollector, ReportGenerator

def load_config(config_file: str) -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        config_file: 配置文件路径
    
    Returns:
        Dict[str, Any]: 配置字典
    """
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"加载配置文件失败: {str(e)}")
        return {}

def setup_directories(config: Dict[str, Any]):
    """
    设置必要的目录结构
    
    Args:
        config: 配置字典
    """
    # 分析数据目录
    analytics_config = config.get("analytics", {})
    data_dir = analytics_config.get("data_dir", "data")
    output_dir = analytics_config.get("output_dir", "output")
    
    # 创建目录
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(data_dir, "device_data"), exist_ok=True)
    os.makedirs(os.path.join(data_dir, "security_data"), exist_ok=True)
    os.makedirs(os.path.join(data_dir, "performance_data"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "reports"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "visualizations"), exist_ok=True)

def run_platform(config: Dict[str, Any], logger):
    """
    运行平台
    
    Args:
        config: 配置字典
        logger: 日志记录器
    """
    # 1. 初始化平台连接器
    platform_config = config.get("platform", {})
    
    # 初始化EdgeX连接器
    edgex_config = platform_config.get("edgex", {})
    edgex_connector = EdgeXConnector(edgex_config)
    
    # 初始化ThingsBoard连接器
    thingsboard_config = platform_config.get("thingsboard", {})
    thingsboard_connector = ThingsBoardConnector(thingsboard_config)
    
    # 2. 连接到平台
    edgex_connected = edgex_connector.connect()
    thingsboard_connected = thingsboard_connector.connect()
    
    if not edgex_connected:
        logger.warning("无法连接到EdgeX Foundry，设备将不会注册到EdgeX")
    
    if not thingsboard_connected:
        logger.warning("无法连接到ThingsBoard Edge，设备将不会注册到ThingsBoard")
    
    # 3. 初始化设备工厂
    device_config = {
        "edgex": edgex_config,
        "thingsboard": thingsboard_config,
        "devices": config.get("devices", {}).get("list", [])
    }
    
    device_factory = DeviceFactory(device_config)
    if not device_factory.initialize():
        logger.error("初始化设备工厂失败")
        return
    
    # 4. 创建设备
    devices = device_factory.create_all_devices()
    if not devices:
        logger.error("创建设备失败")
        return
    
    logger.info(f"成功创建 {len(devices)} 个设备")
    
    # 5. 初始化设备模拟器
    device_simulator = DeviceSimulator(list(devices.values()))
    
    # 6. 初始化安全节点
    security_config = config.get("security", {})
    security_nodes = []
    
    # 创建安全节点
    for node_config in security_config.get("nodes", []):
        node = SecurityNode(node_config, node_id=node_config.get("node_id"))
        security_nodes.append(node)
    
    # 7. 初始化攻击模拟器
    attack_simulator = AttackSimulator(security_config.get("attack_simulator", {}))
    
    # 8. 初始化数据分析组件
    analytics_config = config.get("analytics", {})
    data_collector = DataCollector(analytics_config)
    statistical_analyzer = StatisticalAnalyzer(analytics_config)
    report_generator = ReportGenerator(analytics_config)
    
    try:
        # 启动设备模拟
        device_simulator.start_all()
        logger.info("设备模拟已启动")
        
        # 启动安全节点
        for node in security_nodes:
            node.start()
        logger.info("安全节点已启动")
        
        # 启动攻击模拟
        attack_simulator.start_simulation()
        logger.info("攻击模拟已启动")
        
        # 启动数据收集
        data_collector.start()
        logger.info("数据收集已启动")
        
        # 每小时生成分析报告的线程
        def analysis_task():
            while True:
                try:
                    # 生成可视化
                    statistical_analyzer.generate_visualizations()
                    
                    # 等待1小时
                    time.sleep(3600)
                except Exception as e:
                    logger.error(f"分析任务错误: {str(e)}")
                    time.sleep(300)  # 错误后等待5分钟再试
        
        analysis_thread = threading.Thread(target=analysis_task)
        analysis_thread.daemon = True
        analysis_thread.start()
        
        # 保持程序运行
        logger.info("小米AIoT边缘安全防护研究平台已启动")
        logger.info("按Ctrl+C停止...")
        
        # 主循环
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("收到停止信号，正在关闭平台...")
    finally:
        # 停止所有组件
        device_simulator.stop_all()
        attack_simulator.stop_simulation()
        data_collector.stop()
        
        for node in security_nodes:
            node.stop()
        
        # 断开平台连接
        thingsboard_connector.disconnect()
        edgex_connector.disconnect()
        
        logger.info("小米AIoT边缘安全防护研究平台已停止")

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='小米AIoT边缘安全防护研究平台')
    parser.add_argument('--config', '-c', default='config/platform.yaml', help='配置文件路径')
    parser.add_argument('--log-level', '-l', default='info', choices=['debug', 'info', 'warning', 'error'], help='日志级别')
    args = parser.parse_args()
    
    # 设置日志
    log_level = getattr(logging, args.log_level.upper())
    setup_logger(level=log_level)
    logger = get_logger(__name__)
    
    # 加载配置
    config = load_config(args.config)
    if not config:
        logger.error("加载配置失败，退出程序")
        sys.exit(1)
    
    # 设置目录
    setup_directories(config)
    
    # 运行平台
    run_platform(config, logger)

if __name__ == '__main__':
    main()