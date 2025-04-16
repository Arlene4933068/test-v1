#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
导入修复脚本 - 解决相对导入问题
"""

import os
import sys
import re

def fix_security_config():
    """修复security_config.py中的导入问题"""
    file_path = "src/dashboard/security_config.py"
    
    if not os.path.exists(file_path):
        print(f"错误：找不到文件 {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换问题导入
    new_content = re.sub(
        r'from \.\.utils\.logger import get_logger', 
        'import sys, os\nsys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))\nfrom utils.logger import get_logger', 
        content
    )
    
    if new_content == content:
        print("没有找到需要修复的导入语句")
        return False
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"成功修复 {file_path} 中的导入问题")
    return True

if __name__ == "__main__":
    if fix_security_config():
        print("导入问题已修复，请尝试重新运行应用程序")
    else:
        print("无法自动修复，请手动检查导入语句")