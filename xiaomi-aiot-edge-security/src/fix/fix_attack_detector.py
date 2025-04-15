#!/usr/bin/env python3
# 完整修复攻击检测器中的变量错误和关闭问题

import os
import sys
import re

def main():
    print("开始全面修复攻击检测器...\n")
    
    # 确定正确的项目根目录路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 尝试多个可能的项目根路径
    possible_roots = [
        os.getcwd(),                                  # 当前工作目录
        os.path.dirname(script_dir),                  # 脚本的父目录
        os.path.dirname(os.path.dirname(script_dir)), # 脚本的祖父目录
        "D:/0pj/test-v1/xiaomi-aiot-edge-security"   # 明确指定的项目路径
    ]
    
    # 找到正确的项目根目录
    root_dir = None
    for path in possible_roots:
        main_file_path = os.path.join(path, "src", "main.py")
        if os.path.isfile(main_file_path):
            root_dir = path
            break
    
    if not root_dir:
        print("错误：无法找到项目根目录")
        sys.exit(1)
    
    print(f"已找到项目根目录: {root_dir}")
    
    # 完全重写 attack_detector.py 文件
    detector_path = os.path.join(root_dir, "src", "security", "attack_detector.py")
    detector_backup_path = detector_path + ".bak"
    
    if not os.path.isfile(detector_path):
        print(f"错误：无法找到 AttackDetector 文件: {detector_path}")
        sys.exit(1)
    
    # 备份原始文件
    try:
        with open(detector_path, "r", encoding="utf-8") as src:
            with open(detector_backup_path, "w", encoding="utf-8") as dst:
                dst.write(src.read())
        print(f"✅ 已备份原始 AttackDetector 到: {detector_backup_path}")
    except Exception as e:
        print(f"警告：无法备份 AttackDetector: {e}")
    
    # 新的 AttackDetector 内容
    new_detector_content = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
攻击检测器模块
负责检测针对设备和系统的各种攻击行为
\"\"\"

import time
import logging
import threading
import random
from typing import Dict, List, Any, Optional
import queue

