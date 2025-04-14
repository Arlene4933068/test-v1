# 小米AIoT边缘安全防护研究平台 - 配置指南

## 配置文件格式

平台使用YAML格式的配置文件，主配置文件位于`config/config.yaml`：

```yaml
# 平台基本配置
platform:
  name: "小米AIoT边缘安全防护研究平台"
  version: "1.0.0"
  log_level: "INFO"
  web_port: 8080
  admin_username: "admin"
  admin_password: "xiaomi123"

# 设备模拟器配置
simulators:
  gateway:
    count: 2
    properties:
      model: "xiaomi-gateway-v3"
      firmware: "1.4.6_0012"
  camera:
    count: 3
    properties:
      model: "xiaomi-camera-1080p"
      firmware: "2.1.9_0045"
  speaker:
    count: 2
    properties:
      model: "xiaomi-speaker-pro"
      firmware: "3.2.1_0078"
  router:
    count: 1
    properties:
      model: "xiaomi-router-ax6000"
      firmware: "1.2.7_0034"

# EdgeX连接配置
edgex:
  enabled: true
  host: "localhost"
  port: 48080
  device_service_name: "xiaomi-device-service"

# ThingsBoard连接配置
thingsboard:
  enabled: true
  host: "localhost"
  port: 8080
  access_token: "A1_TEST_TOKEN"

# 安全防护配置
security:
  rules:
    - id: "data_anomaly"
      enabled: true
      threshold: 10.0
    - id: "authentication_failure"
      enabled: true
      max_attempts: 5
    - id: "command_injection"
      enabled: true
      patterns: ["rm -rf", ";\s*", "&&\s*"]
  
# 分析模块配置
analytics:
  storage_path: "./data/analytics"
  report_interval: 3600  # 秒
```

## 环境变量配置

平台支持通过环境变量覆盖配置文件中的设置，环境变量命名规则为：`XIAOMI_AIOT_`前缀加上配置路径，路径中的点和下划线用双下划线替代。

例如：

| 配置项 | 环境变量 |
|-------|----------|
| platform.web_port | XIAOMI_AIOT_PLATFORM__WEB_PORT |
| edgex.host | XIAOMI_AIOT_EDGEX__HOST |
| security.rules[0].threshold | XIAOMI_AIOT_SECURITY__RULES__0__THRESHOLD |

### 环境变量使用示例

Windows:
```cmd
set XIAOMI_AIOT_PLATFORM__WEB_PORT=9090
set XIAOMI_AIOT_EDGEX__HOST=192.168.1.100
python run_simulation.py
```

Linux/macOS:
```bash
export XIAOMI_AIOT_PLATFORM__WEB_PORT=9090
export XIAOMI_AIOT_EDGEX__HOST=192.168.1.100
python run_simulation.py
```

## 配置文件加载优先级

1. 默认配置
2. 配置文件 (`config/config.yaml`)
3. 环境变量
4. 命令行参数

这意味着命令行参数会覆盖环境变量，环境变量会覆盖配置文件中的设置。