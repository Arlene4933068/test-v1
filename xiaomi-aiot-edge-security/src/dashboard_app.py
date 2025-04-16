#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
小米AIoT边缘安全防护研究平台 - 主应用程序
实现各模块数据互通
"""

import os
import sys
import json
import time
import logging
import traceback
import secrets
import functools
import threading
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_socketio import SocketIO, emit

# 设置路径
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(base_dir)

# 导入攻击引擎
from dashboard.attack_engine import AttackEngine

# 辅助函数定义
def banner(message):
    """打印格式化的横幅"""
    line = "=" * 70
    print(f"\n{line}")
    print(f"{message:^70}")
    print(f"{line}\n")

# 禁用Matplotlib的交互模式，避免在无GUI环境中出错
try:
    import matplotlib
    matplotlib.use('Agg')
except ImportError:
    pass

# 配置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger("dashboard")
logger.info("应用启动中...")

# 确保目录路径
templates_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')

# 创建必要的目录
os.makedirs(templates_dir, exist_ok=True)
os.makedirs(static_dir, exist_ok=True)
os.makedirs(os.path.join(static_dir, 'css'), exist_ok=True)
os.makedirs(os.path.join(static_dir, 'js'), exist_ok=True)
os.makedirs(os.path.join(static_dir, 'img'), exist_ok=True)

# 创建Flask应用
app = Flask(__name__, 
           template_folder=templates_dir,
           static_folder=static_dir)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = secrets.token_hex(16)  # 为session和SocketIO设置密钥
app.config['PROPAGATE_EXCEPTIONS'] = True  # 确保错误被传递到日志

# 初始化SocketIO
socketio = SocketIO(app)

# 初始化攻击引擎
attack_engine = AttackEngine()

# 全局应用状态 - 用于在各模块间共享数据
app_state = {
    "devices": [
        {"id": 'gateway_001', "name": '家庭网关', "type": 'gateway', "platform": 'simulator', "status": 'online', "lastActive": '2分钟前', "ip": "192.168.1.1", "security_score": 76},
        {"id": 'speaker_001', "name": '小爱音箱', "type": 'speaker', "platform": 'thingsboard', "status": 'online', "lastActive": '5分钟前', "ip": "192.168.1.2", "security_score": 82},
        {"id": 'camera_001', "name": '门口摄像头', "type": 'camera', "platform": 'thingsboard', "status": 'online', "lastActive": '1分钟前', "ip": "192.168.1.10", "security_score": 65},
        {"id": 'router_001', "name": '客厅路由器', "type": 'router', "platform": 'edgex', "status": 'online', "lastActive": '3分钟前', "ip": "192.168.1.254", "security_score": 70},
        {"id": 'sensor_001', "name": '温湿度传感器', "type": 'sensor', "platform": 'edgex', "status": 'offline', "lastActive": '1小时前', "ip": "192.168.1.20", "security_score": 90}
    ],
    "vulnerabilities": [],
    "active_attacks": [],
    "attack_history": [],
    "system_stats": {
        "security_score": 76,
        "total_vulnerabilities": 24,
        "recent_attacks": 56,
        "fix_rate": 65
    },
    "notifications": [],
    "thingsboard_config": {
        "host": "localhost",
        "port": 8080,
        "mqtt_port": 1883,
        "auth": {
            "username": "yy3205543068@gmail.com",
            "password": "wlsxcdh52jy.L"
        },
        "settings": {
            "mqtt_enabled": True,
            "auto_sync": True,
            "sync_interval_minutes": 15,
            "retry_on_failure": True,
            "max_retries": 3
        }
    }
}

# 身份验证装饰器
def login_required(view_func):
    @functools.wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login', next=request.url))
        return view_func(*args, **kwargs)
    return wrapped_view

@app.route('/login', methods=['GET', 'POST'])
def login():
    """处理登录"""
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'admin' and password == 'admin':
            session['user'] = username
            flash('登录成功！', 'success')
            return redirect(url_for('index'))
        else:
            error = '用户名或密码错误'
    
    return render_template('login.html', error=error, current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/logout')
def logout():
    """处理退出登录"""
    session.pop('user', None)
    flash('您已成功退出登录', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """应用主页/仪表盘"""
    try:
        logger.info("访问仪表盘页面")
        
        # 获取最新的攻击历史
        recent_attacks = app_state['attack_history'][:5]
        
        # 获取设备安全状态
        devices_with_security = app_state['devices']
        
        # 获取系统统计数据
        system_stats = app_state['system_stats']
        
        return render_template('dashboard.html', 
                             current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                             devices=devices_with_security,
                             recent_attacks=recent_attacks,
                             system_stats=system_stats)
    except Exception as e:
        logger.error(f"仪表盘页面渲染错误: {str(e)}")
        logger.error(traceback.format_exc())
        return redirect(url_for('error_page', error=str(e)))

@app.route('/devices')
@login_required
def device_management():
    """设备管理页面"""
    try:
        logger.info("访问设备管理页面")
        
        # 获取设备数据，包括安全相关信息
        devices = app_state['devices']
        
        # 获取设备相关的漏洞信息
        device_vulnerabilities = {}
        for vulnerability in app_state['vulnerabilities']:
            device_id = vulnerability.get('device_id')
            if device_id:
                if device_id not in device_vulnerabilities:
                    device_vulnerabilities[device_id] = []
                device_vulnerabilities[device_id].append(vulnerability)
        
        return render_template('devices.html', 
                             current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                             devices=devices,
                             device_vulnerabilities=device_vulnerabilities)
    except Exception as e:
        logger.error(f"设备管理页面渲染错误: {str(e)}")
        logger.error(traceback.format_exc())
        return redirect(url_for('error_page', error=str(e)))

@app.route('/thingsboard')
@login_required
def thingsboard_integration():
    """ThingsBoard集成页面"""
    try:
        logger.info("访问ThingsBoard集成页面")
        
        # 获取ThingsBoard配置
        config = app_state['thingsboard_config']
        
        # 获取ThingsBoard设备
        thingsboard_devices = [d for d in app_state['devices'] if d['platform'] == 'thingsboard']
        
        return render_template('thingsboard.html', 
                             current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                             config=config,
                             devices=thingsboard_devices)
    except Exception as e:
        logger.error(f"ThingsBoard集成页面渲染错误: {str(e)}")
        logger.error(traceback.format_exc())
        return redirect(url_for('error_page', error=str(e)))

@app.route('/attack')
@login_required
def attack_module():
    """攻击模块页面"""
    try:
        logger.info("访问攻击模块页面")
        
        # 获取可用的设备作为攻击目标
        devices = app_state['devices']
        
        # 获取活跃攻击
        active_attacks = app_state['active_attacks']
        
        # 获取攻击历史
        attack_history = app_state['attack_history']
        
        return render_template('attack.html', 
                             current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                             devices=devices,
                             active_attacks=active_attacks,
                             attack_history=attack_history)
    except Exception as e:
        logger.error(f"攻击模块页面渲染错误: {str(e)}")
        logger.error(traceback.format_exc())
        return redirect(url_for('error_page', error=str(e)))

@app.route('/analysis')
@login_required
def analysis_module():
    """数据分析页面"""
    try:
        logger.info("访问数据分析页面")
        
        # 获取系统统计数据
        system_stats = app_state['system_stats']
        
        # 获取漏洞信息
        vulnerabilities = app_state['vulnerabilities']
        
        # 按设备分组漏洞
        device_vulnerabilities = {}
        for vulnerability in vulnerabilities:
            device_id = vulnerability.get('device_id')
            if device_id:
                if device_id not in device_vulnerabilities:
                    device_vulnerabilities[device_id] = []
                device_vulnerabilities[device_id].append(vulnerability)
        
        # 按类型分组漏洞
        vulnerability_types = {}
        for vulnerability in vulnerabilities:
            vuln_type = vulnerability.get('type', 'unknown')
            if vuln_type not in vulnerability_types:
                vulnerability_types[vuln_type] = {'count': 0, 'severity': {}}
            
            vulnerability_types[vuln_type]['count'] += 1
            severity = vulnerability.get('severity', 'low')
            if severity not in vulnerability_types[vuln_type]['severity']:
                vulnerability_types[vuln_type]['severity'][severity] = 0
            vulnerability_types[vuln_type]['severity'][severity] += 1
        
        # 获取攻击历史
        attack_history = app_state['attack_history']
        
        return render_template('analysis.html', 
                             current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                             system_stats=system_stats,
                             vulnerabilities=vulnerabilities,
                             device_vulnerabilities=device_vulnerabilities,
                             vulnerability_types=vulnerability_types,
                             attack_history=attack_history)
    except Exception as e:
        logger.error(f"数据分析页面渲染错误: {str(e)}")
        logger.error(traceback.format_exc())
        return redirect(url_for('error_page', error=str(e)))

@app.route('/security')
@login_required
def security_monitoring():
    """安全监控页面"""
    try:
        logger.info("访问安全监控页面")
        
        # 获取所有漏洞
        vulnerabilities = app_state['vulnerabilities']
        
        # 获取活跃攻击
        active_attacks = app_state['active_attacks']
        
        # 获取通知
        notifications = app_state['notifications']
        
        return render_template('security.html', 
                             current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                             vulnerabilities=vulnerabilities,
                             active_attacks=active_attacks,
                             notifications=notifications)
    except Exception as e:
        logger.error(f"安全监控页面渲染错误: {str(e)}")
        logger.error(traceback.format_exc())
        return redirect(url_for('error_page', error=str(e)))

@app.route('/error')
def error_page():
    """错误页面"""
    error_message = request.args.get('error', '未知错误')
    
    return render_template('500.html', 
                          current_user=session.get('user', 'Guest'),
                          current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                          error=error_message)

# 设备管理API
@app.route('/api/devices', methods=['GET'])
@login_required
def api_get_devices():
    """API: 获取所有设备"""
    try:
        return jsonify({"success": True, "data": app_state['devices']})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/devices/<device_id>', methods=['GET'])
@login_required
def api_get_device(device_id):
    """API: 获取指定设备信息"""
    try:
        for device in app_state['devices']:
            if device['id'] == device_id:
                # 获取设备相关的漏洞
                device_vulnerabilities = []
                for vulnerability in app_state['vulnerabilities']:
                    if vulnerability.get('device_id') == device_id:
                        device_vulnerabilities.append(vulnerability)
                
                # 获取设备相关的攻击历史
                device_attacks = []
                for attack in app_state['attack_history']:
                    if attack.get('target_id') == device_id or attack.get('target') == device.get('ip'):
                        device_attacks.append(attack)
                
                return jsonify({
                    "success": True, 
                    "data": {
                        "device": device,
                        "vulnerabilities": device_vulnerabilities,
                        "attack_history": device_attacks
                    }
                })
        
        return jsonify({"success": False, "error": f"未找到设备: {device_id}"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/devices', methods=['POST'])
@login_required
def api_add_device():
    """API: 添加设备"""
    try:
        data = request.json
        
        # 生成设备ID
        device_id = f"{data['type']}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        new_device = {
            "id": device_id,
            "name": data['name'],
            "type": data['type'],
            "platform": data.get('platform', 'simulator'),
            "status": 'online',
            "lastActive": '刚刚',
            "ip": data.get('ip', '192.168.1.100'),
            "security_score": data.get('security_score', 80)
        }
        
        app_state['devices'].append(new_device)
        logger.info(f"添加了新设备: {device_id}")
        
        # 发送WebSocket通知所有客户端
        socketio.emit('device_added', {'device': new_device})
        
        return jsonify({"success": True, "data": new_device})
    except Exception as e:
        logger.error(f"添加设备失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

# ThingsBoard配置API
@app.route('/api/thingsboard/config', methods=['GET'])
@login_required
def api_get_tb_config():
    """API: 获取ThingsBoard配置"""
    try:
        # 返回配置时隐藏密码
        config_copy = dict(app_state['thingsboard_config'])
        if 'auth' in config_copy and 'password' in config_copy['auth']:
            config_copy['auth']['password'] = '******'
        return jsonify({"success": True, "data": config_copy})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/thingsboard/config', methods=['POST'])
@login_required
def api_update_tb_config():
    """API: 更新ThingsBoard配置"""
    try:
        data = request.json
        
        # 更新配置
        app_state['thingsboard_config'].update({
            "host": data.get('host', app_state['thingsboard_config']['host']),
            "port": data.get('port', app_state['thingsboard_config']['port']),
            "mqtt_port": data.get('mqtt_port', app_state['thingsboard_config']['mqtt_port'])
        })
        
        # 仅当提供了新密码时更新
        if 'auth' in data:
            app_state['thingsboard_config']['auth'].update({
                "username": data['auth'].get('username', app_state['thingsboard_config']['auth']['username'])
            })
            if data['auth'].get('password') and data['auth']['password'] != '******':
                app_state['thingsboard_config']['auth']['password'] = data['auth']['password']
        
        # 更新设置
        if 'settings' in data:
            app_state['thingsboard_config']['settings'].update(data['settings'])
        
        logger.info("更新了ThingsBoard配置")
        
        # 返回更新后的配置，但隐藏密码
        config_copy = dict(app_state['thingsboard_config'])
        if 'auth' in config_copy and 'password' in config_copy['auth']:
            config_copy['auth']['password'] = '******'
        return jsonify({"success": True, "data": config_copy})
    except Exception as e:
        logger.error(f"更新ThingsBoard配置失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

# 攻击模块API
@app.route('/api/attacks', methods=['GET'])
@login_required
def api_get_attacks():
    """API: 获取所有活动攻击"""
    try:
        return jsonify({"success": True, "data": app_state['active_attacks']})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/attacks/history', methods=['GET'])
@login_required
def api_get_attack_history():
    """API: 获取攻击历史"""
    try:
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        history = app_state['attack_history'][offset:offset+limit]
        return jsonify({"success": True, "data": history})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/attacks/<attack_id>', methods=['GET'])
@login_required
def api_get_attack_details(attack_id):
    """API: 获取攻击详情"""
    try:
        # 先在活动攻击中查找
        for attack in app_state['active_attacks']:
            if attack['id'] == attack_id:
                return jsonify({"success": True, "data": attack})
        
        # 再在历史记录中查找
        for attack in app_state['attack_history']:
            if attack['id'] == attack_id:
                return jsonify({"success": True, "data": attack})
        
        return jsonify({"success": False, "error": f"未找到攻击: {attack_id}"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/attacks', methods=['POST'])
@login_required
def api_launch_attack():
    """API: 启动攻击"""
    try:
        data = request.json
        attack_type = data.get('type')
        target_id = data.get('target')
        params = data.get('params', {})
        duration = data.get('duration', 30)
        analysis = data.get('analysis', True)
        
        if not attack_type or not target_id:
            return jsonify({"success": False, "error": "缺少必要参数"}), 400
        
        # 查找目标设备
        target_device = None
        for device in app_state['devices']:
            if device['id'] == target_id:
                target_device = device
                break
        
        if not target_device:
            return jsonify({"success": False, "error": f"未找到设备: {target_id}"}), 404
        
        # 使用攻击引擎启动攻击
        result = attack_engine.launch_attack(attack_type, target_device['ip'], params, duration, analysis)
        
        if result.get('success'):
            # 创建攻击记录
            attack_id = result.get('attack_id')
            attack_record = {
                "id": attack_id,
                "type": attack_type,
                "target_id": target_id,
                "target": target_device['ip'],
                "target_name": target_device['name'],
                "params": params,
                "status": "running",
                "start_time": datetime.now().isoformat(),
                "duration": duration,
                "logs": [],
                "results": None
            }
            
            # 添加到活动攻击
            app_state['active_attacks'].append(attack_record)
            
            # 创建线程监控攻击状态
            threading.Thread(target=monitor_attack, args=(attack_id,), daemon=True).start()
            
            # 发送WebSocket通知
            socketio.emit('attack_started', {'attack': attack_record})
            
            return jsonify({
                "success": True,
                "attack_id": attack_id,
                "message": f"攻击已启动: {attack_id}"
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get('error', '启动攻击失败')
            }), 500
    except Exception as e:
        logger.error(f"启动攻击失败: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/security/attack/mitm/start', methods=['POST'])
@login_required
def api_start_mitm_attack():
    """API: 启动中间人攻击"""
    try:
        data = request.json
        target_id = data.get('target')
        interface = data.get('interface', 'eth0')
        duration = data.get('duration', 30)
        
        if not target_id:
            return jsonify({"success": False, "error": "缺少目标设备ID"}), 400
        
        # 查找目标设备
        target_device = None
        for device in app_state['devices']:
            if device['id'] == target_id:
                target_device = device
                break
        
        if not target_device:
            return jsonify({"success": False, "error": f"未找到设备: {target_id}"}), 404
        
        # 配置MITM攻击参数
        mitm_params = {
            "interface": interface,
            "target_mac": data.get('target_mac'),  # 可选MAC地址
            "gateway_ip": data.get('gateway_ip'),  # 可选网关IP
            "packet_filter": data.get('packet_filter', ''),  # 可选数据包过滤规则
            "save_pcap": data.get('save_pcap', True)  # 是否保存捕获的数据包
        }
        
        # 使用攻击引擎启动MITM攻击
        result = attack_engine.launch_attack('mitm', target_device['ip'], mitm_params, duration, True)
        
        if result.get('success'):
            attack_id = result.get('attack_id')
            attack_record = {
                "id": attack_id,
                "type": "mitm",
                "target_id": target_id,
                "target": target_device['ip'],
                "target_name": target_device['name'],
                "params": mitm_params,
                "status": "running",
                "start_time": datetime.now().isoformat(),
                "duration": duration,
                "logs": [],
                "results": None
            }
            
            # 添加到活动攻击
            app_state['active_attacks'].append(attack_record)
            
            # 创建线程监控攻击状态
            threading.Thread(target=monitor_attack, args=(attack_id,), daemon=True).start()
            
            return jsonify({
                "success": True,
                "attack_id": attack_id,
                "message": "MITM攻击已启动"
            })
        else:
            return jsonify({
                "success": False,
                "error": result.get('error', '启动MITM攻击失败')
            }), 500
            
    except Exception as e:
        logger.error(f"启动MITM攻击失败: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500
            
            # 发送WebSocket通知
        socketio.emit('attack_launched', {
                'attack': attack_record,
                'device': target_device
            })
            
            # 添加通知
        add_notification(f"启动了对 {target_device['name']} 的 {get_attack_name(attack_type)} 攻击", "warning")
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"启动攻击失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/attacks/<attack_id>', methods=['DELETE'])
@login_required
def api_stop_attack(attack_id):
    """API: 停止攻击"""
    try:
        # 使用攻击引擎停止攻击
        result = attack_engine.stop_attack(attack_id)
        
        if result.get('success'):
            # 更新活动攻击状态
            for i, attack in enumerate(app_state['active_attacks']):
                if attack['id'] == attack_id:
                    app_state['active_attacks'][i]['status'] = 'stopped'
                    
                    # 添加到历史记录
                    attack_copy = app_state['active_attacks'][i].copy()
                    attack_copy['end_time'] = datetime.now().isoformat()
                    app_state['attack_history'].insert(0, attack_copy)
                    
                    # 从活动攻击中移除
                    app_state['active_attacks'].pop(i)
                    
                    # 发送WebSocket通知
                    socketio.emit('attack_stopped', {
                        'attack_id': attack_id,
                        'status': 'stopped'
                    })
                    
                    # 添加通知
                    add_notification(f"停止了对 {attack_copy['target_name']} 的攻击", "info")
                    
                    break
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# 漏洞API
@app.route('/api/vulnerabilities', methods=['GET'])
@login_required
def api_get_vulnerabilities():
    """API: 获取所有漏洞"""
    try:
        return jsonify({"success": True, "data": app_state['vulnerabilities']})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/vulnerabilities/<device_id>', methods=['GET'])
@login_required
def api_get_device_vulnerabilities(device_id):
    """API: 获取指定设备的漏洞"""
    try:
        device_vulnerabilities = []
        for vulnerability in app_state['vulnerabilities']:
            if vulnerability.get('device_id') == device_id:
                device_vulnerabilities.append(vulnerability)
        
        return jsonify({"success": True, "data": device_vulnerabilities})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# 系统状态API
@app.route('/api/system/stats', methods=['GET'])
@login_required
def api_get_system_stats():
    """API: 获取系统统计数据"""
    try:
        return jsonify({"success": True, "data": app_state['system_stats']})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# 调试路由
@app.route('/debug')
def debug():
    """调试页面"""
    try:
        logger.info("访问调试页面")
        
        # 收集系统信息
        import platform
        
        # 检查依赖模块
        dependencies = {}
        for module_name in ['flask', 'werkzeug', 'jinja2', 'matplotlib', 'pandas', 'flask_socketio']:
            try:
                module = __import__(module_name)
                dependencies[module_name] = getattr(module, '__version__', '未知版本')
            except ImportError:
                dependencies[module_name] = '未安装'
        
        # 检查目录
        dirs = {
            '应用目录': base_dir,
            '模板目录': templates_dir,
            '静态文件目录': static_dir
        }
        
        for name, path in dirs.items():
            dirs[name] = {
                'path': path,
                'exists': os.path.exists(path),
                'files': os.listdir(path) if os.path.exists(path) else []
            }
        
        # 返回HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>系统调试 - 小米AIoT边缘安全防护研究平台</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                h1 {{ color: #ff6700; }}
                h2 {{ color: #333; margin-top: 30px; }}
                pre {{ background: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                .section {{ margin-bottom: 30px; }}
                .success {{ color: green; }}
                .error {{ color: red; }}
            </style>
        </head>
        <body>
            <h1>系统调试</h1>
            
            <div class="section">
                <h2>系统信息</h2>
                <pre>Python: {sys.version}
平台: {platform.platform()}
工作目录: {os.getcwd()}</pre>
            </div>
            
            <div class="section">
                <h2>依赖模块</h2>
                <ul>
        """
        
        for name, version in dependencies.items():
            status = "success" if version != "未安装" else "error"
            html += f'<li><span class="{status}">{name}: {version}</span></li>'
        
        html += """
                </ul>
            </div>
            
            <div class="section">
                <h2>目录信息</h2>
        """
        
        for name, info in dirs.items():
            status = "success" if info['exists'] else "error"
            html += f'<h3>{name} <span class="{status}">{"存在" if info["exists"] else "不存在"}</span></h3>'
            html += f'<pre>{info["path"]}</pre>'
            
            if info['exists']:
                if info['files']:
                    html += '<ul>'
                    for file in sorted(info['files']):
                        html += f'<li>{file}</li>'
                    html += '</ul>'
                else:
                    html += '<p>目录为空</p>'
        
        html += """
            </div>
            
            <div class="section">
                <h2>ThingsBoard 集成信息</h2>
        """
        
        tb_config = dict(app_state['thingsboard_config'])
        if 'auth' in tb_config and 'password' in tb_config['auth']:
            tb_config['auth']['password'] = '******'
        
        html += f'<pre>{json.dumps(tb_config, indent=2)}</pre>'
        
        html += """
            </div>
            
            <div class="section">
                <h2>设备信息</h2>
        """
        
        html += f'<pre>{json.dumps(app_state["devices"], indent=2)}</pre>'
        
        html += """
            </div>
            
            <div class="section">
                <h2>攻击模块状态</h2>
        """
        
        attack_engine_state = {
            "active_attacks": len(app_state['active_attacks']),
            "attack_history": len(app_state['attack_history']),
            "available_modules": attack_engine.get_available_modules()
        }
        
        html += f'<pre>{json.dumps(attack_engine_state, indent=2)}</pre>'
        
        html += """
            </div>
            
            <div class="section">
                <h2>系统统计</h2>
        """
        
        html += f'<pre>{json.dumps(app_state["system_stats"], indent=2)}</pre>'
        
        html += """
            </div>
            
            <div class="section">
                <h2>链接</h2>
                <ul>
                    <li><a href="/">首页</a></li>
                    <li><a href="/devices">设备管理</a></li>
                    <li><a href="/thingsboard">ThingsBoard集成</a></li>
                    <li><a href="/attack">攻击模块</a></li>
                    <li><a href="/analysis">数据分析</a></li>
                </ul>
            </div>
        </body>
        </html>
        """
        
        return html
    except Exception as e:
        logger.error(f"调试页面错误: {str(e)}")
        logger.error(traceback.format_exc())
        return f"调试页面生成错误: {str(e)}", 500

