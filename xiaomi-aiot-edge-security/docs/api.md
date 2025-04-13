# 小米AIoT边缘安全防护研究平台 - API文档

## API概述

小米AIoT边缘安全防护研究平台提供了一组RESTful API，用于管理设备、配置安全规则、收集数据和生成报告。所有API都遵循RESTful设计原则，使用JSON作为数据交换格式。

## 基本信息

- **基础URL**: `http://localhost:5000/api`
- **认证方式**: Bearer Token (JWT)
- **响应格式**: JSON
- **时间格式**: ISO 8601 (例如: `2025-04-12T14:30:00Z`)

## 认证API

### 获取令牌

```
POST /auth/token
```

获取用于访问API的JWT令牌。

**请求体**:

```json
{
  "username": "admin",
  "password": "password"
}
```

**响应**:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": "2025-04-13T14:30:00Z"
}
```

## 设备管理API

### 获取所有设备

```
GET /devices
```

获取所有模拟设备的列表。

**请求头**:

```
Authorization: Bearer {token}
```

**查询参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| device_type | string | 可选。按设备类型筛选（gateway, router, speaker, camera） |
| platform | string | 可选。按平台筛选（edgex, thingsboard） |
| status | string | 可选。按状态筛选（running, stopped, error等） |

**响应**:

```json
{
  "devices": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "gateway_550e8400",
      "type": "gateway",
      "status": "running",
      "platform": "edgex",
      "connected": true,
      "created_at": "2025-04-12T10:30:00Z",
      "last_active": "2025-04-12T14:25:00Z"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "name": "camera_550e8400",
      "type": "camera",
      "status": "stopped",
      "platform": "thingsboard",
      "connected": false,
      "created_at": "2025-04-11T15:45:00Z",
      "last_active": "2025-04-12T09:10:00Z"
    }
  ],
  "total": 2
}
```

### 获取单个设备

```
GET /devices/{device_id}
```

获取特定设备的详细信息。

**请求头**:

```
Authorization: Bearer {token}
```

**响应**:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "gateway_550e8400",
  "type": "gateway",
  "status": "running",
  "platform": "edgex",
  "connected": true,
  "attributes": {
    "manufacturer": "Xiaomi",
    "model": "Xiaomi-gateway",
    "firmware_version": "1.0.0",
    "hardware_version": "1.0.0",
    "serial_number": "550e8400-e29b-41d4-a716-446655440000"
  },
  "telemetry": {
    "cpu_usage": 12.5,
    "memory_usage": 256.4,
    "temperature": 42.3,
    "network_status": "online",
    "connected_devices": 3
  },
  "created_at": "2025-04-12T10:30:00Z",
  "last_active": "2025-04-12T14:25:00Z"
}
```

### 创建设备

```
POST /devices
```

创建新的模拟设备。

**请求头**:

```
Authorization: Bearer {token}
```

**请求体**:

```json
{
  "device_type": "gateway",
  "device_name": "living_room_gateway",
  "platform": "edgex",
  "attributes": {
    "location": "living_room",
    "description": "主要的家庭网关设备"
  }
}
```

**响应**:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "name": "living_room_gateway",
  "type": "gateway",
  "status": "initialized",
  "platform": "edgex",
  "connected": false,
  "created_at": "2025-04-12T14:30:00Z"
}
```

### 更新设备

```
PUT /devices/{device_id}
```

更新现有设备的配置。

**请求头**:

```
Authorization: Bearer {token}
```

**请求体**:

```json
{
  "device_name": "updated_gateway_name",
  "attributes": {
    "location": "bedroom",
    "description": "副卧的网关设备"
  }
}
```

**响应**:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "updated_gateway_name",
  "type": "gateway",
  "status": "running",
  "platform": "edgex",
  "connected": true,
  "attributes": {
    "manufacturer": "Xiaomi",
    "model": "Xiaomi-gateway",
    "firmware_version": "1.0.0",
    "hardware_version": "1.0.0",
    "serial_number": "550e8400-e29b-41d4-a716-446655440000",
    "location": "bedroom",
    "description": "副卧的网关设备"
  },
  "updated_at": "2025-04-12T14:35:00Z"
}
```

### 删除设备

```
DELETE /devices/{device_id}
```

删除一个模拟设备。

**请求头**:

```
Authorization: Bearer {token}
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
Authorization: Bearer {token}
```

**请求体**:

```json
{
  "action": "start",  // 可选值: start, stop, restart, update_firmware
  "params": {
    "firmware_version": "1.1.0"  // 如果action是update_firmware，需要提供此参数
  }
}
```

**响应**:

```json
{
  "success": true,
  "device_id": "550e8400-e29b-41d4-a716-446655440000",
  "action": "start",
  "status": "running"
}
```

### 获取设备遥测数据

```
GET /devices/{device_id}/telemetry
```

获取设备的遥测数据历史。

**请求头**:

```
Authorization: Bearer {token}
```

**查询参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| start_time | string | 可选。开始时间（ISO 8601格式） |
| end_time | string | 可选。结束时间（ISO 8601格式） |
| limit | integer | 可选。返回记录的最大数量，默认100 |

**响应**:

```json
{
  "device_id": "550e8400-e29b-41d4-a716-446655440000",
  "telemetry": [
    {
      "timestamp": "2025-04-12T14:00:00Z",
      "cpu_usage": 10.2,
      "memory_usage": 245.8,
      "temperature": 41.5,
      "network_status": "online",
      "connected_devices": 2
    },
    {
      "timestamp": "2025-04-12T14:05:00Z",
      "cpu_usage": 12.5,
      "memory_usage": 256.4,
      "temperature": 42.3,
      "network_status": "online",
      "connected_devices": 3
    }
  ],
  "total": 2
}
```

## 安全管理API

### 获取安全规则

```
GET /security/rules
```

获取所有可用的安全规则。

**请求头**:

```
Authorization: Bearer {token}
```

**响应**:

```json
{
  "rules": [
    {
      "id": "ddos_protection",
      "name": "DDoS防护",
      "description": "检测和防护DDoS攻击",
      "enabled": true,
      "parameters": {
        "threshold": 100,
        "time_window": 60
      }
    },
    {
      "id": "mitm_protection",
      "name": "中间人攻击防护",
      "description": "检测和防护中间人攻击",
      "enabled": true,
      "parameters": {
        "cert_verification": true
      }
    },
    {
      "id": "firmware_protection",
      "name": "固件攻击防护",
      "description": "检测和防护固件篡改攻击",
      "enabled": true,
      "parameters": {
        "verify_signature": true
      }
    },
    {
      "id": "credential_protection",
      "name": "凭证攻击防护",
      "description": "检测和防护凭证攻击",
      "enabled": true,
      "parameters": {
        "password_strength": "high"
      }
    }
  ]
}
```

### 获取设备安全配置

```
GET /devices/{device_id}/security
```

获取设备的安全配置。

**请求头**:

```
Authorization: Bearer {token}
```

**响应**:

```json
{
  "device_id": "550e8400-e29b-41d4-a716-446655440000",
  "security_rules": [
    {
      "rule_id": "ddos_protection",
      "enabled": true,
      "parameters": {
        "threshold": 100,
        "time_window": 60
      }
    },
    {
      "rule_id": "mitm_protection",
      "enabled": true,
      "parameters": {
        "cert_verification": true
      }
    },
    {
      "rule_id": "firmware_protection",
      "enabled": true,
      "parameters": {
        "verify_signature": true
      }
    },
    {
      "rule_id": "credential_protection",
      "enabled": false,
      "parameters": {
        "password_strength": "medium"
      }
    }
  ]
}
```

### 更新设备安全配置

```
PUT /devices/{device_id}/security
```

更新设备的安全配置。

**请求头**:

```
Authorization: Bearer {token}
```

**请求体**:

```json
{
  "security_rules": [
    {
      "rule_id": "ddos_protection",
      "enabled": true,
      "parameters": {
        "threshold": 150,
        "time_window": 30
      }
    },
    {
      "rule_id": "credential_protection",
      "enabled": true,
      "parameters": {
        "password_strength": "high"
      }
    }
  ]
}
```

**响应**:

```json
{
  "success": true,
  "device_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "安全配置已更新"
}
```

### 获取安全事件

```
GET /security/events
```

获取安全事件列表。

**请求头**:

```
Authorization: Bearer {token}
```

**查询参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| device_id | string | 可选。按设备ID筛选 |
| rule_id | string | 可选。按规则ID筛选 |
| severity | string | 可选。按严重程度筛选（low, medium, high, critical） |
| start_time | string | 可选。开始时间（ISO 8601格式） |
| end_time | string | 可选。结束时间（ISO 8601格式） |
| limit | integer | 可选。返回记录的最大数量，默认100 |

