#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
小米AIoT边缘安全防护研究平台 - ThingsBoard Edge 集成
"""

import os
import sys
import json
import logging
import traceback
import secrets
import functools
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime
from attack_engine import AttackEngine

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
base_dir = os.path.dirname(os.path.abspath(__file__))
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
app.config['PROPAGATE_EXCEPTIONS'] = True  # 确保错误被传递到日志
app.secret_key = secrets.token_hex(16)     # 为session设置密钥

# 模拟ThingsBoard连接配置
thingsboard_config = {
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

# 模拟设备数据
devices = [
    {"id": 'gateway_001', "name": '家庭网关', "type": 'gateway', "platform": 'simulator', "status": 'online', "lastActive": '2分钟前'},
    {"id": 'speaker_001', "name": '小爱音箱', "type": 'speaker', "platform": 'thingsboard', "status": 'online', "lastActive": '5分钟前'},
    {"id": 'camera_001', "name": '门口摄像头', "type": 'camera', "platform": 'thingsboard', "status": 'online', "lastActive": '1分钟前'},
    {"id": 'router_001', "name": '客厅路由器', "type": 'router', "platform": 'edgex', "status": 'online', "lastActive": '3分钟前'},
    {"id": 'sensor_001', "name": '温湿度传感器', "type": 'sensor', "platform": 'edgex', "status": 'offline', "lastActive": '1小时前'}
]

# 创建CSS文件
css_file_path = os.path.join(static_dir, 'css', 'dashboard.css')
if not os.path.exists(css_file_path):
    with open(css_file_path, 'w', encoding='utf-8') as f:
        f.write("""/* 基本样式 */
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background-color: #f8f9fa;
}

/* 卡片样式 */
.card {
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  border: none;
  margin-bottom: 20px;
}

.card-header {
  background-color: #fff;
  border-bottom: 1px solid rgba(0,0,0,.125);
}

/* 网格和列表视图切换 */
.grid-view .device-card {
  height: 100%;
}

.list-view .device-card {
  margin-bottom: 10px;
}

.list-view {
  flex-direction: column;
}

/* 设备状态指示器 */
.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 5px;
}

.status-online {
  background-color: #28a745;
}

.status-offline {
  background-color: #6c757d;
}

.status-warning {
  background-color: #ffc107;
}

/* 平台徽章 */
.platform-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  margin-right: 5px;
}

.tb-badge {
  background-color: #1976D2; 
  color: white;
}

