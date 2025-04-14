#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
项目结构重组脚本
用于规范化项目目录结构
"""

import os
import shutil
import sys

def reorganize_project():
    """重组项目结构，规范化目录名称和组织"""
    # 项目根目录
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    # 1. 创建标准化的虚拟环境目录
    venv_dir = os.path.join(root_dir, 'venv')
    if not os.path.exists(venv_dir):
        os.makedirs(venv_dir)
        print(f"创建标准虚拟环境目录: {venv_dir}")
    
    # 2. 移动不规范的虚拟环境目录内容
    old_venv = os.path.join(os.path.dirname(root_dir), '0pjtest-v1xiaomi-aiot-edge-securityvenv')
    if os.path.exists(old_venv):
        # 仅移动必要文件，避免复制整个虚拟环境
        print(f"检测到不规范虚拟环境目录: {old_venv}")
        print("请手动创建新的虚拟环境: python -m venv venv")
    
    # 3. 整合security目录
    security_dir = os.path.join(os.path.dirname(root_dir), 'security')
    if os.path.exists(security_dir):
        target_dir = os.path.join(root_dir, 'src', 'security')
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        
        # 复制文件
        for item in os.listdir(security_dir):
            s = os.path.join(security_dir, item)
            d = os.path.join(target_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
        print(f"整合security目录到: {target_dir}")
    
    print("项目结构重组完成！")

if __name__ == "__main__":
    reorganize_project()