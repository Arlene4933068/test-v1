#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import traceback
from flask import Flask, jsonify

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True

@app.route('/')
def index():
    return """
    <html>
        <head>
            <title>调试页面</title>
            <style>
                body {{ font-family: sans-serif; margin: 20px; }}
                pre {{ background: #f5f5f5; padding: 10px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>Flask应用诊断</h1>
            <h2>环境信息：</h2>
            <ul>
                <li>当前工作目录: <code>{}</code></li>
                <li>Python版本: <code>{}</code></li>
                <li>模块搜索路径:</li>
            </ul>
            <pre>{}</pre>
            
            <h2>目录结构检查：</h2>
            <pre>{}</pre>
            
            <h2>测试路由：</h2>
            <ul>
                <li><a href="/test_template">测试模板渲染</a></li>
                <li><a href="/test_json">测试JSON返回</a></li>
            </ul>
        </body>
    </html>
    """.format(
        os.getcwd(),
        sys.version,
        '\n'.join(sys.path),
        check_directory_structure()
    )

def check_directory_structure():
    """检查关键目录和文件是否存在"""
    result = []
    
    # 检查当前目录
    result.append(f"当前目录内容: {os.listdir('.')}")
    
    # 检查templates目录
    templates_dir = os.path.join('xiaomi-aiot-edge-security', 'src', 'dashboard', 'templates')
    if os.path.exists(templates_dir):
        result.append(f"模板目录存在: {templates_dir}")
        result.append(f"模板目录内容: {os.listdir(templates_dir)}")
    else:
        result.append(f"模板目录不存在: {templates_dir}")
    
    # 检查static目录
    static_dir = os.path.join('xiaomi-aiot-edge-security', 'src', 'dashboard', 'static')
    if os.path.exists(static_dir):
        result.append(f"静态文件目录存在: {static_dir}")
        result.append(f"静态文件目录内容: {os.listdir(static_dir)}")
    else:
        result.append(f"静态文件目录不存在: {static_dir}")
    
    # 检查配置目录
    config_dir = os.path.join('xiaomi-aiot-edge-security', 'config')
    if os.path.exists(config_dir):
        result.append(f"配置目录存在: {config_dir}")
        result.append(f"配置目录内容: {os.listdir(config_dir)}")
    else:
        result.append(f"配置目录不存在: {config_dir}")
    
    return '\n'.join(result)

@app.route('/test_template')
def test_template():
    try:
        return """
        <html>
            <head><title>测试页面</title></head>
            <body>
                <h1>模板测试成功</h1>
                <p>如果您看到此消息，说明基本HTML返回功能正常。</p>
                <p><a href="/">返回诊断页面</a></p>
            </body>
        </html>
        """
    except Exception as e:
        return f"""
        <html>
            <head><title>错误</title></head>
            <body>
                <h1>模板测试失败</h1>
                <p>错误类型: {type(e).__name__}</p>
                <p>错误信息: {str(e)}</p>
                <pre>{traceback.format_exc()}</pre>
                <p><a href="/">返回诊断页面</a></p>
            </body>
        </html>
        """

@app.route('/test_json')
def test_json():
    try:
        return jsonify({
            'status': 'success',
            'message': 'JSON响应测试成功',
            'environment': {
                'python_version': sys.version,
                'working_directory': os.getcwd()
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error_type': type(e).__name__,
            'error_message': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """全局异常处理"""
    print(f"捕获到异常: {e}")
    print(traceback.format_exc())
    return f"""
    <html>
        <head>
            <title>应用错误</title>
            <style>
                body {{ font-family: sans-serif; margin: 20px; }}
                pre {{ background: #f5f5f5; padding: 10px; border-radius: 5px; }}
                .error {{ color: red; }}
            </style>
        </head>
        <body>
            <h1 class="error">应用发生错误</h1>
            <p>类型: <code>{type(e).__name__}</code></p>
            <p>描述: <code>{str(e)}</code></p>
            <h3>错误堆栈:</h3>
            <pre>{traceback.format_exc()}</pre>
            <p><a href="/">返回诊断页面</a></p>
        </body>
    </html>
    """, 500

if __name__ == "__main__":
    print("\n=== Flask应用诊断工具 ===")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"Python版本: {sys.version}")
    print("\n启动诊断服务器...")
    app.run(debug=True, port=5001)
    print("服务器已停止")