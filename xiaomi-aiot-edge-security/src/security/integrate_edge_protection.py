#!/usr/bin/env python3
# 集成边缘计算防护功能到主程序

import os
import sys

def main():
    print("开始集成边缘计算防护功能...\n")
    
    # 找到项目根目录
    project_dir = "D:/0pj/test-v1/xiaomi-aiot-edge-security"
    
    # 首先，确保边缘计算防护模块文件存在
    edge_protection_dir = os.path.join(project_dir, "src", "security")
    
    if not os.path.exists(edge_protection_dir):
        print(f"警告：安全模块目录不存在，将创建: {edge_protection_dir}")
        os.makedirs(edge_protection_dir, exist_ok=True)
    
    # 创建边缘计算防护文件
    edge_protection_path = os.path.join(edge_protection_dir, "edge_security_protector.py")
    
    # 请将边缘计算安全防护模块代码保存到此文件
    print(f"✅ 创建边缘计算防护模块文件: {edge_protection_path}")
    
    # 修改 main.py 文件，集成边缘计算防护
    main_path = os.path.join(project_dir, "src", "main.py")
    
    if not os.path.isfile(main_path):
        print(f"错误：找不到主程序文件: {main_path}")
        sys.exit(1)
    
    # 读取 main.py 文件内容
    with open(main_path, "r", encoding="utf-8") as f:
        main_content = f.read()
    
    # 添加导入语句
    if "from src.security.edge_security_protector import EdgeSecurityProtector" not in main_content:
        import_pos = main_content.find("import")
        if import_pos >= 0:
            # 寻找导入块的结束位置
            import_block_end = main_content.find("\n\n", import_pos)
            if import_block_end >= 0:
                # 在导入块后添加新的导入语句
                updated_content = main_content[:import_block_end] + "\nfrom src.security.edge_security_protector import EdgeSecurityProtector" + main_content[import_block_end:]
                main_content = updated_content
    
    # 在 run_platform 函数中添加边缘计算防护初始化
    if "# 初始化边缘计算安全防护" not in main_content:
        # 在攻击检测器初始化后添加边缘计算防护初始化
        detector_init_pos = main_content.find("detector = AttackDetector(config.get('security', {}))")
        if detector_init_pos >= 0:
            # 找到语句结束位置
            stmt_end = main_content.find("\n", detector_init_pos)
            if stmt_end >= 0:
                # 添加边缘计算防护初始化代码
                edge_protection_init = """
    # 初始化边缘计算安全防护
    edge_protection_config = config.get('edge_protection', {
        'protection_level': 'medium',
        'enable_firewall': True,
        'enable_ids': True,
        'enable_data_protection': True,
        'device_whitelist': []
    })
    edge_protector = EdgeSecurityProtector(edge_protection_config)
    
    # 注册防护回调函数
    def on_protection_activated(protection_data):
        action = protection_data.get('action', '')
        details = protection_data.get('details', {})
        logger.warning(f"边缘计算安全防护措施已激活: {action}, 详情: {details}")
    
    edge_protector.register_protection_callback(on_protection_activated)
    edge_protector.start()
    logger.info("边缘计算安全防护已启动")"""
                
                updated_content = main_content[:stmt_end+1] + edge_protection_init + main_content[stmt_end+1:]
                main_content = updated_content
    
    # 在关闭平台的代码中添加停止边缘计算防护的代码
    if "# 停止边缘计算安全防护" not in main_content:
        attack_simulator_stop_pos = main_content.find("attack_simulator.stop()")
        if attack_simulator_stop_pos >= 0:
            # 找到语句结束位置
            stmt_end = main_content.find("\n", attack_simulator_stop_pos)
            if stmt_end >= 0:
                # 添加停止边缘计算防护的代码
                edge_protection_stop = """
    # 停止边缘计算安全防护
    try:
        if 'edge_protector' in locals():
            edge_protector.stop()
            logger.info("边缘计算安全防护已停止")
    except Exception as e:
        logger.error(f"停止边缘计算安全防护时出错: {str(e)}")"""
                
                updated_content = main_content[:stmt_end+1] + edge_protection_stop + main_content[stmt_end+1:]
                main_content = updated_content
    
    # 保存修改后的 main.py 文件
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(main_content)
    
    print("✅ 已集成边缘计算防护功能到主程序")
    
    # 创建配置示例文件
    config_example_path = os.path.join(project_dir, "config", "edge_protection_example.yaml")
    
    config_example_content = """# 边缘计算安全防护配置示例

edge_protection:
  # 防护级别: low, medium, high
  protection_level: medium
  
  # 是否启用防火墙功能
  enable_firewall: true
  
  # 是否启用入侵检测系统
  enable_ids: true
  
  # 是否启用数据保护（加密）
  enable_data_protection: true
  
  # 设备白名单
  device_whitelist:
    - xiaomi_gateway_01
    - xiaomi_router_01
    - xiaomi_speaker_01
    - xiaomi_camera_01
  
  # 自定义防火墙规则
  firewall_rules:
    - rule_id: custom_rule_001
      protocol: tcp
      port: 8080
      action: allow
      source: 192.168.1.0/24
      description: Allow local network access to web interface
      
    - rule_id: custom_rule_002
      protocol: udp
      port_range: 5000-6000
      action: deny
      source: any
      description: Block unnecessary UDP ports
  
  # 安全扫描设置
  security_scan:
    # 扫描间隔（秒）
    interval: 300
    
    # 配置文件扫描路径
    config_scan_paths:
      - /etc/xiaomi
      - /var/lib/xiaomi/config
    
    # 恶意软件扫描路径
    malware_scan_paths:
      - /tmp
      - /var/lib/xiaomi/downloads
    
    # 忽略路径
    ignore_paths:
      - /var/log
      - /tmp/cache
  
  # 日志设置
  logging:
    # 日志级别: debug, info, warning, error
    level: info
    
    # 是否保存到文件
    save_to_file: true
    
    # 日志文件路径
    log_file: logs/edge_protection.log
    
    # 日志轮转设置
    rotation:
      # 单个日志文件最大大小（字节）
      max_size: 10485760  # 10MB
      
      # 保留的日志文件数量
      backup_count: 5
"""
    
    # 保存配置示例文件
    with open(config_example_path, "w", encoding="utf-8") as f:
        f.write(config_example_content)
    
    print(f"✅ 已创建边缘计算防护配置示例: {config_example_path}")
    print("\n边缘计算防护功能集成完成！")
    print("\n要使用此功能，请在启动程序前修改配置文件，添加 edge_protection 部分。")

if __name__ == "__main__":
    main()