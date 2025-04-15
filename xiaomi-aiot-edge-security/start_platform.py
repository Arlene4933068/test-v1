#!/usr/bin/env python3
# 小米AIoT边缘安全防护研究平台启动脚本

import os
import sys
import logging
import traceback

def setup_environment():
    # 确保工作目录正确
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 添加项目根目录到Python路径
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # 确保所有必要的目录存在
    dirs_to_create = [
        "logs", 
        "data", 
        "config", 
        "quarantine",
        "data_backup",
        "telemetry_backup"
    ]
    
    for directory in dirs_to_create:
        dir_path = os.path.join(project_root, directory)
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
                print(f"创建目录: {dir_path}")
            except Exception as e:
                print(f"警告: 无法创建目录 {dir_path}: {e}")
    
    # 设置基本日志配置
    log_file = os.path.join(project_root, "logs", "platform.log")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return project_root

def main():
    try:
        # 设置环境
        project_root = setup_environment()
        print(f"正在启动小米AIoT边缘安全防护研究平台...")
        print(f"项目根目录: {project_root}")
        print(f"Python 版本: {sys.version}")
        print(f"Python 路径: {sys.executable}")
        
        # 如果需要转发到其他脚本，使用以下格式而不是导入
        # 这样可以避免导入相关的问题
        main_script = os.path.join(project_root, "src", "main.py")
        
        # 使用 exec 执行主脚本，避免导入问题
        with open(main_script, 'r', encoding='utf-8') as f:
            script_content = f.read()
        
        # 构建全局和局部命名空间
        global_namespace = {
            '__file__': main_script,
            '__name__': '__main__'
        }
        
        # 在项目根目录的上下文中执行脚本
        exec(script_content, global_namespace)
        
    except Exception as e:
        print(f"错误: 运行程序时出现异常: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
