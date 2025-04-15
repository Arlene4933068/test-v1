#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统计分析器模块
对收集的安全和性能数据进行分析和可视化
"""

import os
import logging
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from .utils.logger import get_logger

class StatisticalAnalyzer:
    """统计分析器类，用于分析收集的数据并生成统计结果和可视化"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化统计分析器
        
        Args:
            config: 配置参数
        """
        self.logger = get_logger(__name__)
        self.config = config
        
        # 数据目录
        self.data_dir = config.get("data_dir", "data")
        
        # 分析配置
        self.analysis_config = config.get("analysis", {})
        self.time_window = self.analysis_config.get("time_window", "daily")  # daily, weekly, monthly
        self.metrics = self.analysis_config.get("metrics", ["cpu_usage", "memory_usage", "network_throughput", "attack_detection_rate"])
        
        # 可视化配置
        self.visualization_config = config.get("visualization", {})
        self.visualization_enabled = self.visualization_config.get("enabled", True)
        self.visualization_format = self.visualization_config.get("format", "png")
        self.visualization_dpi = self.visualization_config.get("dpi", 300)
        
        # 输出目录
        self.output_dir = config.get("output_dir", os.path.join(self.data_dir, "analysis"))
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 确保可视化输出目录存在
        self.visualization_dir = os.path.join(self.output_dir, "visualizations")
        os.makedirs(self.visualization_dir, exist_ok=True)
        
        self.logger.info("统计分析器已初始化")
    
    def load_data(self, data_type: str, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> pd.DataFrame:
        """
        加载指定类型的数据
        
        Args:
            data_type: 数据类型 ('device', 'security', 'performance')
            start_time: 开始时间
            end_time: 结束时间
        
        Returns:
            pd.DataFrame: 加载的数据
        """
        # 确定数据目录
        data_path = os.path.join(self.data_dir, f"{data_type}_data")
        if not os.path.exists(data_path):
            self.logger.warning(f"数据目录不存在: {data_path}")
            return pd.DataFrame()
        
        # 列出所有JSON数据文件
        all_files = []
        for root, _, files in os.walk(data_path):
            for file in files:
                if file.endswith(".json"):
                    all_files.append(os.path.join(root, file))
        
        if not all_files:
            self.logger.warning(f"没有找到数据文件: {data_path}")
            return pd.DataFrame()
        
        # 加载数据
        data_frames = []
        for file_path in all_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 将数据转换为DataFrame
                df = pd.DataFrame(data)
                
                # 确保时间戳列存在并转换为datetime
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                else:
                    self.logger.warning(f"文件中没有时间戳列: {file_path}")
                    continue
                
                # 筛选时间范围
                if start_time and end_time:
                    df = df[(df['timestamp'] >= start_time) & (df['timestamp'] <= end_time)]
                
                data_frames.append(df)
            except Exception as e:
                self.logger.error(f"加载数据文件时出错 {file_path}: {str(e)}")
        
        # 合并所有数据
        if data_frames:
            return pd.concat(data_frames, ignore_index=True)
        
        return pd.DataFrame()
    
    def analyze_device_performance(self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        分析设备性能数据
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
        
        Returns:
            Dict[str, Any]: 设备性能分析结果
        """
        # 设置默认时间范围
        if not end_time:
            end_time = datetime.now()
        
        if not start_time:
            if self.time_window == "daily":
                start_time = end_time - timedelta(days=1)
            elif self.time_window == "weekly":
                start_time = end_time - timedelta(days=7)
            elif self.time_window == "monthly":
                start_time = end_time - timedelta(days=30)
            else:
                start_time = end_time - timedelta(days=1)
        
        # 加载设备数据
        device_data = self.load_data('device', start_time, end_time)
        if device_data.empty:
            self.logger.warning("没有设备性能数据可分析")
            return {}
        
        # 分析结果
        result = {"time_range": {"start": start_time, "end": end_time}}
        
        # 分析CPU使用率
        if 'cpu_usage' in device_data.columns:
            cpu_stats = self._analyze_numeric_metric(device_data, 'cpu_usage')
            result['cpu_usage'] = cpu_stats
        
        # 分析内存使用率
        if 'memory_usage' in device_data.columns:
            memory_stats = self._analyze_numeric_metric(device_data, 'memory_usage')
            result['memory_usage'] = memory_stats
        
        # 分析网络吞吐量
        if 'network_throughput' in device_data.columns:
            network_stats = self._analyze_numeric_metric(device_data, 'network_throughput')
            result['network_throughput'] = network_stats
        
        # 分析设备类型分布
        if 'device_type' in device_data.columns:
            device_type_counts = device_data['device_type'].value_counts().to_dict()
            result['device_type_distribution'] = device_type_counts
        
        # 分析连接设备数
        if 'connected_devices' in device_data.columns:
            connected_stats = self._analyze_numeric_metric(device_data, 'connected_devices')
            result['connected_devices'] = connected_stats
        
        # 分析设备状态分布
        if 'status' in device_data.columns:
            status_counts = device_data['status'].value_counts().to_dict()
            result['status_distribution'] = status_counts
        
        # 设备时间序列分析
        if 'timestamp' in device_data.columns:
            # 按设备和时间分组的性能指标
            if 'device_id' in device_data.columns:
                device_ids = device_data['device_id'].unique()
                time_series = {}
                
                for device_id in device_ids:
                    device_df = device_data[device_data['device_id'] == device_id]
                    
                    # 对每个设备的时间序列数据进行重采样
                    device_df = device_df.sort_values('timestamp')
                    device_time_series = {}
                    
                    # 收集每个设备的时间序列数据
                    for metric in ['cpu_usage', 'memory_usage', 'network_throughput', 'connected_devices']:
                        if metric in device_df.columns:
                            metric_series = device_df[['timestamp', metric]].dropna()
                            if not metric_series.empty:
                                # 将时间序列转换为列表格式
                                metric_data = []
                                for _, row in metric_series.iterrows():
                                    metric_data.append({
                                        'timestamp': row['timestamp'].timestamp() * 1000,  # 转换为毫秒
                                        'value': row[metric]
                                    })
                                device_time_series[metric] = metric_data
                    
                    time_series[device_id] = device_time_series
                
                result['time_series'] = time_series
        
        return result
    
    def analyze_security_threats(self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        分析安全威胁数据
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
        
        Returns:
            Dict[str, Any]: 安全威胁分析结果
        """
        # 设置默认时间范围
        if not end_time:
            end_time = datetime.now()
        
        if not start_time:
            if self.time_window == "daily":
                start_time = end_time - timedelta(days=1)
            elif self.time_window == "weekly":
                start_time = end_time - timedelta(days=7)
            elif self.time_window == "monthly":
                start_time = end_time - timedelta(days=30)
            else:
                start_time = end_time - timedelta(days=1)
        
        # 加载安全数据
        security_data = self.load_data('security', start_time, end_time)
        if security_data.empty:
            self.logger.warning("没有安全威胁数据可分析")
            return {}
        
        # 分析结果
        result = {"time_range": {"start": start_time, "end": end_time}}
        
        # 威胁类型分布
        if 'type' in security_data.columns:
            threat_types = security_data['type'].value_counts().to_dict()
            result['threat_types'] = threat_types
        
        # 子类型分布
        if 'subtype' in security_data.columns:
            subtype_counts = security_data['subtype'].value_counts().to_dict()
            result['threat_subtypes'] = subtype_counts
        
        # 威胁源分布
        if 'source' in security_data.columns:
            source_counts = security_data['source'].value_counts().head(10).to_dict()  # 仅显示前10个
            result['threat_sources'] = source_counts
        
        # 威胁目标分布
        target_column = None
        for col in ['target_id', 'target', 'target_device_id']:
            if col in security_data.columns:
                target_column = col
                break
        
        if target_column:
            target_counts = security_data[target_column].value_counts().head(10).to_dict()  # 仅显示前10个
            result['threat_targets'] = target_counts
        
        # 威胁置信度统计
        if 'confidence' in security_data.columns:
            confidence_stats = self._analyze_numeric_metric(security_data, 'confidence')
            result['confidence_stats'] = confidence_stats
        
        # 按小时统计威胁
        if 'timestamp' in security_data.columns:
            security_data['hour'] = security_data['timestamp'].dt.hour
            hourly_threats = security_data.groupby('hour').size().to_dict()
            result['hourly_distribution'] = hourly_threats
        
        # 威胁检测率
        if 'type' in security_data.columns and 'detected' in security_data.columns:
            security_data['detected'] = security_data['detected'].astype(bool)
            detection_by_type = security_data.groupby('type')['detected'].mean().to_dict()
            result['detection_rate_by_type'] = detection_by_type
            
            overall_detection_rate = security_data['detected'].mean()
            result['overall_detection_rate'] = overall_detection_rate
        
        # 威胁时间序列分析
        if 'timestamp' in security_data.columns and 'type' in security_data.columns:
            # 按时间和威胁类型分组
            security_data = security_data.sort_values('timestamp')
            security_data['date'] = security_data['timestamp'].dt.date
            
            threat_timeseries = {}
            for threat_type in security_data['type'].unique():
                type_df = security_data[security_data['type'] == threat_type]
                daily_counts = type_df.groupby('date').size()
                
                # 转换为列表格式
                time_points = []
                for date, count in daily_counts.items():
                    time_points.append({
                        'timestamp': datetime.combine(date, datetime.min.time()).timestamp() * 1000,  # 转换为毫秒
                        'count': int(count)
                    })
                
                threat_timeseries[threat_type] = time_points
            
            result['threat_timeseries'] = threat_timeseries
        
        return result
    
    def analyze_system_performance(self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        分析系统性能数据
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
        
        Returns:
            Dict[str, Any]: 系统性能分析结果
        """
        # 设置默认时间范围
        if not end_time:
            end_time = datetime.now()
        
        if not start_time:
            if self.time_window == "daily":
                start_time = end_time - timedelta(days=1)
            elif self.time_window == "weekly":
                start_time = end_time - timedelta(days=7)
            elif self.time_window == "monthly":
                start_time = end_time - timedelta(days=30)
            else:
                start_time = end_time - timedelta(days=1)
        
        # 加载性能数据
        performance_data = self.load_data('performance', start_time, end_time)
        if performance_data.empty:
            self.logger.warning("没有系统性能数据可分析")
            return {}
        
        # 分析结果
        result = {"time_range": {"start": start_time, "end": end_time}}
        
        # 分析CPU利用率
        metrics = []
        for metric in ['cpu_utilization', 'cpu_usage']:
            if metric in performance_data.columns:
                metrics.append(metric)
                cpu_stats = self._analyze_numeric_metric(performance_data, metric)
                result[metric] = cpu_stats
        
        # 分析内存使用
        for metric in ['memory_usage', 'ram_usage', 'memory_utilization']:
            if metric in performance_data.columns:
                metrics.append(metric)
                memory_stats = self._analyze_numeric_metric(performance_data, metric)
                result[metric] = memory_stats
        
        # 分析磁盘使用
        for metric in ['disk_usage', 'storage_usage']:
            if metric in performance_data.columns:
                metrics.append(metric)
                disk_stats = self._analyze_numeric_metric(performance_data, metric)
                result[metric] = disk_stats
        
        # 分析网络吞吐量
        for metric in ['network_throughput', 'bandwidth_usage']:
            if metric in performance_data.columns:
                metrics.append(metric)
                network_stats = self._analyze_numeric_metric(performance_data, metric)
                result[metric] = network_stats
        
        # 分析系统类型分布
        if 'system' in performance_data.columns:
            system_counts = performance_data['system'].value_counts().to_dict()
            result['system_distribution'] = system_counts
        
        # 性能时间序列分析
        if 'timestamp' in performance_data.columns:
            performance_data = performance_data.sort_values('timestamp')
            
            # 对每个系统的时间序列数据进行分析
            if 'system' in performance_data.columns:
                systems = performance_data['system'].unique()
                time_series = {}
                
                for system in systems:
                    system_df = performance_data[performance_data['system'] == system]
                    system_time_series = {}
                    
                    # 收集每个系统的时间序列数据
                    for metric in metrics:
                        if metric in system_df.columns:
                            metric_series = system_df[['timestamp', metric]].dropna()
                            if not metric_series.empty:
                                # 将时间序列转换为列表格式
                                metric_data = []
                                for _, row in metric_series.iterrows():
                                    metric_data.append({
                                        'timestamp': row['timestamp'].timestamp() * 1000,  # 转换为毫秒
                                        'value': row[metric]
                                    })
                                system_time_series[metric] = metric_data
                    
                    time_series[system] = system_time_series
                
                result['time_series'] = time_series
        
        return result
    
    def calculate_attack_detection_rate(self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        计算攻击检测率
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
        
        Returns:
            Dict[str, Any]: 攻击检测率结果
        """
        # 设置默认时间范围
        if not end_time:
            end_time = datetime.now()
        
        if not start_time:
            if self.time_window == "daily":
                start_time = end_time - timedelta(days=1)
            elif self.time_window == "weekly":
                start_time = end_time - timedelta(days=7)
            elif self.time_window == "monthly":
                start_time = end_time - timedelta(days=30)
            else:
                start_time = end_time - timedelta(days=1)
        
        # 加载安全数据
        security_data = self.load_data('security', start_time, end_time)
        if security_data.empty:
            self.logger.warning("没有安全威胁数据可分析")
            return {}
        
        # 分析结果
        result = {"time_range": {"start": start_time, "end": end_time}}
        
        # 攻击检测率分析
        if 'detected' not in security_data.columns:
            self.logger.warning("安全数据中没有检测标志")
            return result
        
        # 确保detected列为布尔类型
        security_data['detected'] = security_data['detected'].astype(bool)
        
        # 总体检测率
        total_attacks = len(security_data)
        detected_attacks = security_data['detected'].sum()
        overall_rate = detected_attacks / total_attacks if total_attacks > 0 else 0
        
        result['total_attacks'] = total_attacks
        result['detected_attacks'] = int(detected_attacks)
        result['overall_detection_rate'] = overall_rate
        
        # 按攻击类型的检测率
        if 'type' in security_data.columns:
            detection_by_type = {}
            for attack_type in security_data['type'].unique():
                type_data = security_data[security_data['type'] == attack_type]
                type_total = len(type_data)
                type_detected = type_data['detected'].sum()
                type_rate = type_detected / type_total if type_total > 0 else 0
                
                detection_by_type[attack_type] = {
                    'total': type_total,
                    'detected': int(type_detected),
                    'rate': type_rate
                }
            
            result['detection_by_type'] = detection_by_type
        
        # 按时间的检测率趋势
        if 'timestamp' in security_data.columns:
            security_data['date'] = security_data['timestamp'].dt.date
            daily_rates = {}
            
            for date, group in security_data.groupby('date'):
                daily_total = len(group)
                daily_detected = group['detected'].sum()
                daily_rate = daily_detected / daily_total if daily_total > 0 else 0
                
                daily_rates[date.strftime('%Y-%m-%d')] = {
                    'total': daily_total,
                    'detected': int(daily_detected),
                    'rate': daily_rate
                }
            
            result['daily_detection_rates'] = daily_rates
        
        return result
    
    def calculate_response_latency(self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        计算响应延迟
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
        
        Returns:
            Dict[str, Any]: 响应延迟结果
        """
        # 设置默认时间范围
        if not end_time:
            end_time = datetime.now()
        
        if not start_time:
            if self.time_window == "daily":
                start_time = end_time - timedelta(days=1)
            elif self.time_window == "weekly":
                start_time = end_time - timedelta(days=7)
            elif self.time_window == "monthly":
                start_time = end_time - timedelta(days=30)
            else:
                start_time = end_time - timedelta(days=1)
        
        # 加载安全数据
        security_data = self.load_data('security', start_time, end_time)
        if security_data.empty:
            self.logger.warning("没有安全威胁数据可分析")
            return {}
        
        # 检查是否有响应延迟数据
        if 'detection_time' not in security_data.columns or 'response_time' not in security_data.columns:
            if 'response_latency' not in security_data.columns:
                self.logger.warning("安全数据中没有响应延迟相关列")
                return {"time_range": {"start": start_time, "end": end_time}}
        
        # 分析结果
        result = {"time_range": {"start": start_time, "end": end_time}}
        
        # 处理直接的响应延迟数据
        if 'response_latency' in security_data.columns:
            latency_stats = self._analyze_numeric_metric(security_data, 'response_latency')
            result['latency_stats'] = latency_stats
        
        # 计算响应延迟(如果有detection_time和response_time)
        elif 'detection_time' in security_data.columns and 'response_time' in security_data.columns:
            # 确保时间戳列为datetime类型
            for col in ['detection_time', 'response_time']:
                if security_data[col].dtype != 'datetime64[ns]':
                    security_data[col] = pd.to_datetime(security_data[col], unit='ms')
            
            # 计算延迟(毫秒)
            security_data['latency_ms'] = (security_data['response_time'] - security_data['detection_time']).dt.total_seconds() * 1000
            
            # 统计延迟
            latency_stats = self._analyze_numeric_metric(security_data, 'latency_ms')
            result['latency_stats'] = latency_stats
        
        # 按攻击类型的响应延迟
        latency_column = 'response_latency' if 'response_latency' in security_data.columns else 'latency_ms'
        
        if latency_column in security_data.columns and 'type' in security_data.columns:
            latency_by_type = {}
            for attack_type in security_data['type'].unique():
                type_data = security_data[security_data['type'] == attack_type]
                type_latency_stats = self._analyze_numeric_metric(type_data, latency_column)
                latency_by_type[attack_type] = type_latency_stats
            
            result['latency_by_type'] = latency_by_type
        
        # 按设备的响应延迟
        target_column = None
        for col in ['target_id', 'target', 'target_device_id']:
            if col in security_data.columns:
                target_column = col
                break
        
        if latency_column in security_data.columns and target_column:
            latency_by_device = {}
            for device in security_data[target_column].unique():
                device_data = security_data[security_data[target_column] == device]
                device_latency_stats = self._analyze_numeric_metric(device_data, latency_column)
                latency_by_device[device] = device_latency_stats
            
            result['latency_by_device'] = latency_by_device
        
        return result
    
    def calculate_resource_usage(self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        计算资源占用
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
        
        Returns:
            Dict[str, Any]: 资源占用结果
        """
        # 设置默认时间范围
        if not end_time:
            end_time = datetime.now()
        
        if not start_time:
            if self.time_window == "daily":
                start_time = end_time - timedelta(days=1)
            elif self.time_window == "weekly":
                start_time = end_time - timedelta(days=7)
            elif self.time_window == "monthly":
                start_time = end_time - timedelta(days=30)
            else:
                start_time = end_time - timedelta(days=1)
        
        # 加载性能数据
        performance_data = self.load_data('performance', start_time, end_time)
        if performance_data.empty:
            self.logger.warning("没有系统性能数据可分析")
            return {}
        
        # 分析结果
        result = {"time_range": {"start": start_time, "end": end_time}}
        
        # 计算各种资源占用统计
        resource_metrics = {
            'cpu_usage': '处理器使用率',
            'cpu_utilization': '处理器利用率',
            'memory_usage': '内存使用率',
            'ram_usage': 'RAM使用率',
            'disk_usage': '磁盘使用率',
            'storage_usage': '存储使用率',
            'network_throughput': '网络吞吐量',
            'bandwidth_usage': '带宽使用率'
        }
        
        for metric, description in resource_metrics.items():
            if metric in performance_data.columns:
                stats = self._analyze_numeric_metric(performance_data, metric)
                result[metric] = stats
                result[metric]['description'] = description
        
        # 计算安全模块资源占用
        security_performance = performance_data[performance_data['system'] == 'security'] if 'system' in performance_data.columns else pd.DataFrame()
        
        if not security_performance.empty:
            security_result = {}
            for metric, description in resource_metrics.items():
                if metric in security_performance.columns:
                    stats = self._analyze_numeric_metric(security_performance, metric)
                    security_result[metric] = stats
                    security_result[metric]['description'] = f"安全模块{description}"
            
            result['security_module'] = security_result
        
        # 资源占用随时间变化趋势
        if 'timestamp' in performance_data.columns:
            performance_data = performance_data.sort_values('timestamp')
            
            # 按时间段统计资源占用
            performance_data['hour'] = performance_data['timestamp'].dt.hour
            
            hourly_stats = {}
            for metric in resource_metrics.keys():
                if metric in performance_data.columns:
                    hourly_metric = performance_data.groupby('hour')[metric].mean().to_dict()
                    hourly_stats[metric] = hourly_metric
            
            result['hourly_stats'] = hourly_stats
        
        return result
    
    def generate_visualizations(self) -> List[str]:
        """
        生成数据可视化
        
        Returns:
            List[str]: 生成的可视化文件路径列表
        """
        if not self.visualization_enabled:
            self.logger.info("可视化功能已禁用")
            return []
        
        # 设置matplotlib样式
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set(style="darkgrid")
        
        # 可视化文件路径列表
        visualization_files = []
        
        # 设置时间范围
        end_time = datetime.now()
        if self.time_window == "daily":
            start_time = end_time - timedelta(days=1)
        elif self.time_window == "weekly":
            start_time = end_time - timedelta(days=7)
        elif self.time_window == "monthly":
            start_time = end_time - timedelta(days=30)
        else:
            start_time = end_time - timedelta(days=1)
        
        try:
            # 1. 设备性能可视化
            device_data = self.load_data('device', start_time, end_time)
            if not device_data.empty:
                # CPU使用率随时间变化
                if 'cpu_usage' in device_data.columns and 'timestamp' in device_data.columns:
                    file_path = self._plot_time_series(
                        device_data, 'timestamp', 'cpu_usage', 'device_id',
                        'CPU使用率随时间变化', '时间', 'CPU使用率(%)',
                        'cpu_usage_time_series'
                    )
                    if file_path:
                        visualization_files.append(file_path)
                
                # 内存使用率随时间变化
                if 'memory_usage' in device_data.columns and 'timestamp' in device_data.columns:
                    file_path = self._plot_time_series(
                        device_data, 'timestamp', 'memory_usage', 'device_id',
                        '内存使用率随时间变化', '时间', '内存使用率(%)',
                        'memory_usage_time_series'
                    )
                    if file_path:
                        visualization_files.append(file_path)
                
                # 设备类型分布
                if 'device_type' in device_data.columns:
                    file_path = self._plot_category_distribution(
                        device_data, 'device_type',
                        '设备类型分布', '设备类型', '数量',
                        'device_type_distribution'
                    )
                    if file_path:
                        visualization_files.append(file_path)
            
            # 2. 安全威胁可视化
            security_data = self.load_data('security', start_time, end_time)
            if not security_data.empty:
                # 威胁类型分布
                if 'type' in security_data.columns:
                    file_path = self._plot_category_distribution(
                        security_data, 'type',
                        '威胁类型分布', '威胁类型', '数量',
                        'threat_type_distribution'
                    )
                    if file_path:
                        visualization_files.append(file_path)
                
                # 威胁检测率
                if 'type' in security_data.columns and 'detected' in security_data.columns:
                    security_data['detected'] = security_data['detected'].astype(bool)
                    file_path = self._plot_detection_rate_by_type(
                        security_data, 'type', 'detected',
                        '各类威胁检测率', '威胁类型', '检测率(%)',
                        'threat_detection_rate'
                    )
                    if file_path:
                        visualization_files.append(file_path)
                
                # 每小时威胁数量
                if 'timestamp' in security_data.columns:
                    security_data['hour'] = security_data['timestamp'].dt.hour
                    file_path = self._plot_hourly_distribution(
                        security_data, 'hour',
                        '每小时威胁数量', '小时', '威胁数量',
                        'hourly_threat_distribution'
                    )
                    if file_path:
                        visualization_files.append(file_path)
            
            # 3. 系统性能可视化
            performance_data = self.load_data('performance', start_time, end_time)
            if not performance_data.empty:
                # CPU利用率随时间变化
                cpu_metric = None
                for metric in ['cpu_utilization', 'cpu_usage']:
                    if metric in performance_data.columns:
                        cpu_metric = metric
                        break
                
                if cpu_metric and 'timestamp' in performance_data.columns:
                    file_path = self._plot_time_series(
                        performance_data, 'timestamp', cpu_metric, 'system',
                        'CPU利用率随时间变化', '时间', 'CPU利用率(%)',
                        'cpu_utilization_time_series'
                    )
                    if file_path:
                        visualization_files.append(file_path)
                
                # 内存使用率随时间变化
                memory_metric = None
                for metric in ['memory_usage', 'ram_usage']:
                    if metric in performance_data.columns:
                        memory_metric = metric
                        break
                
                if memory_metric and 'timestamp' in performance_data.columns:
                    file_path = self._plot_time_series(
                        performance_data, 'timestamp', memory_metric, 'system',
                        '内存使用率随时间变化', '时间', '内存使用率(%)',
                        'memory_utilization_time_series'
                    )
                    if file_path:
                        visualization_files.append(file_path)
                
                # 资源占用比较
                resource_metrics = []
                for metric in ['cpu_usage', 'memory_usage', 'disk_usage', 'network_throughput']:
                    if metric in performance_data.columns:
                        resource_metrics.append(metric)
                
                if resource_metrics and 'system' in performance_data.columns:
                    file_path = self._plot_resource_comparison(
                        performance_data, 'system', resource_metrics,
                        '各系统资源占用比较', '系统', '资源占用',
                        'resource_usage_comparison'
                    )
                    if file_path:
                        visualization_files.append(file_path)
            
            # 4. 综合分析可视化
            if not security_data.empty and not performance_data.empty:
                # 威胁与资源占用关系
                if 'timestamp' in security_data.columns and 'timestamp' in performance_data.columns:
                    # 合并安全和性能数据
                    security_data['date'] = security_data['timestamp'].dt.date
                    threat_counts = security_data.groupby('date').size().reset_index(name='threat_count')
                    
                    performance_data['date'] = performance_data['timestamp'].dt.date
                    if cpu_metric:
                        cpu_avg = performance_data.groupby('date')[cpu_metric].mean().reset_index()
                        merged_data = pd.merge(threat_counts, cpu_avg, on='date', how='inner')
                        
                        file_path = self._plot_correlation(
                            merged_data, 'threat_count', cpu_metric,
                            '威胁数量与CPU利用率相关性', '威胁数量', 'CPU利用率(%)',
                            'threat_cpu_correlation'
                        )
                        if file_path:
                            visualization_files.append(file_path)
            
            # 5. 响应延迟分析可视化
            if not security_data.empty:
                latency_column = None
                # 检查是否有直接的响应延迟列
                if 'response_latency' in security_data.columns:
                    latency_column = 'response_latency'
                # 或者计算延迟
                elif 'detection_time' in security_data.columns and 'response_time' in security_data.columns:
                    security_data['detection_time'] = pd.to_datetime(security_data['detection_time'])
                    security_data['response_time'] = pd.to_datetime(security_data['response_time'])
                    security_data['latency_ms'] = (security_data['response_time'] - security_data['detection_time']).dt.total_seconds() * 1000
                    latency_column = 'latency_ms'
                
                if latency_column and 'type' in security_data.columns:
                    file_path = self._plot_latency_by_type(
                        security_data, 'type', latency_column,
                        '各类威胁响应延迟', '威胁类型', '响应延迟(ms)',
                        'response_latency_by_type'
                    )
                    if file_path:
                        visualization_files.append(file_path)
        
        except Exception as e:
            self.logger.error(f"生成可视化时出错: {str(e)}")
        
        self.logger.info(f"成功生成 {len(visualization_files)} 个可视化文件")
        return visualization_files
    
    def _analyze_numeric_metric(self, data: pd.DataFrame, metric: str) -> Dict[str, Any]:
        """
        分析数值型指标
        
        Args:
            data: 数据DataFrame
            metric: 指标名称
        
        Returns:
            Dict[str, Any]: 分析结果
        """
        if metric not in data.columns:
            return {}
        
        metric_data = data[metric].dropna()
        if metric_data.empty:
            return {}
        
        # 基本统计
        stats = {
            "min": float(metric_data.min()),
            "max": float(metric_data.max()),
            "avg": float(metric_data.mean()),
            "median": float(metric_data.median()),
            "std_dev": float(metric_data.std()),
            "count": int(metric_data.count())
        }
        
        # 百分位数
        percentiles = [5, 25, 50, 75, 95]
        for p in percentiles:
            stats[f"p{p}"] = float(metric_data.quantile(p/100))
        
        return stats
    
    def _plot_time_series(self, data: pd.DataFrame, x_column: str, y_column: str, group_column: str,
                         title: str, x_label: str, y_label: str, file_name: str) -> Optional[str]:
        """
        绘制时间序列图
        
        Args:
            data: 数据DataFrame
            x_column: X轴列名
            y_column: Y轴列名
            group_column: 分组列名
            title: 图表标题
            x_label: X轴标签
            y_label: Y轴标签
            file_name: 输出文件名
        
        Returns:
            Optional[str]: 生成的文件路径，失败时返回None
        """
        try:
            # 创建图形和轴
            plt.figure(figsize=(12, 8))
            
            # 检查并确保时间戳列是datetime类型
            if data[x_column].dtype != 'datetime64[ns]':
                data = data.copy()
                data[x_column] = pd.to_datetime(data[x_column])
            
                        # 为每个组绘制一条线
            for group in data[group_column].unique():
                group_data = data[data[group_column] == group]
                
                # 按时间顺序排列
                group_data = group_data.sort_values(x_column)
                
                # 绘制线条
                plt.plot(group_data[x_column], group_data[y_column], label=str(group))
            
            # 设置图表属性
            plt.title(title, fontsize=16)
            plt.xlabel(x_label, fontsize=12)
            plt.ylabel(y_label, fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.legend(title=group_column, fontsize=10)
            
            # 格式化x轴日期
            plt.gcf().autofmt_xdate()
            
            # 保存图表
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(self.visualization_dir, f"{file_name}_{timestamp}.{self.visualization_format}")
            plt.savefig(file_path, dpi=self.visualization_dpi, bbox_inches='tight')
            plt.close()
            
            return file_path
        except Exception as e:
            self.logger.error(f"绘制时间序列图错误: {str(e)}")
            return None
    
    def _plot_category_distribution(self, data: pd.DataFrame, category_column: str,
                                   title: str, x_label: str, y_label: str,
                                   file_name: str) -> Optional[str]:
        """
        绘制类别分布图
        
        Args:
            data: 数据DataFrame
            category_column: 类别列名
            title: 图表标题
            x_label: X轴标签
            y_label: Y轴标签
            file_name: 输出文件名
        
        Returns:
            Optional[str]: 生成的文件路径，失败时返回None
        """
        try:
            # 计算类别分布
            category_counts = data[category_column].value_counts()
            
            # 创建图形和轴
            plt.figure(figsize=(12, 8))
            
            # 绘制条形图
            sns.barplot(x=category_counts.index, y=category_counts.values)
            
            # 设置图表属性
            plt.title(title, fontsize=16)
            plt.xlabel(x_label, fontsize=12)
            plt.ylabel(y_label, fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.7, axis='y')
            
            # 如果类别太多，旋转标签
            if len(category_counts) > 6:
                plt.xticks(rotation=45, ha='right')
            
            # 保存图表
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(self.visualization_dir, f"{file_name}_{timestamp}.{self.visualization_format}")
            plt.savefig(file_path, dpi=self.visualization_dpi, bbox_inches='tight')
            plt.close()
            
            return file_path
        except Exception as e:
            self.logger.error(f"绘制类别分布图错误: {str(e)}")
            return None
    
    def _plot_detection_rate_by_type(self, data: pd.DataFrame, type_column: str, detected_column: str,
                                    title: str, x_label: str, y_label: str,
                                    file_name: str) -> Optional[str]:
        """
        绘制按类型的检测率图
        
        Args:
            data: 数据DataFrame
            type_column: 类型列名
            detected_column: 检测标志列名
            title: 图表标题
            x_label: X轴标签
            y_label: Y轴标签
            file_name: 输出文件名
        
        Returns:
            Optional[str]: 生成的文件路径，失败时返回None
        """
        try:
            # 确保detected列是布尔类型
            data = data.copy()
            data[detected_column] = data[detected_column].astype(bool)
            
            # 按类型计算检测率
            detection_rates = data.groupby(type_column)[detected_column].mean() * 100
            
            # 创建图形和轴
            plt.figure(figsize=(12, 8))
            
            # 绘制条形图
            sns.barplot(x=detection_rates.index, y=detection_rates.values)
            
            # 设置图表属性
            plt.title(title, fontsize=16)
            plt.xlabel(x_label, fontsize=12)
            plt.ylabel(y_label, fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.7, axis='y')
            
            # 将检测率值添加到条形的顶部
            for i, rate in enumerate(detection_rates):
                plt.text(i, rate + 1, f'{rate:.1f}%', ha='center')
            
            # 设置y轴范围从0到100
            plt.ylim(0, 110)
            
            # 如果类别太多，旋转标签
            if len(detection_rates) > 6:
                plt.xticks(rotation=45, ha='right')
            
            # 保存图表
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(self.visualization_dir, f"{file_name}_{timestamp}.{self.visualization_format}")
            plt.savefig(file_path, dpi=self.visualization_dpi, bbox_inches='tight')
            plt.close()
            
            return file_path
        except Exception as e:
            self.logger.error(f"绘制检测率图错误: {str(e)}")
            return None
    
    def _plot_hourly_distribution(self, data: pd.DataFrame, hour_column: str,
                                 title: str, x_label: str, y_label: str,
                                 file_name: str) -> Optional[str]:
        """
        绘制按小时分布图
        
        Args:
            data: 数据DataFrame
            hour_column: 小时列名
            title: 图表标题
            x_label: X轴标签
            y_label: Y轴标签
            file_name: 输出文件名
        
        Returns:
            Optional[str]: 生成的文件路径，失败时返回None
        """
        try:
            # 按小时计算分布
            hourly_counts = data[hour_column].value_counts().sort_index()
            
            # 确保所有24个小时都有数据点
            all_hours = pd.Series(range(24))
            hourly_counts = hourly_counts.reindex(all_hours, fill_value=0)
            
            # 创建图形和轴
            plt.figure(figsize=(12, 8))
            
            # 绘制柱状图
            plt.bar(hourly_counts.index, hourly_counts.values, width=0.8, edgecolor='k', alpha=0.7)
            
            # 设置图表属性
            plt.title(title, fontsize=16)
            plt.xlabel(x_label, fontsize=12)
            plt.ylabel(y_label, fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.7, axis='y')
            
            # 设置x轴刻度
            plt.xticks(range(24), [f"{h:02d}:00" for h in range(24)], rotation=45)
            
            # 保存图表
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(self.visualization_dir, f"{file_name}_{timestamp}.{self.visualization_format}")
            plt.savefig(file_path, dpi=self.visualization_dpi, bbox_inches='tight')
            plt.close()
            
            return file_path
        except Exception as e:
            self.logger.error(f"绘制小时分布图错误: {str(e)}")
            return None
    
    def _plot_resource_comparison(self, data: pd.DataFrame, system_column: str, resource_metrics: List[str],
                                 title: str, x_label: str, y_label: str,
                                 file_name: str) -> Optional[str]:
        """
        绘制资源占用比较图
        
        Args:
            data: 数据DataFrame
            system_column: 系统列名
            resource_metrics: 资源指标列名列表
            title: 图表标题
            x_label: X轴标签
            y_label: Y轴标签
            file_name: 输出文件名
        
        Returns:
            Optional[str]: 生成的文件路径，失败时返回None
        """
        try:
            # 为每个系统和指标计算平均值
            system_resource_avg = data.groupby(system_column)[resource_metrics].mean().reset_index()
            
            # 创建图形和轴
            fig, ax = plt.subplots(figsize=(14, 10))
            
            # 设置分组条形图的宽度和间距
            bar_width = 0.8 / len(resource_metrics)
            index = np.arange(len(system_resource_avg))
            
            # 绘制每个指标的条形
            for i, metric in enumerate(resource_metrics):
                offset = i * bar_width
                rects = ax.bar(index + offset, system_resource_avg[metric], bar_width, label=metric)
            
            # 设置图表属性
            plt.title(title, fontsize=16)
            plt.xlabel(x_label, fontsize=12)
            plt.ylabel(y_label, fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.7, axis='y')
            
            # 设置x轴刻度
            plt.xticks(index + bar_width * len(resource_metrics) / 2 - bar_width / 2, system_resource_avg[system_column])
            
            # 添加图例
            plt.legend(title='资源指标', fontsize=10)
            
            # 保存图表
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(self.visualization_dir, f"{file_name}_{timestamp}.{self.visualization_format}")
            plt.savefig(file_path, dpi=self.visualization_dpi, bbox_inches='tight')
            plt.close()
            
            return file_path
        except Exception as e:
            self.logger.error(f"绘制资源比较图错误: {str(e)}")
            return None
    
    def _plot_correlation(self, data: pd.DataFrame, x_column: str, y_column: str,
                         title: str, x_label: str, y_label: str,
                         file_name: str) -> Optional[str]:
        """
        绘制相关性散点图
        
        Args:
            data: 数据DataFrame
            x_column: X轴列名
            y_column: Y轴列名
            title: 图表标题
            x_label: X轴标签
            y_label: Y轴标签
            file_name: 输出文件名
        
        Returns:
            Optional[str]: 生成的文件路径，失败时返回None
        """
        try:
            # 创建图形和轴
            plt.figure(figsize=(12, 8))
            
            # 绘制散点图和拟合线
            sns.regplot(x=x_column, y=y_column, data=data, scatter_kws={'alpha': 0.5})
            
            # 计算相关系数
            correlation = data[[x_column, y_column]].corr().iloc[0, 1]
            
            # 设置图表属性
            plt.title(f"{title} (r = {correlation:.2f})", fontsize=16)
            plt.xlabel(x_label, fontsize=12)
            plt.ylabel(y_label, fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.7)
            
            # 保存图表
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(self.visualization_dir, f"{file_name}_{timestamp}.{self.visualization_format}")
            plt.savefig(file_path, dpi=self.visualization_dpi, bbox_inches='tight')
            plt.close()
            
            return file_path
        except Exception as e:
            self.logger.error(f"绘制相关性图错误: {str(e)}")
            return None
    
    def _plot_latency_by_type(self, data: pd.DataFrame, type_column: str, latency_column: str,
                             title: str, x_label: str, y_label: str,
                             file_name: str) -> Optional[str]:
        """
        绘制按类型的响应延迟箱线图
        
        Args:
            data: 数据DataFrame
            type_column: 类型列名
            latency_column: 延迟列名
            title: 图表标题
            x_label: X轴标签
            y_label: Y轴标签
            file_name: 输出文件名
        
        Returns:
            Optional[str]: 生成的文件路径，失败时返回None
        """
        try:
            # 创建图形和轴
            plt.figure(figsize=(14, 8))
            
            # 绘制箱线图
            sns.boxplot(x=type_column, y=latency_column, data=data, palette='viridis')
            
            # 叠加散点图
            sns.stripplot(x=type_column, y=latency_column, data=data, size=4, alpha=0.3, jitter=True, color='black')
            
            # 设置图表属性
            plt.title(title, fontsize=16)
            plt.xlabel(x_label, fontsize=12)
            plt.ylabel(y_label, fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.7, axis='y')
            
            # 如果类别太多，旋转标签
            if len(data[type_column].unique()) > 6:
                plt.xticks(rotation=45, ha='right')
            
            # 保存图表
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(self.visualization_dir, f"{file_name}_{timestamp}.{self.visualization_format}")
            plt.savefig(file_path, dpi=self.visualization_dpi, bbox_inches='tight')
            plt.close()
            
            return file_path
        except Exception as e:
            self.logger.error(f"绘制延迟箱线图错误: {str(e)}")
            return None