**响应**:

```json
{
  "events": [
    {
      "id": "event-550e8400-0001",
      "device_id": "550e8400-e29b-41d4-a716-446655440000",
      "rule_id": "ddos_protection",
      "timestamp": "2025-04-12T13:45:00Z",
      "severity": "high",
      "title": "检测到DDoS攻击",
      "description": "在60秒内接收到超过150个连接请求",
      "source_ip": "192.168.1.100",
      "action_taken": "blocked_source"
    },
    {
      "id": "event-550e8400-0002",
      "device_id": "550e8400-e29b-41d4-a716-446655440001",
      "rule_id": "firmware_protection",
      "timestamp": "2025-04-12T14:05:00Z",
      "severity": "critical",
      "title": "检测到固件篡改",
      "description": "固件签名验证失败",
      "source_ip": "192.168.1.105",
      "action_taken": "prevented_update"
    }
  ],
  "total": 2
}
```

## 分析API

### 获取性能数据

```
GET /analytics/performance
```

获取系统性能数据。

**请求头**:

```
Authorization: Bearer {token}
```

**查询参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| device_id | string | 可选。按设备ID筛选 |
| metric | string | 可选。按指标类型筛选（cpu_usage, memory_usage, network_traffic, response_time） |
| start_time | string | 可选。开始时间（ISO 8601格式） |
| end_time | string | 可选。结束时间（ISO 8601格式） |
| interval | string | 可选。数据聚合间隔（minute, hour, day） |

**响应**:

```json
{
  "device_id": "550e8400-e29b-41d4-a716-446655440000",
  "metric": "cpu_usage",
  "interval": "hour",
  "data": [
    {
      "timestamp": "2025-04-12T12:00:00Z",
      "value": 10.5,
      "min": 5.2,
      "max": 15.7,
      "avg": 9.8
    },
    {
      "timestamp": "2025-04-12T13:00:00Z",
      "value": 12.3,
      "min": 8.1,
      "max": 18.5,
      "avg": 11.7
    },
    {
      "timestamp": "2025-04-12T14:00:00Z",
      "value": 15.2,
      "min": 9.3,
      "max": 22.1,
      "avg": 14.3
    }
  ]
}
```

### 获取安全统计数据

```
GET /analytics/security
```

获取安全相关的统计数据。

**请求头**:

```
Authorization: Bearer {token}
```

**查询参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| start_time | string | 可选。开始时间（ISO 8601格式） |
| end_time | string | 可选。结束时间（ISO 8601格式） |
| group_by | string | 可选。分组方式（device, rule, severity, action） |

**响应**:

```json
{
  "period": {
    "start": "2025-04-05T00:00:00Z",
    "end": "2025-04-12T23:59:59Z"
  },
  "group_by": "rule",
  "stats": [
    {
      "rule_id": "ddos_protection",
      "attacks_detected": 152,
      "attacks_prevented": 145,
      "prevention_rate": 95.4,
      "avg_response_time": 250,
      "severity_distribution": {
        "low": 25,
        "medium": 78,
        "high": 42,
        "critical": 7
      }
    },
    {
      "rule_id": "mitm_protection",
      "attacks_detected": 23,
      "attacks_prevented": 23,
      "prevention_rate": 100.0,
      "avg_response_time": 180,
      "severity_distribution": {
        "low": 0,
        "medium": 5,
        "high": 15,
        "critical": 3
      }
    },
    {
      "rule_id": "firmware_protection",
      "attacks_detected": 8,
      "attacks_prevented": 8,
      "prevention_rate": 100.0,
      "avg_response_time": 320,
      "severity_distribution": {
        "low": 0,
        "medium": 0,
        "high": 2,
        "critical": 6
      }
    },
    {
      "rule_id": "credential_protection",
      "attacks_detected": 67,
      "attacks_prevented": 65,
      "prevention_rate": 97.0,
      "avg_response_time": 120,
      "severity_distribution": {
        "low": 32,
        "medium": 25,
        "high": 10,
        "critical": 0
      }
    }
  ],
  "totals": {
    "attacks_detected": 250,
    "attacks_prevented": 241,
    "overall_prevention_rate": 96.4
  }
}
```

### 生成报告

```
POST /analytics/reports
```

生成分析报告。

**请求头**:

```
Authorization: Bearer {token}
```

**请求体**:

```json
{
  "report_type": "security_analysis",
  "title": "边缘设备安全分析报告",
  "period": {
    "start": "2025-04-05T00:00:00Z",
    "end": "2025-04-12T23:59:59Z"
  },
  "devices": ["550e8400-e29b-41d4-a716-446655440000", "550e8400-e29b-41d4-a716-446655440001"],
  "include_sections": ["attack_summary", "performance_impact", "recommendations"],
  "format": "pdf"
}
```

**响应**:

```json
{
  "success": true,
  "report_id": "report-550e8400-0001",
  "status": "generating",
  "estimated_completion": "2025-04-12T14:40:00Z"
}
```

### 获取报告状态

```
GET /analytics/reports/{report_id}
```

获取报告生成状态。

**请求头**:

```
Authorization: Bearer {token}
```

**响应**:

```json
{
  "report_id": "report-550e8400-0001",
  "title": "边缘设备安全分析报告",
  "status": "completed",
  "created_at": "2025-04-12T14:30:00Z",
  "completed_at": "2025-04-12T14:38:00Z",
  "download_url": "/api/analytics/reports/report-550e8400-0001/download"
}
```

### 下载报告

```
GET /analytics/reports/{report_id}/download
```

下载生成的报告。

**请求头**:

```
Authorization: Bearer {token}
```

**响应**:
报告文件（PDF、XLSX等）的二进制数据。

## 仿真场景API

### 获取可用仿真场景

```
GET /scenarios
```

获取可用的安全仿真场景列表。

**请求头**:

```
Authorization: Bearer {token}
```

**响应**:

```json
{
  "scenarios": [
    {
      "id": "ddos_attack",
      "name": "DDoS攻击仿真",
      "description": "模拟针对边缘设备的分布式拒绝服务攻击",
      "parameters": [
        {
          "name": "attack_duration",
          "type": "integer",
          "description": "攻击持续时间（秒）",
          "default": 300,
          "min": 60,
          "max": 3600
        },
        {
          "name": "attack_intensity",
          "type": "string",
          "description": "攻击强度",
          "default": "medium",
          "enum": ["low", "medium", "high", "extreme"]
        }
      ]
    },
    {
      "id": "mitm_attack",
      "name": "中间人攻击仿真",
      "description": "模拟针对边缘设备的中间人攻击",
      "parameters": [
        {
          "name": "target_protocol",
          "type": "string",
          "description": "目标协议",
          "default": "http",
          "enum": ["http", "mqtt", "coap", "zigbee"]
        },
        {
          "name": "cert_tampering",
          "type": "boolean",
          "description": "是否包含证书篡改",
          "default": true
        }
      ]
    },
    {
      "id": "firmware_tampering",
      "name": "固件篡改攻击仿真",
      "description": "模拟针对边缘设备的固件篡改攻击",
      "parameters": [
        {
          "name": "tampering_method",
          "type": "string",
          "description": "篡改方法",
          "default": "signature_bypass",
          "enum": ["signature_bypass", "downgrade", "malicious_code_injection"]
        }
      ]
    },
    {
      "id": "credential_attack",
      "name": "凭证攻击仿真",
      "description": "模拟针对边缘设备的凭证攻击",
      "parameters": [
        {
          "name": "attack_type",
          "type": "string",
          "description": "攻击类型",
          "default": "brute_force",
          "enum": ["brute_force", "dictionary", "replay", "phishing"]
        },
        {
          "name": "attempts",
          "type": "integer",
          "description": "尝试次数",
          "default": 100,
          "min": 10,
          "max": 1000
        }
      ]
    }
  ]
}
```

### 运行仿真场景

```
POST /scenarios/{scenario_id}/run
```

启动一个安全仿真场景。

**请求头**:

```
Authorization: Bearer {token}
```

**请求体**:

```json
{
  "target_devices": ["550e8400-e29b-41d4-a716-446655440000", "550e8400-e29b-41d4-a716-446655440001"],
  "parameters": {
    "attack_duration": 180,
    "attack_intensity": "high"
  },
  "schedule": {
    "start_time": "2025-04-12T15:00:00Z",
    "end_time": "2025-04-12T15:03:00Z"
  }
}
```

**响应**:

```json
{
  "success": true,
  "simulation_id": "sim-550e8400-0001",
  "scenario_id": "ddos_attack",
  "status": "scheduled",
  "target_devices": ["550e8400-e29b-41d4-a716-446655440000", "550e8400-e29b-41d4-a716-446655440001"],
  "schedule": {
    "start_time": "2025-04-12T15:00:00Z",
    "end_time": "2025-04-12T15:03:00Z"
  }
}
```

