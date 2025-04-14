# 小米AIoT边缘安全防护研究平台 - Docker部署指南

## Docker环境要求

- Docker 19.03或更高版本
- Docker Compose 1.27.0或更高版本
- 至少4GB RAM和20GB磁盘空间

## 基本部署

### 1. 构建Docker镜像

在项目根目录下运行：

```bash
docker build -t xiaomi-aiot-edge-security:latest .
```

### 2. 使用Docker Compose启动所有服务

```bash
docker-compose up -d
```

这将启动以下容器：
- 小米AIoT边缘安全防护平台
- EdgeX Foundry服务
- ThingsBoard Edge服务
- MongoDB数据库
- Redis缓存

### 3. 验证部署

访问Web控制面板：http://localhost:8080

## 容器说明

`docker-compose.yml`文件定义了以下服务：

1. **xiaomi-aiot-platform**: 主平台容器
2. **edgex-core-data**: EdgeX核心数据服务
3. **edgex-core-metadata**: EdgeX元数据服务
4. **edgex-core-command**: EdgeX命令服务
5. **edgex-device-virtual**: EdgeX虚拟设备服务
6. **thingsboard-edge**: ThingsBoard Edge服务
7. **mongodb**: MongoDB数据库
8. **redis**: Redis缓存

## 自定义配置

### 修改端口映射

如果默认端口有冲突，可以修改`docker-compose.yml`中的端口映射：

```yaml
services:
  xiaomi-aiot-platform:
    ports:
      - "9090:8080"  # 将8080改为9090
```

### 使用环境变量文件

创建`.env`文件设置环境变量：

```
XIAOMI_AIOT_PLATFORM__WEB_PORT=8080
XIAOMI_AIOT_EDGEX__HOST=edgex-core-data
XIAOMI_AIOT_THINGSBOARD__HOST=thingsboard-edge
```

然后在启动时引用：

```bash
docker-compose --env-file .env up -d
```

## 持久化数据

默认情况下，数据存储在Docker卷中。可以修改`docker-compose.yml`将数据映射到主机目录：

```yaml
services:
  mongodb:
    volumes:
      - ./data/mongodb:/data/db
  
  redis:
    volumes:
      - ./data/redis:/data
      
  xiaomi-aiot-platform:
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
```

## 分布式部署

### 多主机部署

对于跨多台主机的部署，可以使用Docker Swarm或Kubernetes：

#### Docker Swarm部署

1. 初始化Swarm集群：

```bash
docker swarm init
```

2. 创建`docker-stack.yml`文件：

```yaml
version: '3.8'

services:
  xiaomi-aiot-platform:
    image: xiaomi-aiot-edge-security:latest
    deploy:
      replicas: 2
    ports:
      - "8080:8080"
    networks:
      - aiot-network
      
  edgex-services:
    image: edgexfoundry/docker-edgex-no-secty:2.0.0
    deploy:
      replicas: 1
    ports:
      - "48080:48080"
    networks:
      - aiot-network
      
  thingsboard-edge:
    image: thingsboard/tb-edge:latest
    deploy:
      replicas: 1
    ports:
      - "8080:8080"
      - "1883:1883"
    networks:
      - aiot-network
      
networks:
  aiot-network:
    driver: overlay
```

3. 部署堆栈：

```bash
docker stack deploy -c docker-stack.yml xiaomi-aiot
```

## 资源限制

为容器设置资源限制：

```yaml
services:
  xiaomi-aiot-platform:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## 日志管理

### 查看容器日志

```bash
docker-compose logs -f xiaomi-aiot-platform
```

### 配置日志驱动

```yaml
services:
  xiaomi-aiot-platform:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 故障排除

### 容器无法启动

检查日志：

```bash
docker-compose logs xiaomi-aiot-platform
```

### 网络连接问题

检查网络：

```bash
docker network inspect xiaomi-aiot-edge-security_default
```

### 资源不足

检查资源使用情况：

```bash
docker stats
```

## 更新部署

更新到新版本：

```bash
# 拉取最新代码
git pull

# 重新构建镜像
docker-compose build

# 更新服务
docker-compose up -d
```

## 备份和恢复

### 备份数据

```bash
# 备份MongoDB数据
docker run --rm --volumes-from xiaomi-aiot-edge-security_mongodb_1 -v $(pwd)/backup:/backup ubuntu tar cvf /backup/mongodb-backup.tar /data/db

# 备份平台数据
docker run --rm --volumes-from xiaomi-aiot-edge-security_xiaomi-aiot-platform_1 -v $(pwd)/backup:/backup ubuntu tar cvf /backup/platform-backup.tar /app/data
```

### 恢复数据

```bash
# 恢复MongoDB数据
docker run --rm --volumes-from xiaomi-aiot-edge-security_mongodb_1 -v $(pwd)/backup:/backup ubuntu bash -c "cd / && tar xvf /backup/mongodb-backup.tar"

# 恢复平台数据
docker run --rm --volumes-from xiaomi-aiot-edge-security_xiaomi-aiot-platform_1 -v $(pwd)/backup:/backup ubuntu bash -c "cd / && tar xvf /backup/platform-backup.tar"
```