#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
增强型Flask应用诊断工具
- 修复了花括号转义问题
- 添加了更多诊断功能
- 改进了错误处理
"""

import os
import sys
import traceback
import inspect
import platform
import datetime
import subprocess
from flask import Flask, jsonify, send_from_directory, request

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True

# 主页路由 - 修复了花括号转义问题
@app.route('/')
def index():
    # CSS样式作为单独变量，避免与格式化混淆
    css_style = """
        body { font-family: sans-serif; margin: 20px; }
        pre { background: #f5f5f5; padding: 10px; border-radius: 5px; }
        .success { color: green; font-weight: bold; }
        .warning { color: orange; font-weight: bold; }
        .error { color: red; font-weight: bold; }
        .info { color: blue; font-weight: bold; }
        .card { border: 1px solid #ddd; padding: 15px; margin-bottom: 20px; border-radius: 5px; }
        .hidden { display: none; }
        button { padding: 5px 10px; margin: 5px; cursor: pointer; }
    """
    
    # 系统信息
    current_dir = os.getcwd()
    python_version = sys.version
    platform_info = platform.platform()
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 路径信息
    sys_path = '<br>'.join(sys.path)
    
    # 目录结构检查
    dir_structure = check_directory_structure()
    
    html_content = f"""
    <html>
        <head>
            <title>增强型Flask诊断工具</title>
            <style>
                {css_style}
            </style>
            <script>
                function toggleSection(id) {{
                    var section = document.getElementById(id);
                    if (section.style.display === 'none') {{
                        section.style.display = 'block';
                    }} else {{
                        section.style.display = 'none';
                    }}
                }}
            </script>
        </head>
        <body>
            <h1>增强型Flask应用诊断</h1>
            
            <div class="card">
                <h2>环境信息 <button onclick="toggleSection('env-info')">显示/隐藏</button></h2>
                <div id="env-info">
                    <p><strong>当前时间:</strong> {current_time}</p>
                    <p><strong>当前工作目录:</strong> <code>{current_dir}</code></p>
                    <p><strong>Python版本:</strong> <code>{python_version}</code></p>
                    <p><strong>操作系统:</strong> <code>{platform_info}</code></p>
                    <p><strong>Python路径变量:</strong></p>
                    <pre>{sys_path}</pre>
                </div>
            </div>
            
            <div class="card">
                <h2>目录结构检查 <button onclick="toggleSection('dir-structure')">显示/隐藏</button></h2>
                <div id="dir-structure">
                    <pre>{dir_structure}</pre>
                </div>
            </div>
            
            <div class="card">
                <h2>依赖检查 <button onclick="toggleSection('dependencies')">显示/隐藏</button></h2>
                <div id="dependencies">
                    <p>正在检查关键依赖...</p>
                    <ul>
                        <li>Flask: <span class="success">已安装</span> - {check_dependency('flask')}</li>
                        <li>Flask-CORS: <span class="{get_class_for_dependency('flask-cors')}">
                            {check_dependency_status('flask-cors')}</span> - {check_dependency('flask-cors')}</li>
                        <li>Requests: <span class="{get_class_for_dependency('requests')}">
                            {check_dependency_status('requests')}</span> - {check_dependency('requests')}</li>
                    </ul>
                </div>
            </div>
            
            <div class="card">
                <h2>诊断工具 <button onclick="toggleSection('diagnostic-tools')">显示/隐藏</button></h2>
                <div id="diagnostic-tools">
                    <h3>测试路由</h3>
                    <ul>
                        <li><a href="/test/plain-text">测试纯文本响应</a></li>
                        <li><a href="/test/json">测试JSON响应</a></li>
                        <li><a href="/test/html">测试HTML响应</a></li>
                        <li><a href="/test/static-file">测试静态文件响应</a></li>
                    </ul>
                    
                    <h3>配置检查</h3>
                    <ul>
                        <li><a href="/check/config">检查配置文件</a></li>
                        <li><a href="/check/template-dir">检查模板目录</a></li>
                        <li><a href="/check/static-dir">检查静态文件目录</a></li>
                    </ul>
                    
                    <h3>修复工具</h3>
                    <ul>
                        <li><a href="/fix/create-directories">创建必要目录</a></li>
                        <li><a href="/fix/create-templates">创建基本模板</a></li>
                        <li><a href="/fix/create-config">创建配置文件</a></li>
                    </ul>
                </div>
            </div>
            
            <div class="card">
                <h2>下一步</h2>
                <ol>
                    <li>运行上面的诊断工具检查系统状态</li>
                    <li>使用修复工具解决发现的问题</li>
                    <li>尝试运行简化版应用: <code>python xiaomi-aiot-edge-security/src/dashboard/simple_app.py</code></li>
                </ol>
            </div>
            
            <footer style="margin-top: 50px; text-align: center; color: #888;">
                <p>增强型Flask应用诊断工具 | 当前版本: 1.0.0 | 运行于: {current_time}</p>
            </footer>
        </body>
    </html>
    """
    
    return html_content

def check_directory_structure():
    """检查关键目录和文件是否存在"""
    result = []
    
    # 检查项目根目录
    project_root = 'xiaomi-aiot-edge-security'
    if os.path.exists(project_root):
        result.append(f"✅ 项目根目录存在: {project_root}")
        result.append(f"   内容: {', '.join(os.listdir(project_root))}")
    else:
        result.append(f"❌ 项目根目录不存在: {project_root}")
    
    # 关键目录列表
    key_directories = [
        ('src', f'{project_root}/src'),
        ('dashboard', f'{project_root}/src/dashboard'),
        ('templates', f'{project_root}/src/dashboard/templates'),
        ('static', f'{project_root}/src/dashboard/static'),
        ('config', f'{project_root}/config'),
        ('data', f'{project_root}/data'),
    ]
    
    # 检查每个目录
    for name, path in key_directories:
        if os.path.exists(path):
            result.append(f"✅ {name} 目录存在: {path}")
            try:
                contents = os.listdir(path)
                if contents:
                    result.append(f"   内容: {', '.join(contents)}")
                else:
                    result.append(f"   目录为空")
            except Exception as e:
                result.append(f"   无法列出内容: {str(e)}")
        else:
            result.append(f"❌ {name} 目录不存在: {path}")
    
    # 检查关键文件
    key_files = [
        ('配置文件', f'{project_root}/config/dashboard.json'),
        ('登录模板', f'{project_root}/src/dashboard/templates/login.html'),
        ('仪表盘模板', f'{project_root}/src/dashboard/templates/dashboard.html'),
        ('CSS样式', f'{project_root}/src/dashboard/static/css/dashboard.css'),
    ]
    
    # 检查每个文件
    for name, path in key_files:
        if os.path.exists(path):
            size = os.path.getsize(path)
            result.append(f"✅ {name}存在: {path} (大小: {size} 字节)")
        else:
            result.append(f"❌ {name}不存在: {path}")
    
    return '\n'.join(result)

def check_dependency(package):
    """检查依赖包版本"""
    try:
        module = __import__(package.replace('-', '_'))
        if hasattr(module, '__version__'):
            return module.__version__
        elif hasattr(module, 'version'):
            return module.version
        else:
            return "已安装 (版本未知)"
    except ImportError:
        return "未安装"
    except Exception as e:
        return f"检查失败 ({str(e)})"

def check_dependency_status(package):
    """检查依赖包状态"""
    try:
        __import__(package.replace('-', '_'))
        return "已安装"
    except ImportError:
        return "未安装"
    except Exception:
        return "检查失败"

def get_class_for_dependency(package):
    """根据依赖包状态返回CSS类"""
    try:
        __import__(package.replace('-', '_'))
        return "success"
    except ImportError:
        return "error"
    except Exception:
        return "warning"

# 测试路由
@app.route('/test/plain-text')
def test_plain_text():
    return "纯文本响应测试成功！"

@app.route('/test/json')
def test_json():
    return jsonify({
        'status': 'success',
        'message': 'JSON响应测试成功',
        'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'environment': {
            'python_version': sys.version,
            'platform': platform.platform(),
            'working_directory': os.getcwd()
        }
    })

@app.route('/test/html')
def test_html():
    html = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>HTML响应测试</title>
            <style>
                body { font-family: sans-serif; margin: 20px; text-align: center; }
                .success { color: green; font-weight: bold; }
            </style>
        </head>
        <body>
            <h1>HTML响应测试</h1>
            <p class="success">HTML响应测试成功！</p>
            <p><a href="/">返回诊断页面</a></p>
        </body>
    </html>
    """
    return html

@app.route('/test/static-file')
def test_static_file():
    # 创建一个临时静态文件用于测试
    static_dir = 'static'
    os.makedirs(static_dir, exist_ok=True)
    
    test_file = os.path.join(static_dir, 'test.txt')
    with open(test_file, 'w') as f:
        f.write("这是一个测试静态文件，生成于 " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    return send_from_directory(os.getcwd(), test_file)

# 检查路由
@app.route('/check/config')
def check_config():
    config_path = 'xiaomi-aiot-edge-security/config/dashboard.json'
    result = {'status': 'unknown', 'message': '', 'content': None}
    
    if not os.path.exists(config_path):
        result['status'] = 'error'
        result['message'] = f'配置文件不存在: {config_path}'
    else:
        try:
            import json
            with open(config_path, 'r') as f:
                content = json.load(f)
                result['status'] = 'success'
                result['message'] = '配置文件格式正确'
                result['content'] = content
        except json.JSONDecodeError as e:
            result['status'] = 'error'
            result['message'] = f'配置文件格式错误: {str(e)}'
        except Exception as e:
            result['status'] = 'error'
            result['message'] = f'读取配置文件时出错: {str(e)}'
    
    return jsonify(result)

@app.route('/check/template-dir')
def check_template_dir():
    template_dir = 'xiaomi-aiot-edge-security/src/dashboard/templates'
    result = {'status': 'unknown', 'message': '', 'files': []}
    
    if not os.path.exists(template_dir):
        result['status'] = 'error'
        result['message'] = f'模板目录不存在: {template_dir}'
    else:
        try:
            files = os.listdir(template_dir)
            result['status'] = 'success'
            result['message'] = f'模板目录存在，包含 {len(files)} 个文件'
            
            for file in files:
                file_path = os.path.join(template_dir, file)
                file_info = {
                    'name': file,
                    'size': os.path.getsize(file_path),
                    'modified': datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
                }
                result['files'].append(file_info)
        except Exception as e:
            result['status'] = 'error'
            result['message'] = f'检查模板目录时出错: {str(e)}'
    
    return jsonify(result)

@app.route('/check/static-dir')
def check_static_dir():
    static_dir = 'xiaomi-aiot-edge-security/src/dashboard/static'
    result = {'status': 'unknown', 'message': '', 'directories': []}
    
    if not os.path.exists(static_dir):
        result['status'] = 'error'
        result['message'] = f'静态文件目录不存在: {static_dir}'
    else:
        try:
            directories = []
            for item in os.listdir(static_dir):
                item_path = os.path.join(static_dir, item)
                if os.path.isdir(item_path):
                    dir_info = {
                        'name': item,
                        'files': os.listdir(item_path) if os.path.exists(item_path) else []
                    }
                    directories.append(dir_info)
            
            result['status'] = 'success'
            result['message'] = f'静态文件目录存在，包含 {len(directories)} 个子目录'
            result['directories'] = directories
        except Exception as e:
            result['status'] = 'error'
            result['message'] = f'检查静态文件目录时出错: {str(e)}'
    
    return jsonify(result)

# 修复路由
@app.route('/fix/create-directories')
def fix_create_directories():
    directories = [
        'xiaomi-aiot-edge-security/src/dashboard/templates',
        'xiaomi-aiot-edge-security/src/dashboard/static/css',
        'xiaomi-aiot-edge-security/src/dashboard/static/js',
        'xiaomi-aiot-edge-security/config',
        'xiaomi-aiot-edge-security/data/attack_logs',
        'xiaomi-aiot-edge-security/data/packet_capture',
    ]
    
    results = []
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            results.append(f'✅ 已创建目录: {directory}')
        except Exception as e:
            results.append(f'❌ 创建目录失败: {directory} - {str(e)}')
    
    return jsonify({
        'status': 'success',
        'message': f'已处理 {len(directories)} 个目录',
        'results': results
    })

@app.route('/fix/create-templates')
def fix_create_templates():
    # 登录页面模板
    login_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>登录 - 小米AIoT边缘安全防护研究平台</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css">
</head>
<body class="bg-light">
    <div class="container">
        <div class="row justify-content-center mt-5">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header bg-primary text-white text-center">
                        <h4>小米AIoT边缘安全防护研究平台</h4>
                    </div>
                    <div class="card-body">
                        {% if error %}
                        <div class="alert alert-danger">{{ error }}</div>
                        {% endif %}
                        
                        {% with messages = get_flashed_messages(with_categories=true) %}
                            {% if messages %}
                                {% for category, message in messages %}
                                <div class="alert alert-{{ category }}">{{ message }}</div>
                                {% endfor %}
                            {% endif %}
                        {% endwith %}
                        
                        <form method="POST">
                            <div class="form-group">
                                <label for="username">用户名</label>
                                <input type="text" class="form-control" id="username" name="username" required>
                            </div>
                            <div class="form-group">
                                <label for="password">密码</label>
                                <input type="password" class="form-control" id="password" name="password" required>
                            </div>
                            <button type="submit" class="btn btn-primary btn-block">登录</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/jquery@3.5.1/dist/jquery.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""
    
    # 仪表盘页面模板
    dashboard_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>仪表盘 - 小米AIoT边缘安全防护研究平台</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/dashboard.css') }}">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <a class="navbar-brand" href="/">小米AIoT边缘安全防护研究平台</a>
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav">
                <li class="nav-item active">
                    <a class="nav-link" href="/">首页</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="/devices">设备管理</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="/security">安全监控</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="/network">网络分析</a>
                </li>
            </ul>
            <ul class="navbar-nav ml-auto">
                <li class="nav-item">
                    <a class="nav-link" href="/logout">退出</a>
                </li>
            </ul>
        </div>
    </nav>

    <div class="container-fluid mt-4">
        <div class="row">
            <div class="col-12">
                <h2>系统概况</h2>
                <p>欢迎使用小米AIoT边缘安全防护研究平台</p>
                <div class="alert alert-success">
                    系统运行正常！
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h5 class="card-title mb-0">设备状态</h5>
                    </div>
                    <div class="card-body">
                        <p>模拟数据: 设备总数 4，在线设备 3</p>
                        <div class="progress mb-3">
                            <div class="progress-bar bg-success" role="progressbar" style="width: 75%">
                                75% 在线
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h5 class="card-title mb-0">安全事件</h5>
                    </div>
                    <div class="card-body">
                        <p>模拟数据: 今日安全事件 2 起</p>
                        <ul>
                            <li>DDoS攻击 - 高危</li>
                            <li>中间人攻击尝试 - 中危</li>
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">
                        <h5 class="card-title mb-0">系统资源</h5>
                    </div>
                    <div class="card-body">
                        <p>模拟数据: 系统资源使用情况</p>
                        <div>CPU: 35%</div>
                        <div class="progress mb-2">
                            <div class="progress-bar" role="progressbar" style="width: 35%"></div>
                        </div>
                        <div>内存: 48%</div>
                        <div class="progress">
                            <div class="progress-bar bg-info" role="progressbar" style="width: 48%"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/jquery@3.5.1/dist/jquery.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""
    
    # CSS文件内容
    css_content = """/* 基本样式 */
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
}"""

    # 路径
    template_dir = 'xiaomi-aiot-edge-security/src/dashboard/templates'
    css_dir = 'xiaomi-aiot-edge-security/src/dashboard/static/css'
    
    # 确保目录存在
    os.makedirs(template_dir, exist_ok=True)
    os.makedirs(css_dir, exist_ok=True)
    
    results = []
    
    # 写入模板文件
    try:
        with open(os.path.join(template_dir, 'login.html'), 'w', encoding='utf-8') as f:
            f.write(login_template)
        results.append('✅ 已创建登录页面模板')
    except Exception as e:
        results.append(f'❌ 创建登录页面模板失败: {str(e)}')
    
    try:
        with open(os.path.join(template_dir, 'dashboard.html'), 'w', encoding='utf-8') as f:
            f.write(dashboard_template)
        results.append('✅ 已创建仪表盘页面模板')
    except Exception as e:
        results.append(f'❌ 创建仪表盘页面模板失败: {str(e)}')
    
    # 写入CSS文件
    try:
        with open(os.path.join(css_dir, 'dashboard.css'), 'w', encoding='utf-8') as f:
            f.write(css_content)
        results.append('✅ 已创建CSS样式文件')
    except Exception as e:
        results.append(f'❌ 创建CSS样式文件失败: {str(e)}')
    
    return jsonify({
        'status': 'success',
        'message': '模板文件处理完成',
        'results': results
    })

@app.route('/fix/create-config')
def fix_create_config():
    import json
    
    config_dir = 'xiaomi-aiot-edge-security/config'
    os.makedirs(config_dir, exist_ok=True)
    
    config = {
        "web_port": 5000,
        "log_dir": "data/attack_logs",
        "capture_dir": "data/packet_capture",
        "attack_log_retention_days": 30,
        "packet_capture_limit": 100,
        "refresh_interval": 5,
        "enable_packet_capture": True,
        "interfaces": ["eth0"],
        "secret_key": os.urandom(24).hex(),
        "debug": True
    }
    
    try:
        with open(os.path.join(config_dir, 'dashboard.json'), 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        return jsonify({
            'status': 'success',
            'message': '配置文件已创建',
            'config': config
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'创建配置文件失败: {str(e)}'
        })

@app.errorhandler(Exception)
def handle_exception(e):
    """全局异常处理"""
    print(f"捕获到异常: {e}")
    print(traceback.format_exc())

    # 提取异常堆栈
    stack_trace = traceback.format_exc()
    
    # 提供友好的HTML错误页面
    html_response = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>应用错误</title>
            <style>
                body {{ font-family: sans-serif; margin: 20px; }}
                pre {{ background: #f5f5f5; padding: 10px; border-radius: 5px; }}
                .error {{ color: red; }}
                .code {{ font-family: monospace; }}
            </style>
        </head>
        <body>
            <h1 class="error">应用发生错误</h1>
            <p>类型: <code>{type(e).__name__}</code></p>
            <p>描述: <code>{str(e)}</code></p>
            
            <h3>错误堆栈:</h3>
            <pre>{stack_trace}</pre>
            
            <h3>可能的解决方案:</h3>
            <ul>
                <li>检查代码中的字符串格式化方式，避免CSS花括号与格式化占位符冲突</li>
                <li>使用<a href="/fix/create-directories">修复工具</a>创建必要的目录</li>
                <li>使用<a href="/fix/create-templates">创建模板</a>生成基本模板文件</li>
            </ul>
            
            <p><a href="/">返回诊断页面</a></p>
        </body>
    </html>
    """
    return html_response, 500

# 创建一个简化版应用
@app.route('/create-simple-app')
def create_simple_app():
    app_content = """#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for, session, flash
import os

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates')

# 确保目录存在
os.makedirs(os.path.join(os.path.dirname(__file__), 'static'), exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(__file__), 'templates'), exist_ok=True)

# 设置密钥
app.secret_key = os.urandom(24).hex()

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'admin' and password == 'admin':
            session['user'] = username
            return redirect(url_for('index'))
        else:
            error = '用户名或密码错误'
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('您已成功退出', 'info')
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# 简单错误处理
@app.errorhandler(404)
def page_not_found(e):
    return render_template('login.html', error='页面不存在'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('login.html', error=f'服务器内部错误: {str(e)}'), 500

if __name__ == '__main__':
    port = 5000
    print(f"启动简化版应用，访问地址: http://localhost:{port}")
    print("默认登录信息 - 用户名: admin, 密码: admin")
    app.run(host='0.0.0.0', port=port, debug=True)
"""
    
    app_path = 'xiaomi-aiot-edge-security/src/dashboard/simple_app.py'
    
    # 确保目录存在
    os.makedirs(os.path.dirname(app_path), exist_ok=True)
    
    try:
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(app_content)
        
        return jsonify({
            'status': 'success',
            'message': '简化版应用已创建',
            'path': app_path,
            'run_command': 'python xiaomi-aiot-edge-security/src/dashboard/simple_app.py'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'创建应用失败: {str(e)}'
        })

if __name__ == "__main__":
    print("\n=== 增强型Flask应用诊断工具 ===")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"Python版本: {sys.version}")
    print(f"平台信息: {platform.platform()}")
    print("\n启动诊断服务器...")
    print("访问地址: http://localhost:5001")
    app.run(debug=True, port=5001)
    print("服务器已停止")