.edgex-badge {
  background-color: #6610f2; 
  color: white;
}""")
    logger.info(f"创建了CSS文件: {css_file_path}")

# 身份验证装饰器 - 修复了重复端点的问题
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
        return render_template('dashboard.html', 
                             current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                             devices=devices)
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
        return render_template('devices.html', 
                             current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                             devices=devices)
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
        return render_template('thingsboard.html', 
                             current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                             config=thingsboard_config,
                             devices=[d for d in devices if d['platform'] == 'thingsboard'])
    except Exception as e:
        logger.error(f"ThingsBoard集成页面渲染错误: {str(e)}")
        logger.error(traceback.format_exc())
        return redirect(url_for('error_page', error=str(e)))

@app.route('/security')
@login_required
def security_monitoring():
    """安全监控页面"""
    try:
        logger.info("访问安全监控页面")
        return render_template('security.html', 
                             current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                             devices=devices)
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

@app.route('/api/devices', methods=['GET'])
@login_required
def api_get_devices():
    """API: 获取所有设备"""
    try:
        return jsonify({"success": True, "data": devices})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/devices', methods=['POST'])
@login_required
def api_add_device():
    """API: 添加设备"""
    try:
        data = request.json
        new_device = {
            "id": f"{data['type']}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "name": data['name'],
            "type": data['type'],
            "platform": data.get('platform', 'simulator'),
            "status": 'online',
            "lastActive": '刚刚'
        }
        devices.append(new_device)
        logger.info(f"添加了新设备: {new_device['id']}")
        return jsonify({"success": True, "data": new_device})
    except Exception as e:
        logger.error(f"添加设备失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/thingsboard/config', methods=['GET'])
@login_required
def api_get_tb_config():
    """API: 获取ThingsBoard配置"""
    try:
        # 返回配置时隐藏密码
        config_copy = dict(thingsboard_config)
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
        thingsboard_config.update({
            "host": data.get('host', thingsboard_config['host']),
            "port": data.get('port', thingsboard_config['port']),
            "mqtt_port": data.get('mqtt_port', thingsboard_config['mqtt_port'])
        })
        
        # 仅当提供了新密码时更新
        if 'auth' in data:
            thingsboard_config['auth'].update({
                "username": data['auth'].get('username', thingsboard_config['auth']['username'])
            })
            if data['auth'].get('password') and data['auth']['password'] != '******':
                thingsboard_config['auth']['password'] = data['auth']['password']
        
        # 更新设置
        if 'settings' in data:
            thingsboard_config['settings'].update(data['settings'])
        
        logger.info("更新了ThingsBoard配置")
        
        # 返回更新后的配置，但隐藏密码
        config_copy = dict(thingsboard_config)
        if 'auth' in config_copy and 'password' in config_copy['auth']:
            config_copy['auth']['password'] = '******'
        return jsonify({"success": True, "data": config_copy})
    except Exception as e:
        logger.error(f"更新ThingsBoard配置失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/attack')
@login_required
def attack_module():
    """攻击模块页面"""
    try:
        logger.info("访问攻击模块页面")
        return render_template('attack.html', 
                             current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        logger.error(f"攻击模块页面渲染错误: {str(e)}")
        logger.error(traceback.format_exc())
        return redirect(url_for('error_page', error=str(e)))


# 创建攻击引擎实例
attack_engine = AttackEngine()

# 添加以下路由
@app.route('/api/attack')
@login_required
def attack_api():
    """攻击模块API页面"""
    try:
        logger.info("访问攻击模块API页面")
        return render_template('attack.html', 
                             current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        logger.error(f"攻击模块API页面渲染错误: {str(e)}")
        logger.error(traceback.format_exc())
        return redirect(url_for('error_page', error=str(e)))

@app.route('/analytics')
@login_required
def analytics():
    """数据分析页面"""
    try:
        logger.info("访问数据分析页面")
        
        # 获取统计数据
        devices_count = len(devices)
        online_devices = len([d for d in devices if d['status'] == 'online'])
        
        # 从攻击引擎获取攻击和警报数据
        attack_history = attack_engine.get_attack_history(limit=100)
        attack_count = len(attack_history)
        alert_count = len([a for a in attack_history if a.get('severity', '') == 'high'])
        
        return render_template('analysis.html',
                             current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                             devices_count=devices_count,
                             online_devices=online_devices,
                             attack_count=attack_count,
                             alert_count=alert_count)
    except Exception as e:
        logger.error(f"数据分析页面渲染错误: {str(e)}")
        logger.error(traceback.format_exc())
        return redirect(url_for('error_page', error=str(e)))

@app.route('/api/analysis/data', methods=['GET'])
@login_required
def get_analysis_data():
    """获取分析数据API"""
    try:
        data_type = request.args.get('type', 'device_status')
        time_range = request.args.get('range', '24h')
        
        if data_type == 'device_status':
            # 返回设备状态数据
            return jsonify({
                'success': True,
                'data': {
                    'online': len([d for d in devices if d['status'] == 'online']),
                    'offline': len([d for d in devices if d['status'] == 'offline'])
                }
            })
        elif data_type == 'security_events':
            # 返回安全事件数据
            events = attack_engine.get_attack_history(limit=100)
            return jsonify({
                'success': True,
                'data': {
                    'attacks': len(events),
                    'alerts': len([e for e in events if e.get('severity') == 'high'])
                }
            })
        else:
            return jsonify({'success': False, 'error': '不支持的数据类型'}), 400
            
    except Exception as e:
        logger.error(f"获取分析数据失败: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 攻击模块API路由
@app.route('/api/attacks', methods=['GET'])
@login_required
def api_get_attacks():
    """API: 获取所有活动攻击"""
    try:
        return jsonify({"success": True, "data": attack_engine.get_active_attacks()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/attacks/history', methods=['GET'])
@login_required
def api_get_attack_history():
    """API: 获取攻击历史"""
    try:
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        return jsonify({"success": True, "data": attack_engine.get_attack_history(limit, offset)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/attacks/<attack_id>', methods=['GET'])
@login_required
def api_get_attack_details(attack_id):
    """API: 获取攻击详情"""
    try:
        attack = attack_engine.get_attack_details(attack_id)
        if not attack:
            return jsonify({"success": False, "error": f"未找到攻击: {attack_id}"}), 404
        return jsonify({"success": True, "data": attack})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/attacks', methods=['POST'])
@login_required
def api_launch_attack():
    """API: 启动攻击"""
    try:
        data = request.json
        attack_type = data.get('type')
        target = data.get('target')
        params = data.get('params', {})
        duration = data.get('duration', 30)
        analysis = data.get('analysis', True)
        
        if not attack_type or not target:
            return jsonify({"success": False, "error": "缺少必要参数"}), 400
        
        result = attack_engine.launch_attack(attack_type, target, params, duration, analysis)
        return jsonify(result)
    except Exception as e:
        logger.error(f"启动攻击失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/attacks/<attack_id>', methods=['DELETE'])
@login_required
def api_stop_attack(attack_id):
    """API: 停止攻击"""
    try:
        result = attack_engine.stop_attack(attack_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/debug')
def debug():
    """调试页面"""
    try:
        logger.info("访问调试页面")
        
        # 收集系统信息
        import platform
        
        # 检查依赖模块
        dependencies = {}
        for module_name in ['flask', 'werkzeug', 'jinja2', 'matplotlib', 'pandas']:
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
                <pre>""" + json.dumps(thingsboard_config, indent=2).replace(thingsboard_config['auth']['password'], '******') + """</pre>
            </div>
            
            <div class="section">
                <h2>模拟设备</h2>
                <pre>""" + json.dumps(devices, indent=2) + """</pre>
            </div>
            
            <div class="section">
                <h2>链接</h2>
                <ul>
                    <li><a href="/">首页</a></li>
                    <li><a href="/devices">设备管理</a></li>
                    <li><a href="/thingsboard">ThingsBoard集成</a></li>
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

def init_templates():
    """初始化应用所需的HTML模板"""
    # 确保模板目录存在
    os.makedirs(templates_dir, exist_ok=True)
    
    # 登录页模板
    login_template_path = os.path.join(templates_dir, 'login.html')
    if not os.path.exists(login_template_path):
        with open(login_template_path, 'w', encoding='utf-8') as f:
            f.write("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>登录 - 小米AIoT边缘安全防护研究平台</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@5.15.4/css/all.css">
    <style>
        body {
            background-color: #f8f9fa;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-container {
            max-width: 450px;
            width: 100%;
            padding: 15px;
        }
        .card {
            border: none;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        .card-header {
            border-radius: 10px 10px 0 0 !important;
            background: linear-gradient(135deg, #4e73df 0%, #36b9cc 100%);
            padding: 25px 20px;
            text-align: center;
            border: none;
        }
        .platform-logo {
            max-width: 80px;
            margin-bottom: 15px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #4e73df 0%, #36b9cc 100%);
            border: none;
            padding: 10px;
        }
        .btn-primary:hover {
            background: linear-gradient(135deg, #3e63cf 0%, #26a9bc 100%);
        }
        .card-body {
            padding: 30px;
        }
        .form-group label {
            font-weight: 500;
            font-size: 14px;
        }
        .form-control {
            padding: 12px;
            height: auto;
        }
        .footer-text {
            margin-top: 20px;
            text-align: center;
            font-size: 12px;
            color: #6c757d;
        }
        .platform-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            margin: 0 3px;
        }
        .tb-badge { background-color: #1976D2; color: white; }
        .edgex-badge { background-color: #6610f2; color: white; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="card">
            <div class="card-header text-white">
                <img src="https://i.imgur.com/IyvGWDM.png" alt="Platform Logo" class="platform-logo">
                <h4 class="mb-0">小米AIoT边缘安全防护研究平台</h4>
                <p class="mb-0">边缘设备安全仿真与防护系统</p>
            </div>
            <div class="card-body">
                {% if error %}
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle"></i> {{ error }}
                </div>
                {% endif %}
                
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                        <div class="alert alert-{{ category }}">
                            <i class="fas fa-info-circle"></i> {{ message }}
                        </div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
                
                <form method="POST">
                    <div class="form-group">
                        <label for="username">
                            <i class="fas fa-user"></i> 用户名
                        </label>
                        <input type="text" class="form-control" id="username" name="username" placeholder="输入您的用户名" required autofocus>
                    </div>
                    <div class="form-group">
                        <label for="password">
                            <i class="fas fa-lock"></i> 密码
                        </label>
                        <input type="password" class="form-control" id="password" name="password" placeholder="输入您的密码" required>
                    </div>
                    <div class="form-group form-check">
                        <input type="checkbox" class="form-check-input" id="remember" name="remember">
                        <label class="form-check-label" for="remember">记住我</label>
                    </div>
                    <button type="submit" class="btn btn-primary btn-block">
                        <i class="fas fa-sign-in-alt"></i> 登录
                    </button>
                </form>
                
                <div class="mt-4">
                    <h6 class="text-center">集成平台</h6>
                    <div class="text-center">
                        <span class="platform-badge tb-badge">
                            <i class="fas fa-cloud"></i> ThingsBoard Edge
                        </span>
                        <span class="platform-badge edgex-badge">
                            <i class="fas fa-server"></i> EdgeX Foundry
                        </span>
                    </div>
                </div>
            </div>
        </div>
        <div class="footer-text">
            <p>小米AIoT边缘安全防护研究平台 &copy; 2025</p>
            <p>当前时间: <span id="current-time">{{ current_time }}</span></p>
            <p>推荐使用Chrome、Firefox或Edge浏览器访问</p>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/jquery@3.5.1/dist/jquery.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // 更新时间显示
        function updateTime() {
            const now = new Date();
            const year = now.getFullYear();
            const month = String(now.getMonth() + 1).padStart(2, '0');
            const day = String(now.getDate()).padStart(2, '0');
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');
            
            const formattedTime = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
            document.getElementById('current-time').textContent = formattedTime;
        }
        
        // 每秒更新一次时间
        setInterval(updateTime, 1000);
        updateTime();
    </script>
</body>
</html>""")
        logger.info(f"创建了登录页面模板: {login_template_path}")
    
    # 404错误页面
    not_found_template_path = os.path.join(templates_dir, '404.html')
    if not os.path.exists(not_found_template_path):
        with open(not_found_template_path, 'w', encoding='utf-8') as f:
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
        logger.info(f"创建了404错误模板: {not_found_template_path}")
    
    # 500错误页面
    error_template_path = os.path.join(templates_dir, '500.html')
    if not os.path.exists(error_template_path):
        with open(error_template_path, 'w', encoding='utf-8') as f:
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
        logger.info(f"创建了500错误模板: {error_template_path}")

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
        
        print("\n启动服务器，访问 http://localhost:5000 查看应用...")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.critical(f"启动失败: {str(e)}")
        logger.critical(traceback.format_exc())
        print(f"\n严重错误: {str(e)}")
        print("请查看日志获取更多信息。")