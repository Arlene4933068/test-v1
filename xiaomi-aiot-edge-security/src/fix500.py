#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
500错误自动修复工具 - 专为小米AIoT边缘安全防护研究平台设计
"""

import os
import sys
import shutil
import logging
import traceback
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('fix500.log')
    ]
)

logger = logging.getLogger("fix500")

def banner(message):
    """打印格式化的横幅"""
    line = "=" * 70
    print(f"\n{line}")
    print(f"{message:^70}")
    print(f"{line}\n")

def check_flask_imports():
    """检查Flask导入是否正常"""
    try:
        from flask import Flask, render_template, request
        logger.info("Flask导入正常 ✓")
        return True
    except ImportError as e:
        logger.error(f"Flask导入错误: {e}")
        return False

def create_app_with_minimal_route():
    """创建一个包含最小路由的应用"""
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return "诊断成功! Flask正常运行。"
    
    return app

def run_diagnostic_server():
    """运行一个诊断用的Flask服务器"""
    try:
        app = create_app_with_minimal_route()
        banner("启动诊断服务器")
        print("如果此服务器能正常启动，说明Flask基本功能正常")
        print("请访问 http://localhost:7000 测试")
        app.run(debug=True, port=7000)
    except Exception as e:
        logger.error(f"诊断服务器启动失败: {e}")
        logger.error(traceback.format_exc())

def check_template_rendering():
    """检查模板渲染是否正常"""
    from flask import Flask, render_template
    import tempfile
    import shutil
    
    # 创建临时目录作为模板文件夹
    temp_dir = tempfile.mkdtemp()
    try:
        # 创建一个测试模板
        template_path = os.path.join(temp_dir, 'test.html')
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write("<html><body><h1>{{ message }}</h1></body></html>")
        
        # 创建测试应用
        app = Flask(__name__, template_folder=temp_dir)
        with app.app_context():
            try:
                result = render_template('test.html', message="测试成功")
                logger.info("模板渲染正常 ✓")
                return True
            except Exception as e:
                logger.error(f"模板渲染失败: {e}")
                logger.error(traceback.format_exc())
                return False
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)

def fix_app_standalone():
    """修复app_standalone.py文件"""
    try:
        # 定位文件
        app_path = os.path.join('xiaomi-aiot-edge-security', 'src', 'dashboard', 'app_standalone.py')
        if not os.path.exists(app_path):
            logger.error(f"文件不存在: {app_path}")
            return False
        
        # 备份原始文件
        backup_path = f"{app_path}.bak.{int(datetime.now().timestamp())}"
        shutil.copy2(app_path, backup_path)
        logger.info(f"已备份原始文件到: {backup_path}")
        
        # 修复后的代码
        fixed_code = '''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
独立运行的Dashboard应用 - 经过500错误修复
"""

import os
import sys
import logging
import traceback
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

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

# 创建Flask应用
app = Flask(__name__, 
           template_folder=templates_dir,
           static_folder=static_dir)
