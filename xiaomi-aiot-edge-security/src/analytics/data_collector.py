"""
小米AIoT边缘安全防护研究平台 - 数据收集器
负责收集边缘设备的性能和安全数据
"""

import logging
import time
import yaml
import os
import json
from datetime import datetime, timedelta
from threading import Thread, Event
from typing import Dict, List, Any, Optional

class DataCollector:
    """数据收集器，负责收集和存储边缘设备的性能及安全数据"""
    
    def __init__(self, config_path: str = "../config/analytics.yaml"):
        """
        初始化数据收集器
        
        Args:
            config_path: 分析配置文件路径
        """
        self.logger = logging.getLogger("analytics.data_collector")
        self.config = self._load_config(config_path)
        self.data_dir = self.config.get('data_dir', '../data/analytics')
        self.collection_interval = self.config.get('collection_interval', 60)  # 默认60秒
        
        # 确保数据目录存在
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 收集的数据类别
        self.data_categories = {
            'performance': ['cpu_usage', 'memory_usage', 'network_throughput', 'response_time', 'packet_loss'],
            'security': ['attacks_detected', 'alerts_generated', 'defenses_triggered', 'vulnerability_scans'],
            'devices': ['device_status', 'connectivity', 'uptime', 'firmware_version']
        }
        
        self.collector_thread = None
        self.stop_event = Event()
        self.device_connectors = {}  # 存储设备连接器
    
    def _load_config(self, config_path: str) -> Dict:
        """
        加载分析配置
        
        Args:
            config_path: 分析配置文件路径
            
        Returns:
            配置字典
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config.get('data_collector', {})
        except Exception as e:
            self.logger.error(f"加载分析配置文件失败: {str(e)}")
            return {}
    
    def register_device_connector(self, device_type: str, connector):
        """
        注册设备连接器
        
        Args:
            device_type: 设备类型
            connector: 设备连接器对象
        """
        self.device_connectors[device_type] = connector
        self.logger.info(f"已注册 {device_type} 设备连接器")
    
    def start(self):
        """启动数据收集器"""
        if self.collector_thread and self.collector_thread.is_alive():
            self.logger.warning("数据收集器已经在运行")
            return
            
        self.stop_event.clear()
        self.collector_thread = Thread(target=self._collection_loop)
        self.collector_thread.daemon = True
        self.collector_thread.start()
        self.logger.info("数据收集器已启动")
    
    def stop(self):
        """停止数据收集器"""
        if not self.collector_thread or not self.collector_thread.is_alive():
            return
            
        self.stop_event.set()
        self.collector_thread.join(timeout=5.0)
        self.logger.info("数据收集器已停止")
    
    def _collection_loop(self):
        """数据收集主循环"""
        while not self.stop_event.is_set():
            try:
                # 收集所有设备数据
                self._collect_all_devices_data()
                
                # 保存收集的数据
                self._save_collected_data()
                
            except Exception as e:
                self.logger.error(f"数据收集循环发生错误: {str(e)}")
                
            # 等待下一个收集周期
            self.stop_event.wait(self.collection_interval)
    
    def _collect_all_devices_data(self):
        """从所有已注册的设备收集数据"""
        # 收集时间戳
        timestamp = datetime.now().isoformat()
        
        # 遍历设备连接器
        for device_type, connector in self.device_connectors.items():
            try:
                # 获取该类型的所有设备
                devices = connector.get_all_devices()
                
                for device in devices:
                    device_id = device.get('id')
                    
                    if not device_id:
                        continue
                    
                    # 收集设备性能数据
                    performance_data = self._collect_performance_data(connector, device_id)
                    
                    # 收集设备安全数据
                    security_data = self._collect_security_data(connector, device_id)
                    
                    # 收集设备状态数据
                    device_data = self._collect_device_data(connector, device_id)
                    
                    # 整合数据
                    collected_data = {
                        'timestamp': timestamp,
                        'device_id': device_id,
                        'device_type': device_type,
                        'performance': performance_data,
                        'security': security_data,
                        'device': device_data
                    }
                    
                    # 存储数据
                    self._store_device_data(device_id, collected_data)
                    
            except Exception as e:
                self.logger.error(f"收集 {device_type} 设备数据时出错: {str(e)}")
    
    def _collect_performance_data(self, connector, device_id: str) -> Dict[str, Any]:
        """
        收集设备性能数据
        
        Args:
            connector: 设备连接器
            device_id: 设备ID
            
        Returns:
            性能数据字典
        """
        try:
            # 通过连接器获取性能数据
            cpu_usage = connector.get_cpu_usage(device_id)
            memory_usage = connector.get_memory_usage(device_id)
            network_throughput = connector.get_network_throughput(device_id)
            response_time = connector.get_response_time(device_id)
            packet_loss = connector.get_packet_loss(device_id)
            
            return {
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage,
                'network_throughput': network_throughput,
                'response_time': response_time,
                'packet_loss': packet_loss
            }
        except Exception as e:
            self.logger.error(f"收集设备 {device_id} 性能数据时出错: {str(e)}")
            return {}
    
    def _collect_security_data(self, connector, device_id: str) -> Dict[str, Any]:
        """
        收集设备安全数据
        
        Args:
            connector: 设备连接器
            device_id: 设备ID
            
        Returns:
            安全数据字典
        """
        try:
            # 通过连接器获取安全数据
            attacks_detected = connector.get_attacks_detected(device_id)
            alerts_generated = connector.get_alerts_generated(device_id)
            defenses_triggered = connector.get_defenses_triggered(device_id)
            vulnerability_scans = connector.get_vulnerability_scans(device_id)
            
            return {
                'attacks_detected': attacks_detected,
                'alerts_generated': alerts_generated,
                'defenses_triggered': defenses_triggered,
                'vulnerability_scans': vulnerability_scans
            }
        except Exception as e:
            self.logger.error(f"收集设备 {device_id} 安全数据时出错: {str(e)}")
            return {}
    
    def _collect_device_data(self, connector, device_id: str) -> Dict[str, Any]:
        """
        收集设备状态数据
        
        Args:
            connector: 设备连接器
            device_id: 设备ID
            
        Returns:
            设备状态数据字典
        """
        try:
            # 通过连接器获取设备状态数据
            device_status = connector.get_device_status(device_id)
            connectivity = connector.get_connectivity(device_id)
            uptime = connector.get_uptime(device_id)
            firmware_version = connector.get_firmware_version(device_id)
            
            return {
                'device_status': device_status,
                'connectivity': connectivity,
                'uptime': uptime,
                'firmware_version': firmware_version
            }
        except Exception as e:
            self.logger.error(f"收集设备 {device_id} 状态数据时出错: {str(e)}")
            return {}
    
    def _store_device_data(self, device_id: str, data: Dict[str, Any]):
        """
        存储设备数据
        
        Args:
            device_id: 设备ID
            data: 设备数据
        """
        # 构建数据文件路径
        date_str = datetime.now().strftime("%Y-%m-%d")
        device_dir = os.path.join(self.data_dir, device_id)
        data_file = os.path.join(device_dir, f"{date_str}.jsonl")
        
        # 确保设备数据目录存在
        os.makedirs(device_dir, exist_ok=True)
        
        try:
            # 以追加模式写入数据
            with open(data_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(data) + '\n')
        except Exception as e:
            self.logger.error(f"存储设备 {device_id} 数据时出错: {str(e)}")
    
    def _save_collected_data(self):
        """保存所有收集的数据到数据库或文件"""
        # 实际应用中，可以将数据存储到时序数据库，如InfluxDB
        # 本示例中已在_store_device_data中实现了文件存储
        pass
    
    def get_device_data(self, device_id: str, start_time: Optional[datetime] = None, 
                       end_time: Optional[datetime] = None, 
                       data_categories: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        获取设备历史数据
        
        Args:
            device_id: 设备ID
            start_time: 开始时间（可选，默认24小时前）
            end_time: 结束时间（可选，默认当前时间）
            data_categories: 数据类别列表（可选，默认所有类别）
            
        Returns:
            设备历史数据列表
        """
        if not start_time:
            start_time = datetime.now() - timedelta(hours=24)
        
        if not end_time:
            end_time = datetime.now()
        
        # 确保时间范围有效
        if start_time > end_time:
            self.logger.error("时间范围无效：开始时间晚于结束时间")
            return []
        
        # 查找数据文件
        device_dir = os.path.join(self.data_dir, device_id)
        if not os.path.exists(device_dir):
            self.logger.warning(f"未找到设备 {device_id} 的数据目录")
            return []
        
        # 确定需要加载的日期
        current_date = start_time.date()
        end_date = end_time.date()
        date_list = []
        
        while current_date <= end_date:
            date_list.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)
        
        # 加载数据
        all_data = []
        for date_str in date_list:
            data_file = os.path.join(device_dir, f"{date_str}.jsonl")
            if not os.path.exists(data_file):
                continue
            
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            data = json.loads(line.strip())
                            data_time = datetime.fromisoformat(data['timestamp'])
                            
                            # 检查时间范围
                            if start_time <= data_time <= end_time:
                                # 如果指定了数据类别，只返回这些类别的数据
                                if data_categories:
                                    filtered_data = {k: v for k, v in data.items() if k in data_categories or k in ['timestamp', 'device_id', 'device_type']}
                                    all_data.append(filtered_data)
                                else:
                                    all_data.append(data)
                        except json.JSONDecodeError:
                            continue
                        except Exception as e:
                            self.logger.error(f"处理数据行时出错: {str(e)}")
            except Exception as e:
                self.logger.error(f"读取数据文件 {data_file} 时出错: {str(e)}")
        
        # 按时间戳排序
        all_data.sort(key=lambda x: x['timestamp'])
        return all_data
    
    def get_latest_device_data(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        获取设备最新数据
        
        Args:
            device_id: 设备ID
            
        Returns:
            设备最新数据（如果有）
        """
        today_str = datetime.now().strftime("%Y-%m-%d")
        device_dir = os.path.join(self.data_dir, device_id)
        data_file = os.path.join(device_dir, f"{today_str}.jsonl")
        
        if not os.path.exists(data_file):
            yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            data_file = os.path.join(device_dir, f"{yesterday_str}.jsonl")
            
            if not os.path.exists(data_file):
                self.logger.warning(f"未找到设备 {device_id} 的最新数据")
                return None
        
        try:
            # 读取文件中的最后一行数据
            with open(data_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                if not lines:
                    return None
                
                last_line = lines[-1].strip()
                return json.loads(last_line)
        except Exception as e:
            self.logger.error(f"获取设备 {device_id} 最新数据时出错: {str(e)}")
            return None
    
    def get_all_devices(self) -> List[str]:
        """
        获取所有已收集数据的设备ID
        
        Returns:
            设备ID列表
        """
        devices = []
        
        try:
            # 列出数据目录中的所有子目录（每个子目录对应一个设备）
            for entry in os.listdir(self.data_dir):
                entry_path = os.path.join(self.data_dir, entry)
                if os.path.isdir(entry_path):
                    devices.append(entry)
        except Exception as e:
            self.logger.error(f"获取所有设备列表时出错: {str(e)}")
        
        return devices