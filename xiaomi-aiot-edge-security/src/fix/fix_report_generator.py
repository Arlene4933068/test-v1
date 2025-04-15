#!/usr/bin/env python3
# 修复 ReportGenerator 中的类型错误

import os
import sys

def main():
    print("开始修复 ReportGenerator 类型错误...\n")
    
    # 确定正确的项目根目录路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 尝试多个可能的项目根路径
    possible_roots = [
        os.getcwd(),                                  # 当前工作目录
        os.path.dirname(script_dir),                  # 脚本的父目录
        os.path.dirname(os.path.dirname(script_dir)), # 脚本的祖父目录
        "D:/0pj/test-v1/xiaomi-aiot-edge-security"   # 明确指定的项目路径
    ]
    
    # 找到正确的项目根目录
    root_dir = None
    for path in possible_roots:
        main_file_path = os.path.join(path, "src", "main.py")
        if os.path.isfile(main_file_path):
            root_dir = path
            break
    
    if not root_dir:
        print("错误：无法找到项目根目录")
        sys.exit(1)
    
    print(f"已找到项目根目录: {root_dir}")
    
    # 修复 ReportGenerator 文件
    report_gen_path = os.path.join(root_dir, "src", "analytics", "report_generator.py")
    
    if not os.path.isfile(report_gen_path):
        print(f"错误：无法找到 ReportGenerator 文件: {report_gen_path}")
        sys.exit(1)
    
    # 读取文件内容
    with open(report_gen_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 修改 __init__ 方法以处理字典类型的配置
    original_init = """    def __init__(self, output_dir: str):
        \"\"\"
        初始化报告生成器
        
        Args:
            output_dir: 输出目录路径
        \"\"\"
        self.logger = logging.getLogger(__name__)
        self.output_dir = output_dir
        
        # 确保输出目录存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)"""
    
    modified_init = """    def __init__(self, config):
        \"\"\"
        初始化报告生成器
        
        Args:
            config: 可以是输出目录路径字符串或包含配置的字典
        \"\"\"
        self.logger = logging.getLogger(__name__)
        
        # 处理不同类型的配置参数
        if isinstance(config, dict):
            self.output_dir = config.get('output_dir', 'output')
        else:
            self.output_dir = config
        
        # 确保输出目录存在
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)"""
    
    # 替换内容
    new_content = content.replace(original_init, modified_init)
    
    # 如果找不到准确的原始内容，尝试更模糊的匹配
    if new_content == content:
        import re
        pattern = r"def __init__\(self, output_dir: str\):.*?os\.makedirs\(output_dir\)"
        new_content = re.sub(pattern, modified_init, content, flags=re.DOTALL)
    
    # 写入修改后的内容
    with open(report_gen_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print(f"✅ 已修复 ReportGenerator 类")
    
    # 修改 main.py 文件以正确传递 analytics_config
    main_path = os.path.join(root_dir, "src", "main.py")
    
    with open(main_path, "r", encoding="utf-8") as f:
        main_content = f.read()
    
    # 修改创建 ReportGenerator 的行
    original_line = "    report_generator = ReportGenerator(analytics_config)"
    modified_line = "    report_generator = ReportGenerator(analytics_config.get('output_dir', 'output'))"
    
    # 替换内容
    new_main_content = main_content.replace(original_line, modified_line)
    
    # 如果未找到准确的行，尝试更模糊的匹配
    if new_main_content == main_content:
        modified_line = """    # 确保正确传递 analytics 配置
    output_dir = analytics_config.get('output_dir', 'output') if isinstance(analytics_config, dict) else 'output'
    report_generator = ReportGenerator(output_dir)"""
        
        import re
        pattern = r"report_generator = ReportGenerator\(analytics_config\)"
        new_main_content = re.sub(pattern, modified_line, main_content)
    
    # 写入修改后的内容
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(new_main_content)
    
    print(f"✅ 已修复 main.py 文件")
    
    # 创建输出目录
    output_dir = os.path.join(root_dir, "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"✅ 已创建输出目录: {output_dir}")
    
    print("\n🚀 所有修复已完成！现在您可以运行主程序:")
    print(f"python {os.path.join(root_dir, 'src', 'main.py')}")

if __name__ == "__main__":
    main()