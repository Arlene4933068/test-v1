#!/usr/bin/env python3
# 完整修复所有导入问题

import os
import sys
import re

def main():
    print("开始全面修复导入问题...\n")
    
    # 找到项目根目录
    project_dir = "D:/0pj/test-v1/xiaomi-aiot-edge-security"
    
    # 创建边缘计算防护文件 (如果不存在)
    edge_protection_dir = os.path.join(project_dir, "src", "security")
    os.makedirs(edge_protection_dir, exist_ok=True)
    
    # 创建边缘计算防护文件
    edge_protection_path = os.path.join(edge_protection_dir, "edge_security_protector.py")
    
    # 修改所有使用了相对导入的 Python 文件
    src_dir = os.path.join(project_dir, "src")
    
    # 第一步：创建 __init__.py 文件确保包结构正确
    for root, dirs, files in os.walk(src_dir):
        if os.path.isdir(root) and root != src_dir:
            init_file = os.path.join(root, "__init__.py")
            if not os.path.exists(init_file):
                with open(init_file, "w") as f:
                    f.write("# Auto-generated __init__.py file\n")
                print(f"创建了 {init_file}")
    
    # 第二步：修复所有 Python 文件中的相对导入
    fixed_files = []
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_imports_in_file(file_path, src_dir, project_dir):
                    fixed_files.append(file_path)
    
    print(f"已修复 {len(fixed_files)} 个文件中的导入问题")
    
    # 创建更健壮的启动脚本
    create_robust_launcher(project_dir)
    
    print("\n所有导入问题修复完成！请使用新的启动脚本启动您的应用程序：")
    print("python start_platform.py")

def fix_imports_in_file(file_path, src_dir, project_dir):
    """修复单个文件中的导入问题"""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    original_content = content
    
    # 替换相对导入（例如：from .utils.logger import get_logger）
    # 转换为绝对导入（例如：from src.utils.logger import get_logger）
    rel_import_pattern = r'from\s+\.\.([a-zA-Z0-9_\.]+)\s+import\s+'
    
    # 计算模块的相对位置
    rel_path = os.path.relpath(os.path.dirname(file_path), src_dir)
    if rel_path == ".":
        module_path = "src"
    else:
        module_path = "src." + rel_path.replace(os.path.sep, ".")
    
    # 创建替换函数
    def replace_rel_import(match):
        rel_module = match.group(1)
        # 计算绝对导入路径
        parts = module_path.split('.')
        levels = 0
        for i, c in enumerate(rel_module):
            if c == '.':
                levels += 1
            else:
                rel_module = rel_module[i:]
                break
        
        # 回到上层目录
        if levels >= len(parts):
            # 如果相对导入超出了顶层包，使用src作为基础
            abs_module = "src"
            if rel_module:
                abs_module += "." + rel_module
        else:
            abs_parts = parts[:-levels]
            abs_module = ".".join(abs_parts)
            if rel_module:
                abs_module += "." + rel_module
        
        return f'from {abs_module} import '
    
    # 替换相对导入
    content = re.sub(rel_import_pattern, replace_rel_import, content)
    
    # 替换特定的相对导入模式 from src import X
    rel_import_pattern2 = r'from\s+\.\s+import\s+'
    parent_module = ".".join(module_path.split('.')[:-1])
    if not parent_module:
        parent_module = "src"
    content = re.sub(rel_import_pattern2, f'from {parent_module} import ', content)
    
    # 替换 from src. 开头的导入为直接导入
    content = content.replace("from src.", "from src.")
    
    # 如果文件发生了变化，保存它
    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"修复了导入: {file_path}")
        return True
    
    return False

def create_robust_launcher(project_dir):
    """创建更健壮的启动脚本"""
    launcher_path = os.path.join(project_dir, "start_platform.py")
    
    launcher_content = """#!/usr/bin/env python3
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
"""
    
    with open(launcher_path, "w", encoding="utf-8") as f:
        f.write(launcher_content)
    
    print(f"✅ 已创建健壮的启动脚本: {launcher_path}")
    
    # 创建简单的配置检查脚本
    config_checker_path = os.path.join(project_dir, "check_config.py")
    
    config_checker_content = """#!/usr/bin/env python3
# 配置检查脚本

import os
import sys
import yaml
import json
import logging
from pprint import pprint

def main():
    # 设置基本日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    
    logger = logging.getLogger("ConfigChecker")
    
    # 项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 检查配置文件
    config_dir = os.path.join(project_root, "config")
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
        logger.warning(f"创建了配置目录: {config_dir}")
    
    # 平台配置
    platform_config_path = os.path.join(config_dir, "platform.yaml")
    if not os.path.exists(platform_config_path):
        # 创建默认配置
        default_config = {
            "platform": {
                "edgex": {
                    "host": "localhost",
                    "port": 59880,
                    "metadata_port": 59881,
                    "core_command_port": 59882,
                    "api_version": "v2",
                    "device_service_name": "xiaomi-device-service"
                },
                "thingsboard": {
                    "host": "localhost",
                    "port": 8080,
                    "username": "yy3205543808@gmail.com",
                    "password": "wlsxcdh52jy.L"
                }
            },
            "security": {
                "scan_interval": 10,
                "detection_threshold": 0.7,
                "enable_attack_simulation": True,
                "simulation_probability": 0.1
            },
            "analytics": {
                "output_dir": "output",
                "report_interval": 3600
            },
            "edge_protection": {
                "protection_level": "medium",
                "enable_firewall": True,
                "enable_ids": True,
                "enable_data_protection": True,
                "device_whitelist": [
                    "xiaomi_gateway_01",
                    "xiaomi_router_01",
                    "xiaomi_speaker_01",
                    "xiaomi_camera_01"
                ]
            }
        }
        
        with open(platform_config_path, "w", encoding="utf-8") as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        logger.info(f"创建了默认平台配置: {platform_config_path}")
    
    try:
        # 加载平台配置
        with open(platform_config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        # 检查配置是否有效
        logger.info("成功加载平台配置")
        logger.info("配置包含以下部分:")
        
        # 输出配置节
        for section in config:
            print(f"- {section}")
        
        # 检查必要的配置部分
        required_sections = ["platform", "security", "analytics"]
        missing_sections = [section for section in required_sections if section not in config]
        
        if missing_sections:
            logger.warning(f"缺少以下配置部分: {', '.join(missing_sections)}")
        
        # 查看是否启用了边缘计算防护
        if "edge_protection" in config:
            print("\n边缘计算防护配置:")
            pprint(config["edge_protection"])
        else:
            logger.warning("未配置边缘计算防护!")
            
    except Exception as e:
        logger.error(f"检查配置时发生错误: {str(e)}")
        return False
    
    print("\n配置检查完成。如果需要，请编辑 config/platform.yaml 文件以更新配置。")
    return True

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
"""
    
    with open(config_checker_path, "w", encoding="utf-8") as f:
        f.write(config_checker_content)
    
    print(f"✅ 已创建配置检查脚本: {config_checker_path}")

if __name__ == "__main__":
    main()