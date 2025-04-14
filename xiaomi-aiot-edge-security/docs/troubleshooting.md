# 小米AIoT边缘安全防护研究平台 - 故障排除指南

## 常见错误及解决方案

### 1. 平台启动失败

**症状**: 运行`run_simulation.py`后，平台无法正常启动。

**可能原因及解决方案**:

- **端口冲突**:
  - 症状: 日志中出现`Address already in use`错误
  - 解决: 修改`config.yaml`中的`platform.web_port`或设置环境变量`XIAOMI_AIOT_PLATFORM__WEB_PORT`

- **配置文件错误**:
  - 症状: 日志中出现`Configuration error`或YAML解析错误
  - 解决: 检查`config/config.yaml`文件格式是否正确

- **依赖项缺失**:
  - 症状: 日志中出现`ImportError`或`ModuleNotFoundError`
  - 解决: 运行`pip install -r requirements.txt`确保所有依赖已安装

### 2. 设备模拟器连接问题

**症状**: 设备模拟器无法连接到EdgeX或ThingsBoard平台。

**可能原因及解决方案**:

- **平台未启动**:
  - 检查EdgeX或ThingsBoard服务是否正在运行
  - 运行`docker ps`查看容器状态

- **网络配置错误**:
  - 检查`config.yaml`中的主机名和端口配置
  - 确保防火墙未阻止相关端口

- **认证失败**:
  - 检查访问令牌或凭据是否正确
  - 查看平台日志中的认证错误信息

### 3. 安全规则不触发

**症状**: 模拟攻击场景，但安全规则没有触发或记录。

**可能原因及解决方案**:

- **规则未启用**:
  - 检查`config.yaml`中规则的`enabled`属性是否为`true`

- **阈值设置不当**:
  - 调整规则阈值，例如`security.rules[0].threshold`

- **日志级别过高**:
  - 将`platform.log_level`设置为`DEBUG`以查看更多信息

### 4. 性能问题

**症状**: 系统运行缓慢或资源占用过高。

**可能原因及解决方案**:

- **模拟设备过多**:
  - 减少`simulators`配置中的设备数量

- **数据生成频率过高**:
  - 调整遥测数据发送间隔

- **日志记录过于详细**:
  - 提高日志级别，减少日志输出

### 5. Docker相关问题

**症状**: Docker容器无法启动或运行异常。

**可能原因及解决方案**:

- **Docker服务未运行**:
  - 运行`sc query docker`检查Docker服务状态
  - 启动Docker服务: `net start docker`

- **端口映射冲突**:
  - 检查`docker-compose.yml`中的端口映射
  - 修改冲突端口

- **容器资源限制**:
  - 检查Docker资源分配（内存、CPU）
  - 调整`docker-compose.yml`中的资源限制

## 日志文件位置

- 平台主日志: `logs/platform.log`
- 设备模拟器日志: `logs/simulators/`
- 安全事件日志: `logs/security_events.log`
- EdgeX连接器日志: `logs/connectors/edgex.log`
- ThingsBoard连接器日志: `logs/connectors/thingsboard.log`

## 诊断命令

### 检查系统状态

```bash
python scripts/check_status.py
```

### 验证配置

```bash
python scripts/validate_config.py
```

### 测试连接

```bash
python scripts/test_connection.py --target edgex
python scripts/test_connection.py --target thingsboard
```

### 清理环境

```bash
python scripts/cleanup.py
```

## 获取支持

如果您遇到无法解决的问题，请通过以下方式获取支持：

1. 查看详细文档: `docs/`目录
2. 提交GitHub Issue: [项目Issues页面](https://github.com/xiaomi/aiot-edge-security/issues)
3. 联系开发团队: aiot-support@xiaomi.com