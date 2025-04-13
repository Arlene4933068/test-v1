# 小米AIoT边缘安全防护研究平台 - 使用指南

## 平台简介

小米AIoT边缘安全防护研究平台是一个用于研究和测试边缘计算环境中智能设备安全性的综合平台。该平台通过模拟多种小米AIoT设备，结合EdgeX Foundry和ThingsBoard Edge等边缘计算平台，实现了多样化的安全防护场景模拟和分析功能。

## 平台组件

平台由以下主要组件构成：

1. **设备模拟器** - 模拟各类边缘设备，包括网关、路由器、小爱音箱和摄像头
2. **平台连接器** - 与EdgeX Foundry和ThingsBoard Edge平台的接口
3. **安全防护模块** - 实现对设备的安全监测和防护
4. **数据分析模块** - 收集和分析安全事件和性能数据
5. **控制面板** - 提供图形化界面管理平台

## 基本使用流程

### 1. 启动平台

平台可以通过以下方式启动：

```bash
# 使用启动脚本
bash scripts/start_simulation.sh

# 或者手动启动
python -m src.dashboard.app
```

启动后，控制面板将在 http://localhost:5000 可访问。

### 2. 创建和管理设备

#### 2.1 通过Web界面创建设备

1. 打开控制面板，导航至"设备管理"页面
2. 点击"添加设备"按钮
3. 填写设备信息：
   - 设备类型（网关、路由器、小爱音箱或摄像头）
   - 设备名称（可选）
   - 平台选择（EdgeX或ThingsBoard）
4. 点击"创建"按钮

#### 2.2 通过API创建设备

```python
import requests

# 创建网关设备
response = requests.post('http://localhost:5000/api/devices', json={
    'device_type': 'gateway',
    'device_name': 'my_gateway',
    'platform': 'edgex'
})

device_id = response.json()['device_id']
print(f"创建的设备ID: {device_id}")
```

#### 2.3 通过Python代码创建设备

```python
from src.device_simulator.gateway import GatewaySimulator
from src.platform_connector.edgex_connector import EdgeXConnector

# 创建EdgeX连接器
edgex = EdgeXConnector()

# 创建网关设备
gateway = GatewaySimulator(device_name="my_gateway")

# 连接到EdgeX
gateway.connect(edgex)

# 启动设备模拟
gateway.start()
```

### 3. 配置安全防护规则

#### 3.1 通过Web界面配置

1. 导航至"安全配置"页面
2. 选择要配置的设备
3. 启用/禁用所需的安全规则
4. 调整规则参数
5. 点击"保存配置"按钮

#### 3.2 通过配置文件配置

编辑 `config/security.yaml` 文件：

```yaml
security:
  rules:
    ddos_protection:
      enabled: true
      threshold: 100
      time_window: 60
    mitm_protection:
      enabled: true
      cert_verification: true
    firmware_protection:
      enabled: true
      verify_signature: true
    credential_protection:
      enabled: true
      password_strength: high
```

### 4. 运行安全仿真场景

平台提供多种预设的安全仿真场景：

#### 4.1 DDoS攻击模拟

```bash
python -m src.security.scenarios.ddos_simulation
```

#### 4.2 中间人攻击模拟

```bash
python -m src.security.scenarios.mitm_simulation
```

#### 4.3 固件篡改攻击模拟

```bash
python -m src.security.scenarios.firmware_tampering
```

#### 4.4 凭证攻击模拟

```bash
python -m src.security.scenarios.credential_attack
```

### 5. 分析安全事件和性能数据

#### 5.1 通过Web界面查看数据

1. 导航至"数据分析"页面
2. 选择分析时间范围
3. 选择要查看的数据类型：
   - 攻击检测统计
   - 响应延迟
   - 资源占用
   - 防护成功率
4. 查看生成的图表和统计信息

#### 5.2 生成分析报告

```bash
# 使用脚本生成报告
bash scripts/generate_report.sh

# 或手动生成
python -m src.analytics.report_generator --output=reports/security_report.pdf
```

### 6. 自定义扩展平台

#### 6.1 添加新的设备类型

1. 在 `src/device_simulator/` 目录下创建新的设备类文件
2. 继承 `DeviceSimulatorBase` 类并实现必要的方法
3. 在 `src/device_simulator/__init__.py` 中注册新设备类型

#### 6.2 添加新的安全规则

1. 在 `src/security/rules/` 目录下创建新的规则文件
2. 继承 `SecurityRuleBase` 类并实现必要的方法
3. 在 `src/security/rules/__init__.py` 中注册新规则

## 进阶使用

### 多设备协同仿真

```python
from src.device_simulator.gateway import GatewaySimulator
from src.device_simulator.camera import CameraSimulator
from src.device_simulator.speaker import SpeakerSimulator
from src.platform_connector.edgex_connector import EdgeXConnector

# 创建EdgeX连接器
edgex = EdgeXConnector()

# 创建多个设备
gateway = GatewaySimulator(device_name="living_room_gateway")
camera = CameraSimulator(device_name="front_door_camera")
speaker = SpeakerSimulator(device_name="kitchen_speaker")

# 连接到EdgeX
gateway.connect(edgex)
camera.connect(edgex)
speaker.connect(edgex)

# 启动设备模拟
gateway.start()
camera.start()
speaker.start()

# 在网关中注册摄像头和音箱
gateway.register_child_device(camera.device_id)
gateway.register_child_device(speaker.device_id)
```

### 自定义攻击场景

```python
from src.security.attack_detector import AttackDetector
from src.security.protection_engine import ProtectionEngine

# 创建攻击检测器和防护引擎
detector = AttackDetector()
protection = ProtectionEngine()

# 自定义攻击场景
def custom_attack_scenario(target_device):
    # 模拟异常流量
    for i in range(1000):
        target_device.add_message({
            "method": "setAttribute",
            "params": {
                "key": f"test_key_{i}",
                "value": f"test_value_{i}"
            }
        })
    
    # 检测攻击并应用防护
    attack_info = detector.detect_attacks(target_device)
    if attack_info:
        protection.apply_protection(target_device, attack_info)
```

### 跨平台设备集成

```python
from src.device_simulator.router import RouterSimulator
from src.platform_connector.edgex_connector import EdgeXConnector
from src.platform_connector.thingsboard_connector import ThingsBoardConnector

# 创建平台连接器
edgex = EdgeXConnector()
thingsboard = ThingsBoardConnector()

# 创建设备并连接到不同平台
router1 = RouterSimulator(device_name="router_edgex")
router1.connect(edgex)

router2 = RouterSimulator(device_name="router_thingsboard")
router2.connect(thingsboard)

# 启动设备
router1.start()
router2.start()
```

## 故障排除

### 设备连接问题

如果设备无法连接到平台：

1. 检查平台连接器配置
2. 确认平台服务正在运行
3. 查看日志文件: `logs/device_[设备类型]_[设备ID].log`

### 安全规则未触发

如果安全规则未按预期触发：

1. 检查规则配置是否正确
2. 调整规则阈值
3. 查看安全日志: `logs/security.log`

### 性能问题

如果平台性能不佳：

1. 减少同时运行的设备数量
2. 增加设备数据生成间隔
3. 检查系统资源使用情况

## 完整API参考

有关平台API的完整参考，请参阅 [API文档](api.md)。