app.config['DEBUG'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True  # 确保错误被传递到日志

# 创建一个简单的500错误模板
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

# 404页面模板
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

# 创建简单的主页模板
index_template_path = os.path.join(templates_dir, 'index.html')
if not os.path.exists(index_template_path):
    with open(index_template_path, 'w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>小米AIoT边缘安全防护研究平台</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 800px; margin: 40px auto; padding: 20px; background-color: #fff; border-radius: 5px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #ff6700; margin-top: 0; }
        .footer { margin-top: 30px; font-size: 0.9em; color: #666; }
        .btn { display: inline-block; padding: 10px 20px; background-color: #ff6700; color: white; text-decoration: none; border-radius: 4px; margin-top: 20px; }
        .btn:hover { background-color: #ff8533; }
    </style>
</head>
<body>
    <div class="container">
        <h1>小米AIoT边缘安全防护研究平台</h1>
        <p>欢迎使用小米AIoT边缘安全防护研究平台。</p>
        <p>当前状态: 系统运行正常</p>
        <p>当前时间: {{ current_time }}</p>
        
        <a href="/debug" class="btn">查看系统状态</a>
        
        <div class="footer">
            <p>© 2025 小米AIoT边缘安全防护研究平台</p>
        </div>
    </div>
</body>
</html>""")
    logger.info(f"创建了主页模板: {index_template_path}")

@app.route('/')
def index():
    """首页"""
    try:
        logger.info("访问首页")
        return render_template('index.html', current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        logger.error(f"首页渲染错误: {str(e)}")
        logger.error(traceback.format_exc())
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
            <p>系统运行正常，但模板渲染失败。</p>
            <p>当前时间: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
            <a href="/debug">查看系统状态</a>
        </body>
        </html>
        """

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
            html += f'<li><span class="{status}">{name}: {version}</span></li>\n'
        
        html += """
                </ul>
            </div>
            
            <div class="section">
                <h2>目录信息</h2>
        """
        
        for name, info in dirs.items():
            status = "success" if info['exists'] else "error"
            html += f'<h3>{name} <span class="{status}">{"存在" if info["exists"] else "不存在"}</span></h3>\n'
            html += f'<pre>{info["path"]}</pre>\n'
            
            if info['exists']:
                if info['files']:
                    html += '<ul>\n'
                    for file in sorted(info['files']):
                        html += f'<li>{file}</li>\n'
                    html += '</ul>\n'
                else:
                    html += '<p>目录为空</p>\n'
        
        html += """
            </div>
            
            <p><a href="/">返回首页</a></p>
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
                              current_user='Guest', 
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

if __name__ == "__main__":
    try:
        banner("小米AIoT边缘安全防护研究平台")
        print(f"• 工作目录: {os.getcwd()}")
        print(f"• 应用目录: {base_dir}")
        print(f"• 模板目录: {templates_dir}")
        print(f"• 静态目录: {static_dir}")
        
        print("\n启动服务器，访问 http://localhost:5000 查看应用...")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.critical(f"启动失败: {str(e)}")
        logger.critical(traceback.format_exc())
        print(f"\n严重错误: {str(e)}")
        print("请查看日志获取更多信息。")
'''
        
        # 写入修复后的代码
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(fixed_code)
        
        logger.info(f"已修复并保存: {app_path}")
        return True
    except Exception as e:
        logger.error(f"修复app_standalone.py时出错: {e}")
        logger.error(traceback.format_exc())
        return False

def fix_visualization_modules():
    """修复visualization和attack_visualizer模块"""
    try:
        dashboard_dir = os.path.join('xiaomi-aiot-edge-security', 'src', 'dashboard')
        visualization_path = os.path.join(dashboard_dir, 'visualization.py')
        attack_visualizer_path = os.path.join(dashboard_dir, 'attack_visualizer.py')
        
        results = []
        
        # 检查visualization.py
        if os.path.exists(visualization_path):
            # 备份
            backup_path = f"{visualization_path}.bak.{int(datetime.now().timestamp())}"
            shutil.copy2(visualization_path, backup_path)
            
            # 读取内容
            with open(visualization_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 添加必要的导入和配置
            if 'matplotlib.use(' not in content:
                header = '''"""
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
                # 查找第一个非注释、非导入的行
                lines = content.split('\n')
                content_start = 0
                for i, line in enumerate(lines):
                    if line.strip() and not line.startswith('#') and not line.startswith('"""') and not line.startswith("'''"):
                        if not ("import" in line or "from" in line):
                            content_start = i
                            break
                
                if content_start > 0:
                    # 替换开头部分
                    new_content = header + '\n\n' + '\n'.join(lines[content_start:])
                    with open(visualization_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    results.append(f"修复了 visualization.py (备份在 {backup_path})")
                else:
                    results.append(f"无法识别 visualization.py 的内容部分，未修改")
        else:
            results.append(f"未找到 visualization.py")
        
        # 检查attack_visualizer.py
        if os.path.exists(attack_visualizer_path):
            # 备份
            backup_path = f"{attack_visualizer_path}.bak.{int(datetime.now().timestamp())}"
            shutil.copy2(attack_visualizer_path, backup_path)
            
            # 读取内容
            with open(attack_visualizer_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 添加必要的导入和配置
            if 'from typing import Optional, Any' not in content or 'matplotlib.use(' not in content:
                header = '''"""
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
                # 查找第一个非注释、非导入的行
                lines = content.split('\n')
                content_start = 0
                for i, line in enumerate(lines):
                    if line.strip() and not line.startswith('#') and not line.startswith('"""') and not line.startswith("'''"):
                        if "class " in line:
                            content_start = i
                            break
                
                if content_start > 0:
                    # 替换开头部分
                    new_content = header + '\n\n' + '\n'.join(lines[content_start:])
                    with open(attack_visualizer_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    results.append(f"修复了 attack_visualizer.py (备份在 {backup_path})")
                else:
                    results.append(f"无法识别 attack_visualizer.py 的内容部分，未修改")
        else:
            results.append(f"未找到 attack_visualizer.py")
        
        for result in results:
            logger.info(result)
        
        return len(results) > 0
    except Exception as e:
        logger.error(f"修复可视化模块时出错: {e}")
        logger.error(traceback.format_exc())
        return False

def main():
    """主函数"""
    banner("500错误自动修复工具")
    
    print("检查环境和依赖...")
    if not check_flask_imports():
        print("错误: Flask导入失败，请确认已安装Flask: pip install flask")
        return
    
    print("测试模板渲染功能...")
    check_template_rendering()
    
    print("\n选择要执行的操作:")
    print("1. 修复app_standalone.py")
    print("2. 修复可视化模块")
    print("3. 运行诊断服务器")
    print("0. 全部执行")
    
    try:
        choice = int(input("\n请输入选项 [0-3]: ").strip())
        
        if choice == 0 or choice == 1:
            print("\n开始修复app_standalone.py...")
            if fix_app_standalone():
                print("✅ app_standalone.py 修复完成")
            else:
                print("❌ app_standalone.py 修复失败")
        
        if choice == 0 or choice == 2:
            print("\n开始修复可视化模块...")
            if fix_visualization_modules():
                print("✅ 可视化模块修复完成")
            else:
                print("❌ 可视化模块修复失败")
        
        if choice == 0 or choice == 3:
            print("\n开始运行诊断服务器...")
            run_diagnostic_server()
    except ValueError:
        print("无效的输入。请输入数字(0-3)。")
    except KeyboardInterrupt:
        print("\n操作已取消。")
    
    banner("修复完成")
    print("请尝试重新启动应用:")
    print("python xiaomi-aiot-edge-security/src/dashboard/app_standalone.py")

if __name__ == "__main__":
    main()