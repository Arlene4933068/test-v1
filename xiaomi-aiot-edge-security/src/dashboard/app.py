import os
import json
import time
import logging
from logging.config import dictConfig
from flask import Flask, render_template, request, jsonify, send_from_directory
from datetime import datetime

# Configure logging first, before other imports that might use the logger
def configure_logging():
    """Configure logging with the 'root' key that was missing"""
    logging_config = {
        'version': 1,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'standard',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logging.FileHandler',
                'level': 'INFO',
                'formatter': 'standard',
                'filename': 'app.log',
                'mode': 'a',
            }
        },
        'root': {  # This was the missing key
            'level': 'INFO',
            'handlers': ['console', 'file']
        },
        'loggers': {
            '': {  # Root logger
                'level': 'INFO',
                'handlers': ['console', 'file'],
                'propagate': True
            }
        }
    }
    
    dictConfig(logging_config)

# Configure logging before imports that might use it
configure_logging()

# Now import modules that depend on logging
try:
    from .device_manager import DeviceManager
    from .security_config import SecurityConfig
    from .visualization import Visualization
    from src.utils.logger import get_logger
except ImportError as e:
    logging.warning(f"Import error: {e}. Using mock implementations for development.")
    
    # Mock implementations for development
    class DeviceManager:
        def __init__(self, config=None):
            self.devices = []
            
        def add_device(self, **kwargs):
            device_id = f"dev-{len(self.devices) + 1}"
            device = {"id": device_id, **kwargs}
            self.devices.append(device)
            return device
            
        def remove_device(self, device_id, platform):
            self.devices = [d for d in self.devices if d["id"] != device_id]
            return {"removed": device_id}
            
        def get_all_device_status(self):
            return [{"id": d["id"], "status": "online" if i % 3 != 0 else "offline"} 
                   for i, d in enumerate(self.devices)]
                   
        def get_all_devices(self):
            return self.devices

    class SecurityConfig:
        def __init__(self, config=None):
            self.config = {
                "firewall": {"enabled": True},
                "intrusion_detection": {"enabled": True},
                "data_protection": {"enabled": True}
            }
            
        def get_config(self):
            return self.config
            
        def update_config(self, new_config):
            self.config.update(new_config)
            return self.config
            
        def get_security_status(self):
            return {"status": "secure", "alerts": 2}
            
        def get_security_stats(self):
            return {
                "alerts_last_24h": 5,
                "blocked_attempts": 42,
                "security_score": 92
            }

    class Visualization:
        def get_analytics_data(self, data_type):
            if data_type == 'performance':
                return {
                    "cpu_usage": [30, 45, 32, 50, 35, 38, 42],
                    "memory_usage": [45, 50, 48, 55, 60, 52, 48],
                    "labels": ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"]
                }
            elif data_type == 'security':
                return {
                    "alerts": [5, 3, 8, 2, 4, 7, 3],
                    "blocked": [12, 8, 15, 10, 14, 9, 11],
                    "labels": ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"]
                }
            else:
                return {
                    "performance": {
                        "cpu_usage": [30, 45, 32, 50, 35, 38, 42],
                        "memory_usage": [45, 50, 48, 55, 60, 52, 48]
                    },
                    "security": {
                        "alerts": [5, 3, 8, 2, 4, 7, 3],
                        "blocked": [12, 8, 15, 10, 14, 9, 11]
                    },
                    "labels": ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"]
                }
                
        def generate_report(self, report_type):
            return {
                "filename": f"{report_type}-report-{int(time.time())}.pdf",
                "url": f"/reports/{report_type}-report-{int(time.time())}.pdf"
            }
            
        def get_performance_stats(self):
            return {
                "cpu_average": 38.2,
                "memory_average": 51.1,
                "network_throughput": 256.7,
                "response_time": 218
            }

# Initialize Flask app
app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')

