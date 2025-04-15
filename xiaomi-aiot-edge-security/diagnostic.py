#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
诊断工具 - 用于排除Flask应用的500错误
"""

import os
import sys
import logging
import traceback
from datetime import datetime

# 尝试导入Flask，并处理可能的导入错误
try:
    from flask import Flask, request, jsonify
    print("Flask导入成功！")
except ImportError as e:
    print(f"无法导入Flask: {e}")
    print("请运行: pip install flask")
    sys.exit(1)

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('diagnostic.log')
    ]
)

logger = logging.getLogger("diagnostic")
logger.info("诊断工具启动")

# 创建应用前记录路径信息
current_dir = os.path.dirname(os.path.abspath(__file__))
template_path = os.path.join(current_dir, 'templates')
static_path = os.path.join(current_dir, 'static')

logger.info(f"当前目录: {current_dir}")
logger.info(f"模板路径: {template_path}")
logger.info(f"静态文件路径: {static_path}")

# 确保这些目录存在
os.makedirs(template_path, exist_ok=True)
os.makedirs(static_path, exist_ok=True)

# 创建Flask应用
app = Flask(__name__)

# 添加一系列诊断路由

@app.route('/')
def index():
    """主页 - 简单的欢迎页面"""
    try:
        logger.info("访问主页")
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>诊断工具</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                h1 { color: #4a86e8; }
                ul { list-style-type: none; padding: 0; }
                li { margin: 10px 0; }
                                a { color: #4a86e8; text-decoration: none; }
                a:hover { text-decoration: underline; }
                .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1>Flask 应用诊断工具</h1>
            
            <div class="section">
                <h2>诊断选项</h2>
                <ul>
                    <li><a href="/system-info">系统信息</a> - 查看系统环境详情</li>
                    <li><a href="/file-check">文件检查</a> - 检查关键文件和目录</li>
                    <li><a href="/force-error">触发错误</a> - 故意触发500错误进行测试</li>
                    <li><a href="/minimal">最小化页面</a> - 测试最简单的页面渲染</li>
                </ul>
            </div>
            
            <div class="section">
                <h2>仪表盘应用修复</h2>
                <ul>
                    <li><a href="/fix-standalone">修复独立应用</a> - 修复app_standalone.py</li>
                    <li><a href="/fix-visualization">修复可视化问题</a> - 修复visualization相关问题</li>
                </ul>
            </div>
            
            <p>当前时间: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        </body>
        </html>
        """
    except Exception as e:
        logger.error(f"首页渲染错误: {e}")
        logger.error(traceback.format_exc())
        return f"错误: {str(e)}", 500

@app.route('/system-info')
def system_info():
    """显示系统信息"""
    try:
        logger.info("访问系统信息页面")
        
        # 收集系统信息
        info = {
            "python_version": sys.version,
            "platform": sys.platform,
            "executable": sys.executable,
            "cwd": os.getcwd(),
            "file_location": __file__,
            "env_vars": {k: v for k, v in os.environ.items() if k.startswith(('PYTHON', 'PATH', 'FLASK'))}
        }
        
        # 检查模块版本
        try:
            import flask
            info["flask_version"] = flask.__version__
        except:
            info["flask_version"] = "无法获取"
            
        try:
            import matplotlib
            info["matplotlib_version"] = matplotlib.__version__
        except ImportError:
            info["matplotlib_version"] = "未安装"
            
        try:
            import pandas
            info["pandas_version"] = pandas.__version__
        except ImportError:
            info["pandas_version"] = "未安装"
        
        # 输出为HTML
        html_parts = [
            "<!DOCTYPE html><html><head><title>系统信息</title>",
            "<style>body{font-family:Arial,sans-serif; padding:20px;} ",
            "table{border-collapse:collapse; width:100%;} ",
            "th,td{padding:8px; text-align:left; border:1px solid #ddd;} ",
            "th{background-color:#f2f2f2;} tr:nth-child(even){background-color:#f9f9f9;}</style>",
            "</head><body><h1>系统信息</h1>"
        ]
        
        # Python信息
        html_parts.append("<h2>Python环境</h2>")
        html_parts.append("<table><tr><th>项目</th><th>值</th></tr>")
        html_parts.append(f"<tr><td>Python版本</td><td>{info['python_version']}</td></tr>")
        html_parts.append(f"<tr><td>平台</td><td>{info['platform']}</td></tr>")
        html_parts.append(f"<tr><td>可执行文件</td><td>{info['executable']}</td></tr>")
        html_parts.append(f"<tr><td>当前工作目录</td><td>{info['cwd']}</td></tr>")
        html_parts.append(f"<tr><td>脚本位置</td><td>{info['file_location']}</td></tr>")
        html_parts.append("</table>")
        
        # 模块版本
        html_parts.append("<h2>模块版本</h2>")
        html_parts.append("<table><tr><th>模块</th><th>版本</th></tr>")
        html_parts.append(f"<tr><td>Flask</td><td>{info['flask_version']}</td></tr>")
        html_parts.append(f"<tr><td>Matplotlib</td><td>{info['matplotlib_version']}</td></tr>")
        html_parts.append(f"<tr><td>Pandas</td><td>{info['pandas_version']}</td></tr>")
        html_parts.append("</table>")
        
        # 环境变量
        html_parts.append("<h2>环境变量</h2>")
        html_parts.append("<table><tr><th>变量</th><th>值</th></tr>")
        for k, v in info['env_vars'].items():
            html_parts.append(f"<tr><td>{k}</td><td>{v}</td></tr>")
        html_parts.append("</table>")
        
        html_parts.append("<p><a href='/'>返回首页</a></p>")
        html_parts.append("</body></html>")
        
        return "".join(html_parts)
    except Exception as e:
        logger.error(f"系统信息页面错误: {e}")
        logger.error(traceback.format_exc())
        return f"获取系统信息时出错: {str(e)}", 500

