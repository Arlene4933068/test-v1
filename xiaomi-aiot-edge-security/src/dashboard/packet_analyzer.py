#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
网络数据包捕获和分析模块
负责捕获网络流量并进行分析
"""

import time
import json
import logging
import threading
from typing import Dict, List, Any, Optional
from collections import defaultdict
from scapy.all import Packet, IP, TCP, UDP, rdpcap, wrpcap, sniff  # 需要安装: pip install scapy

# 设置日志
logger = logging.getLogger(__name__)

class PacketAnalyzer:
    """网络数据包分析器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.capture_active = False
        self.packet_buffer = defaultdict(list)  # 设备ID -> 数据包列表
        self.analysis_results = defaultdict(dict)  # 设备ID -> 分析结果
        self.capture_thread = None
        self.max_packets = config.get("packet_capture_limit", 100)
        self.capture_dir = config.get("capture_dir", "data/packet_capture")
        self.interfaces = config.get("interfaces", ["eth0"])
        logger.info(f"数据包分析器初始化完成，监听接口: {self.interfaces}")
    
    def start_capture(self, device_id: Optional[str] = None):
        """开始捕获指定设备或所有设备的数据包"""
        if self.capture_active:
            logger.warning("数据包捕获已经在运行")
            return False
            
        self.capture_active = True
        self.capture_thread = threading.Thread(
            target=self._capture_packets,
            args=(device_id,),
            daemon=True
        )
        self.capture_thread.start()
        logger.info(f"开始捕获{'所有' if device_id is None else device_id + '的'}数据包")
        return True
    
    def stop_capture(self):
        """停止数据包捕获"""
        if not self.capture_active:
            logger.warning("数据包捕获未在运行")
            return False
            
        self.capture_active = False
        if self.capture_thread:
            self.capture_thread.join(timeout=5.0)
        logger.info("停止数据包捕获")
        return True
    
    def _capture_packets(self, device_id: Optional[str] = None):
        """数据包捕获线程"""
        try:
            # 使用pcapy捕获数据包
            for interface in self.interfaces:
                try:
                    cap = pcapy.open_live(interface, 65536, True, 1000)
                    
                    # 设置过滤器，如果指定了设备ID
                    if device_id:
                        # 假设设备ID可以映射到IP地址
                        device_ip = self._get_device_ip(device_id)
                        if device_ip:
                            cap.setfilter(f"host {device_ip}")
                    
                    while self.capture_active:
                        (header, packet) = cap.next()
                        if header and packet:
                            # 解析数据包
                            parsed_packet = self._parse_packet(packet)
                            if parsed_packet:
                                # 如果指定了设备ID，则只存储该设备的数据包
                                if device_id:
                                    if self._packet_belongs_to_device(parsed_packet, device_id):
                                        self._store_packet(device_id, parsed_packet)
                                else:
                                    # 尝试确定数据包归属的设备
                                    packet_device_id = self._identify_device_from_packet(parsed_packet)
                                    if packet_device_id:
                                        self._store_packet(packet_device_id, parsed_packet)
                except Exception as e:
                    logger.error(f"接口 {interface} 捕获数据包失败: {str(e)}")
        except Exception as e:
            logger.error(f"数据包捕获线程发生错误: {str(e)}")
        finally:
            # 捕获结束时进行分析
            self._analyze_captured_packets(device_id)
    
    def _parse_packet(self, packet_data):
        """解析原始数据包"""
        try:
            # 使用scapy解析数据包
            packet = Packet(packet_data)
            return packet
        except Exception as e:
            logger.debug(f"解析数据包失败: {str(e)}")
            return None
    
    def _store_packet(self, device_id: str, packet):
        """存储数据包"""
        # 限制每个设备的数据包数量
        if len(self.packet_buffer[device_id]) >= self.max_packets:
            self.packet_buffer[device_id].pop(0)  # 移除最旧的数据包
        
        # 添加新数据包
        self.packet_buffer[device_id].append({
            'timestamp': time.time(),
            'packet': packet
        })
    
    def _get_device_ip(self, device_id: str) -> Optional[str]:
        """从设备ID获取设备IP地址"""
        # 实现从设备ID到IP的映射逻辑
        # 此处为示例，实际应用需要根据系统设计实现
        device_ip_mapping = {
            "gateway-001": "192.168.1.1",
            "camera-001": "192.168.1.100",
            # 添加更多设备映射...
        }
        return device_ip_mapping.get(device_id)
    
    def _packet_belongs_to_device(self, packet, device_id: str) -> bool:
        """判断数据包是否属于指定设备"""
        device_ip = self._get_device_ip(device_id)
        if not device_ip or not packet:
            return False
            
        if IP in packet:
            return packet[IP].src == device_ip or packet[IP].dst == device_ip
        return False
    
    def _identify_device_from_packet(self, packet) -> Optional[str]:
        """从数据包识别设备ID"""
        if not packet or IP not in packet:
            return None
            
        # 反向映射：从IP到设备ID
        ip_device_mapping = {
            "192.168.1.1": "gateway-001",
            "192.168.1.100": "camera-001",
            # 添加更多映射...
        }
        
        src_device = ip_device_mapping.get(packet[IP].src)
        if src_device:
            return src_device
            
        dst_device = ip_device_mapping.get(packet[IP].dst)
        if dst_device:
            return dst_device
            
        return None
    
    def _analyze_captured_packets(self, device_id: Optional[str] = None):
        """分析已捕获的数据包"""
        devices_to_analyze = [device_id] if device_id else list(self.packet_buffer.keys())
        
        for current_device in devices_to_analyze:
            if not self.packet_buffer[current_device]:
                continue
                
            # 保存PCAP文件用于进一步分析
            self._save_pcap_file(current_device)
            
            # 进行基本分析
            packets = [p['packet'] for p in self.packet_buffer[current_device]]
            
            # 协议分布
            protocol_stats = self._analyze_protocols(packets)
            
            # 流量分析
            traffic_stats = self._analyze_traffic(packets)
            
            # 时间模式
            time_pattern = self._analyze_time_patterns(self.packet_buffer[current_device])
            
            # 潜在异常
            anomalies = self._detect_anomalies(packets)
            
            # 存储分析结果
            self.analysis_results[current_device] = {
                'timestamp': time.time(),
                'packet_count': len(packets),
                'protocol_stats': protocol_stats,
                'traffic_stats': traffic_stats,
                'time_pattern': time_pattern,
                'anomalies': anomalies
            }
            
            logger.info(f"完成设备 {current_device} 的数据包分析，发现 {len(anomalies)} 个潜在异常")
    
    def _save_pcap_file(self, device_id: str):
        """将设备数据包保存为PCAP文件"""
        import os
        if not os.path.exists(self.capture_dir):
            os.makedirs(self.capture_dir)
            
        filename = f"{self.capture_dir}/{device_id}_{int(time.time())}.pcap"
        packets = [p['packet'] for p in self.packet_buffer[device_id]]
        
        try:
            wrpcap(filename, packets)
            logger.info(f"数据包已保存到 {filename}")
        except Exception as e:
            logger.error(f"保存PCAP文件失败: {str(e)}")
    
    def _analyze_protocols(self, packets):
        """分析数据包的协议分布"""
        protocols = {
            'TCP': 0,
            'UDP': 0,
            'ICMP': 0,
            'Other': 0
        }
        
        for packet in packets:
            if TCP in packet:
                protocols['TCP'] += 1
            elif UDP in packet:
                protocols['UDP'] += 1
            elif IP in packet and packet[IP].proto == 1:  # ICMP
                protocols['ICMP'] += 1
            else:
                protocols['Other'] += 1
                
        return protocols
    
    def _analyze_traffic(self, packets):
        """分析流量情况"""
        total_bytes = 0
        port_activity = defaultdict(int)
        
        for packet in packets:
            # 计算包大小
            if hasattr(packet, 'len'):
                total_bytes += packet.len
            
            # 记录端口活动
            if TCP in packet:
                port_activity[f"TCP:{packet[TCP].sport}"] += 1
                port_activity[f"TCP:{packet[TCP].dport}"] += 1
            elif UDP in packet:
                port_activity[f"UDP:{packet[UDP].sport}"] += 1
                port_activity[f"UDP:{packet[UDP].dport}"] += 1
        
        # 找出最活跃的端口
        top_ports = sorted(port_activity.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_bytes': total_bytes,
            'top_ports': dict(top_ports)
        }
    
    def _analyze_time_patterns(self, packet_data):
        """分析数据包的时间模式"""
        if not packet_data:
            return {}
            
        timestamps = [p['timestamp'] for p in packet_data]
        
        # 计算时间间隔
        intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
        
        if not intervals:
            return {'avg_interval': 0}
            
        avg_interval = sum(intervals) / len(intervals)
        
        # 检测突发情况
        bursts = []
        burst_threshold = avg_interval * 0.2  # 低于平均间隔20%认为是突发
        
        for i, interval in enumerate(intervals):
            if interval < burst_threshold:
                burst_start = timestamps[i]
                # 寻找突发结束
                j = i + 1
                while j < len(intervals) and intervals[j] < burst_threshold:
                    j += 1
                burst_end = timestamps[min(j+1, len(timestamps)-1)]
                bursts.append({
                    'start': burst_start,
                    'end': burst_end,
                    'duration': burst_end - burst_start,
                    'packet_count': j - i + 2
                })
                i = j
        
        return {
            'avg_interval': avg_interval,
            'burst_count': len(bursts),
            'bursts': bursts
        }
    
    def _detect_anomalies(self, packets):
        """检测数据包中的潜在异常"""
        anomalies = []
        
        # 检测不常见的端口
        suspicious_ports = [22, 23, 3389, 5900]  # SSH, Telnet, RDP, VNC
        
        for i, packet in enumerate(packets):
            # 检测是否使用可疑端口
            if TCP in packet:
                if packet[TCP].dport in suspicious_ports:
                    anomalies.append({
                        'type': 'suspicious_port',
                        'description': f"访问可疑端口 {packet[TCP].dport}",
                        'packet_index': i,
                        'severity': 'medium'
                    })
            
            # 检测可能的端口扫描
            # 此处简化实现，实际应根据具体需求开发更复杂的逻辑
            
            # 其他可能的异常检测...
        
        return anomalies
    
    def get_analysis_results(self, device_id: Optional[str] = None) -> Dict[str, Any]:
        """获取分析结果"""
        if device_id:
            return self.analysis_results.get(device_id, {})
        return self.analysis_results
    
    def clear_data(self, device_id: Optional[str] = None):
        """清除数据"""
        if device_id:
            if device_id in self.packet_buffer:
                self.packet_buffer[device_id] = []
            if device_id in self.analysis_results:
                self.analysis_results[device_id] = {}
        else:
            self.packet_buffer.clear()
            self.analysis_results.clear()
        logger.info(f"已清除{'所有' if device_id is None else device_id + '的'}数据包数据")