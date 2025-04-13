# src/dashboard/visualization.py
import os
import json
import time
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from ..utils.logger import get_logger
from ..analytics.statistical_analyzer import StatisticalAnalyzer
from ..analytics.report_generator import ReportGenerator

class Visualization:
    """数据可视化：提供数据分析和可视化功能"""
    
    def __init__(self):
        self.logger = get_logger("Visualization")
        self.analyzer = StatisticalAnalyzer()
        self.report_generator = ReportGenerator()
        self.logger.info("数据可视化模块初始化完成")
    
    def get_analytics_data(self, data_type='all'):
        """获取分析数据
        
        Args:
            data_type: 数据类型 (detection, response, resource, all)
            
        Returns:
            dict: 分析数据
        """
        # 这里可以从数据收集模块获取实际数据
        # 暂时使用模拟数据
        if data_type == 'detection' or data_type == 'all':
            detection_data = self._get_detection_data()
            if data_type == 'detection':
                return detection_data
        
        if data_type == 'response' or data_type == 'all':
            response_data = self._get_response_data()
            if data_type == 'response':
                return response_data
        
        if data_type == 'resource' or data_type == 'all':
            resource_data = self._get_resource_data()
            if data_type == 'resource':
                return resource_data
        
        if data_type == 'all':
            return {
                "detection": detection_data,
                "response": response_data,
                "resource": resource_data
            }
        
        self.logger.warning(f"未知的数据类型: {data_type}")
        return {}
    
    def _get_detection_data(self):
        """获取检测数据
        
        Returns:
            dict: 检测数据
        """
        # 模拟数据
        raw_data = []
        attack_types = ["ddos", "mitm", "firmware", "credential"]
        detection_rates = {
            "ddos": 0.95,
            "mitm": 0.92,
            "firmware": 0.88,
            "credential": 0.93
        }
        
        # 生成每种攻击类型的数据点
        for attack_type in attack_types:
            success_rate = detection_rates[attack_type]
            total_samples = 100
            
            # 成功检测的样本
            for i in range(int(total_samples * success_rate)):
                raw_data.append({
                    "attack_type": attack_type,
                    "detected": True,
                    "timestamp": time.time() - i * 3600,
                    "device_type": ["gateway", "router", "speaker", "camera"][i % 4]
                })
            
            # 未检测到的样本
            for i in range(int(total_samples * (1 - success_rate))):
                raw_data.append({
                    "attack_type": attack_type,
                    "detected": False,
                    "timestamp": time.time() - i * 3600,
                    "device_type": ["gateway", "router", "speaker", "camera"][i % 4]
                })
        
        # 使用分析器分析数据
        analysis_result = self.analyzer.analyze_detection_rate(raw_data)
        return analysis_result
    
    def _get_response_data(self):
        """获取响应时间数据
        
Returns:
            dict: 响应时间数据
        """
        # 模拟数据
        raw_data = []
        device_types = ["gateway", "router", "speaker", "camera"]
        avg_response_times = {
            "gateway": 25.3,  # ms
            "router": 18.7,
            "speaker": 42.1,
            "camera": 35.8
        }
        
        # 生成每种设备类型的数据点
        for device_type in device_types:
            avg_time = avg_response_times[device_type]
            total_samples = 100
            
            for i in range(total_samples):
                # 生成随机波动的响应时间
                import random
                response_time = max(1, avg_time + random.uniform(-10, 10))
                
                raw_data.append({
                    "device_type": device_type,
                    "response_time": response_time,
                    "timestamp": time.time() - i * 60,
                    "protection_active": i % 2 == 0  # 隔行设置是否启用保护
                })
        
        # 使用分析器分析数据
        analysis_result = self.analyzer.analyze_response_time(raw_data)
        return analysis_result
    
    def _get_resource_data(self):
        """获取资源使用数据
        
        Returns:
            dict: 资源使用数据
        """
        # 模拟数据
        raw_data = []
        device_types = ["gateway", "router", "speaker", "camera"]
        avg_resource_usage = {
            "gateway": {"cpu": 15.2, "memory": 28.5, "network": 125.3},
            "router": {"cpu": 12.8, "memory": 22.3, "network": 248.7},
            "speaker": {"cpu": 8.5, "memory": 18.4, "network": 35.2},
            "camera": {"cpu": 22.7, "memory": 35.6, "network": 185.4}
        }
        
        # 生成每种设备类型的数据点
        for device_type in device_types:
            data = avg_resource_usage[device_type]
            total_samples = 100
            
            for i in range(total_samples):
                # 生成随机波动的资源使用率
                import random
                cpu = max(0.1, min(100, data["cpu"] + random.uniform(-5, 5)))
                memory = max(0.1, min(100, data["memory"] + random.uniform(-8, 8)))
                network = max(0.1, data["network"] + random.uniform(-20, 20))
                
                # 设置保护状态(50%开启，50%关闭)
                protection_active = i % 2 == 0
                
                # 如果开启保护，增加一些资源占用
                if protection_active:
                    cpu += 3.5
                    memory += 5.2
                
                raw_data.append({
                    "device_type": device_type,
                    "cpu_usage": cpu,
                    "memory_usage": memory,
                    "network_usage": network,
                    "timestamp": time.time() - i * 60,
                    "protection_active": protection_active
                })
        
        # 使用分析器分析数据
        analysis_result = self.analyzer.analyze_resource_usage(raw_data)
        return analysis_result
    
    def get_performance_stats(self):
        """获取性能统计数据
        
        Returns:
            dict: 性能统计数据
        """
        # 整合响应时间和资源使用数据
        response_data = self._get_response_data()
        resource_data = self._get_resource_data()
        
        # 计算综合得分（简单示例：响应时间越低、资源占用越低得分越高）
        device_types = ["gateway", "router", "speaker", "camera"]
        performance_scores = {}
        
        for device in device_types:
            if device in response_data["by_device_type"] and device in resource_data["by_device_type"]:
                response_score = 100 - (response_data["by_device_type"][device]["mean"] / 100)
                resource_score = 100 - (
                    resource_data["by_device_type"][device]["cpu"] * 0.5 + 
                    resource_data["by_device_type"][device]["memory"] * 0.5
                ) / 100
                
                # 综合得分 (0-100)
                performance_scores[device] = (response_score * 0.6 + resource_score * 0.4)
        
        return {
            "response_time": {
                "overall": response_data["overall_stats"]["mean"],
                "by_device": {dev: data["mean"] for dev, data in response_data["by_device_type"].items()}
            },
            "resource_usage": {
                "overall_cpu": resource_data["overall_usage"]["cpu"],
                "overall_memory": resource_data["overall_usage"]["memory"],
                "by_device": {
                    dev: {
                        "cpu": data["cpu"],
                        "memory": data["memory"]
                    } for dev, data in resource_data["by_device_type"].items()
                }
            },
            "performance_scores": performance_scores,
            "timestamp": time.time()
        }
    
    def generate_report(self, report_type='comprehensive'):
        """生成分析报告
        
        Args:
            report_type: 报告类型 (detection, performance, comprehensive)
            
        Returns:
            dict: 报告生成结果
        """
        try:
            if report_type == 'detection':
                # 生成检测报告
                detection_data = self._get_detection_data()
                report_path = self.report_generator.generate_detection_report(detection_data)
                
                return {
                    "type": "detection",
                    "path": report_path,
                    "timestamp": time.time()
                }
                
            elif report_type == 'performance':
                # 生成性能报告
                response_data = self._get_response_data()
                resource_data = self._get_resource_data()
                report_path = self.report_generator.generate_performance_report(
                    response_data, resource_data
                )
                
                return {
                    "type": "performance",
                    "path": report_path,
                    "timestamp": time.time()
                }
                
            elif report_type == 'comprehensive':
                # 生成综合报告
                data = {
                    "detection": self._get_detection_data(),
                    "response_time": self._get_response_data(),
                    "resource_usage": self._get_resource_data()
                }
                report_path = self.report_generator.generate_comprehensive_report(data)
                
                return {
                    "type": "comprehensive",
                    "path": report_path,
                    "timestamp": time.time()
                }
                
            else:
                self.logger.warning(f"未知的报告类型: {report_type}")
                return {
                    "error": f"未知的报告类型: {report_type}"
                }
        except Exception as e:
            self.logger.error(f"生成报告出错: {str(e)}")
            return {
                "error": str(e)
            }