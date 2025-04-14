"""小米AIoT边缘安全防护研究平台 - 攻击仿真测试"""

import time
from .attack_simulator import AttackSimulator

def main():
    # 初始化攻击仿真器
    simulator = AttackSimulator()
    
    # 设置目标设备ID
    target_device_id = "test_device_001"
    
    try:
        # 运行完整的攻击仿真
        simulator.run_attack_simulation(target_device_id)
        
        # 等待所有防护措施执行完成
        time.sleep(5)
        
        print("攻击仿真测试完成")
        
    except KeyboardInterrupt:
        print("测试被用户中断")
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")

if __name__ == '__main__':
    main()