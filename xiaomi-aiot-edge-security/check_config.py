#!/usr/bin/env python3
# 配置检查脚本

import os
import sys
import yaml
import json
import logging
from pprint import pprint

def main():
    # 设置基本日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    
    logger = logging.getLogger("ConfigChecker")
    
    # 项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 检查配置文件
    config_dir = os.path.join(project_root, "config")
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
        logger.warning(f"创建了配置目录: {config_dir}")
    
    # 平台配置
    platform_config_path = os.path.join(config_dir, "platform.yaml")
    if not os.path.exists(platform_config_path):
        # 创建默认配置
        default_config = {
            "platform": {
                "edgex": {
                    "host": "localhost",
                    "port": 59880,
                    "metadata_port": 59881,
                    "core_command_port": 59882,
                    "api_version": "v2",
                    "device_service_name": "xiaomi-device-service"
                },
                "thingsboard": {
                    "host": "localhost",
                    "port": 8080,
                    "username": "yy3205543808@gmail.com",
                    "password": "wlsxcdh52jy.L"
                }
            },
            "security": {
                "scan_interval": 10,
                "detection_threshold": 0.7,
                "enable_attack_simulation": True,
                "simulation_probability": 0.1
            },
            "analytics": {
                "output_dir": "output",
                "report_interval": 3600
            },
            "edge_protection": {
                "protection_level": "medium",
                "enable_firewall": True,
                "enable_ids": True,
                "enable_data_protection": True,
                "device_whitelist": [
                    "xiaomi_gateway_01",
                    "xiaomi_router_01",
                    "xiaomi_speaker_01",
                    "xiaomi_camera_01"
                ]
            }
        }
        
        with open(platform_config_path, "w", encoding="utf-8") as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        logger.info(f"创建了默认平台配置: {platform_config_path}")
    
    try:
        # 加载平台配置
        with open(platform_config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        # 检查配置是否有效
        logger.info("成功加载平台配置")
        logger.info("配置包含以下部分:")
        
        # 输出配置节
        for section in config:
            print(f"- {section}")
        
        # 检查必要的配置部分
        required_sections = ["platform", "security", "analytics"]
        missing_sections = [section for section in required_sections if section not in config]
        
        if missing_sections:
            logger.warning(f"缺少以下配置部分: {', '.join(missing_sections)}")
        
        # 查看是否启用了边缘计算防护
        if "edge_protection" in config:
            print("
边缘计算防护配置:")
            pprint(config["edge_protection"])
        else:
            logger.warning("未配置边缘计算防护!")
            
    except Exception as e:
        logger.error(f"检查配置时发生错误: {str(e)}")
        return False
    
    print("
配置检查完成。如果需要，请编辑 config/platform.yaml 文件以更新配置。")
    return True

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