### 获取仿真状态

```
GET /simulations/{simulation_id}
```

获取仿真运行状态。

**请求头**:

```
Authorization: Bearer {token}
```

**响应**:

```json
{
  "simulation_id": "sim-550e8400-0001",
  "scenario_id": "ddos_attack",
  "status": "running",
  "progress": 45,
  "start_time": "2025-04-12T15:00:00Z",
  "estimated_end_time": "2025-04-12T15:03:00Z",
  "metrics": {
    "total_attacks": 85,
    "detected_attacks": 82,
    "prevented_attacks": 79,
    "avg_response_time": 145
  }
}
```

### 停止仿真

```
POST /simulations/{simulation_id}/stop
```

停止正在运行的仿真。

**请求头**:

```
Authorization: Bearer {token}
```

**响应**:

```json
{
  "success": true,
  "simulation_id": "sim-550e8400-0001",
  "status": "stopped",
  "stop_time": "2025-04-12T15:01:30Z"
}
```

### 获取仿真结果

```
GET /simulations/{simulation_id}/results
```

获取仿真的结果数据。

**请求头**:

```
Authorization: Bearer {token}
```

**响应**:

```json
{
  "simulation_id": "sim-550e8400-0001",
  "scenario_id": "ddos_attack",
  "status": "completed",
  "duration": 180,
  "start_time": "2025-04-12T15:00:00Z",
  "end_time": "2025-04-12T15:03:00Z",
  "summary": {
    "total_attacks": 183,
    "detected_attacks": 178,
    "prevented_attacks": 173,
    "detection_rate": 97.3,
    "prevention_rate": 94.5,
    "avg_detection_time": 120,
    "avg_response_time": 150
  },
  "device_results": [
    {
      "device_id": "550e8400-e29b-41d4-a716-446655440000",
      "device_name": "gateway_550e8400",
      "attacks_targeted": 95,
      "attacks_detected": 93,
      "attacks_prevented": 91,
      "detection_rate": 97.9,
      "prevention_rate": 95.8,
      "max_cpu_usage": 68.5,
      "max_memory_usage": 512.3
    },
    {
      "device_id": "550e8400-e29b-41d4-a716-446655440001",
      "device_name": "camera_550e8400",
      "attacks_targeted": 88,
      "attacks_detected": 85,
      "attacks_prevented": 82,
      "detection_rate": 96.6,
      "prevention_rate": 93.2,
      "max_cpu_usage": 72.1,
      "max_memory_usage": 348.7
    }
  ],
  "timeline": [
    {
      "timestamp": "2025-04-12T15:00:30Z",
      "event_type": "attack_initiated",
      "details": {
        "attack_type": "SYN_flood",
        "target": "550e8400-e29b-41d4-a716-446655440000",
        "intensity": 45
      }
    },
    {
      "timestamp": "2025-04-12T15:00:32Z",
      "event_type": "attack_detected",
      "details": {
        "attack_type": "SYN_flood",
        "target": "550e8400-e29b-41d4-a716-446655440000",
        "detection_time": 2000
      }
    },
    {
      "timestamp": "2025-04-12T15:00:33Z",
      "event_type": "protection_applied",
      "details": {
        "attack_type": "SYN_flood",
        "target": "550e8400-e29b-41d4-a716-446655440000",
        "protection_method": "rate_limiting",
        "response_time": 1000
      }
    }
  ]
}
```

## 系统配置API

### 获取系统配置

```
GET /config
```

获取系统配置信息。

**请求头**:

```
Authorization: Bearer {token}
```

**响应**:

```json
{
  "system": {
    "version": "1.0.0",
    "environment": "development",
    "log_level": "info"
  },
  "edgex": {
    "url": "http://localhost:48080",
    "metadata_url": "http://localhost:48081",
    "command_url": "http://localhost:48082"
  },
  "thingsboard": {
    "url": "http://localhost:8080",
    "username": "tenant@thingsboard.org"
  },
  "simulator": {
    "default_interval": 5,
    "auto_run": true
  },
  "security": {
    "rules": {
      "ddos_protection": {
        "enabled": true,
        "threshold": 100,
        "time_window": 60
      },
      "mitm_protection": {
        "enabled": true,
        "cert_verification": true
      },
      "firmware_protection": {
        "enabled": true,
        "verify_signature": true
      },
      "credential_protection": {
        "enabled": true,
        "password_strength": "high"
      }
    }
  }
}
```

