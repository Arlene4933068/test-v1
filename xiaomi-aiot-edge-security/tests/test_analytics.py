#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据分析模块测试
用于测试数据收集、统计分析和报告生成功能
"""

import os
import sys
import unittest
import json
import time
import datetime
import tempfile
from unittest.mock import MagicMock, patch, Mock
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.analytics.data_collector import DataCollector
from src.analytics.statistical_analyzer import StatisticalAnalyzer
from src.analytics.report_generator import ReportGenerator
from src.utils.config import load_config


class TestDataCollector(unittest.TestCase):
    """测试数据收集器"""
    
    def setUp(self):
        """在每个测试之前设置"""
        # 创建一个临时数据目录
        self.temp_dir = tempfile.mkdtemp()
        
        # 模拟配置
        self.config = {
            "data_dir": self.temp_dir,
            "collection_interval": 1.0,
            "file_rotation": {
                "max_size": 10485760,  # 10MB
                "interval": "daily"
            },
            "data_sources": [
                {"type": "device", "name": "gateway_telemetry", "enabled": True},
                {"type": "security", "name": "threat_logs", "enabled": True},
                {"type": "performance", "name": "system_metrics", "enabled": True}
            ]
        }
        
        # 创建数据收集器实例
        self.collector = DataCollector(self.config)
    
    def tearDown(self):
        """在每个测试之后清理"""
        # 删除临时目录中的所有文件
        for root, dirs, files in os.walk(self.temp_dir):
            for file in files:
                os.remove(os.path.join(root, file))
        # 删除临时目录
        os.rmdir(self.temp_dir)
    
    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.collector.config, self.config)
        self.assertEqual(self.collector.data_dir, self.temp_dir)
        self.assertEqual(self.collector.collection_interval, 1.0)
        self.assertFalse(self.collector.collection_active)
        self.assertIsNone(self.collector.collection_thread)
        
        # 检查数据源是否已初始化
        self.assertEqual(len(self.collector.data_sources), 3)
        for source in self.collector.data_sources:
            self.assertTrue(source["enabled"])
    
    def test_start_stop_collection(self):
        """测试启动和停止数据收集"""
        # 模拟线程
        with patch('threading.Thread') as mock_thread:
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance
            
            # 测试启动收集
            result = self.collector.start_collection()
            self.assertTrue(result)
            self.assertTrue(self.collector.collection_active)
            
            # 线程应该已启动
            mock_thread_instance.start.assert_called_once()
            
            # 测试停止收集
            result = self.collector.stop_collection()
            self.assertTrue(result)
            self.assertFalse(self.collector.collection_active)
    
    def test_collect_device_data(self):
        """测试设备数据收集"""
        # 模拟设备遥测数据
        device_data = {
            "device_id": "test-gateway",
            "device_type": "gateway",
            "timestamp": int(time.time() * 1000),
            "data": {
                "connected_devices": 5,
                "data_throughput": 256.5,
                "cpu_usage": 15.2,
                "memory_usage": 256.7
            }
        }
        
        # 收集数据
        result = self.collector.collect_device_data(device_data)
        self.assertTrue(result)
        
        # 检查数据文件是否已创建
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        data_file = os.path.join(self.temp_dir, f"gateway_telemetry_{date_str}.json")
        self.assertTrue(os.path.exists(data_file))
        
        # 检查文件内容
        with open(data_file, "r") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 1)
            
            saved_data = json.loads(lines[0])
            self.assertEqual(saved_data["device_id"], device_data["device_id"])
            self.assertEqual(saved_data["data"], device_data["data"])
    
    def test_collect_security_data(self):
        """测试安全数据收集"""
        # 模拟安全威胁数据
        security_data = {
            "threat_id": "threat-1",
            "type": "ddos",
            "confidence": 85,
            "source": "192.168.1.100",
            "target": "192.168.1.1",
            "timestamp": int(time.time() * 1000),
            "details": {
                "packet_count": 5000,
                "duration": 30
            }
        }
        
        # 收集数据
        result = self.collector.collect_security_data(security_data)
        self.assertTrue(result)
        
        # 检查数据文件是否已创建
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        data_file = os.path.join(self.temp_dir, f"threat_logs_{date_str}.json")
        self.assertTrue(os.path.exists(data_file))
        
        # 检查文件内容
        with open(data_file, "r") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 1)
            
            saved_data = json.loads(lines[0])
            self.assertEqual(saved_data["threat_id"], security_data["threat_id"])
            self.assertEqual(saved_data["type"], security_data["type"])
            self.assertEqual(saved_data["details"], security_data["details"])
    
    def test_collect_performance_data(self):
        """测试性能数据收集"""
        # 模拟系统性能数据
        performance_data = {
            "timestamp": int(time.time() * 1000),
            "system": "edge-gateway",
            "metrics": {
                "cpu_utilization": 25.3,
                "memory_usage": 512.4,
                "disk_usage": 1024.5,
                "network_throughput": 1500.6
            }
        }
        
        # 收集数据
        result = self.collector.collect_performance_data(performance_data)
        self.assertTrue(result)
        
        # 检查数据文件是否已创建
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        data_file = os.path.join(self.temp_dir, f"system_metrics_{date_str}.json")
        self.assertTrue(os.path.exists(data_file))
        
        # 检查文件内容
        with open(data_file, "r") as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 1)
            
            saved_data = json.loads(lines[0])
            self.assertEqual(saved_data["system"], performance_data["system"])
            self.assertEqual(saved_data["metrics"], performance_data["metrics"])


class TestStatisticalAnalyzer(unittest.TestCase):
    """测试统计分析器"""
    
    def setUp(self):
        """在每个测试之前设置"""
        # 创建一个临时数据目录
        self.temp_dir = tempfile.mkdtemp()
        
        # 模拟配置
        self.config = {
            "data_dir": self.temp_dir,
            "analysis": {
                "time_window": "daily",
                "metrics": ["cpu_usage", "memory_usage", "network_throughput", "attack_detection_rate"]
            },
            "visualization": {
                "enabled": True,
                "format": "png",
                "dpi": 300
            }
        }
        
        # 创建统计分析器实例
        self.analyzer = StatisticalAnalyzer(self.config)
        
        # 创建测试数据文件
        self._create_test_data()
    
    def tearDown(self):
        """在每个测试之后清理"""
        # 删除临时目录中的所有文件
        for root, dirs, files in os.walk(self.temp_dir):
            for file in files:
                os.remove(os.path.join(root, file))
        # 删除临时目录
        os.rmdir(self.temp_dir)
    
    def _create_test_data(self):
        """创建测试数据文件"""
        # 设备遥测数据
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        device_file = os.path.join(self.temp_dir, f"gateway_telemetry_{date_str}.json")
        
        with open(device_file, "w") as f:
            for i in range(10):
                data = {
                    "device_id": "test-gateway",
                    "device_type": "gateway",
                    "timestamp": int(time.time() * 1000) - i * 60000,
                    "data": {
                        "connected_devices": 5 + i,
                        "data_throughput": 256.5 + i * 10,
                        "cpu_usage": 15.2 + i * 0.5,
                        "memory_usage": 256.7 + i * 5
                    }
                }
                f.write(json.dumps(data) + "\n")
        
        # 安全威胁数据
        security_file = os.path.join(self.temp_dir, f"threat_logs_{date_str}.json")
        
        with open(security_file, "w") as f:
            for i in range(5):
                data = {
                    "threat_id": f"threat-{i+1}",
                    "type": "ddos" if i % 2 == 0 else "mitm",
                    "confidence": 70 + i * 5,
                    "source": f"192.168.1.{100+i}",
                    "target": "192.168.1.1",
                    "timestamp": int(time.time() * 1000) - i * 600000,
                    "details": {
                        "packet_count": 1000 * (i + 1),
                        "duration": 10 * (i + 1)
                    }
                }
                f.write(json.dumps(data) + "\n")
        
        # 系统性能数据
        performance_file = os.path.join(self.temp_dir, f"system_metrics_{date_str}.json")
        
        with open(performance_file, "w") as f:
            for i in range(8):
                data = {
                    "timestamp": int(time.time() * 1000) - i * 300000,
                    "system": "edge-gateway",
                    "metrics": {
                        "cpu_utilization": 20.0 + i * 2,
                        "memory_usage": 400.0 + i * 25,
                        "disk_usage": 1000.0 + i * 50,
                        "network_throughput": 1000.0 + i * 100
                    }
                }
                f.write(json.dumps(data) + "\n")
    
    def test_load_device_data(self):
        """测试加载设备数据"""
        # 加载数据
        df = self.analyzer.load_device_data()
        
        # 验证数据框
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 10)
        
        # 检查列
        self.assertIn("device_id", df.columns)
        self.assertIn("device_type", df.columns)
        self.assertIn("timestamp", df.columns)
        self.assertIn("connected_devices", df.columns)
        self.assertIn("data_throughput", df.columns)
        self.assertIn("cpu_usage", df.columns)
        self.assertIn("memory_usage", df.columns)
    
    def test_load_security_data(self):
        """测试加载安全数据"""
        # 加载数据
        df = self.analyzer.load_security_data()
        
        # 验证数据框
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 5)
        
        # 检查列
        self.assertIn("threat_id", df.columns)
        self.assertIn("type", df.columns)
        self.assertIn("confidence", df.columns)
        self.assertIn("source", df.columns)
        self.assertIn("target", df.columns)
        self.assertIn("timestamp", df.columns)
    
    def test_load_performance_data(self):
        """测试加载性能数据"""
        # 加载数据
        df = self.analyzer.load_performance_data()
        
        # 验证数据框
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 8)
        
        # 检查列
        self.assertIn("timestamp", df.columns)
        self.assertIn("system", df.columns)
        self.assertIn("cpu_utilization", df.columns)
        self.assertIn("memory_usage", df.columns)
        self.assertIn("disk_usage", df.columns)
        self.assertIn("network_throughput", df.columns)
    
    def test_analyze_device_performance(self):
        """测试设备性能分析"""
        # 分析设备性能
        results = self.analyzer.analyze_device_performance()
        
        # 验证结果
        self.assertIsInstance(results, dict)
        self.assertIn("cpu_usage", results)
        self.assertIn("memory_usage", results)
        
        # 检查CPU使用率统计
        cpu_stats = results["cpu_usage"]
        self.assertIn("mean", cpu_stats)
        self.assertIn("std", cpu_stats)
        self.assertIn("min", cpu_stats)
        self.assertIn("max", cpu_stats)
        
        # 检查内存使用率统计
        memory_stats = results["memory_usage"]
        self.assertIn("mean", memory_stats)
        self.assertIn("std", memory_stats)
        self.assertIn("min", memory_stats)
        self.assertIn("max", memory_stats)
    
    def test_analyze_security_threats(self):
        """测试安全威胁分析"""
        # 分析安全威胁
        results = self.analyzer.analyze_security_threats()
        
        # 验证结果
        self.assertIsInstance(results, dict)
        self.assertIn("threat_types", results)
        self.assertIn("confidence_stats", results)
        
        # 检查威胁类型分布
        threat_types = results["threat_types"]
        self.assertIn("ddos", threat_types)
        self.assertIn("mitm", threat_types)
        
        # 检查置信度统计
        confidence_stats = results["confidence_stats"]
        self.assertIn("mean", confidence_stats)
        self.assertIn("std", confidence_stats)
        self.assertIn("min", confidence_stats)
        self.assertIn("max", confidence_stats)
    
    def test_analyze_system_performance(self):
        """测试系统性能分析"""
        # 分析系统性能
        results = self.analyzer.analyze_system_performance()
        
        # 验证结果
        self.assertIsInstance(results, dict)
        self.assertIn("cpu_utilization", results)
        self.assertIn("memory_usage", results)
        self.assertIn("network_throughput", results)
        
        # 检查CPU利用率统计
        cpu_stats = results["cpu_utilization"]
        self.assertIn("mean", cpu_stats)
        self.assertIn("std", cpu_stats)
        self.assertIn("min", cpu_stats)
        self.assertIn("max", cpu_stats)
        
        # 检查网络吞吐量统计
        network_stats = results["network_throughput"]
        self.assertIn("mean", network_stats)
        self.assertIn("std", network_stats)
        self.assertIn("min", network_stats)
        self.assertIn("max", network_stats)
    
    def test_generate_visualizations(self):
        """测试生成可视化"""
        # 模拟plt.savefig以避免实际创建图像文件
        with patch('matplotlib.pyplot.savefig') as mock_savefig:
            mock_savefig.return_value = None
            
            # 生成可视化
            vis_files = self.analyzer.generate_visualizations()
            
            # 验证结果
            self.assertIsInstance(vis_files, list)
            self.assertGreater(len(vis_files), 0)
            
            # savefig应该被调用多次
            self.assertGreater(mock_savefig.call_count, 0)


class TestReportGenerator(unittest.TestCase):
    """测试报告生成器"""
    
    def setUp(self):
        """在每个测试之前设置"""
        # 创建一个临时数据目录
        self.temp_dir = tempfile.mkdtemp()
        self.reports_dir = os.path.join(self.temp_dir, "reports")
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # 模拟配置
        self.config = {
            "reports_dir": self.reports_dir,
            "templates_dir": "../src/analytics/report_templates",
            "report_format": "html",
            "sections": [
                "executive_summary",
                "device_performance",
                "security_analysis",
                "system_performance",
                "recommendations"
            ]
        }
        
        # 创建模拟分析数据
        self.analysis_data = {
            "device_performance": {
                "cpu_usage": {
                    "mean": 20.0,
                    "std": 2.5,
                    "min": 15.2,
                    "max": 25.0
                },
                "memory_usage": {
                    "mean": 300.0,
                    "std": 25.0,
                    "min": 256.7,
                    "max": 350.0
                }
            },
            "security_threats": {
                "threat_types": {
                    "ddos": 3,
                    "mitm": 2
                },
                "confidence_stats": {
                    "mean": 80.0,
                    "std": 10.0,
                    "min": 70.0,
                    "max": 90.0
                }
            },
            "system_performance": {
                "cpu_utilization": {
                    "mean": 30.0,
                    "std": 5.0,
                    "min": 20.0,
                    "max": 40.0
                },
                "memory_usage": {
                    "mean": 500.0,
                    "std": 50.0,
                    "min": 400.0,
                    "max": 600.0
                },
                "network_throughput": {
                    "mean": 1500.0,
                    "std": 200.0,
                    "min": 1000.0,
                    "max": 1800.0
                }
            }
        }
        
        # 创建报告生成器实例
        self.generator = ReportGenerator(self.config)
    
    def tearDown(self):
        """在每个测试之后清理"""
        # 删除临时目录中的所有文件
        for root, dirs, files in os.walk(self.temp_dir):
            for file in files:
                os.remove(os.path.join(root, file))
        # 删除临时目录及其子目录
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for dir_name in dirs:
                os.rmdir(os.path.join(root, dir_name))
        os.rmdir(self.temp_dir)
    
    @patch('src.analytics.report_generator.ReportGenerator._load_template')
    @patch('src.analytics.report_generator.ReportGenerator._fill_template')
    def test_generate_html_report(self, mock_fill_template, mock_load_template):
        """测试生成HTML报告"""
        # 模拟模板加载和填充
        mock_load_template.return_value = "<html>{{ content }}</html>"
        mock_fill_template.return_value = "<html>Report content</html>"
        
        # 生成报告
        report_file = self.generator.generate_report(
            title="测试报告",
            analysis_data=self.analysis_data,
            visualization_files=["cpu_usage.png", "memory_usage.png"]
        )
        
        # 验证结果
        self.assertIsNotNone(report_file)
        mock_load_template.assert_called()
        mock_fill_template.assert_called()
    
    @patch('src.analytics.report_generator.ReportGenerator._load_template')
    @patch('src.analytics.report_generator.ReportGenerator._fill_template')
    def test_generate_pdf_report(self, mock_fill_template, mock_load_template):
        """测试生成PDF报告"""
        # 修改配置为PDF格式
        self.generator.config["report_format"] = "pdf"
        
        # 模拟模板加载和填充
        mock_load_template.return_value = "<html>{{ content }}</html>"
        mock_fill_template.return_value = "<html>Report content</html>"
        
        # 模拟PDF转换
        with patch('weasyprint.HTML') as mock_weasyprint:
            mock_weasyprint_instance = MagicMock()
            mock_weasyprint.return_value = mock_weasyprint_instance
            
            # 生成报告
            report_file = self.generator.generate_report(
                title="测试报告",
                analysis_data=self.analysis_data,
                visualization_files=["cpu_usage.png", "memory_usage.png"]
            )
            
            # 验证结果
            self.assertIsNotNone(report_file)
            mock_load_template.assert_called()
            mock_fill_template.assert_called()
            mock_weasyprint.assert_called()
            mock_weasyprint_instance.write_pdf.assert_called()
    
    def test_generate_executive_summary(self):
        """测试生成执行摘要"""
        # 生成执行摘要
        summary = self.generator._generate_executive_summary(self.analysis_data)
        
        # 验证结果
        self.assertIsInstance(summary, str)
        self.assertGreater(len(summary), 0)
    
    def test_generate_device_performance_section(self):
        """测试生成设备性能部分"""
        # 生成设备性能部分
        section = self.generator._generate_device_performance_section(self.analysis_data["device_performance"])
        
        # 验证结果
        self.assertIsInstance(section, str)
        self.assertGreater(len(section), 0)
    
    def test_generate_security_analysis_section(self):
        """测试生成安全分析部分"""
        # 生成安全分析部分
        section = self.generator._generate_security_analysis_section(self.analysis_data["security_threats"])
        
        # 验证结果
        self.assertIsInstance(section, str)
        self.assertGreater(len(section), 0)
    
    def test_generate_system_performance_section(self):
        """测试生成系统性能部分"""
        # 生成系统性能部分
        section = self.generator._generate_system_performance_section(self.analysis_data["system_performance"])
        
        # 验证结果
        self.assertIsInstance(section, str)
        self.assertGreater(len(section), 0)
    
    def test_generate_recommendations(self):
        """测试生成建议部分"""
        # 生成建议部分
        recommendations = self.generator._generate_recommendations(self.analysis_data)
        
        # 验证结果
        self.assertIsInstance(recommendations, str)
        self.assertGreater(len(recommendations), 0)


class TestIntegration(unittest.TestCase):
    """数据分析模块集成测试"""
    
    def setUp(self):
        """在每个测试之前设置"""
        # 创建一个临时数据目录
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.temp_dir, "data")
        self.reports_dir = os.path.join(self.temp_dir, "reports")
        
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # 配置数据收集器
        collector_config = {
            "data_dir": self.data_dir,
            "collection_interval": 1.0,
            "file_rotation": {
                "max_size": 10485760,  # 10MB
                "interval": "daily"
            },
            "data_sources": [
                {"type": "device", "name": "gateway_telemetry", "enabled": True},
                {"type": "security", "name": "threat_logs", "enabled": True},
                {"type": "performance", "name": "system_metrics", "enabled": True}
            ]
        }
        
        # 配置统计分析器
        analyzer_config = {
            "data_dir": self.data_dir,
            "analysis": {
                "time_window": "daily",
                "metrics": ["cpu_usage", "memory_usage", "network_throughput", "attack_detection_rate"]
            },
            "visualization": {
                "enabled": True,
                "format": "png",
                "dpi": 300
            }
        }
        
        # 配置报告生成器
        generator_config = {
            "reports_dir": self.reports_dir,
            "templates_dir": "../src/analytics/report_templates",
            "report_format": "html",
            "sections": [
                "executive_summary",
                "device_performance",
                "security_analysis",
                "system_performance",
                "recommendations"
            ]
        }
        
        # 创建组件实例
        self.collector = DataCollector(collector_config)
        self.analyzer = StatisticalAnalyzer(analyzer_config)
        self.generator = ReportGenerator(generator_config)
    
    def tearDown(self):
        """在每个测试之后清理"""
        # 删除临时目录中的所有文件和子目录
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir_name in dirs:
                os.rmdir(os.path.join(root, dir_name))
        os.rmdir(self.temp_dir)
    
    @unittest.skip("长时间运行的集成测试")
    def test_analytics_integration(self):
        """测试数据分析组件的集成"""
        # 1. 收集样本数据
        # 设备遥测数据
        for i in range(10):
            device_data = {
                "device_id": "test-gateway",
                "device_type": "gateway",
                "timestamp": int(time.time() * 1000) - i * 60000,
                "data": {
                    "connected_devices": 5 + i,
                    "data_throughput": 256.5 + i * 10,
                    "cpu_usage": 15.2 + i * 0.5,
                    "memory_usage": 256.7 + i * 5
                }
            }
            self.collector.collect_device_data(device_data)
        
        # 安全威胁数据
        for i in range(5):
            security_data = {
                "threat_id": f"threat-{i+1}",
                "type": "ddos" if i % 2 == 0 else "mitm",
                "confidence": 70 + i * 5,
                "source": f"192.168.1.{100+i}",
                "target": "192.168.1.1",
                "timestamp": int(time.time() * 1000) - i * 600000,
                "details": {
                    "packet_count": 1000 * (i + 1),
                    "duration": 10 * (i + 1)
                }
            }
            self.collector.collect_security_data(security_data)
        
        # 系统性能数据
        for i in range(8):
            performance_data = {
                "timestamp": int(time.time() * 1000) - i * 300000,
                "system": "edge-gateway",
                "metrics": {
                    "cpu_utilization": 20.0 + i * 2,
                    "memory_usage": 400.0 + i * 25,
                    "disk_usage": 1000.0 + i * 50,
                    "network_throughput": 1000.0 + i * 100
                }
            }
            self.collector.collect_performance_data(performance_data)
        
        # 2. 分析收集的数据
        # 分析设备性能
        device_performance = self.analyzer.analyze_device_performance()
        self.assertIsInstance(device_performance, dict)
        self.assertIn("cpu_usage", device_performance)
        self.assertIn("memory_usage", device_performance)
        
        # 分析安全威胁
        security_threats = self.analyzer.analyze_security_threats()
        self.assertIsInstance(security_threats, dict)
        self.assertIn("threat_types", security_threats)
        self.assertIn("confidence_stats", security_threats)
        
        # 分析系统性能
        system_performance = self.analyzer.analyze_system_performance()
        self.assertIsInstance(system_performance, dict)
        self.assertIn("cpu_utilization", system_performance)
        self.assertIn("memory_usage", system_performance)
        self.assertIn("network_throughput", system_performance)
        
        # 生成可视化（模拟）
        with patch('matplotlib.pyplot.savefig') as mock_savefig:
            mock_savefig.return_value = None
            visualization_files = self.analyzer.generate_visualizations()
            self.assertIsInstance(visualization_files, list)
        
        # 3. 生成分析报告
        # 组合分析数据
        analysis_data = {
            "device_performance": device_performance,
            "security_threats": security_threats,
            "system_performance": system_performance
        }
        
        # 使用模拟的模板生成和填充
        with patch('src.analytics.report_generator.ReportGenerator._load_template') as mock_load_template, \
             patch('src.analytics.report_generator.ReportGenerator._fill_template') as mock_fill_template:
            
            mock_load_template.return_value = "<html>{{ content }}</html>"
            mock_fill_template.return_value = "<html>Report content</html>"
            
            # 生成报告
            report_file = self.generator.generate_report(
                title="边缘计算安全分析报告",
                analysis_data=analysis_data,
                visualization_files=["mock_visualization_1.png", "mock_visualization_2.png"]
            )
            
            # 验证结果
            self.assertIsNotNone(report_file)
            mock_load_template.assert_called()
            mock_fill_template.assert_called()


if __name__ == '__main__':
    unittest.main()