# 错误处理器
@app.errorhandler(404)
def page_not_found(e):
    """处理404错误"""
    logger.warning(f"404错误: {request.path}")
    try:
        return render_template('404.html', 
                              path=request.path,
                              current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')), 404
    except Exception as template_error:
        logger.error(f"渲染404模板失败: {str(template_error)}")
        return f"404 - 页面未找到: {request.path}", 404

@app.errorhandler(500)
def internal_error(error):
    """处理500错误"""
    logger.error(f'服务器错误: {error}')
    logger.error(traceback.format_exc())
    
    try:
        return render_template('500.html', 
                              current_user=session.get('user', 'Guest'), 
                              current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                              error=str(error)), 500
    except Exception as template_error:
        logger.error(f"渲染错误模板失败: {str(template_error)}")
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>服务器错误</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                h1 {{ color: #e53e3e; }}
                pre {{ background: #f5f5f5; padding: 10px; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <h1>500 - 服务器错误</h1>
            <p>服务器遇到内部错误，无法完成请求。</p>
            <h3>错误信息:</h3>
            <pre>{str(error)}</pre>
            <p>模板渲染也失败: {str(template_error)}</p>
            <p><a href="/">返回首页</a></p>
        </body>
        </html>
        """, 500

# WebSocket事件处理
@socketio.on('connect')
def handle_connect():
    """处理客户端连接"""
    logger.info(f"WebSocket客户端连接: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """处理客户端断开连接"""
    logger.info(f"WebSocket客户端断开连接: {request.sid}")

@socketio.on('subscribe_attack_updates')
def handle_subscribe_attack(data):
    """处理客户端订阅攻击更新"""
    attack_id = data.get('attack_id')
    logger.info(f"客户端 {request.sid} 订阅攻击 {attack_id} 的更新")

# 辅助函数
def monitor_attack(attack_id):
    """监控攻击状态并更新数据"""
    try:
        # 每秒检查一次攻击状态
        while True:
            attack_details = attack_engine.get_attack_details(attack_id)
            
            if not attack_details:
                # 如果找不到攻击，可能已结束
                for i, attack in enumerate(app_state['active_attacks']):
                    if attack['id'] == attack_id:
                        # 更新状态
                        app_state['active_attacks'][i]['status'] = 'completed'
                        
                        # 添加到历史记录
                        attack_copy = app_state['active_attacks'][i].copy()
                        attack_copy['end_time'] = datetime.now().isoformat()
                        app_state['attack_history'].insert(0, attack_copy)
                        
                        # 从活动攻击中移除
                        app_state['active_attacks'].pop(i)
                        
                        # 发送WebSocket通知
                        socketio.emit('attack_completed', {
                            'attack_id': attack_id,
                            'status': 'completed',
                            'attack': attack_copy
                        })
                        
                        # 处理漏洞发现
                        process_attack_results(attack_copy)
                        
                        break
                break
            
            # 更新攻击状态
            for i, attack in enumerate(app_state['active_attacks']):
                if attack['id'] == attack_id:
                    # 更新状态、日志和结果
                    app_state['active_attacks'][i]['status'] = attack_details.get('status', attack['status'])
                    app_state['active_attacks'][i]['logs'] = attack_details.get('logs', attack.get('logs', []))
                    app_state['active_attacks'][i]['results'] = attack_details.get('results', attack.get('results'))
                    
                    # 如果攻击已完成
                    if attack_details.get('status') in ['completed', 'failed', 'stopped']:
                        # 添加到历史记录
                        attack_copy = app_state['active_attacks'][i].copy()
                        attack_copy['end_time'] = datetime.now().isoformat()
                        app_state['attack_history'].insert(0, attack_copy)
                        
                        # 从活动攻击中移除
                        app_state['active_attacks'].pop(i)
                        
                        # 发送WebSocket通知
                        socketio.emit('attack_completed', {
                            'attack_id': attack_id,
                            'status': attack_details.get('status', 'completed'),
                            'attack': attack_copy
                        })
                        
                        # 处理漏洞发现
                        process_attack_results(attack_copy)
                        
                        return
                    
                    # 发送WebSocket更新
                    socketio.emit('attack_update', {
                        'attack_id': attack_id,
                        'logs': app_state['active_attacks'][i]['logs'][-5:] if app_state['active_attacks'][i]['logs'] else [],
                        'status': app_state['active_attacks'][i]['status']
                    })
                    break
            
            time.sleep(1)
    except Exception as e:
        logger.error(f"监控攻击 {attack_id} 时出错: {str(e)}")

def process_attack_results(attack):
    """处理攻击结果，提取漏洞并更新系统状态"""
    try:
        results = attack.get('results', {})
        findings = results.get('findings', [])
        
        if not findings:
            return
        
        # 查找目标设备
        target_device = None
        for device in app_state['devices']:
            if device['id'] == attack['target_id']:
                target_device = device
                break
        
        if not target_device:
            logger.warning(f"找不到攻击目标设备: {attack['target_id']}")
            return
        
        # 处理每个发现的漏洞
        for finding in findings:
            # 创建漏洞记录
            vuln_id = f"VULN-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(app_state['vulnerabilities'])}"
            
            vulnerability = {
                "id": vuln_id,
                "device_id": target_device['id'],
                "device_name": target_device['name'],
                "attack_id": attack['id'],
                "type": finding.get('type', 'unknown'),
                "severity": finding.get('severity', 'low'),
                "details": finding.get('details', '无详细信息'),
                "discovered_at": datetime.now().isoformat(),
                "status": "open"
            }
            
            # 添加到漏洞列表
            app_state['vulnerabilities'].append(vulnerability)
            
            # 降低设备安全评分
            severity_score = {
                'critical': 15,
                'high': 10,
                'medium': 5,
                'low': 2
            }
            
            score_reduction = severity_score.get(finding.get('severity', 'low'), 2)
            target_device['security_score'] = max(0, target_device['security_score'] - score_reduction)
            
            # 更新系统统计数据
            app_state['system_stats']['total_vulnerabilities'] += 1
            
            # 发送WebSocket通知
            socketio.emit('vulnerability_found', {
                'vulnerability': vulnerability,
                'device': target_device
            })
            
            # 添加通知
            severity_text = {
                'critical': '严重',
                'high': '高危',
                'medium': '中危',
                'low': '低危'
            }
            
            severity = finding.get('severity', 'low')
            add_notification(
                f"在 {target_device['name']} 上发现了 {severity_text.get(severity, '未知')} 级别的 {get_vulnerability_name(finding.get('type', 'unknown'))} 漏洞",
                "danger" if severity in ['critical', 'high'] else "warning"
            )
        
        # 重新计算系统安全评分
        recalculate_system_security_score()
        
    except Exception as e:
        logger.error(f"处理攻击结果时出错: {str(e)}")

def add_notification(message, level="info"):
    """添加系统通知"""
    notification = {
        "id": len(app_state['notifications']),
        "message": message,
        "level": level,
        "timestamp": datetime.now().isoformat(),
        "read": False
    }
    
    app_state['notifications'].insert(0, notification)
    
    # 保持通知数量在合理范围内
    if len(app_state['notifications']) > 50:
        app_state['notifications'] = app_state['notifications'][:50]
    
    # 发送WebSocket通知
    socketio.emit('notification', notification)

def recalculate_system_security_score():
    """重新计算系统安全评分"""
    try:
        # 基于设备安全评分计算整体评分
        if not app_state['devices']:
            return
        
        total_score = sum(d['security_score'] for d in app_state['devices'])
        avg_score = total_score / len(app_state['devices'])
        
        # 考虑漏洞数量的影响
        vuln_penalty = min(20, len(app_state['vulnerabilities']) * 0.5)
        
        # 计算最终评分
        final_score = max(0, min(100, avg_score - vuln_penalty))
        
        # 更新系统统计
        app_state['system_stats']['security_score'] = round(final_score)
        app_state['system_stats']['recent_attacks'] = len(app_state['attack_history'])
        
        # 计算修复比例
        fixed_vulns = sum(1 for v in app_state['vulnerabilities'] if v['status'] == 'fixed')
        total_vulns = len(app_state['vulnerabilities'])
        fix_rate = (fixed_vulns / total_vulns * 100) if total_vulns > 0 else 100
        
        app_state['system_stats']['fix_rate'] = round(fix_rate)
        
    except Exception as e:
        logger.error(f"计算安全评分时出错: {str(e)}")

def get_attack_name(attack_type):
    """获取攻击类型的中文名称"""
    attack_names = {
        'dos': 'DoS/DDoS攻击',
        'arp-spoof': 'ARP欺骗攻击',
        'wifi-deauth': 'Wi-Fi去认证攻击',
        'port-scan': '端口扫描',
        'man-in-middle': '中间人攻击',
        'packet-sniffing': '数据包嗅探',
        'wifi-crack': 'Wi-Fi密码破解',
        'dns-spoof': 'DNS欺骗',
        'syn-flood': 'SYN洪水攻击',
        'icmp-flood': 'ICMP洪水攻击',
        'mqtt-vuln': 'MQTT协议漏洞攻击',
        'coap-vuln': 'CoAP协议漏洞攻击',
        'zigbee-vuln': 'Zigbee协议漏洞攻击',
        'firmware-extract': '固件提取',
        'password-bypass': '密码绕过',
        'custom-script': '自定义脚本攻击'
    }
    return attack_names.get(attack_type, attack_type)

def get_vulnerability_name(vuln_type):
    """获取漏洞类型的中文名称"""
    vuln_names = {
        'authentication': '认证漏洞',
        'topic_enumeration': '主题枚举漏洞',
        'payload_injection': '负载注入漏洞',
        'weak_password': '弱密码漏洞',
        'sql_injection': 'SQL注入漏洞',
        'command_injection': '命令注入漏洞',
        'xss': '跨站脚本漏洞',
        'csrf': '跨站请求伪造漏洞',
        'session_manipulation': '会话操纵漏洞'
    }
    return vuln_names.get(vuln_type, vuln_type)

# 初始化页面模板
def init_templates():
    """初始化应用所需的HTML模板"""
    # 确保模板目录存在
    os.makedirs(templates_dir, exist_ok=True)
    
    # 初始化404错误页面模板
    error_404_path = os.path.join(templates_dir, '404.html')
    if not os.path.exists(error_404_path):
        with open(error_404_path, 'w', encoding='utf-8') as f:
            f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>页面不存在 - 小米AIoT边缘安全防护研究平台</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 800px; margin: 40px auto; padding: 20px; background-color: #fff; border-radius: 5px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #3182ce; margin-top: 0; }
        .footer { margin-top: 30px; font-size: 0.9em; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h1>404 - 页面不存在</h1>
        <p>抱歉，您请求的页面不存在。</p>
        <p>路径: {{ path }}</p>
        
        <div class="footer">
            <p>时间: {{ current_time }}</p>
            <p><a href="/">返回首页</a></p>
        </div>
    </div>
</body>
</html>""")
    
    # 初始化500错误页面模板
    error_500_path = os.path.join(templates_dir, '500.html')
    if not os.path.exists(error_500_path):
        with open(error_500_path, 'w', encoding='utf-8') as f:
            f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>服务器错误 - 小米AIoT边缘安全防护研究平台</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 800px; margin: 40px auto; padding: 20px; background-color: #fff; border-radius: 5px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #e53e3e; margin-top: 0; }
        pre { background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }
        .footer { margin-top: 30px; font-size: 0.9em; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h1>500 - 服务器内部错误</h1>
        <p>抱歉，服务器遇到了内部错误，无法完成您的请求。</p>
        <h3>错误信息:</h3>
        <pre>{{ error }}</pre>
        
        <div class="footer">
            <p>时间: {{ current_time }}</p>
            <p>用户: {{ current_user }}</p>
            <p><a href="/">返回首页</a></p>
        </div>
    </div>
</body>
</html>""")
    
    # 可以根据需要添加其他模板的初始化

if __name__ == "__main__":
    try:
        # 初始化模板
        init_templates()
        
        banner("小米AIoT边缘安全防护研究平台")
        print(f"• 工作目录: {os.getcwd()}")
        print(f"• 应用目录: {base_dir}")
        print(f"• 模板目录: {templates_dir}")
        print(f"• 静态目录: {static_dir}")
        print("\n• 账号信息: 用户名=admin, 密码=admin")
        
        # 在子线程中定期更新系统状态，模拟真实环境
        def update_system_state():
            while True:
                try:
                    # 更新设备活跃时间
                    for i, device in enumerate(app_state['devices']):
                        if device['status'] == 'online':
                            app_state['devices'][i]['lastActive'] = '刚刚'
                    
                    # 模拟随机事件
                    if len(app_state['active_attacks']) > 0 and random.random() < 0.1:
                        # 随机更新攻击日志
                        attack = random.choice(app_state['active_attacks'])
                        attack['logs'].append({
                            "timestamp": datetime.now().isoformat(),
                            "level": random.choice(["info", "success", "warning", "error"]),
                            "message": f"自动生成的攻击日志消息 {datetime.now().strftime('%H:%M:%S')}"
                        })
                except Exception as e:
                    logger.error(f"更新系统状态时出错: {str(e)}")
                
                time.sleep(30)  # 每30秒更新一次
        
        # 启动后台任务线程
        import random
        import threading
        threading.Thread(target=update_system_state, daemon=True).start()
        
        print("\n启动服务器，访问 http://localhost:5000 查看应用...")
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.critical(f"启动失败: {str(e)}")
        logger.critical(traceback.format_exc())
        print(f"\n严重错误: {str(e)}")
        print("请查看日志获取更多信息。")