@app.route('/file-check')
def file_check():
    """检查文件和目录结构"""
    try:
        logger.info("访问文件检查页面")
        
        current_dir = os.getcwd()
        
        # 尝试定位关键目录和文件
        dashboard_dir = os.path.join(current_dir, 'xiaomi-aiot-edge-security', 'src', 'dashboard')
        template_dir = os.path.join(dashboard_dir, 'templates')
        static_dir = os.path.join(dashboard_dir, 'static')
        app_standalone_path = os.path.join(dashboard_dir, 'app_standalone.py')
        visualization_path = os.path.join(dashboard_dir, 'visualization.py')
        
        results = {
            "current_dir": current_dir,
            "dashboard_dir": {"path": dashboard_dir, "exists": os.path.exists(dashboard_dir)},
            "template_dir": {"path": template_dir, "exists": os.path.exists(template_dir)},
            "static_dir": {"path": static_dir, "exists": os.path.exists(static_dir)},
            "app_standalone_py": {"path": app_standalone_path, "exists": os.path.exists(app_standalone_path)},
            "visualization_py": {"path": visualization_path, "exists": os.path.exists(visualization_path)}
        }
        
        # 检查模板文件
        if results["template_dir"]["exists"]:
            template_files = os.listdir(template_dir)
            results["template_files"] = template_files
            results["has_500_html"] = "500.html" in template_files
        else:
            results["template_files"] = []
            results["has_500_html"] = False
        
        # 转换为HTML输出
        html_parts = [
            "<!DOCTYPE html><html><head><title>文件检查</title>",
            "<style>body{font-family:Arial,sans-serif;padding:20px}",
            ".success{color:green}.error{color:red}",
            "table{border-collapse:collapse;width:100%}",
            "th,td{padding:8px;text-align:left;border:1px solid #ddd}</style>",
            "</head><body><h1>文件和目录检查</h1>"
        ]
        
        # 主要目录状态
        html_parts.append("<h2>关键路径检查</h2>")
        html_parts.append("<table><tr><th>项目</th><th>路径</th><th>状态</th></tr>")
        
        # 当前目录
        html_parts.append(f"<tr><td>当前工作目录</td><td>{results['current_dir']}</td><td class='success'>存在</td></tr>")
        
        # 其他目录和文件
        for key in ["dashboard_dir", "template_dir", "static_dir", "app_standalone_py", "visualization_py"]:
            item = results[key]
            status_class = "success" if item["exists"] else "error"
            status_text = "存在" if item["exists"] else "不存在"
            html_parts.append(f"<tr><td>{key}</td><td>{item['path']}</td>")
            html_parts.append(f"<td class='{status_class}'>{status_text}</td></tr>")
        
        html_parts.append("</table>")
        
        # 模板文件检查
        html_parts.append("<h2>模板文件检查</h2>")
        if results["template_dir"]["exists"]:
            if results["template_files"]:
                html_parts.append("<p>找到以下模板文件:</p><ul>")
                for file in results["template_files"]:
                    html_parts.append(f"<li>{file}</li>")
                html_parts.append("</ul>")
                
                if results["has_500_html"]:
                    html_parts.append("<p class='success'>500.html 模板文件存在。</p>")
                else:
                    html_parts.append("<p class='error'>缺少 500.html 模板文件！</p>")
            else:
                html_parts.append("<p class='error'>模板目录存在但为空！</p>")
        else:
            html_parts.append("<p class='error'>模板目录不存在！</p>")
        
        # 返回链接
        html_parts.append("<p><a href='/'>返回首页</a></p>")
        html_parts.append("<p><a href='/fix-standalone'>修复独立应用</a></p>")
        html_parts.append("</body></html>")
        
        return "".join(html_parts)
    except Exception as e:
        logger.error(f"文件检查页面错误: {e}")
        logger.error(traceback.format_exc())
        return f"检查文件时出错: {str(e)}", 500

