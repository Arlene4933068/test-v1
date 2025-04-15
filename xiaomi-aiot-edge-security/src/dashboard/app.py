#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Dashboard Web应用
整合设备状态、安全防护、网络分析等可视化功能
"""

from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_cors import CORS
import os
import time
import json
import logging
from datetime import datetime, timedelta
from functools import wraps
import threading

# 导入自定义模块
from .architecture import DashboardConfig, DashboardIntegrationManager
from .packet_analyzer import PacketAnalyzer
from .attack_logger import AttackLogger

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 配置
DEFAULT_CONFIG = {
    "web_port": 5000,
    "log_dir": "data/attack_logs",
    "capture_dir": "data/packet_capture",
    "attack_log_retention_days": 30,
    "packet_capture_limit": 100,
    "refresh_interval": 5,
    "enable_packet_capture": True,
    "interfaces": ["eth0"],
    "secret_key": os.urandom(24).hex()
}

# 加载配置
def load_config():
    config_path = os.environ.get('DASHBOARD_CONFIG', 'config/dashboard.json')
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
                logger.info(f"已加载配置文件: {config_path}")
                return {**DEFAULT_CONFIG, **config}  # 合并默认配置
    except Exception as e:
        logger.error(f"加载配置失败: {str(e)}")
    
    logger.warning(f"使用默认配置")
    return DEFAULT_CONFIG

config = load_config()

# 初始化组件
dashboard_config = DashboardConfig(
    refresh_interval=config.get('refresh_interval', 5),
    max_history_records=config.get('max_history_records', 1000),
    enable_realtime_monitoring=config.get('enable_realtime_monitoring', True),
    enable_packet_capture=config.get('enable_packet_capture', True),
    packet_capture_limit=config.get('packet_capture_limit', 100),
    attack_log_retention_days=config.get('attack_log_retention_days', 30)
)

integration_manager = DashboardIntegrationManager(dashboard_config)
packet_analyzer = PacketAnalyzer(config)
attack_logger = AttackLogger(config)

# 连接组件
# 注: 在实际应用中，应该在启动时连接到实际的设备管理器、安全管理器等组件
# 此处为演示，实际操作时需要修改为实际组件的连接方式
try:
    from src.device_simulator import DeviceManager
    from src.security import SecurityManager
    from src.platform_connector import PlatformConnector
    
    # 加载外部组件实例并连接
    device_manager = DeviceManager()
    security_manager = SecurityManager()
    platform_connector = PlatformConnector()
    
    integration_manager.connect_device_manager(device_manager)
    integration_manager.connect_security_manager(security_manager)
    integration_manager.connect_platform_connector(platform_connector)
except ImportError:
    logger.warning("无法导入外部组件，将使用模拟数据")
    # 使用模拟数据
    pass

# 连接数据包分析器
integration_manager.connect_packet_analyzer(packet_analyzer)

# 初始化Flask应用
app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')
app.secret_key = config.get('secret_key', os.urandom(24).hex())
CORS(app)

class DashboardApp:
    """Dashboard应用程序类"""
    
    def __init__(self):
        self.app = app
        
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """运行Dashboard应用"""
        self.app.run(host=host, port=port, debug=debug)

# 身份验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('请先登录', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 简单的身份验证，实际应用中应使用更安全的方法
        if username == 'admin' and password == 'admin':
            session['user'] = username
            next_page = request.args.get('next', url_for('index'))
            return redirect(next_page)
        else:
            error = '用户名或密码错误'
    
    return render_template('login.html', error=error)

# 登出
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('您已成功退出', 'info')
    return redirect(url_for('login'))

# 主页
@app.route('/')
@login_required
def index():
    return render_template('dashboard.html')

# 设备页面
@app.route('/devices')
@login_required
def devices():
    return render_template('devices.html')

# 安全事件页面
@app.route('/security')
@login_required
def security():
    return render_template('security.html')

# 网络分析页面
@app.route('/network')
@login_required
def network():
    return render_template('network.html')

# 报告页面
@app.route('/reports')
@login_required
def reports():
    return render_template('reports.html')

# 设置页面
@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html', config=config)

# API路由 - 获取设备状态
@app.route('/api/devices')
@login_required
def api_devices():
    try:
        devices = integration_manager.get_device_status()
        return jsonify({"success": True, "devices": devices})
    except Exception as e:
        logger.error(f"获取设备状态失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

# API路由 - 获取安全事件
@app.route('/api/security/events')
@login_required
def api_security_events():
    try:
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        device_id = request.args.get('device_id')
        attack_type = request.args.get('attack_type')
        severity = request.args.get('severity')
        handled = request.args.get('handled')
        
        # 构建过滤器
        filters = {}
        if device_id:
            filters['device_id'] = device_id
        if attack_type:
            filters['attack_type'] = attack_type
        if severity:
            filters['severity'] = severity
        if handled is not None:
            filters['handled'] = handled == 'true'
            
        # 获取时间范围
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        
        if start_time:
            start_time = int(start_time)
        if end_time:
            end_time = int(end_time)
        
        events = attack_logger.get_attack_events(
            filters=filters,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            offset=offset
        )
        
        return jsonify({"success": True, "events": events})
    except Exception as e:
        logger.error(f"获取安全事件失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

# API路由 - 获取安全统计信息
@app.route('/api/security/statistics')
@login_required
def api_security_statistics():
    try:
        group_by = request.args.get('group_by', 'day')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        
        if start_time:
            start_time = int(start_time)
        if end_time:
            end_time = int(end_time)
        
        statistics = attack_logger.get_attack_statistics(
            group_by=group_by,
            start_time=start_time,
            end_time=end_time
        )
        
        return jsonify({"success": True, **statistics})
    except Exception as e:
        logger.error(f"获取安全统计信息失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

# API路由 - 处理攻击事件
@app.route('/api/security/events/<int:event_id>', methods=['PUT'])
@login_required
def api_update_event(event_id):
    try:
        data = request.get_json()
        handled = data.get('handled', True)
        
        success = attack_logger.mark_event_handled(event_id, handled)
        
        return jsonify({"success": success})
    except Exception as e:
        logger.error(f"更新事件状态失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

# API路由 - 获取网络分析结果
@app.route('/api/network/analysis')
@login_required
def api_network_analysis():
    try:
        device_id = request.args.get('device_id')
        analysis = packet_analyzer.get_analysis_results(device_id)
        
        return jsonify({"success": True, "analysis": analysis})
    except Exception as e:
        logger.error(f"获取网络分析结果失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

# API路由 - 控制数据包捕获
@app.route('/api/network/capture', methods=['POST'])
@login_required
def api_network_capture():
    try:
        data = request.get_json()
        action = data.get('action')
        device_id = data.get('device_id')
        
        if action == 'start':
            success = packet_analyzer.start_capture(device_id)
            return jsonify({"success": success, "action": "started"})
        elif action == 'stop':
            success = packet_analyzer.stop_capture()
            return jsonify({"success": success, "action": "stopped"})
        else:
            return jsonify({"success": False, "error": "无效的操作"})
    except Exception as e:
        logger.error(f"控制数据包捕获失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

# API路由 - 记录攻击事件
@app.route('/api/security/report', methods=['POST'])
def api_report_attack():
    try:
        data = request.get_json()
        
        # 验证API密钥 (简单版本，实际使用应更安全)
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != config.get('api_key', 'default_key'):
            return jsonify({"success": False, "error": "无效的API密钥"}), 403
        
        event_id = attack_logger.log_attack_event(data)
        
        if event_id > 0:
            return jsonify({"success": True, "event_id": event_id})
        else:
            return jsonify({"success": False, "error": "记录攻击事件失败"})
    except Exception as e:
        logger.error(f"报告攻击失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

# API路由 - 记录错误
@app.route('/api/error/report', methods=['POST'])
def api_report_error():
    try:
        data = request.get_json()
        
        # 验证API密钥
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != config.get('api_key', 'default_key'):
            return jsonify({"success": False, "error": "无效的API密钥"}), 403
        
        error_id = attack_logger.log_error(data)
        
        if error_id > 0:
            return jsonify({"success": True, "error_id": error_id})
        else:
            return jsonify({"success": False, "error": "记录错误信息失败"})
    except Exception as e:
        logger.error(f"报告错误失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

# API路由 - 获取平台状态
@app.route('/api/status')
@login_required
def api_status():
    try:
        metrics = integration_manager.get_platform_metrics()
        return jsonify({"success": True, "metrics": metrics})
    except Exception as e:
        logger.error(f"获取平台状态失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

# 定时任务 - 清理过期日志
def scheduled_cleanup():
    while True:
        try:
            # 每天执行一次清理
            attack_logger.cleanup_old_logs()
            time.sleep(24 * 60 * 60)  # 24小时
        except Exception as e:
            logger.error(f"定时清理任务失败: {str(e)}")
            time.sleep(60 * 60)  # 发生错误时1小时后重试

# 启动定时任务
cleanup_thread = threading.Thread(target=scheduled_cleanup, daemon=True)
cleanup_thread.start()

# 主函数
def main():
    port = config.get('web_port', 5000)
    debug = config.get('debug', False)
    
    logger.info(f"启动Dashboard应用，监听端口: {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)

if __name__ == "__main__":
    main()