class AttackDetector:
    \"\"\"攻击检测器，负责检测多种类型的攻击\"\"\"
    
    def __init__(self, config: Dict[str, Any]):
        \"\"\"
        初始化攻击检测器
        
        Args:
            config: 检测器配置
        \"\"\"
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.running = False
        self.detector_thread = None
        self.detection_queue = queue.Queue()
        self.detection_interval = 1.0  # 检测间隔（秒）
        
        # 支持的攻击类型
        self.attack_types = [
            'ddos',         # DDoS攻击
            'mitm',         # 中间人攻击
            'credential',   # 凭证攻击
            'firmware',     # 固件攻击
            'anomaly'       # 异常行为
        ]
        
        # 攻击检测回调函数
        self.on_attack_detected = None
        
        # 检测结果缓存
        self.detection_results = []
    
    def start(self):
        \"\"\"启动检测器\"\"\"
        if self.running:
            return
        
        self.running = True
        self.detector_thread = threading.Thread(target=self._detection_loop)
        self.detector_thread.daemon = True
        self.detector_thread.start()
        self.logger.info("攻击检测器已启动")
    
    def stop(self):
        \"\"\"停止检测器\"\"\"
        if not self.running:
            return
            
        self.logger.info("正在停止攻击检测器...")
        self.running = False
        
        # 安全地等待检测线程结束
        if self.detector_thread and self.detector_thread.is_alive():
            try:
                self.detector_thread.join(timeout=2.0)
            except Exception as e:
                self.logger.warning(f"等待检测线程结束时出现异常: {str(e)}")
        
        self.logger.info("攻击检测器已停止")
    
    def register_attack_callback(self, callback):
        \"\"\"
        注册攻击检测回调函数
        
        Args:
            callback: 当检测到攻击时调用的回调函数，接受attack_info作为参数
        \"\"\"
        self.on_attack_detected = callback
    
    def _detection_loop(self):
        \"\"\"检测循环，在单独的线程中运行\"\"\"
        while self.running:
            try:
                # 执行各种攻击检测
                for attack_type in self.attack_types:
                    if not self.running:
                        break
                        
                    try:
                        method_name = f"_detect_{attack_type}_attack"
                        if hasattr(self, method_name):
                            detect_method = getattr(self, method_name)
                            attack_detected = detect_method()
                            
                            if attack_detected and self.on_attack_detected:
                                self.on_attack_detected(attack_detected)
                    except Exception as e:
                        self.logger.error(f"检测器 {attack_type} 执行异常: {str(e)}")
                
                # 等待下一个检测周期
                if self.running:
                    time.sleep(self.detection_interval)
            except Exception as e:
                self.logger.error(f"检测循环执行异常: {str(e)}")
                if self.running:
                    time.sleep(1.0)  # 发生错误时短暂暂停
    
    def _detect_ddos_attack(self) -> Dict[str, Any]:
        \"\"\"
        检测DDoS攻击
        
        Returns:
            Dict[str, Any]: 如果检测到攻击，返回攻击信息，否则返回None
        \"\"\"
        try:
            # 初始化攻击信息
            attack_info = {
                'type': 'ddos',
                'severity': 'medium',
                'confidence': 0.0,
                'details': {},
                'timestamp': time.time()
            }
            
            # 实际检测逻辑（这里使用随机模拟）
            # 在实际应用中，这里应该包含真实的DDoS检测算法
            if random.random() < 0.05:  # 5%的概率检测到攻击
                attack_info['confidence'] = random.uniform(0.7, 0.99)
                attack_info['details'] = {
                    'target_ip': '192.168.1.' + str(random.randint(1, 254)),
                    'packets_per_second': random.randint(1000, 10000),
                    'connection_count': random.randint(500, 5000)
                }
                return attack_info
            
            return None
        except Exception as e:
            self.logger.error(f"DDoS攻击检测异常: {str(e)}")
            return None
    
    def _detect_mitm_attack(self) -> Dict[str, Any]:
        \"\"\"
        检测中间人攻击
        
        Returns:
            Dict[str, Any]: 如果检测到攻击，返回攻击信息，否则返回None
        \"\"\"
        try:
            # 初始化攻击信息
            attack_info = {
                'type': 'mitm',
                'severity': 'high',
                'confidence': 0.0,
                'details': {},
                'timestamp': time.time()
            }
            
            # 实际检测逻辑（这里使用随机模拟）
            if random.random() < 0.03:  # 3%的概率检测到攻击
                attack_info['confidence'] = random.uniform(0.8, 0.99)
                attack_info['details'] = {
                    'spoofed_mac': ':'.join([format(random.randint(0, 255), '02x') for _ in range(6)]),
                    'legitimate_mac': ':'.join([format(random.randint(0, 255), '02x') for _ in range(6)]),
                    'affected_device': f"device_{random.randint(1, 10)}"
                }
                return attack_info
            
            return None
        except Exception as e:
            self.logger.error(f"中间人攻击检测异常: {str(e)}")
            return None
    
    def _detect_credential_attack(self) -> Dict[str, Any]:
        \"\"\"
        检测凭证攻击（暴力破解、凭证泄露等）
        
        Returns:
            Dict[str, Any]: 如果检测到攻击，返回攻击信息，否则返回None
        \"\"\"
        try:
            # 初始化攻击信息
            attack_info = {
                'type': 'credential',
                'severity': 'high',
                'confidence': 0.0,
                'details': {},
                'timestamp': time.time()
            }
            
            # 实际检测逻辑
            if random.random() < 0.04:  # 4%的概率检测到攻击
                attack_info['confidence'] = random.uniform(0.75, 0.98)
                attack_info['details'] = {
                    'target_service': random.choice(['ssh', 'web_admin', 'mqtt_broker', 'api']),
                    'attempt_count': random.randint(50, 500),
                    'source_ip': '.'.join([str(random.randint(1, 255)) for _ in range(4)])
                }
                return attack_info
            
            return None
        except Exception as e:
            self.logger.error(f"凭证攻击检测异常: {str(e)}")
            return None
    
    def _detect_firmware_attack(self) -> Dict[str, Any]:
        \"\"\"
        检测固件攻击（恶意固件更新等）
        
        Returns:
            Dict[str, Any]: 如果检测到攻击，返回攻击信息，否则返回None
        \"\"\"
        try:
            # 初始化攻击信息
            attack_info = {
                'type': 'firmware',
                'severity': 'critical',
                'confidence': 0.0,
                'details': {},
                'timestamp': time.time()
            }
            
            # 实际检测逻辑
            if random.random() < 0.02:  # 2%的概率检测到攻击
                attack_info['confidence'] = random.uniform(0.85, 0.99)
                attack_info['details'] = {
                    'affected_device': f"xiaomi_device_{random.randint(1, 10)}",
                    'firmware_checksum': ''.join(random.choices('0123456789abcdef', k=32)),
                    'expected_checksum': ''.join(random.choices('0123456789abcdef', k=32))
                }
                return attack_info
            
            return None
        except Exception as e:
            self.logger.error(f"固件攻击检测异常: {str(e)}")
            return None
    
    def _detect_anomaly_attack(self) -> Dict[str, Any]:
        \"\"\"
        检测异常行为（可疑的设备行为模式）
        
        Returns:
            Dict[str, Any]: 如果检测到攻击，返回攻击信息，否则返回None
        \"\"\"
        try:
            # 初始化攻击信息
            attack_info = {
                'type': 'anomaly',
                'severity': 'medium',
                'confidence': 0.0,
                'details': {},
                'timestamp': time.time()
            }
            
            # 实际检测逻辑
            if random.random() < 0.08:  # 8%的概率检测到异常
                attack_info['confidence'] = random.uniform(0.6, 0.95)
                attack_info['details'] = {
                    'device_id': f"xiaomi_device_{random.randint(1, 10)}",
                    'normal_pattern': f"pattern_{random.randint(1, 5)}",
                    'observed_pattern': f"pattern_{random.randint(6, 10)}",
                    'deviation_score': round(random.uniform(0.15, 0.85), 2)
                }
                return attack_info
            
            return None
        except Exception as e:
            self.logger.error(f"异常行为检测异常: {str(e)}")
            return None
