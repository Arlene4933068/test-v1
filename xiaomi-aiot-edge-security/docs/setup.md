# 小米AIoT边缘安全防护研究平台 - 安装指南

## 系统要求

- **操作系统**: Linux (推荐 Ubuntu 20.04 或更高版本)，Windows 10 或 macOS 10.15+
- **Python 版本**: Python 3.8 或更高版本
- **Docker**: Docker 20.10.0 或更高版本
- **Docker Compose**: 1.29.0 或更高版本
- **硬件要求**:
  - CPU: 双核处理器或更高
  - 内存: 至少 4GB RAM
  - 磁盘空间: 至少 20GB 可用空间

## 前置条件

在安装平台之前，确保您已经在本地部署了以下环境:

1. Docker 环境
2. EdgeX Foundry (Docker 部署)
3. ThingsBoard Edge (Docker 部署)

### 验证 Docker 环境

```bash
docker --version
docker-compose --version
```

### 验证 EdgeX Foundry 和 ThingsBoard Edge 部署

确认 EdgeX Foundry 容器运行状态:

```bash
docker ps | grep edgex
```

确认 ThingsBoard Edge 容器运行状态:

```bash
docker ps | grep thingsboard
```

## 克隆仓库

```bash
git clone https://github.com/your-username/xiaomi-aiot-edge-security.git
cd xiaomi-aiot-edge-security
```

## 安装依赖

### 使用 pip 安装依赖

```bash
pip install -r requirements.txt
```

或者使用虚拟环境:

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或者
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## 配置平台

### 修改配置文件

平台使用 YAML 格式的配置文件，需要根据您的环境进行修改:

1. EdgeX Foundry 连接配置:

```bash
cp config/edgex.yaml.example config/edgex.yaml
```

根据你的 EdgeX Foundry 部署情况修改 `config/edgex.yaml`:

```yaml
edgex:
  url: http://localhost:48080  # 替换为你的 EdgeX Core Data 服务地址
  metadata_url: http://localhost:48081  # 替换为你的 EdgeX Core Metadata 服务地址
  command_url: http://localhost:48082  # 替换为你的 EdgeX Core Command 服务地址
  auth_token: ""  # 如果启用了安全功能，请设置认证令牌
```

2. ThingsBoard Edge 连接配置:

```bash
cp config/thingsboard.yaml.example config/thingsboard.yaml
```

编辑 `config/thingsboard.yaml`:

```yaml
thingsboard:
  url: http://localhost:8080  # 替换为你的 ThingsBoard Edge 地址
  username: tenant@thingsboard.org  # 替换为你的用户名
  password: tenant  # 替换为你的密码
```

3. 设备模拟器配置:

```bash
cp config/simulator.yaml.example config/simulator.yaml
```

编辑 `config/simulator.yaml` 根据需求调整设备模拟器的参数。

4. 安全防护配置:

```bash
cp config/security.yaml.example config/security.yaml
```

## 安装平台

使用提供的安装脚本:

```bash
bash scripts/setup.sh
```

或者手动安装:

```bash
python setup.py install
```

## Docker 部署 (可选)

如果您希望使用 Docker 部署整个平台:

```bash
docker-compose up -d
```

此命令将根据 `docker-compose.yml` 配置文件启动所有必要的服务。

## 验证安装

执行测试脚本验证平台是否安装成功:

```bash
python -m tests.test_simulator
python -m tests.test_connector
```

如果所有测试都通过，表示平台已成功安装。你现在可以启动平台了:

```bash
bash scripts/start_simulation.sh
```

## 常见问题解决

### EdgeX Foundry 连接问题

如果无法连接到 EdgeX Foundry:

1. 检查 EdgeX 服务是否正常运行:
   ```bash
   docker ps | grep edgex
   ```

2. 确认配置文件中的 URL 是否正确
3. 检查网络端口是否开放

### ThingsBoard Edge 连接问题

如果无法连接到 ThingsBoard Edge:

1. 检查 ThingsBoard 服务是否正常运行:
   ```bash
   docker ps | grep thingsboard
   ```

2. 尝试手动登录 ThingsBoard 网页界面验证凭据
3. 确认配置文件中的连接信息是否正确

### Python 依赖问题

如果遇到 Python 依赖相关错误:

```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Docker 网络问题

如果使用 Docker 部署时遇到网络问题:

1. 检查 Docker 网络设置:
   ```bash
   docker network ls
   ```

2. 确保平台容器与 EdgeX 和 ThingsBoard 容器在同一网络中或能够互相访问