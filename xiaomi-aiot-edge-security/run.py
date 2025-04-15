#!/usr/bin/env python3
# 小米AIoT边缘安全防护研究平台启动脚本

import os
import sys

def main():
    # 添加当前目录到Python路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    
    try:
        # 导入并运行主程序
        from src.main import main
        main()
    except Exception as e:
        print(f"错误: 运行程序时出现异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
