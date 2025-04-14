"""小米AIoT边缘安全防护研究平台 - 数据包可视化模块
负责展示和分析网络数据包信息"""

import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime
import json
import os

class PacketVisualizer:
    """数据包可视化器，用于展示网络流量和攻击数据"""
    
    def __init__(self, capture_dir: str):
        """初始化可视化器
        
        Args:
            capture_dir: 抓包数据存储目录
        """
        self.capture_dir = capture_dir
        self.app = dash.Dash(__name__)
        self.packet_data = []
        self.setup_layout()
        
    def setup_layout(self):
        """设置可视化界面布局"""
        self.app.layout = html.Div([
            html.H1('网络数据包分析面板'),
            
            # 实时流量图表
            html.Div([
                html.H3('实时网络流量'),
                dcc.Graph(id='traffic-graph'),
                dcc.Interval(
                    id='traffic-update',
                    interval=1000,  # 每秒更新
                    n_intervals=0
                )
            ]),
            
            # 协议分布饼图
            html.Div([
                html.H3('协议分布'),
                dcc.Graph(id='protocol-pie')
            ]),
            
            # 数据包详情表格
            html.Div([
                html.H3('数据包详情'),
                html.Table(id='packet-table')
            ])
        ])
        
        # 注册回调函数
        self.register_callbacks()
    
    def register_callbacks(self):
        """注册数据更新回调"""
        @self.app.callback(
            Output('traffic-graph', 'figure'),
            Input('traffic-update', 'n_intervals')
        )
        def update_traffic_graph(n):
            # 获取最新的流量数据
            df = pd.DataFrame(self.packet_data)
            if df.empty:
                return go.Figure()
            
            # 按时间统计数据包数量
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            traffic_data = df.groupby(pd.Grouper(key='timestamp', freq='1S')).size()
            
            return {
                'data': [{
                    'x': traffic_data.index,
                    'y': traffic_data.values,
                    'type': 'scatter',
                    'name': '数据包/秒'
                }],
                'layout': {
                    'title': '网络流量统计',
                    'xaxis': {'title': '时间'},
                    'yaxis': {'title': '数据包数量'}
                }
            }
        
        @self.app.callback(
            Output('protocol-pie', 'figure'),
            Input('traffic-update', 'n_intervals')
        )
        def update_protocol_pie(n):
            df = pd.DataFrame(self.packet_data)
            if df.empty:
                return go.Figure()
            
            # 统计协议分布
            protocol_counts = df['protocol'].value_counts()
            
            return {
                'data': [{
                    'labels': protocol_counts.index,
                    'values': protocol_counts.values,
                    'type': 'pie',
                    'name': '协议分布'
                }],
                'layout': {
                    'title': '协议分布统计'
                }
            }
        
        @self.app.callback(
            Output('packet-table', 'children'),
            Input('traffic-update', 'n_intervals')
        )
        def update_packet_table(n):
            # 显示最新的10个数据包
            packets = self.packet_data[-10:]
            
            # 创建表头
            header = html.Tr([
                html.Th('时间'),
                html.Th('源IP'),
                html.Th('目标IP'),
                html.Th('协议'),
                html.Th('端口'),
                html.Th('状态')
            ])
            
            # 创建表格行
            rows = []
            for packet in packets:
                rows.append(html.Tr([
                    html.Td(datetime.fromtimestamp(packet['timestamp']).strftime('%Y-%m-%d %H:%M:%S')),
                    html.Td(packet['src_ip']),
                    html.Td(packet['dst_ip']),
                    html.Td(packet['protocol']),
                    html.Td(f"{packet.get('src_port', '-')} -> {packet.get('dst_port', '-')}"),
                    html.Td(packet.get('tcp_flags', '-'))
                ]))
            
            return [html.Thead(header), html.Tbody(rows)]
    
    def update_data(self, packet_info: dict):
        """更新数据包信息
        
        Args:
            packet_info: 数据包信息字典
        """
        self.packet_data.append(packet_info)
        # 保持数据量在合理范围内
        if len(self.packet_data) > 1000:
            self.packet_data = self.packet_data[-1000:]
    
    def start(self, host: str = '0.0.0.0', port: int = 8050):
        """启动可视化服务
        
        Args:
            host: 服务主机地址
            port: 服务端口
        """
        try:
            self.logger.info(f"正在启动数据包可视化服务，监听地址: {host}:{port}")
            self.app.run_server(debug=False, host=host, port=port, use_reloader=False)
        except Exception as e:
            self.logger.error(f"启动数据包可视化服务失败: {str(e)}")
            raise