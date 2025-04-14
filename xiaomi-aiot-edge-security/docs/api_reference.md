# 小米AIoT边缘安全防护研究平台 - API参考文档

## 目录

- [API概述](#api概述)
- [认证与授权](#认证与授权)
- [设备管理API](#设备管理api)
- [安全规则API](#安全规则api)
- [遥测数据API](#遥测数据api)
- [事件管理API](#事件管理api)
- [分析报告API](#分析报告api)
- [系统管理API](#系统管理api)
- [WebSocket API](#websocket-api)
- [错误处理](#错误处理)
- [速率限制](#速率限制)
- [SDK与客户端库](#sdk与客户端库)

## API概述

小米AIoT边缘安全防护研究平台提供了全面的RESTful API，允许开发者与平台进行交互，管理设备、配置安全规则、收集数据和生成报告。本文档详细说明了所有可用的API端点、参数和返回值。

### 基本信息

- **基础URL**: `http://localhost:8080/api/v1`
- **内容类型**: `application/json`
- **字符编码**: UTF-8
- **时间格式**: ISO 8601 (例如: `2023-04-12T14:30:00Z`)

## 认证与授权

所有API请求都需要进行认证。平台支持以下认证方式：

### JWT认证

#### 获取访问令牌

```
POST /auth/token
```

获取用于访问API的JWT令牌。

**请求体**:

```json
{
  "username": "admin",
  "password": "xiaomi123"
}
```

**响应**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### 刷新访问令牌

```
POST /auth/refresh
```

使用刷新令牌获取新的访问令牌。

**请求体**:

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**响应**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### 吊销令牌

```
POST /auth/revoke
```

吊销当前的访问令牌。

**请求头**:

```
Authorization: Bearer {access_token}
```

**响应**:

```json
{
  "message": "令牌已成功吊销"
}
```

### API密钥认证

对于服务器间通信，可以使用API密钥认证。

#### 创建API密钥

```
POST /auth/api-keys
```

创建新的API密钥。

**请求头**:

```
Authorization: Bearer {access_token}
```

**请求体**:

```json
{
  "name": "服务器集成",
  "expires_in": 2592000,  // 30天，单位：秒
  "permissions": ["read:devices", "write:telemetry"]
}
```

**响应**:

```json
{
  "api_key": "xm_api_5f9d7a8b3c1e2d4f6a9b8c7d",
  "secret": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",  // 仅在创建时返回一次
  "name": "服务器集成",
  "expires_at": "2023-05-12T14:30:00Z",
  "permissions": ["read:devices", "write:telemetry"]
}
```

#### 使用API密钥

在请求头中添加API密钥：

```
X-API-Key: xm_api_5f9d7a8b3c1e2d4f6a9b8c7d:a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

## 设备管理API

### 获取所有设备

```
GET /devices
```

获取所有模拟设备的列表。

**请求头**:

```
Authorization: Bearer {access_token}
```

**查询参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| type | string | 可选。按设备类型筛选（gateway, camera, speaker, router） |
| platform | string | 可选。按平台筛选（edgex, thingsboard） |
| status | string | 可选。按状态筛选（running, stopped, error） |
| page | integer | 可选。页码，默认为1 |
| per_page | integer | 可选。每页记录数，默认为20，最大为100 |

**响应**:

```json
{
  "devices": [
    {
      "id": "gateway-001",
      "name": "客厅网关",
      "type": "gateway",
      "status": "running",
      "platform": "edgex",
      "connected": true,
      "properties": {
        "model": "xiaomi-gateway-v3",
        "firmware": "1.4.6_0012",
        "location": "living_room"
      },
      "created_at": "2023-04-12T10:30:00Z",
      "last_active": "2023-04-12T14:25:00Z"
    },
    {
      "id": "camera-001",
      "name": "门口摄像头",
      "type": "camera",
      "status": "running",
      "platform": "thingsboard",
      "connected": true,
      "properties": {
        "model": "xiaomi-camera-1080p",
        "firmware": "2.1.9_0045",
        "location": "entrance"
      },
      "created_at": "2023-04-11T15:45:00Z",
      "last_active": "2023-04-12T14:20:00Z"
    }
  ],
  "pagination": {
    "total": 45,
    "page": 1,
    "per_page": 20,
    "pages": 3
  }
}
```

### 获取单个设备

```
GET /devices/{device_id}
```

获取特定设备的详细信息。

**请求头**:

```
Authorization: Bearer {access_token}
```

**响应**:

```json
{
  "id": "gateway-001",
  "name": "客厅网关",
  "type": "gateway",
  "status": "running",
  "platform": "edgex",
  "connected": true,
  "properties": {
    "model": "xiaomi-gateway-v3",
    "firmware": "1.4.6_0012",
    "location": "living_room",
    "manufacturer": "Xiaomi",
    "serial_number": "SN12345678",
    "hardware_version": "3.0"
  },
  "telemetry": {
    "temperature": 24.5,
    "humidity": 60,
    "connected_devices": 5,
    "cpu_usage": 12.3,
    "memory_usage": 256.4,
    "network_status": "online"
  },
  "created_at": "2023-04-12T10:30:00Z",
  "last_active": "2023-04-12T14:25:00Z"
}
```

### 创建设备

```
POST /devices
```

创建新的模拟设备。

**请求头**:

```
Authorization: Bearer {access_token}
```

**请求体**:

```json
{
  "id": "speaker-002",  // 可选，如不提供则自动生成
  "name": "卧室音箱",
  "type": "speaker",
  "platform": "thingsboard",
  "properties": {
    "model": "xiaomi-speaker-pro",
    "firmware": "3.2.1_0078",
    "location": "bedroom"
  }
}
```

**响应**:

```json
{
  "id": "speaker-002",
  "name": "卧室音箱",
  "type": "speaker",
  "status": "initialized",
  "platform": "thingsboard",
  "connected": false,
  "properties": {
    "model": "xiaomi-speaker-pro",
    "firmware": "3.2.1_0078",
    "location": "bedroom"
  },
  "created_at": "2023-04-12T14:30:00Z"
}
```

### 更新设备

```
PUT /devices/{device_id}
```

更新现有设备的配置。

**请求头**:

```
Authorization: Bearer {access_token}
```

**请求体**:

```json
{
  "name": "主卧音箱",
  "properties": {
    "location": "master_bedroom",
    "firmware": "3.2.2_0080"
  }
}
```

**响应**:

```json
{
  "id": "speaker-002",
  "name": "主卧音箱",
  "type": "speaker",
  "status": "running",
  "platform": "thingsboard",
  "connected": true,
  "properties": {
    "model": "xiaomi-speaker-pro",
    "firmware": "3.2.2_0080",
    "location": "master_bedroom"
  },
  "updated_at": "2023-04-12T14:35:00Z"
}
```

### 删除设备

```
DELETE /devices/{device_id}
```

删除一个模拟设备。

**请求头**:

```
Authorization: Bearer {access_token}
```

**响应**:

```json
{
  "success": true,
  "message": "设备已成功删除"
}
```

### 设备控制

```
POST /devices/{device_id}/control
```

控制设备的操作。

**请求头**:

```
Authorization: Bearer {access_token}
```

**请求体**:

```json
{
  "action": "start",  // 可选值: start, stop, restart, reboot, update_firmware
  "params": {
    "firmware_version": "3.2.3_0085"  // 如果action是update_firmware，需要提供此参数
  }
}
```

**响应**:

```json
{
  "success": true,
  "device_id": "speaker-002",
  "action": "start",
  "status": "running",
  "timestamp": "2023-04-12T14:40:00Z"
}
```

### 批量设备操作

```
POST /devices/batch
```

对多个设备执行批量操作。

**请求头**:

```
Authorization: Bearer {access_token}
```

**请求体**:

```json
{
  "device_ids": ["speaker-001", "speaker-002", "speaker-003"],
  "action": "restart"
}
```

**响应**:

```json
{
  "success": true,
  "results": [
    {
      "device_id": "speaker-001",
      "success": true,
      "status": "restarting"
    },
    {
      "device_id": "speaker-002",
      "success": true,
      "status": "restarting"
    },
    {
      "device_id": "speaker-003",
      "success": false,
      "error": "设备未连接",
      "status": "error"
    }
  ],
  "timestamp": "2023-04-12T14:45:00Z"
}
```

## 安全规则API

### 获取所有安全规则

```
GET /security/rules
```

获取所有可用的安全规则。

**请求头**:

```
Authorization: Bearer {access_token}
```

**查询参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| enabled | boolean | 可选。按启用状态筛选 |
| category | string | 可选。按类别筛选（data_anomaly, authentication, command_injection等） |

**响应**:

```json
{
  "rules": [
    {
      "id": "data_anomaly_rule",
      "name": "数据异常检测",
      "description": "检测设备遥测数据中的异常变化",
      "category": "data_anomaly",
      "enabled": true,
      "parameters": {
        "threshold": 10.0,
        "time_window": 300
      },
      "created_at": "2023-04-10T09:00:00Z",
      "updated_at": "2023-04-11T11:30:00Z"
    },
    {
      "id": "authentication_failure_rule",
      "name": "认证失败检测",
      "description": "检测多次认证失败尝试",
      "category": "authentication",
      "enabled": true,
      "parameters": {
        "max_attempts": 5,
        "time_window": 600
      },
      "created_at": "2023-04-10T09:05:00Z",
      "updated_at": "2023-04-11T11:35:00Z"
    },
    {
      "id": "command_injection_rule",
      "name": "命令注入检测",
      "description": "检测命令中的注入攻击模式",
      "category": "command_injection",
      "enabled": true,
      "parameters": {
        "patterns": ["rm -rf", ";\\s*", "&&\\s*"]
      },
      "created_at": "2023-04-10T09:10:00Z",
      "updated_at": "2023-04-11T11:40:00Z"
    }
  ]
}
```

### 获取单个安全规则

```
GET /security/rules/{rule_id}
```

获取特定安全规则的详细信息。

**请求头**:

```
Authorization: Bearer {access_token}
```

**响应**:

```json
{
  "id": "data_anomaly_rule",
  "name": "数据异常检测",
  "description": "检测设备遥测数据中的异常变化",
  "category": "data_anomaly",
  "enabled": true,
  "parameters": {
    "threshold": 10.0,
    "time_window": 300
  },
  "created_at": "2023-04-10T09:00:00Z",
  "updated_at": "2023-04-11T11:30:00Z",
  "stats": {
    "total_evaluations": 12500,
    "triggered_count": 23,
    "last_triggered": "2023-04-12T13:45:00Z"
  }
}
```

### 创建安全规则

```
POST /security/rules
```

创建新的安全规则。

**请求头**:

```
Authorization: Bearer {access_token}
```

**请求体**:

```json
{
  "id": "network_scan_rule",  // 可选，如不提供则自动生成
  "name": "网络扫描检测",
  "description": "检测针对设备的网络端口扫描活动",
  "category": "network_attack",
  "enabled": true,
  "parameters": {
    "scan_threshold": 10,
    "time_window": 60,
    "port_range": "1-1024"
  }
}
```

**响应**:

```json
{
  "id": "network_scan_rule",
  "name": "网络扫描检测",
  "description": "检测针对设备的网络端口扫描活动",
  "category": "network_attack",
  "enabled": true,
  "parameters": {
    "scan_threshold": 10,
    "time_window": 60,
    "port_range": "1-1024"
  },
  "created_at": "2023-04-12T15:00:00Z"
}
```

### 更新安全规则

```
PUT /security/rules/{rule_id}
```

更新现有安全规则的配置。

**请求头**:

```
Authorization: Bearer {access_token}
```

**请求体**:

```json
{
  "name": "高级网络扫描检测",
  "enabled": true,
  "parameters": {
    "scan_threshold": 5,
    "time_window": 30,
    "port_range": "1-65535"
  }
}
```

**响应**:

```json
{
  "id": "network_scan_rule",
  "name": "高级网络扫描检测",
  "description": "检测针对设备的网络端口扫描活动",
  "category": "network_attack",
  "enabled": true,
  "parameters": {
    "scan_threshold": 5,
    "time_window": 30,
    "port_range": "1-65535"
  },
  "created_at": "2023-04-12T15:00:00Z",
  "updated_at": "2023-04-12T15:10:00Z"
}
```

### 删除安全规则

```
DELETE /security/rules/{rule_id}
```

删除一个安全规则。

**请求头**:

```
Authorization: Bearer {access_token}
```

**响应**:

```json
{
  "success": true,
  "message": "安全规则已成功删除"
}
```

### 应用安全规则到设备

```
POST /security/apply
```

将安全规则应用到特定设备或设备组。

**请求头**:

```
Authorization: Bearer {access_token}
```

**请求体**:

```json
{
  "rule_ids": ["data_anomaly_rule", "network_scan_rule"],
  "device_ids": ["gateway-001", "gateway-002"],
  "device_types": ["gateway"],  // 可选，应用到特定类型的所有设备
  "override_parameters": {  // 可选，覆盖规则默认参数
    "data_anomaly_rule": {
      "threshold": 15.0
    }
  }
}
```

**响应**:

```json
{
  "success": true,
  "applied_count": 2,
  "details": [
    {
      "device_id": "gateway-001",
      "rules_applied": ["data_anomaly_rule", "network_scan_rule"]
    },
    {
      "device_id": "gateway-002",
      "rules_applied": ["data_anomaly_rule", "network_scan_rule"]
    }
  ]
}
```

## 遥测数据API

### 获取设备遥测数据

```
GET /telemetry/devices/{device_id}
```

获取特定设备的遥测数据历史。

**请求头**:

```
Authorization: Bearer {access_token}
```

**查询参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| start_time | string | 可选。开始时间（ISO 8601格式） |
| end_time | string | 可选。结束时间（ISO 8601格式） |
| metrics | string | 可选。要获取的指标，逗号分隔（例如：temperature,humidity） |
| interval | string | 可选。数据聚合间隔（raw, 1m, 5m, 1h, 1d） |
| limit | integer | 可选。返回记录的最大数量，默认100 |

**响应**:

```json
{
  "device_id": "gateway-001",
  "start_time": "2023-04-12T14:00:00Z",
  "end_time": "2023-04-12T15:00:00Z",
  "interval": "5m",
  "metrics": ["temperature", "humidity", "connected_devices"],
  "data": [
    {
      "timestamp": "2023-04-12T14:00:00Z",
      "temperature": 24.2,
      "humidity": 58,
      "connected_devices": 4
    },
    {
      "timestamp": "2023-04-12T14:05:00Z",
      "temperature": 24.5,
      "humidity": 59,
      "connected_devices": 4
    },
    {
      "timestamp": "2023-04-12T14:10:00Z",
      "temperature": 24.8,
      "humidity": 60,
      "connected_devices": 5
    }
    // 更多数据点...
  ],
  "total": 13
}
```

### 发送设备遥测数据

```
POST /telemetry/devices/{device_id}
```

向特定设备发送遥测数据。

**请求头**:

```
Authorization: Bearer {access_token}
```

**请求体**:

```json
{
  "timestamp": "2023-04-12T15:15:00Z",  // 可选，默认为当前时间
  "data": {
    "temperature": 25.3,
    "humidity": 62,
    "connected_devices": 6,
    "cpu_usage": 15.2,
    "memory_usage": 278.6
  }
}
```

**响应**:

```json
{
  "success": true,
  "device_id": "gateway-001",
  "timestamp": "2023-04-12T15:15:00Z",
  "processed_at": "2023-04-12T15:15:01Z"
}
```

### 批量发送遥测数据

```
POST /telemetry/batch
```

批量发送多个设备的遥测数据。

**请求头**:

```
Authorization: Bearer {access_token}
```

**请求体**:

```json
{
  "devices": [
    {
      "device_id": "gateway-001",
      "timestamp": "2023-04-12T15:20:00Z",
      "data": {
        "temperature": 25.5,
        "humidity": 63,
        "connected_devices": 6
      }
    },
    {
      "device_id": "camera-001",
      "timestamp": "2023-04-12T15:20:00Z",
      "data": {
        "motion_detected": true,
        "light_level": 75
      }
    }
  ]
}
```

**响应**:

```json
{
  "success": true,
  "processed": 2,
  "failed": 0,
  "processed_at": "2023-04-12T15:20:01Z"
}
```

### 获取遥测统计数据

```
GET /telemetry/stats
```

获取遥测数据的统计信息。

**请求头**:

```
Authorization: Bearer {access_token}
```

**查询参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| device_id | string | 可选。特定设备ID |
| device_type | string | 可选。设备类型 |
| metric | string | 必需。要统计的指标 |
| start_time | string | 可选。开始时间（ISO 8601格式） |
| end_time | string | 可选。结束时间（ISO 8601格式） |
| function | string | 可选。统计函数（avg, min, max, sum, count），默认为avg |

**响应**:

```json
{
  "metric": "temperature",
  "device_type": "gateway",
  "start_time": "2023-04-12T00:00:00Z",
  "end_time": "2023-04-12T23:59:59Z",
  "function": "avg",
  "value": 24.