class DashboardApp:
    """控制面板应用类：提供Web界面管理AIoT边缘安全防护平台"""
    
    def __init__(self, config=None):
        try:
            self.logger = get_logger("DashboardApp")
        except Exception as e:
            # Fallback to standard logging if get_logger fails
            self.logger = logging.getLogger("DashboardApp")
            self.logger.warning(f"Failed to get custom logger, using standard logging: {e}")
            
        self.config = config
        self.device_manager = DeviceManager(config)
        self.security_config = SecurityConfig(config)
        self.visualization = Visualization()
        
        self._init_routes()
        self.logger.info("控制面板应用初始化完成")
    
    def _init_routes(self):
        """初始化路由"""
        # Original routes
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
        
        # Add new API endpoints for analytics.html to avoid Not Found errors
        app.add_url_rule('/api/analytics/performance', 'api_performance_data', self.api_performance_data, methods=['GET'])
        app.add_url_rule('/api/analytics/security', 'api_security_data', self.api_security_data, methods=['GET'])
        app.add_url_rule('/api/analytics/bandwidth', 'api_bandwidth_data', self.api_bandwidth_data, methods=['GET'])
        app.add_url_rule('/api/analytics/reliability', 'api_reliability_data', self.api_reliability_data, methods=['GET'])
        
        # Add a catch-all route for other static files
        app.add_url_rule('/settings', 'settings', self.settings)
        
        # Error handler for 404
        app.register_error_handler(404, self.page_not_found)
        # Add this line after the 404 error handler registration
        app.register_error_handler(500, self.internal_server_error)
    
    def page_not_found(self, e):
        """404错误处理"""
        self.logger.warning(f"页面未找到: {request.path}")
        return render_template('404.html'), 404

    def internal_server_error(self, e):
        """500错误处理"""
        self.logger.error(f"服务器内部错误: {str(e)}")
        return render_template('500.html'), 500
    
    def index(self):
        """首页视图"""
        current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        current_user = "Arlene4933068"  # This would normally come from your authentication system
        return render_template('index.html', current_time=current_time, current_user=current_user)
    
    def devices(self):
        """设备管理页面"""
        return render_template('devices.html')
    
    def settings(self):
        """系统设置页面"""
        return render_template('settings.html')
    
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
        # Create reports directory if it doesn't exist
        os.makedirs(reports_dir, exist_ok=True)
        
        # If the file doesn't exist, create a dummy PDF
        report_path = os.path.join(reports_dir, filename)
        if not os.path.exists(report_path):
            self.logger.warning(f"报告文件不存在, 创建空报告: {filename}")
            with open(report_path, 'w') as f:
                f.write("This is a placeholder report file.")
        
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
    
    # New API endpoints for analytics.html
    def api_performance_data(self):
        """获取性能分析数据API"""
        try:
            # Generate mock data for performance chart
            labels = ['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00']
            cpu_data = [25, 28, 32, 45, 60, 58, 42, 35]
            memory_data = [40, 42, 45, 52, 55, 58, 50, 45]
            latency_data = [15, 18, 20, 25, 32, 28, 22, 18]
            
            data = {
                "labels": labels,
                "datasets": [
                    {
                        "label": "CPU使用率 (%)",
                        "data": cpu_data,
                        "borderColor": "#ff6700"
                    },
                    {
                        "label": "内存使用率 (%)",
                        "data": memory_data,
                        "borderColor": "#1890ff"
                    },
                    {
                        "label": "延迟 (ms)",
                        "data": latency_data,
                        "borderColor": "#52c41a"
                    }
                ],
                "table_data": [
                    {"device": "主网关", "cpu": 32.5, "memory": 45.2, "latency": 18, "status": "normal"},
                    {"device": "前门摄像头", "cpu": 62.1, "memory": 58.3, "latency": 42, "status": "warning"},
                    {"device": "客厅传感器", "cpu": 15.3, "memory": 22.7, "latency": 12, "status": "normal"},
                    {"device": "电源管理单元", "cpu": 28.9, "memory": 35.6, "latency": 24, "status": "normal"},
                    {"device": "后院摄像头", "cpu": 78.2, "memory": 73.4, "latency": 67, "status": "alert"}
                ]
            }
            return jsonify({"success": True, "data": data})
        except Exception as e:
            self.logger.error(f"获取性能分析数据失败: {str(e)}")
            return jsonify({"success": False, "message": f"获取性能分析数据失败: {str(e)}"})
    
    def api_security_data(self):
        """获取安全分析数据API"""
        try:
            # Generate mock data for security chart
            labels = ['4-8', '4-9', '4-10', '4-11', '4-12', '4-13', '4-14']
            high_data = [2, 3, 1, 0, 4, 1, 2]
            medium_data = [5, 4, 6, 3, 5, 4, 3]
            low_data = [8, 7, 10, 6, 9, 7, 5]
            
            data = {
                "labels": labels,
                "datasets": [
                    {
                        "label": "高风险",
                        "data": high_data,
                        "backgroundColor": "rgba(245, 34, 45, 0.8)"
                    },
                    {
                        "label": "中风险",
                        "data": medium_data,
                        "backgroundColor": "rgba(250, 173, 20, 0.8)"
                    },
                    {
                        "label": "低风险",
                        "data": low_data,
                        "backgroundColor": "rgba(82, 196, 26, 0.8)"
                    }
                ],
                "table_data": [
                    {"time": "2025-04-14 08:23", "device": "主网关", "event": "未授权访问尝试", "risk": "high", "status": "alert"},
                    {"time": "2025-04-14 05:47", "device": "前门摄像头", "event": "异常数据传输", "risk": "medium", "status": "info"},
                    {"time": "2025-04-13 22:15", "device": "电源管理单元", "event": "固件漏洞", "risk": "high", "status": "info"},
                    {"time": "2025-04-13 16:32", "device": "后院摄像头", "event": "弱密码", "risk": "medium", "status": "warning"},
                    {"time": "2025-04-13 10:08", "device": "客厅传感器", "event": "异常通信", "risk": "low", "status": "info"}
                ]
            }
            return jsonify({"success": True, "data": data})
        except Exception as e:
            self.logger.error(f"获取安全分析数据失败: {str(e)}")
            return jsonify({"success": False, "message": f"获取安全分析数据失败: {str(e)}"})
    
    def api_bandwidth_data(self):
        """获取带宽分析数据API"""
        try:
            # Generate mock data for bandwidth chart
            labels = ['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00']
            upload_data = [25, 28, 20, 45, 80, 65, 42, 35]
            download_data = [40, 45, 35, 60, 95, 85, 55, 45]
            
            data = {
                "labels": labels,
                "datasets": [
                    {
                        "label": "上传 (Mbps)",
                        "data": upload_data,
                        "borderColor": "#1890ff"
                    },
                    {
                        "label": "下载 (Mbps)",
                        "data": download_data,
                        "borderColor": "#ff6700"
                    }
                ],
                "table_data": [
                    {"device": "主网关", "upload": 54.2, "download": 78.5, "total": 36.7, "status": "normal"},
                    {"device": "前门摄像头", "upload": 12.3, "download": 2.1, "total": 8.4, "status": "normal"},
                    {"device": "后院摄像头", "upload": 18.7, "download": 1.9, "total": 15.2, "status": "warning"},
                    {"device": "客厅传感器", "upload": 0.8, "download": 0.2, "total": 0.4, "status": "normal"},
                    {"device": "电源管理单元", "upload": 1.2, "download": 0.5, "total": 0.6, "status": "normal"}
                ]
            }
            return jsonify({"success": True, "data": data})
        except Exception as e:
            self.logger.error(f"获取带宽分析数据失败: {str(e)}")
            return jsonify({"success": False, "message": f"获取带宽分析数据失败: {str(e)}"})
    
    def api_reliability_data(self):
        """获取可靠性分析数据API"""
        try:
            # Generate mock data for reliability chart
            devices = ['主网关', '前门摄像头', '后院摄像头', '客厅传感器', '电源管理单元', '智能照明控制器']
            uptime_data = [99.98, 98.76, 92.45, 99.92, 99.85, 94.32]
            
            # Colors based on uptime value
            background_colors = []
            for value in uptime_data:
                if value > 99.5:
                    background_colors.append('rgba(82, 196, 26, 0.8)')  # 优秀 - 绿色
                elif value > 98:
                    background_colors.append('rgba(82, 196, 26, 0.6)')   # 良好 - 浅绿色
                elif value > 95:
                    background_colors.append('rgba(250, 173, 20, 0.8)')  # 中等 - 黄色
                else:
                    background_colors.append('rgba(245, 34, 45, 0.8)')   # 差 - 红色
            
            data = {
                "labels": devices,
                "datasets": [
                    {
                        "label": "正常运行时间 (%)",
                        "data": uptime_data,
                        "backgroundColor": background_colors,
                        "borderColor": background_colors
                    }
                ],
                "table_data": [
                    {"device": "主网关", "uptime": 99.98, "mtbf": 45.2, "failures": 1, "rating": "优秀"},
                    {"device": "前门摄像头", "uptime": 98.76, "mtbf": 28.3, "failures": 3, "rating": "良好"},
                    {"device": "客厅传感器", "uptime": 99.92, "mtbf": 38.5, "failures": 2, "rating": "优秀"},
                    {"device": "电源管理单元", "uptime": 99.85, "mtbf": 42.1, "failures": 1, "rating": "优秀"},
                    {"device": "后院摄像头", "uptime": 92.45, "mtbf": 12.7, "failures": 8, "rating": "需改进"}
                ]
            }
            return jsonify({"success": True, "data": data})
        except Exception as e:
            self.logger.error(f"获取可靠性分析数据失败: {str(e)}")
            return jsonify({"success": False, "message": f"获取可靠性分析数据失败: {str(e)}"})
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """启动应用"""
        self.logger.info(f"控制面板应用启动，监听地址: {host}:{port}")
        app.run(host=host, port=port, debug=debug, threaded=True)