### 更新系统配置

```
PUT /config
```

更新系统配置。

**请求头**:

```
Authorization: Bearer {token}
```

**请求体**:

```json
{
  "simulator": {
    "default_interval": 10,
    "auto_run": true
  },
  "security": {
    "rules": {
      "ddos_protection": {
        "threshold": 150,
        "time_window": 30
      }
    }
  }
}
```

**响应**:

```json
{
  "success": true,
  "message": "系统配置已更新"
}
```

### 重置系统配置

```
POST /config/reset
```

将系统配置重置为默认值。

**请求头**:

```
Authorization: Bearer {token}
```

**响应**:

```json
{
  "success": true,
  "message": "系统配置已重置为默认值"
}
```

## 日志API

### 获取系统日志

```
GET /logs
```

获取系统日志。

**请求头**:

```
Authorization: Bearer {token}
```

**查询参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| level | string | 可选。按日志级别筛选（debug, info, warning, error, critical） |
| source | string | 可选。按日志源筛选（system, device, security, analytics） |
| start_time | string | 可选。开始时间（ISO 8601格式） |
| end_time | string | 可选。结束时间（ISO 8601格式） |
| limit | integer | 可选。返回记录的最大数量，默认100 |

**响应**:

```json
{
  "logs": [
    {
      "timestamp": "2025-04-12T14:15:00Z",
      "level": "info",
      "source": "device",
      "device_id": "550e8400-e29b-41d4-a716-446655440000",
      "message": "设备已启动"
    },
    {
      "timestamp": "2025-04-12T14:25:30Z",
      "level": "warning",
      "source": "security",
      "device_id": "550e8400-e29b-41d4-a716-446655440000",
      "message": "检测到可疑的连接请求"
    },
    {
      "timestamp": "2025-04-12T14:26:00Z",
      "level": "error",
      "source": "system",
      "message": "无法连接到EdgeX服务"
    }
  ],
  "total": 3
}
```

### 获取设备日志

```
GET /devices/{device_id}/logs
```

获取特定设备的日志。

**请求头**:

```
Authorization: Bearer {token}
```

**查询参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| level | string | 可选。按日志级别筛选（debug, info, warning, error, critical） |
| start_time | string | 可选。开始时间（ISO 8601格式） |
| end_time | string | 可选。结束时间（ISO 8601格式） |
| limit | integer | 可选。返回记录的最大数量，默认100 |

**响应**:

```json
{
  "device_id": "550e8400-e29b-41d4-a716-446655440000",
  "logs": [
    {
      "timestamp": "2025-04-12T14:15:00Z",
      "level": "info",
      "message": "设备已启动"
    },
    {
      "timestamp": "2025-04-12T14:20:00Z",
      "level": "info",
      "message": "生成遥测数据: cpu_usage=10.2, memory_usage=245.8, temperature=41.5"
    },
    {
      "timestamp": "2025-04-12T14:25:30Z",
      "level": "warning",
      "message": "检测到可疑的连接请求"
    }
  ],
  "total": 3
}
```

### 清除日志

```
DELETE /logs
```

清除系统日志。

**请求头**:

```
Authorization: Bearer {token}
```

**查询参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| device_id | string | 可选。指定设备ID，仅清除该设备的日志 |
| level | string | 可选。按日志级别筛选（debug, info, warning, error, critical） |
| older_than | string | 可选。清除早于指定时间的日志（ISO 8601格式） |

**响应**:

```json
{
  "success": true,
  "message": "日志已清除",
  "removed_logs": 156
}
```

## 用户管理API

### 获取用户列表

```
GET /users
```

获取系统用户列表。

**请求头**:

```
Authorization: Bearer {token}
```

**响应**:

```json
{
  "users": [
    {
      "id": "user-550e8400-0001",
      "username": "admin",
      "role": "admin",
      "email": "admin@example.com",
      "created_at": "2025-03-01T10:00:00Z",
      "last_login": "2025-04-12T09:30:00Z"
    },
    {
      "id": "user-550e8400-0002",
      "username": "researcher",
      "role": "researcher",
      "email": "researcher@example.com",
      "created_at": "2025-03-15T14:30:00Z",
      "last_login": "2025-04-11T16:45:00Z"
    },
    {
      "id": "user-550e8400-0003",
      "username": "viewer",
      "role": "viewer",
      "email": "viewer@example.com",
      "created_at": "2025-04-01T09:15:00Z",
      "last_login": "2025-04-10T11:20:00Z"
    }
  ],
  "total": 3
}
```

