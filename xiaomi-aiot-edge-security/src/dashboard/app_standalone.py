#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
独立运行的Dashboard应用
"""

import os
from flask import Flask

app = Flask(__name__)

# 确保静态资源目录存在
static_dir = os.path.join(os.path.dirname(__file__), 'static')
os.makedirs(static_dir, exist_ok=True)
os.makedirs(os.path.join(static_dir, 'css'), exist_ok=True)
os.makedirs(os.path.join(static_dir, 'js'), exist_ok=True)

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'服务器错误: {error}')
    return render_template('500.html', 
                         current_user='Guest', 
                         current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                         error=error), 500

if __name__ == "__main__":
    print("静态资源目录已创建:")
    print(f"- {static_dir}")
    print(f"- {os.path.join(static_dir, 'css')}")
    print(f"- {os.path.join(static_dir, 'js')}")