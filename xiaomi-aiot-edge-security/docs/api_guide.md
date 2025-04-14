# 小米AIoT边缘安全防护研究平台 - API使用指南

## 设备模拟器配置

### 基本配置示例

```python
# 配置网关设备模拟器
from src.simulators import GatewaySimulator

# 创建网关模拟器实例
gateway = GatewaySimulator(
    device_id="gateway-001",
    name="客厅网关",
    properties={
        "model": "xiaomi-gateway-v3",
        "firmware": "1.4.6_0012",
        "location": "living_room"
    }
)

# 启动模拟器
gateway.start()

# 发送遥测数据
gateway.send_telemetry({
    "temperature": 24.5,
    "humidity": 60,
    "connected_devices": 5
})

# 处理命令
gateway.on_command("reboot", lambda params: gateway.reboot())