### 创建用户

```
POST /users
```

创建新用户。

**请求头**:

```
Authorization: Bearer {token}
```

**请求体**:

```json
{
  "username": "new_user",
  "password": "secure_password",
  "role": "researcher",
  "email": "new_user@example.com",
  "full_name": "New User"
}
```

**响应**:

```json
{
  "success": true,
  "user_id": "user-550e8400-0004",
  "username": "new_user",
  "role": "researcher",
  "created_at": "2025-04-12T14:45:00Z"
}
```

### 更新用户

```
PUT /users/{user_id}
```

更新用户信息。

**请求头**:

```
Authorization: Bearer {token}
```

**请求体**:

```json
{
  "role": "admin",
  "email": "updated_email@example.com",
  "full_name": "Updated Name"
}
```

**响应**:

```json
{
  "success": true,
  "user_id": "user-550e8400-0002",
  "message": "用户信息已更新"
}
```

### 删除用户

```
DELETE /users/{user_id}
```

删除用户。

**请求头**:

```
Authorization: Bearer {token}
```

**响应**:

```json
{
  "success": true,
  "user_id": "user-550e8400-0003",
  "message": "用户已删除"
}
```

### 修改密码

```
PUT /users/{user_id}/password
```

修改用户密码。

**请求头**:

```
Authorization: Bearer {token}
```

**请求体**:

```json
{
  "current_password": "old_password",
  "new_password": "new_secure_password"
}
```

**响应**:

```json
{
  "success": true,
  "message": "密码已更新"
}
```

## WebSocket API

除了 RESTful API 外，平台还提供 WebSocket 接口用于实时数据更新。

### 设备状态更新

```
WebSocket: /ws/devices
```

订阅设备状态更新。

**认证**:

连接时需要提供有效的 JWT 令牌作为 URL 参数:
```
/ws/devices?token={jwt_token}
```

**消息格式**:

```json
{
  "event": "device_status_update",
  "data": {
    "device_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "running",
    "connected": true,
    "timestamp": "2025-04-12T14:50:00Z"
  }
}
```

### 安全事件通知

```
WebSocket: /ws/security
```

订阅安全事件通知。

**认证**:

连接时需要提供有效的 JWT 令牌作为 URL 参数:
```
/ws/security?token={jwt_token}
```

**消息格式**:

```json
{
  "event": "security_alert",
  "data": {
    "id": "event-550e8400-0003",
    "device_id": "550e8400-e29b-41d4-a716-446655440000",
    "rule_id": "ddos_protection",
    "timestamp": "2025-04-12T14:55:00Z",
    "severity": "high",
    "title": "检测到DDoS攻击",
    "description": "在60秒内接收到超过150个连接请求"
  }
}
```

### 遥测数据流

```
WebSocket: /ws/telemetry/{device_id}
```

订阅特定设备的实时遥测数据。

**认证**:

连接时需要提供有效的 JWT 令牌作为 URL 参数:
```
/ws/telemetry/{device_id}?token={jwt_token}
```

**消息格式**:

```json
{
  "event": "telemetry_update",
  "data": {
    "device_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-04-12T14:56:00Z",
    "metrics": {
      "cpu_usage": 12.5,
      "memory_usage": 256.4,
      "temperature": 42.3,
      "network_status": "online",
      "connected_devices": 3
    }
  }
}
```

## 错误处理

所有 API 在发生错误时将返回适当的 HTTP 状态码和包含错误详情的 JSON 响应。

### 错误响应格式

```json
{
  "error": true,
  "code": "error_code",
  "message": "错误描述信息",
  "details": {
    "field": "错误的字段",
    "reason": "详细错误原因"
  }
}
```

### 常见错误码

| HTTP 状态码 | 错误码 | 描述 |
|------------|--------|------|
| 400 | invalid_request | 请求格式不正确或缺少必要参数 |
| 401 | unauthorized | 认证失败，令牌无效或已过期 |
| 403 | forbidden | 用户没有执行请求操作的权限 |
| 404 | not_found | 请求的资源不存在 |
| 409 | conflict | 资源冲突，例如创建已存在的设备 |
| 422 | validation_error | 请求参数验证失败 |
| 429 | too_many_requests | 请求频率超过限制 |
| 500 | internal_error | 服务器内部错误 |

