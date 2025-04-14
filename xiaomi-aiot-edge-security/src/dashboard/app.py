# src/dashboard/app.py
import os
import json
import time
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory
from .device_manager import DeviceManager
from .security_config import SecurityConfig
from .visualization import Visualization
from src.utils.logger import get_logger

app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')

class DashboardApp:
    """控制面板应用类：提供Web界面管理AIoT边缘安全防护平台"""
    
    def __init__(self, config=None):
        self.logger = get_logger("DashboardApp")
        self.config = config
        self.device_manager = DeviceManager(config)
        self.security_config = SecurityConfig(config)
        self.visualization = Visualization()
        
        self._init_routes()
        self.logger.info("控制面板应用初始化完成")
    
    def _init_routes(self):
        """初始化路由"""
        app.add_url_rule('/', 'index', self.index)
        app.add_url_rule('/devices', 'devices', self.devices, methods=['GET'])
        app.add_url_rule('/devices/add', 'add_device', self.add_device, methods=['POST'])
        app.add_url_rule('/devices/remove', 'remove_device', self.remove_device, methods=['POST'])
        app.add_url_rule('/devices/status', 'device_status', self.device_status, methods=['GET'])
        
        app.add_url_rule('/security', 'security', self.security, methods=['GET'])
        app.add_url_rule('/security/config', 'security_config', self.get_security_config, methods=['GET'])
        app.add_url_rule('/security/config/update', 'update_security_config', self.update_security_config, methods=['POST'])
        app.add_url_rule('/security/status', 'security_status', self.security_status, methods=['GET'])
        
        app.add_url_rule('/analytics', 'analytics', self.analytics, methods=['GET'])
        app.add_url_rule('/analytics/data', 'analytics_data', self.analytics_data, methods=['GET'])
        app.add_url_rule('/analytics/generate_report', 'generate_report', self.generate_report, methods=['POST'])
        
        app.add_url_rule('/reports/<path:filename>', 'get_report', self.get_report)
        
        # API endpoints
        app.add_url_rule('/api/devices', 'api_devices', self.api_devices, methods=['GET'])
        app.add_url_rule('/api/security/stats', 'api_security_stats', self.api_security_stats, methods=['GET'])
        app.add_url_rule('/api/performance/stats', 'api_performance_stats', self.api_performance_stats, methods=['GET'])
    
    def index(self):
        """首页视图"""
        return render_template('index.html')
    
    def devices(self):
        """设备管理页面"""
        return render_template('devices.html')
    
    def add_device(self):
        """添加设备API"""
        data = request.json
        try:
            result = self.device_manager.add_device(
                device_type=data.get('device_type'),
                name=data.get('name'),
                platform=data.get('platform'),
                properties=data.get('properties', {})
            )
            return jsonify({"success": True, "message": "设备添加成功", "data": result})
        except Exception as e:
            self.logger.error(f"添加设备失败: {str(e)}")
            return jsonify({"success": False, "message": f"添加设备失败: {str(e)}"})
    
    def remove_device(self):
        """移除设备API"""
        data = request.json
        try:
            result = self.device_manager.remove_device(
                device_id=data.get('device_id'),
                platform=data.get('platform')
            )
            return jsonify({"success": True, "message": "设备移除成功", "data": result})
        except Exception as e:
            self.logger.error(f"移除设备失败: {str(e)}")
            return jsonify({"success": False, "message": f"移除设备失败: {str(e)}"})
    
    def device_status(self):
        """获取设备状态API"""
        try:
            status = self.device_manager.get_all_device_status()
            return jsonify({"success": True, "data": status})
        except Exception as e:
            self.logger.error(f"获取设备状态失败: {str(e)}")
            return jsonify({"success": False, "message": f"获取设备状态失败: {str(e)}"})
    
    def security(self):
        """安全管理页面"""
        return render_template('security.html')
    
    def get_security_config(self):
        """获取安全配置API"""
        try:
            config = self.security_config.get_config()
            return jsonify({"success": True, "data": config})
        except Exception as e:
            self.logger.error(f"获取安全配置失败: {str(e)}")
            return jsonify({"success": False, "message": f"获取安全配置失败: {str(e)}"})
    
    def update_security_config(self):
        """更新安全配置API"""
        data = request.json
        try:
            result = self.security_config.update_config(data)
            return jsonify({"success": True, "message": "安全配置更新成功", "data": result})
        except Exception as e:
            self.logger.error(f"更新安全配置失败: {str(e)}")
            return jsonify({"success": False, "message": f"更新安全配置失败: {str(e)}"})
    
    def security_status(self):
        """获取安全状态API"""
        try:
            status = self.security_config.get_security_status()
            return jsonify({"success": True, "data": status})
        except Exception as e:
            self.logger.error(f"获取安全状态失败: {str(e)}")
            return jsonify({"success": False, "message": f"获取安全状态失败: {str(e)}"})
    
    def analytics(self):
        """数据分析页面"""
        return render_template('analytics.html')
    
    def analytics_data(self):
        """获取分析数据API"""
        data_type = request.args.get('type', 'all')
        try:
            data = self.visualization.get_analytics_data(data_type)
            return jsonify({"success": True, "data": data})
        except Exception as e:
            self.logger.error(f"获取分析数据失败: {str(e)}")
            return jsonify({"success": False, "message": f"获取分析数据失败: {str(e)}"})
    
    def generate_report(self):
        """生成报告API"""
        data = request.json
        try:
            report_type = data.get('report_type', 'comprehensive')
            result = self.visualization.generate_report(report_type)
            return jsonify({"success": True, "message": "报告生成成功", "data": result})
        except Exception as e:
            self.logger.error(f"生成报告失败: {str(e)}")
            return jsonify({"success": False, "message": f"生成报告失败: {str(e)}"})
    
    def get_report(self, filename):
        """获取报告文件"""
        reports_dir = os.path.join(os.getcwd(), 'reports')
        return send_from_directory(reports_dir, filename)
    
    def api_devices(self):
        """设备列表API"""
        try:
            devices = self.device_manager.get_all_devices()
            return jsonify({"success": True, "data": devices})
        except Exception as e:
            self.logger.error(f"获取设备列表失败: {str(e)}")
            return jsonify({"success": False, "message": f"获取设备列表失败: {str(e)}"})
    
    def api_security_stats(self):
        """安全统计数据API"""
        try:
            stats = self.security_config.get_security_stats()
            return jsonify({"success": True, "data": stats})
        except Exception as e:
            self.logger.error(f"获取安全统计数据失败: {str(e)}")
            return jsonify({"success": False, "message": f"获取安全统计数据失败: {str(e)}"})
    
    def api_performance_stats(self):
        """性能统计数据API"""
        try:
            stats = self.visualization.get_performance_stats()
            return jsonify({"success": True, "data": stats})
        except Exception as e:
            self.logger.error(f"获取性能统计数据失败: {str(e)}")
            return jsonify({"success": False, "message": f"获取性能统计数据失败: {str(e)}"})
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """启动应用"""
        self.logger.info(f"控制面板应用启动，监听地址: {host}:{port}")
        app.run(host=host, port=port, debug=debug, threaded=True)