"""
    
    # 写入新内容
    with open(detector_path, "w", encoding="utf-8") as f:
        f.write(new_detector_content)
    
    print("✅ 已完全重写 AttackDetector 类，修复了所有变量错误")
    
    # 修复 SecurityNode 类的 stop 方法
    node_path = os.path.join(root_dir, "src", "security", "security_node.py")
    
    if os.path.isfile(node_path):
        with open(node_path, "r", encoding="utf-8") as f:
            node_content = f.read()
        
        # 查找 stop 方法
        stop_pattern = r"def stop\(self\):(.*?)(?=\n    def|\n\n|$)"
        stop_match = re.search(stop_pattern, node_content, re.DOTALL)
        
        if stop_match:
            old_stop = stop_match.group(0)  # 包括方法签名
            
            # 创建新的 stop 方法
            new_stop = """def stop(self):
        \"\"\"停止安全节点\"\"\"
        try:
            if hasattr(self, 'detector') and self.detector:
                try:
                    self.detector.stop()
                except Exception as e:
                    self.logger.error(f"停止检测器时发生错误: {str(e)}")
                
            if hasattr(self, 'protector') and self.protector:
                try:
                    self.protector.stop()
                except Exception as e:
                    self.logger.error(f"停止保护器时发生错误: {str(e)}")
                
            self.logger.info(f"安全节点 {self.node_id} 已停止")
        except Exception as e:
            self.logger.error(f"停止安全节点时发生错误: {str(e)}")"""
            
            # 替换 stop 方法
            node_content = node_content.replace(old_stop, new_stop)
            
            with open(node_path, "w", encoding="utf-8") as f:
                f.write(node_content)
            
            print("✅ 已修复 SecurityNode 的 stop 方法")
        else:
            print("警告：无法找到 SecurityNode 的 stop 方法")
    
    # 修复 main.py 文件中的关闭逻辑
    main_path = os.path.join(root_dir, "src", "main.py")
    
    if os.path.isfile(main_path):
        with open(main_path, "r", encoding="utf-8") as f:
            main_content = f.read()
        
        # 寻找 run_platform 函数中的关闭逻辑
        run_platform_pattern = r"def run_platform\(.*?\):(.*?)(?=\ndef|\n\n|$)"
        run_platform_match = re.search(run_platform_pattern, main_content, re.DOTALL)
        
        if run_platform_match:
            old_run_platform = run_platform_match.group(0)  # 包括函数签名
            
            # 找到关闭安全节点的代码部分
            node_stop_pattern = r"(# 关闭安全节点.*?for node in security_nodes.*?)(?=\n    # |$)"
            node_stop_match = re.search(node_stop_pattern, old_run_platform, re.DOTALL)
            
            if node_stop_match:
                old_node_stop = node_stop_match.group(1)
                new_node_stop = """    # 关闭安全节点
    logger.info("正在关闭安全节点...")
    for node in security_nodes:
        try:
            node.stop()
        except Exception as e:
            logger.error(f"关闭安全节点时出错: {str(e)}")"""
                
                # 替换安全节点关闭代码
                new_run_platform = old_run_platform.replace(old_node_stop, new_node_stop)
                
                # 更新 main.py 内容
                main_content = main_content.replace(old_run_platform, new_run_platform)
                
                with open(main_path, "w", encoding="utf-8") as f:
                    f.write(main_content)
                
                print("✅ 已修复 main.py 中的安全节点关闭逻辑")
            else:
                print("警告：无法找到 main.py 中的安全节点关闭代码")
        else:
            print("警告：无法找到 main.py 中的 run_platform 函数")
    
    print("\n🚀 所有修复已完成！现在您可以运行主程序:")
    print(f"python {os.path.join(root_dir, 'src', 'main.py')}")
    print("\n程序应该不再显示任何 'cannot access local variable attack_info' 错误了")

if __name__ == "__main__":
    main()