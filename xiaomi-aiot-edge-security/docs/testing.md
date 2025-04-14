# 小米AIoT边缘安全防护研究平台 - 测试指南

## 测试框架概述

平台使用多层次测试策略确保功能正确性和系统稳定性：

1. **单元测试**: 测试各个组件的独立功能
2. **集成测试**: 测试组件之间的交互
3. **系统测试**: 测试整个系统的功能
4. **性能测试**: 测试系统的性能和负载能力

## 测试覆盖率

当前测试覆盖率目标：

| 模块 | 行覆盖率 | 分支覆盖率 |
|-----|---------|----------|
| 设备模拟器 | 90% | 85% |
| 平台连接器 | 85% | 80% |
| 安全防护 | 95% | 90% |
| 数据分析 | 80% | 75% |
| Web控制面板 | 75% | 70% |

## 运行测试

### 运行所有测试

```bash
python -m pytest
```

### 运行特定模块测试

```bash
python -m pytest tests/test_simulators.py
python -m pytest tests/test_security.py
python -m pytest tests/test_connectors.py
```

### 生成测试覆盖率报告

```bash
python -m pytest --cov=src --cov-report=html
```

覆盖率报告将生成在`htmlcov/`目录下，可以通过浏览器查看。

## 测试数据

测试使用的模拟数据位于`tests/data/`目录：

- `device_data.json`: 设备模拟数据
- `telemetry_samples.json`: 遥测数据样本
- `security_events.json`: 安全事件样本

## 测试场景

### 1. 基本功能测试

测试平台的基本功能是否正常工作：

```bash
python -m pytest tests/functional/test_basic_functions.py
```

### 2. 安全防护测试

测试安全防护功能是否能正确检测和响应攻击：

```bash
python -m pytest tests/security/test_attack_detection.py
```

### 3. 性能测试

测试系统在高负载下的性能：

```bash
python -m pytest tests/performance/test_high_load.py
```

### 4. 故障恢复测试

测试系统在组件故障时的恢复能力：

```bash
python -m pytest tests/resilience/test_failure_recovery.py
```

## 持续集成

平台使用GitHub Actions进行持续集成测试，配置文件位于`.github/workflows/tests.yml`。

每次提交代码后，CI系统会自动运行测试并生成报告。

## 编写新测试

### 单元测试示例

```python
# tests/test_device_simulator.py
import unittest
from src.simulators import GatewaySimulator

class TestGatewaySimulator(unittest.TestCase):
    def setUp(self):
        self.simulator = GatewaySimulator(
            device_id="test-gateway-001",
            name="测试网关",
            properties={"model": "test-model"}
        )
    
    def test_initialization(self):
        self.assertEqual(self.simulator.device_id, "test-gateway-001")
        self.assertEqual(self.simulator.name, "测试网关")
        self.assertEqual(self.simulator.properties["model"], "test-model")
    
    def test_telemetry_generation(self):
        telemetry = self.simulator.generate_telemetry()
        self.assertIn("temperature", telemetry)
        self.assertIn("humidity", telemetry)
        self.assertIn("connected_devices", telemetry)
    
    def test_command_handling(self):
        result = self.simulator.handle_command("reboot", {})
        self.assertEqual(result["status"], "success")

if __name__ == "__main__":
    unittest.main()
```

### 集成测试示例

```python
# tests/test_security_integration.py
import unittest
from src.simulators import GatewaySimulator
from src.security import SecurityEngine, DataAnomalyRule

class TestSecurityIntegration(unittest.TestCase):
    def setUp(self):
        self.simulator = GatewaySimulator(
            device_id="test-gateway-002",
            name="测试网关2"
        )
        
        self.rule = DataAnomalyRule(threshold=5.0)
        self.engine = SecurityEngine()
        self.engine.add_rule(self.rule)
    
    def test_anomaly_detection(self):
        # 正常数据
        telemetry1 = {"temperature": 25.0, "humidity": 60}
        self.engine.process_telemetry(self.simulator.device_id, telemetry1)
        
        # 异常数据 - 温度突变
        telemetry2 = {"temperature": 35.0, "humidity": 60}
        result = self.engine.process_telemetry(self.simulator.device_id, telemetry2)
        
        self.assertTrue(result)
        self.assertEqual(result["rule_id"], self.rule.id)
        self.assertEqual(result["device_id"], self.simulator.device_id)
        self.assertEqual(result["severity"], "high")

if __name__ == "__main__":
    unittest.main()
```