# Create the 404.html template if it doesn't exist
def ensure_404_template():
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    file_404 = os.path.join(templates_dir, '404.html')
    if not os.path.exists(file_404):
        with open(file_404, 'w', encoding='utf-8') as f:
            f.write('''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>页面未找到 - 小米AIoT边缘安全控制面板</title>
    <style>
        :root {
            --primary: #ff6700;
            --secondary: #2c2c2c;
        }
        body {
            font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background-color: #fafafa;
            color: #333;
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .error-container {
            text-align: center;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            max-width: 500px;
        }
        h1 {
            color: var(--primary);
            font-size: 32px;
            margin-bottom: 20px;
        }
        p {
            margin-bottom: 20px;
            font-size: 16px;
            line-height: 1.6;
        }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            background-color: var(--primary);
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-weight: 500;
            transition: background-color 0.2s;
        }
        .btn:hover {
            background-color: #ff8533;
        }
    </style>
</head>
<body>
    <div class="error-container">
        <h1>404 - 页面未找到</h1>
        <p>抱歉，您请求的页面不存在。可能是URL输入错误或该页面已被移动。</p>
        <a href="/" class="btn">返回首页</a>
    </div>
</body>
</html>''')


# Handle configuration and startup
def main():
    # Ensure 404 template exists
    ensure_404_template()
    
    # Create the application instance
    dashboard = DashboardApp()
    
    # Run the application
    dashboard.run(debug=True)


if __name__ == "__main__":
    main()