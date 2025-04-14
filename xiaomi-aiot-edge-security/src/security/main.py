"""小米AIoT边缘安全防护研究平台 - 主入口"""

import logging
import os
import yaml
from .attack_detector import AttackDetector
from .protection_engine import ProtectionEngine
from .security_logger import SecurityLogger
from .packet_visualizer import PacketVisualizer
from scapy.all import sniff, wrpcap
from .attack_simulator import AttackSimulator

def setup_logging():
    """配置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def load_config():
    """加载安全配置"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'security.yaml')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logging.error(f"加载配置文件失败: {str(e)}")
        return None

def main():
    """主函数"""
    # 设置日志
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # 加载配置
    config = load_config()
    if not config:
        logger.error("无法启动安全服务：配置加载失败")
        return
    
    # 初始化安全日志记录器
    security_logger = SecurityLogger(config.get('audit', {}))
    
    # 初始化攻击检测器
    detector = AttackDetector(config)
    
    # 初始化数据包可视化器
    visualizer = PacketVisualizer(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'captures'))
    
    # 初始化防护引擎
    protection_engine = ProtectionEngine()
    
    # 注册检测器的告警回调
    detector.add_alert_callback(protection_engine.handle_alert)
    
    try:
        # 初始化攻击仿真器
        simulator = AttackSimulator()
        
        # 启动攻击仿真
        simulator.simulate_ddos_attack(target_device_id='device_123')
        simulator.simulate_mitm_attack(target_device_id='device_123')
        simulator.simulate_credential_attack(target_device_id='device_123')
        
        # 捕获网络流量并保存为PCAP文件
        def capture_traffic(interface, pcap_file):
            packets = sniff(iface=interface, count=100)  # 捕获100个数据包
            wrpcap(pcap_file, packets)  # 保存为PCAP文件
        
        # 示例：捕获流量并保存
        capture_traffic('Ethernet', r'd:\0pj\test-v1\xiaomi-aiot-edge-security\config\captures\captured_traffic.pcap')
        
        # 启动检测器
        detector.start()
        logger.info("安全防护服务已启动")
        
        # 保持程序运行
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("正在停止安全防护服务...")
        detector.stop()
        protection_engine.stop()
        logger.info("安全防护服务已停止")

if __name__ == '__main__':
    main()