@app.route('/minimal')
def minimal():
    """最小化页面测试"""
    return "最小化页面测试成功！<br><a href='/'>返回首页</a>"

@app.route('/force-error')
def force_error():
    """故意触发错误"""
    # 制造一个除以零的错误
    logger.info("故意触发500错误")
    result = 1 / 0
    return "永远不会显示这条消息"

@app.route('/fix-standalone')
def fix_standalone():
    """修复app_standalone.py文件"""
    try:
        logger.info("访问修复独立应用页面")
        
        dashboard_dir = os.path.join(os.getcwd(), 'xiaomi-aiot-edge-security', 'src', 'dashboard')
        app_standalone_path = os.path.join(dashboard_dir, 'app_standalone.py')
        
        if not os.path.exists(dashboard_dir):
            return f"错误：目录不存在: {dashboard_dir}", 404
            
        # 检查文件是否存在
        file_exists = os.path.exists(app_standalone_path)
        
        # 准备修复后的代码
        fixed_code = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
独立运行的Dashboard应用
"""

import os
import sys
import logging
import traceback
from flask import Flask, render_template, request
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

# 确保目录路径
base_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')

# 创建必要的目录
os.makedirs(templates_dir, exist_ok=True)
os.makedirs(static_dir, exist_ok=True)
os.makedirs(os.path.join(static_dir, 'css'), exist_ok=True)
os.makedirs(os.path.join(static_dir, 'js'), exist_ok=True)

# 创建Flask应用
app = Flask(__name__, 
           template_folder=templates_dir,
           static_folder=static_dir)
app.config['DEBUG'] = True

# 创建一个简单的500错误模板，如果不存在
error_template_path = os.path.join(templates_dir, '500.html')
if not os.path.exists(error_template_path):
    with open(error_template_path, 'w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>服务器错误</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        h1 { color: #e53e3e; }
        .container { max-width: 800px; margin: 0 auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>500 - 服务器内部错误</h1>
        <p>抱歉，服务器遇到了内部错误，无法完成您的请求。</p>
        <p>错误信息: {{ error }}</p>
        <p>时间: {{ current_time }}</p>
        <p>用户: {{ current_user }}</p>
        <p><a href="/">返回首页</a></p>
    </div>
</body>
</html>""")
    logger.info(f"创建了500错误模板: {error_template_path}")

