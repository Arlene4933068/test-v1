# 小米AIoT边缘安全防护研究平台 - 架构说明

## 核心架构层次
### 1. 设备模拟层

设备模拟层负责模拟各类AIoT边缘设备的行为和数据，是整个平台的基础。

#### 设计特点

- **状态管理**: 每个设备维护自身的状态信息
- **数据生成**: 根据设备特性生成仿真遥测数据
- **消息处理**: 处理来自平台的控制消息
- **事件触发**: 模拟设备事件和异常情况

#### 主要组件

- **设备模拟器基类 (DeviceSimulatorBase)**: 所有设备模拟器的基础类，提供通用功能
- **网关模拟器 (GatewaySimulator)**: 模拟小米网关设备
- **路由器模拟器 (RouterSimulator)**: 模拟智能路由器设备
- **小爱音箱模拟器 (SpeakerSimulator)**: 模拟小爱音箱设备（蓝牙网关）
- **摄像头模拟器 (CameraSimulator)**: 模拟智能摄像头设备

### 2. 平台连接层

平台连接层负责与边缘计算平台（EdgeX Foundry和ThingsBoard Edge）进行通信，将模拟设备集成到这些平台中。

#### 主要组件

- **连接器基类 (ConnectorBase)**: 所有平台连接器的基础类
- **EdgeX连接器 (EdgeXConnector)**: 与EdgeX Foundry平台通信
- **ThingsBoard连接器 (ThingsBoardConnector)**: 与ThingsBoard Edge平台通信

#### 设计特点

- **协议适配**: 适配不同平台的通信协议
- **设备注册**: 自动向平台注册设备
- **数据传输**: 发送遥测数据和接收控制命令
- **服务发现**: 动态发现平台服务

### 3. 安全防护层

安全防护层是平台的核心，负责实现对边缘设备的安全监测和防护功能。

#### 主要组件

- **攻击检测器 (AttackDetector)**: 检测针对设备的各类攻击
- **防护引擎 (ProtectionEngine)**: 实施防护措施
- **安全规则模块**: 包含各类安全防护规则
  - DDoS防护规则
  - 中间人攻击防护规则
  - 固件攻击防护规则
  - 凭证攻击防护规则
- **安全日志记录器 (SecurityLogger)**: 记录安全事件

#### 设计特点

- **规则引擎**: 基于规则的安全检测和防护
- **实时监控**: 实时监控设备状态和通信
- **异常检测**: 基于统计和模式识别的异常检测
- **防护措施**: 自动应用防护措施

### 4. 分析层

分析层负责收集、处理和分析平台产生的数据，为安全研究提供支持。

#### 主要组件

- **数据收集器 (DataCollector)**: 收集设备和安全事件数据
- **统计分析器 (StatisticalAnalyzer)**: 进行数据统计和分析
- **报告生成器 (ReportGenerator)**: 生成分析报告

#### 设计特点

- **时序数据分析**: 分析随时间变化的安全事件
- **性能指标评估**: 评估防护措施的性能
- **可视化**: 生成数据可视化图表
- **报告导出**: 支持多种格式的报告导出

### 5. 控制与展示层

控制与展示层提供用户界面，用于管理平台和查看数据。

#### 主要组件

- **Web应用 (app.py)**: Flask Web应用程序
- **设备管理器 (DeviceManager)**: 管理设备
- **安全配置 (SecurityConfig)**: 配置安全规则
- **数据可视化 (Visualization)**: 可视化数据和报告

#### 设计特点

- **直观界面**: 提供直观的用户界面
- **实时监控**: 实时显示设备状态和安全事件
- **配置管理**: 可视化配置管理
- **数据展示**: 交互式数据可视化

## 设计模式应用

平台采用多种设计模式优化架构：

### 1. 工厂模式

用于创建不同类型的设备模拟器和连接器。

```python
class DeviceFactory:
    @staticmethod
    def create_device(device_type, **kwargs):
        if device_type == "gateway":
            return GatewaySimulator(**kwargs)
        elif device_type == "router":
            return RouterSimulator(**kwargs)
        elif device_type == "speaker":
            return SpeakerSimulator(**kwargs)
        elif device_type == "camera":
            return CameraSimulator(**kwargs)
        else:
            raise ValueError(f"不支持的设备类型: {device_type}")
```

### 2. 观察者模式

用于设备状态变化通知和安全事件传播。

```python
class EventManager:
    def __init__(self):
        self.subscribers = {}
    
    def subscribe(self, event_type, callback):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type, callback):
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(callback)
    
    def notify(self, event_type, data):
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                callback(data)
```

### 3. 策略模式

用于安全规则的实现和应用。

```python
class SecurityRule(ABC):
    @abstractmethod
    def evaluate(self, context):
        pass
    
    @abstractmethod
    def apply_protection(self, device, attack_info):
        pass

class DDoSProtectionRule(SecurityRule):
    def evaluate(self, context):
        # DDoS攻击检测逻辑
        pass
    
    def apply_protection(self, device, attack_info):
        # DDoS防护措施
        pass
```

### 4. 装饰器模式

用于增强设备模拟器和安全功能。

```python
def log_security_event(method):
    def wrapper(self, *args, **kwargs):
        result = method(self, *args, **kwargs)
        # 记录安全事件
        return result
    return wrapper

class ProtectionEngine:
    @log_security_event
    def apply_protection(self, device, attack_info):
        # 应用防护措施
        pass
```

## 工具与辅助组件

### 工具类

- **配置管理 (ConfigManager)**: 管理系统配置
- **日志工具 (Logger)**: 提供日志功能
- **加密工具 (Crypto)**: 提供加密和安全功能
- **协议处理 (Protocol)**: 处理通信协议

### 配置文件

- **simulator.yaml**: 设备模拟器配置
- **edgex.yaml**: EdgeX连接配置
- **thingsboard.yaml**: ThingsBoard连接配置
- **security.yaml**: 安全防护配置
- **logging.yaml**: 日志配置

## 分布式架构
### 部署模型

1. **单机部署**: 所有组件在一台机器上运行
2. **分布式部署**: 组件分布在多个节点
   - 设备模拟器可以分布在多个节点
   - EdgeX和ThingsBoard可以单独部署
   - 安全防护和分析组件可以独立部署

### 通信机制

1. **基于HTTP/HTTPS的RESTful API**: 用于组件间通信
2. **基于MQTT的消息队列**: 用于设备数据传输
3. **WebSocket**: 用于实时数据更新

## 扩展性设计

平台提供多种扩展点：

1. **新设备类型**: 通过继承DeviceSimulatorBase添加
2. **新平台连接器**: 通过继承ConnectorBase添加
3. **新安全规则**: 通过继承SecurityRule添加
4. **新分析方法**: 通过扩展StatisticalAnalyzer添加

## 可测试性

平台设计了完善的测试框架：

1. **单元测试**: 测试各个组件的功能
2. **集成测试**: 测试组件之间的交互
3. **系统测试**: 测试整个系统的功能
4. **性能测试**: 测试系统的性能和负载能力