## 版本控制

API 版本通过 URL 路径或请求头指定。

### 通过 URL 路径指定版本

```
/api/v1/devices
```

### 通过请求头指定版本

```
X-API-Version: 1
```

## 限流策略

API 实施了请求限流策略，以防止过度使用。限流信息通过响应头返回：

```
X-Rate-Limit-Limit: 100
X-Rate-Limit-Remaining: 95
X-Rate-Limit-Reset: 1618248360
```

超过限制时将返回 429 状态码。

## 单点登录集成

平台支持与企业身份提供商（如 LDAP、Azure AD、Okta）集成，实现单点登录。

### 初始化 SSO 登录

```
GET /auth/sso/{provider}
```

其中 `provider` 可以是 `ldap`、`azure`、`okta` 等。

### SSO 回调

```
GET /auth/sso/{provider}/callback
```

用于接收身份提供商的认证回调。

## 附录

### 资源定义

平台的主要资源包括：

1. **设备** - 模拟的边缘设备
2. **安全规则** - 安全防护规则
3. **安全事件** - 检测到的安全事件
4. **仿真场景** - 预定义的安全仿真场景
5. **仿真** - 运行中或已完成的仿真实例
6. **报告** - 生成的分析报告
7. **用户** - 系统用户

### 示例代码

#### Python 使用示例

```python
import requests
import json

# 基础 URL
base_url = "http://localhost:5000/api"

# 获取令牌
def get_token(username, password):
    response = requests.post(f"{base_url}/auth/token", json={
        "username": username,
        "password": password
    })
    return response.json()["token"]

# 创建设备
def create_device(token, device_type, device_name, platform):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{base_url}/devices", headers=headers, json={
        "device_type": device_type,
        "device_name": device_name,
        "platform": platform
    })
    return response.json()

# 启动设备
def start_device(token, device_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{base_url}/devices/{device_id}/control", headers=headers, json={
        "action": "start"
    })
    return response.json()

# 运行仿真场景
def run_simulation(token, scenario_id, target_devices, parameters):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{base_url}/scenarios/{scenario_id}/run", headers=headers, json={
        "target_devices": target_devices,
        "parameters": parameters
    })
    return response.json()

# 使用示例
token = get_token("admin", "password")
device = create_device(token, "gateway", "test_gateway", "edgex")
start_device(token, device["id"])
simulation = run_simulation(token, "ddos_attack", [device["id"]], {
    "attack_duration": 180,
    "attack_intensity": "medium"
})
print(f"仿真ID: {simulation['simulation_id']}")
```

#### JavaScript 使用示例

```javascript
// 基础 URL
const baseUrl = 'http://localhost:5000/api';

// 获取令牌
async function getToken(username, password) {
  const response = await fetch(`${baseUrl}/auth/token`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      username,
      password
    })
  });
  const data = await response.json();
  return data.token;
}

// 创建设备
async function createDevice(token, deviceType, deviceName, platform) {
  const response = await fetch(`${baseUrl}/devices`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      device_type: deviceType,
      device_name: deviceName,
      platform
    })
  });
  return await response.json();
}

// 启动设备
async function startDevice(token, deviceId) {
  const response = await fetch(`${baseUrl}/devices/${deviceId}/control`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      action: 'start'
    })
  });
  return await response.json();
}

// 监听WebSocket事件
function listenForSecurityEvents(token) {
  const ws = new WebSocket(`ws://localhost:5000/ws/security?token=${token}`);
  
  ws.onopen = () => {
    console.log('WebSocket连接已建立');
  };
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('收到安全事件:', data);
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket错误:', error);
  };
  
  ws.onclose = () => {
    console.log('WebSocket连接已关闭');
  };
  
  return ws;
}

// 使用示例
async function main() {
  try {
    const token = await getToken('admin', 'password');
    const device = await createDevice(token, 'router', 'test_router', 'thingsboard');
    await startDevice(token, device.id);
    const ws = listenForSecurityEvents(token);
    
    // 在不需要时关闭WebSocket连接
    setTimeout(() => {
      ws.close();
    }, 300000); // 5分钟后关闭
  } catch (error) {
    console.error('出错了:', error);
  }
}

main();
```