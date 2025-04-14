import os
os.chdir('d:/0pj/test-v1/xiaomi-aiot-edge-security')

from src.security.attack_simulator import AttackSimulator

def main():
    # 创建攻击仿真器实例
    simulator = AttackSimulator('config/security.yaml')
    
    # 运行攻击仿真
    simulator.run_attack_simulation('test_device_001')

if __name__ == '__main__':
    main()