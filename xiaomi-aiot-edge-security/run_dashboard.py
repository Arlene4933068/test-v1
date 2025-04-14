import os
os.chdir('d:/0pj/test-v1/xiaomi-aiot-edge-security')

from src.dashboard.app import DashboardApp

def main():
    # 创建控制面板应用实例
    app = DashboardApp()
    
    # 启动Web服务器
    app.run(host='127.0.0.1', port=5000, debug=True)

if __name__ == '__main__':
    main()