@app.route('/')
def index():
    """首页"""
    try:
        logger.info("访问首页")
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>小米AIoT边缘安全防护研究平台</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                h1 { color: #ff6700; }
            </style>
        </head>
        <body>
            <h1>小米AIoT边缘安全防护研究平台</h1>
            <p>系统运行正常！</p>
            <p>当前时间: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        </body>
        </html>
        """
    except Exception as e:
        logger.error(f"首页渲染错误: {str(e)}")
        logger.error(traceback.format_exc())
        return str(e), 500

@app.errorhandler(500)
def internal_error(error):
    """处理500错误"""
    logger.error(f'服务器错误: {error}')
    logger.error(traceback.format_exc())
    
    try:
        return render_template('500.html', 
                             current_user='Guest', 
                             current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                             error=str(error)), 500
    except Exception as e:
        logger.error(f"渲染错误模板失败: {str(e)}")
        return f"严重错误: {str(error)}", 500

if __name__ == "__main__":
    print("="*50)
    print(" 小米AIoT边缘安全防护研究平台 ".center(50))
    print("="*50)
    print(f"• 工作目录: {os.getcwd()}")
    print(f"• 应用目录: {base_dir}")
    print(f"• 模板目录: {templates_dir}")
    print(f"• 静态目录: {static_dir}")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"启动失败: {str(e)}")
        traceback.print_exc()
'''

        # 显示修复选项
        html_parts = [
            "<!DOCTYPE html><html><head><title>修复独立应用</title>",
            "<style>body{font-family:Arial,sans-serif;padding:20px}",
            "pre{background:#f5f5f5;padding:15px;overflow:auto;white-space:pre-wrap;border:1px solid #ddd}",
            ".btn{display:inline-block;padding:10px 20px;background:#4a86e8;color:#fff;",
            "text-decoration:none;border-radius:4px;margin:10px 0}",
            ".btn:hover{background:#3a76d8}.status{padding:10px;margin:10px 0;border-radius:4px}",
            ".success{background:#d4edda;color:#155724;border:1px solid #c3e6cb}",
            ".error{background:#f8d7da;color:#721c24;border:1px solid #f5c6cb}</style>",
            "</head><body><h1>修复 app_standalone.py</h1>"
        ]
        
        if file_exists:
            html_parts.append(f"<div class='status success'>找到文件: {app_standalone_path}</div>")
        else:
            html_parts.append(f"<div class='status error'>文件不存在: {app_standalone_path}</div>")
        
        html_parts.append("<h2>推荐的修复代码</h2>")
        html_parts.append(f"<pre>{fixed_code}</pre>")
        
        # 添加写入按钮
        html_parts.append("<form method='POST' action='/write-standalone'>")
        html_parts.append("<input type='hidden' name='content' value=\"" + fixed_code.replace('"', '&quot;') + "\">")
        html_parts.append("<button type='submit' class='btn'>写入修复代码到app_standalone.py</button>")
        html_parts.append("</form>")
        
        html_parts.append("<p><a href='/'>返回首页</a></p>")
        html_parts.append("</body></html>")
        
        return "".join(html_parts)
    except Exception as e:
        logger.error(f"修复独立应用页面错误: {e}")
        logger.error(traceback.format_exc())
        return f"显示修复选项时出错: {str(e)}", 500

@app.route('/write-standalone', methods=['POST'])
def write_standalone():
    """写入修复后的app_standalone.py文件"""
    try:
        logger.info("写入修复后的app_standalone.py")
        content = request.form.get('content')
        
        if not content:
            return "错误：没有提供内容", 400
        
        dashboard_dir = os.path.join(os.getcwd(), 'xiaomi-aiot-edge-security', 'src', 'dashboard')
        app_standalone_path = os.path.join(dashboard_dir, 'app_standalone.py')
        
        # 确保目录存在
        os.makedirs(os.path.dirname(app_standalone_path), exist_ok=True)
        
        # 备份原文件（如果存在）
        if os.path.exists(app_standalone_path):
            backup_path = f"{app_standalone_path}.bak.{int(datetime.now().timestamp())}"
            with open(app_standalone_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
                
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            logger.info(f"原文件已备份到: {backup_path}")
        
        # 写入新内容
        with open(app_standalone_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"成功写入修复后的代码到: {app_standalone_path}")
        
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>修复成功</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                .success { background: #d4edda; color: #155724; padding: 15px; border-radius: 4px; }
                .btn { display: inline-block; padding: 10px 20px; background: #4a86e8; color: #fff; 
                      text-decoration: none; border-radius: 4px; margin: 10px 0; }
            </style>
            <meta http-equiv="refresh" content="5;url=/">
        </head>
        <body>
            <h1>文件修复成功</h1>
            <div class="success">
                <p>成功写入修复后的代码到:</p>
                <pre>""" + app_standalone_path + """</pre>
                
                <p>您现在可以重新启动应用:</p>
                <pre>python """ + app_standalone_path + """</pre>
            </div>
            
            <p>5秒后自动返回首页...</p>
            <p><a href="/" class="btn">立即返回首页</a></p>
        </body>
        </html>
        """
    except Exception as e:
        logger.error(f"写入文件时出错: {e}")
        logger.error(traceback.format_exc())
        return f"写入文件时出错: {str(e)}", 500

@app.route('/fix-visualization')
def fix_visualization():
    """修复可视化相关问题"""
    try:
        logger.info("访问修复可视化页面")
        
        dashboard_dir = os.path.join(os.getcwd(), 'xiaomi-aiot-edge-security', 'src', 'dashboard')
        visualization_path = os.path.join(dashboard_dir, 'visualization.py')
        attack_visualizer_path = os.path.join(dashboard_dir, 'attack_visualizer.py')
        
        # 检查文件是否存在
        vis_exists = os.path.exists(visualization_path)
        attack_vis_exists = os.path.exists(attack_visualizer_path)
        
        # 准备修复的visualization.py头部
        vis_fixed_header = '''"""
可视化模块 - 负责展示效果评估和攻击分析结果
"""
import os
import time
import logging
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端，避免在无GUI环境下报错

import matplotlib.pyplot as plt
import pandas as pd
'''

        # 准备修复的attack_visualizer.py头部
        attack_vis_fixed_header = '''"""
攻击数据可视化模块 - 使用图表展示攻击类型、频率和影响
"""
import time
import logging
from typing import Dict, List, Optional, Any
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端，避免在无GUI环境下报错

import matplotlib.pyplot as plt
import pandas as pd
'''

        # 显示修复选项
        html_parts = [
            "<!DOCTYPE html><html><head><title>修复可视化模块</title>",
            "<style>body{font-family:Arial,sans-serif;padding:20px}",
            "pre{background:#f5f5f5;padding:15px;overflow:auto;white-space:pre-wrap;border:1px solid #ddd}",
            ".btn{display:inline-block;padding:10px 20px;background:#4a86e8;color:#fff;",
            "text-decoration:none;border-radius:4px;margin:10px 0}",
            ".btn:hover{background:#3a76d8}.status{padding:10px;margin:10px 0;border-radius:4px}",
            ".success{background:#d4edda;color:#155724;border:1px solid #c3e6cb}",
            ".error{background:#f8d7da;color:#721c24;border:1px solid #f5c6cb}</style>",
            "</head><body><h1>修复可视化模块</h1>"
        ]
        
        # 显示文件状态
        html_parts.append("<h2>文件状态</h2><ul>")
        if vis_exists:
            html_parts.append(f"<li class='status success'>visualization.py: 找到文件</li>")
        else:
            html_parts.append(f"<li class='status error'>visualization.py: 文件不存在</li>")
            
        if attack_vis_exists:
            html_parts.append(f"<li class='status success'>attack_visualizer.py: 找到文件</li>")
        else:
            html_parts.append(f"<li class='status error'>attack_visualizer.py: 文件不存在</li>")
        html_parts.append("</ul>")
        
        # 显示修复代码
        html_parts.append("<h2>visualization.py 修复代码</h2>")
        html_parts.append("<p>修改文件开头为:</p>")
        html_parts.append(f"<pre>{vis_fixed_header}</pre>")
        
        html_parts.append("<h2>attack_visualizer.py 修复代码</h2>")
        html_parts.append("<p>修改文件开头为:</p>")
        html_parts.append(f"<pre>{attack_vis_fixed_header}</pre>")
        
        # 添加修复按钮
        html_parts.append("<form method='POST' action='/write-visualization'>")
        html_parts.append("<input type='hidden' name='vis_header' value=\"" + vis_fixed_header.replace('"', '&quot;') + "\">")
        html_parts.append("<input type='hidden' name='attack_vis_header' value=\"" + attack_vis_fixed_header.replace('"', '&quot;') + "\">")
        html_parts.append("<button type='submit' class='btn'>修复可视化模块</button>")
        html_parts.append("</form>")
        
        html_parts.append("<p><a href='/'>返回首页</a></p>")
        html_parts.append("</body></html>")
        
        return "".join(html_parts)
    except Exception as e:
        logger.error(f"修复可视化页面错误: {e}")
        logger.error(traceback.format_exc())
        return f"显示修复选项时出错: {str(e)}", 500

@app.route('/write-visualization', methods=['POST'])
def write_visualization():
    """写入修复后的可视化模块代码"""
    try:
        logger.info("写入修复后的可视化模块代码")
        vis_header = request.form.get('vis_header')
        attack_vis_header = request.form.get('attack_vis_header')
        
        if not vis_header or not attack_vis_header:
            return "错误：没有提供修复代码", 400
        
        dashboard_dir = os.path.join(os.getcwd(), 'xiaomi-aiot-edge-security', 'src', 'dashboard')
        visualization_path = os.path.join(dashboard_dir, 'visualization.py')
        attack_visualizer_path = os.path.join(dashboard_dir, 'attack_visualizer.py')
        
        results = []
        
        # 修改 visualization.py
        if os.path.exists(visualization_path):
            # 备份原文件
            backup_path = f"{visualization_path}.bak.{int(datetime.now().timestamp())}"
            with open(visualization_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
                
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # 识别原始文件的头部和内容部分
            lines = original_content.split('\n')
            content_start = 0
            for i, line in enumerate(lines):
                if line.strip() and not line.startswith('#') and not line.startswith('"""') and not line.startswith("'''"):
                    if "import " not in line and "from " not in line:
                        content_start = i
                        break
            
            # 替换头部，保留内容
            if content_start > 0:
                with open(visualization_path, 'w', encoding='utf-8') as f:
                    f.write(vis_header)
                    f.write('\n\n')
                    f.write('\n'.join(lines[content_start:]))
                results.append(f"成功修复 visualization.py (备份于 {backup_path})")
            else:
                results.append("无法识别 visualization.py 的内容部分，未修改文件")
        else:
            results.append("visualization.py 不存在，无法修复")
        
        # 修改 attack_visualizer.py
        if os.path.exists(attack_visualizer_path):
            # 备份原文件
            backup_path = f"{attack_visualizer_path}.bak.{int(datetime.now().timestamp())}"
            with open(attack_visualizer_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
                
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # 识别原始文件的头部和内容部分
            lines = original_content.split('\n')
            content_start = 0
            for i, line in enumerate(lines):
                if line.strip() and not line.startswith('#') and not line.startswith('"""') and not line.startswith("'''"):
                    if "import " not in line and "from " not in line and "class " in line:
                        content_start = i
                        break
            
            # 替换头部，保留内容
            if content_start > 0:
                with open(attack_visualizer_path, 'w', encoding='utf-8') as f:
                    f.write(attack_vis_header)
                    f.write('\n\n')
                    f.write('\n'.join(lines[content_start:]))
                results.append(f"成功修复 attack_visualizer.py (备份于 {backup_path})")
            else:
                results.append("无法识别 attack_visualizer.py 的内容部分，未修改文件")
        else:
            results.append("attack_visualizer.py 不存在，无法修复")
            
        # 返回结果
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>修复完成</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                .result { background: #d4edda; color: #155724; padding: 15px; border-radius: 4px; margin-bottom: 10px; }
                .btn { display: inline-block; padding: 10px 20px; background: #4a86e8; color: #fff; 
                      text-decoration: none; border-radius: 4px; margin: 10px 0; }
            </style>
            <meta http-equiv="refresh" content="5;url=/">
        </head>
        <body>
            <h1>可视化模块修复结果</h1>
            
            <div class="result">
                <ul>
                    <li>""" + "</li><li>".join(results) + """</li>
                </ul>
                
                <p>您现在可以重新启动应用，可视化应该可以正常工作了。</p>
            </div>
            
            <p>5秒后自动返回首页...</p>
            <p><a href="/" class="btn">立即返回首页</a></p>
        </body>
        </html>
        """
    except Exception as e:
        logger.error(f"修复可视化模块时出错: {e}")
        logger.error(traceback.format_exc())
        return f"修复可视化模块时出错: {str(e)}", 500

# 全局错误处理
@app.errorhandler(404)
def page_not_found(e):
    logger.warning(f"404错误: {request.path}")
    return f"找不到页面: {request.path}", 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"500错误: {e}")
    logger.error(traceback.format_exc())
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>服务器错误</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; }}
            .error {{ color: #721c24; background: #f8d7da; padding: 15px; border-radius: 4px; }}
            pre {{ background: #f5f5f5; padding: 10px; overflow-x: auto; }}
        </style>
    </head>
    <body>
        <h1>500 - 服务器内部错误</h1>
        
        <div class="error">
            <h3>错误信息:</h3>
            <p>{str(e)}</p>
            
            <h3>错误详情:</h3>
            <pre>{traceback.format_exc()}</pre>
        </div>
        
        <p><a href="/">返回首页</a></p>
    </body>
    </html>
    """, 500

if __name__ == "__main__":
    try:
        print("\n" + "="*50)
        print(f"{'诊断工具已启动':^50}")
        print("="*50)
        print(f"请访问 http://localhost:8000 继续")
        
        # 运行诊断服务器
        app.run(host='0.0.0.0', port=8000, debug=True)
    except Exception as e:
        print(f"启动诊断服务器失败: {e}")
        traceback.print_exc()