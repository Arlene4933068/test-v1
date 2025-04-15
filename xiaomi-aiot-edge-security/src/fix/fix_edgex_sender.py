#!/usr/bin/env python3
# 修复EdgeX连接器中的数据发送功能

import os
import sys

def main():
    print("开始修复EdgeX遥测数据发送功能...\n")
    
    # 找到项目根目录
    project_dir = "D:/0pj/test-v1/xiaomi-aiot-edge-security"
    
    # 修复EdgeX连接器
    edgex_path = os.path.join(project_dir, "src", "platform_connector", "edgex_connector.py")
    
    if not os.path.isfile(edgex_path):
        print(f"错误：找不到EdgeX连接器文件: {edgex_path}")
        sys.exit(1)
    
    # 读取文件内容
    with open(edgex_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 修改发送设备数据方法
    old_send_method = """    def send_device_data(self, device_name: str, readings: List[Dict[str, Any]]) -> bool:
        \"\"\"
        发送设备数据到EdgeX Foundry
        
        Args:
            device_name: 设备名称
            readings: 读数列表，每个读数为包含resourceName、value等字段的字典
        
        Returns:
            bool: 发送成功返回True，否则返回False
        \"\"\"
        try:
            # 尝试发送，但即使失败也模拟成功
            try:
                # 构建事件数据
                event_data = {
                    "apiVersion": "v2",
                    "deviceName": device_name,
                    "readings": readings
                }
                
                response = requests.post(
                    f"{self.core_data_url}/api/v2/event",
                    headers=self.headers,
                    json=event_data
                )
                
                if response.status_code in [200, 201]:
                    self.logger.debug(f"成功发送设备{device_name}的数据")
                    return True
            except Exception:
                pass
                
            # 模拟成功
            self.logger.warning(f"模拟发送设备{device_name}的数据，实际未发送")
            return True
        except Exception as e:
            self.logger.error(f"发送设备数据时发生错误: {str(e)}")
            return True  # 仍然返回成功"""
    
    new_send_method = """    def send_device_data(self, device_name: str, readings: List[Dict[str, Any]]) -> bool:
        \"\"\"
        发送设备数据到EdgeX Foundry
        
        Args:
            device_name: 设备名称
            readings: 读数列表，每个读数为包含resourceName、value等字段的字典
        
        Returns:
            bool: 发送成功返回True，否则返回False
        \"\"\"
        try:
            # 构建事件数据
            event_data = {
                "apiVersion": "v2",
                "deviceName": device_name,
                "readings": readings
            }
            
            # 记录要发送的数据
            self.logger.debug(f"准备发送设备{device_name}的数据: {readings}")
            
            try:
                response = requests.post(
                    f"{self.core_data_url}/api/v2/event",
                    headers=self.headers,
                    json=event_data,
                    timeout=5
                )
                
                if response.status_code in [200, 201]:
                    self.logger.info(f"成功发送设备{device_name}的数据到EdgeX")
                    return True
                else:
                    self.logger.warning(f"发送设备{device_name}数据到EdgeX失败，状态码: {response.status_code}, 响应: {response.text}")
                    
                    # 备份到本地文件
                    self._backup_data_locally(device_name, readings)
                    return False
            except Exception as e:
                self.logger.warning(f"发送设备{device_name}数据到EdgeX时出现异常: {str(e)}")
                
                # 备份到本地文件
                self._backup_data_locally(device_name, readings)
                return False
        except Exception as e:
            self.logger.error(f"处理设备{device_name}数据发送时发生错误: {str(e)}")
            return False
    
    def _backup_data_locally(self, device_name: str, readings: List[Dict[str, Any]]) -> None:
        \"\"\"
        将数据备份到本地文件
        
        Args:
            device_name: 设备名称
            readings: 读数列表
        \"\"\"
        try:
            # 确保备份目录存在
            backup_dir = os.path.join(os.getcwd(), "data_backup")
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # 构造文件名
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"{device_name}_{timestamp}.json")
            
            # 写入数据
            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump({"device": device_name, "timestamp": time.time(), "readings": readings}, f, indent=2)
            
            self.logger.info(f"已将设备{device_name}的数据备份到本地文件: {backup_file}")
        except Exception as e:
            self.logger.error(f"备份设备{device_name}数据到本地文件时出错: {str(e)}")"""
    
    # 替换内容
    new_content = content.replace(old_send_method, new_send_method)
    
    # 确保导入了 os 和 json 模块
    if "import os" not in new_content:
        new_content = new_content.replace("import time", "import os\nimport time")
    
    if "import json" not in new_content:
        new_content = new_content.replace("import time", "import json\nimport time")
    
    # 写入修改后的内容
    with open(edgex_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print("✅ 已修复EdgeX连接器的数据发送功能")
    
    # 修复ThingsBoard连接器
    tb_path = os.path.join(project_dir, "src", "platform_connector", "thingsboard_connector.py") 
    
    if not os.path.isfile(tb_path):
        print(f"错误：找不到ThingsBoard连接器文件: {tb_path}")
        sys.exit(1)
    
    # 读取文件内容
    with open(tb_path, "r", encoding="utf-8") as f:
        tb_content = f.read()
    
    # 修改发送遥测数据的方法
    old_send_telemetry = """    def send_telemetry(self, access_token: str, telemetry_data: Dict[str, Any]) -> bool:
        \"\"\"
        发送设备遥测数据
        
        Args:
            access_token: 设备访问令牌
            telemetry_data: 遥测数据
        
        Returns:
            bool: 发送成功返回True，否则返回False
        \"\"\"
        try:
            # 模拟发送遥测数据
            self.logger.info(f"模拟发送遥测数据，访问令牌: {access_token}")
            return True
        except Exception as e:
            self.logger.error(f"发送遥测数据时发生错误: {str(e)}")
            return True"""
    
    new_send_telemetry = """    def send_telemetry(self, access_token: str, telemetry_data: Dict[str, Any]) -> bool:
        \"\"\"
        发送设备遥测数据
        
        Args:
            access_token: 设备访问令牌
            telemetry_data: 遥测数据
        
        Returns:
            bool: 发送成功返回True，否则返回False
        \"\"\"
        try:
            # 构建URL
            url = f"http://{self.host}:{self.port}/api/v1/{access_token}/telemetry"
            
            # 记录要发送的数据
            self.logger.debug(f"准备发送遥测数据，访问令牌: {access_token}, 数据: {telemetry_data}")
            
            try:
                response = requests.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json=telemetry_data,
                    timeout=5
                )
                
                if response.status_code in [200, 201]:
                    self.logger.info(f"成功发送遥测数据到ThingsBoard, 访问令牌: {access_token}")
                    return True
                else:
                    self.logger.warning(f"发送遥测数据到ThingsBoard失败，状态码: {response.status_code}, 响应: {response.text}")
                    
                    # 备份到本地文件
                    self._backup_data_locally(access_token, telemetry_data)
                    return False
            except Exception as e:
                self.logger.warning(f"发送遥测数据到ThingsBoard时出现异常: {str(e)}")
                
                # 备份到本地文件
                self._backup_data_locally(access_token, telemetry_data)
                return False
        except Exception as e:
            self.logger.error(f"处理遥测数据发送时发生错误: {str(e)}")
            return False
    
    def _backup_data_locally(self, access_token: str, telemetry_data: Dict[str, Any]) -> None:
        \"\"\"
        将遥测数据备份到本地文件
        
        Args:
            access_token: 设备访问令牌
            telemetry_data: 遥测数据
        \"\"\"
        try:
            # 确保备份目录存在
            backup_dir = os.path.join(os.getcwd(), "telemetry_backup")
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # 构造文件名
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            token_short = access_token[-10:] if len(access_token) > 10 else access_token
            backup_file = os.path.join(backup_dir, f"telemetry_{token_short}_{timestamp}.json")
            
            # 写入数据
            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump({"token": access_token, "timestamp": time.time(), "data": telemetry_data}, f, indent=2)
            
            self.logger.info(f"已将遥测数据备份到本地文件: {backup_file}")
        except Exception as e:
            self.logger.error(f"备份遥测数据到本地文件时出错: {str(e)}")"""
    
    # 替换内容
    new_tb_content = tb_content.replace(old_send_telemetry, new_send_telemetry)
    
    # 确保导入了 os 和 json 模块
    if "import os" not in new_tb_content:
        new_tb_content = new_tb_content.replace("import requests", "import os\nimport requests")
    
    if "import json" not in new_tb_content:
        new_tb_content = new_tb_content.replace("import requests", "import json\nimport requests")
    
    if "import time" not in new_tb_content:
        new_tb_content = new_tb_content.replace("import requests", "import time\nimport requests")
    
    # 写入修改后的内容
    with open(tb_path, "w", encoding="utf-8") as f:
        f.write(new_tb_content)
    
    print("✅ 已修复ThingsBoard连接器的遥测数据发送功能")
    print("\n现在，系统将尝试实际发送数据到EdgeX和ThingsBoard平台")
    print("如果连接失败，数据将自动备份到本地文件中")

if __name__ == "__main__":
    main()