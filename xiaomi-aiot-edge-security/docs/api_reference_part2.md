# 小米AIoT边缘安全防护研究平台 - API参考文档（续）

## 事件管理API

### 获取安全事件

```
GET /events/security
```

获取安全事件列表。

**请求头**:

```
Authorization: Bearer {access_token}
```

**查询参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| device_id | string | 可选。按设备ID筛选 |
| rule_id | string | 可选。按规则ID筛选 |
| severity | string | 可选。按严重程度筛选（low, medium, high, critical） |
| start_time | string | 可选。开始时间（ISO 8601格式） |
| end_time | string | 可选。结束时间（ISO 8601格式） |
| status | string | 可选。按状态筛选（new, acknowledged, resolved, false_positive） |
| page | integer | 可选。页码，默认为1 |
| per_page | integer | 可选。每页记录数，默认为20，最大为100 |

**响应**:

```json
{
  "events": [
    {
      "id": "evt-001",
      "device_id": "gateway-001",
      "rule_id": "data_anomaly_rule",
      "severity": "high",
      "description": "异常温度变化: 15.5°C",
      "telemetry": {
        "temperature": 40.0,
        "humidity": 60,
        "connected_devices": 5
      },
      "status": "new",
      "created_at": "2023-04-12T14:25:00Z"
    },
    {
      "id": "evt-002",
      "device_id": "camera-001",
      "rule_id": "authentication_failure_rule",
      "severity": "medium",
      "description": "多次认证失败: 5次尝试",
      "details": {
        "ip_address": "192.168.1.100",
        "username": "admin",
        "attempts": 5
      },
      "status": "acknowledged",
      "created_at": "2023-04-12T13:45:00Z",
      "acknowledged_at": "2023-04-12T13:50:00Z",
      "acknowledged_by": "operator1"
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

### 获取单个安全事件

```
GET /events/security/{event_id}
```

获取特定安全事件的详细信息。

**请求头**:

```
Authorization: Bearer {access_token}
```

**响应**:

```json
{
  "id": "evt-001",
  "device_id": "gateway-001",
  "rule_id": "data_anomaly_rule",
  "severity": "high",
  "description": "异常温度变化: 15.5°C",
  "telemetry": {
    "temperature": 40.0,
    "humidity": 60,
    "connected_devices": 5
  },
  "previous_telemetry": {
    "temperature": 24.5,
    "humidity": 58,
    "connected_devices": 5
  },
  "status": "new",
  "created_at": "2023-04-12T14:25:00Z",
  "device_info": {
    "name": "客厅网关",
    "type": "gateway",
    "properties": {
      "model": "xiaomi-gateway-v3",
      "firmware": "1.4.6_0012",
      "location": "living_room"
    }
  },
  "rule_info": {
    "name": "数据异常检测",
    "description": "检测设备遥测数据中的异常变化",
    "category": "data_anomaly"
  }
}
```

### 更新安全事件状态

```
PUT /events/security/{event_id}/status
```

更新安全事件的状态。

**请求头**:

```
Authorization: Bearer {access_token}
```

**请求体**:

```json
{
  "status": "acknowledged",  // 可选值: new, acknowledged, resolved, false_positive
  "comment": "正在调查此事件"
}
```

**响应**:

```json
{
  "id": "evt-001",
  "status": "acknowledged",
  "updated_at": "2023-04-12T14:30:00Z",
  "updated_by": "operator1",
  "comment": "正在调查此事件"
}
```

### 批量更新安全事件

```
PUT /events/security/batch
```

批量更新多个安全事件的状态。

**请求头**:

```
Authorization: Bearer {access_token}
```

**请求体**:

```json
{
  "event_ids": ["evt-001", "evt-002", "evt-003"],
  "status": "resolved",
  "comment": "已解决的批量事件"
}
```

**响应**:

```json
{
  "success": true,
  "updated_count": 3,
  "updated_at": "2023-04-12T14:35:00Z",
  "updated_by": "operator1"
}
```

### 获取系统事件

```
GET /events/system
```

获取系统事件列表。

**请求头**:

```
Authorization: Bearer {access_token}
```

**查询参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| category | string | 可选。按类别筛选（system, platform, device, user） |
| level | string | 可选。按级别筛选（info, warning, error） |
| start_time | string | 可选。开始时间（ISO 8601格式） |
| end_time | string | 可选。结束时间（ISO 8601格式） |
| page | integer | 可选。页码，默认为1 |
| per_page | integer | 可选。每页记录数，默认为20，最大为100 |

**响应**:

```json
{
  "events": [
    {
      "id": "sys-001",
      "category": "system",
      "level": "info",
      "message": "系统启动成功",
      "details": {
        "version": "1.0.0",
        "startup_time": 5.2
      },
      "timestamp": "2023-04-12T08:00:00Z"
    },
    {
      "id": "sys-002",
      "category": "device",
      "level": "warning",
      "message": "设备连接断开",
      "details": {
        "device_id": "speaker-001",
        "reason": "network_timeout"
      },
      "timestamp": "2023-04-12T10:15:00Z"
    }
  ],
  "pagination": {
    "total": 120,
    "page": 1,
    "per_page": 20,
    "pages": 6
  }
}
```

## 分析报告API

### 获取安全分析报告

```
GET /analytics/security
```

获取安全分析报告。

**请求头**:

```
Authorization: Bearer {access_token}
```

**查询参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| start_time | string | 可选。开始时间（ISO 8601格式） |
| end_time | string | 可选。结束时间（ISO 8601格式） |
| device_id | string | 可选。按设备ID筛选 |
| device_type | string | 可选。按设备类型筛选 |

**响应**:

```json
{
  "report_id": "sec-report-20230412",
  "generated_at": "2023-04-12T23:00:00Z",
  "period": {
    "start": "2023-04-12T00:00:00Z",
    "end": "2023-04-12T23:59:59Z"
  },
  "summary": {
    "total_events": 45,
    "by_severity": {
      "low": 20,
      "medium": 15,
      "high": 8,
      "critical": 2
    },
    "by_rule": {
      "data_anomaly_rule": 12,
      "authentication_failure_rule": 18,
      "command_injection_rule": 5,
      "network_scan_rule": 10
    },
    "by_device_type": {
      "gateway": 22,
      "camera": 15,
      "speaker": 5,
      "router": 3
    },
    "by_status": {
      "new": 10,
      "acknowledged": 15,
      "resolved": 18,
      "false_positive": 2
    }
  },
  "trends": {
    "hourly": [
      {"hour": 0, "count": 1},
      {"hour": 1, "count": 0},
      // ... 更多小时数据
      {"hour": 23, "count": 2}
    ],
    "top_devices": [
      {"device_id": "gateway-001", "count": 8},
      {"device_id": "camera-001", "count": 7},
      {"device_id": "gateway-002", "count": 5}
    ]
  },
  "recommendations": [
    {
      "type": "rule_adjustment",
      "rule_id": "data_anomaly_rule",
      "message": "考虑将阈值从10.0调整到12.0以减少误报",
      "confidence": 0.85
    },
    {
      "type": "firmware_update",
      "device_type": "camera",
      "message": "建议更新摄像头固件以解决安全漏洞",
      "confidence": 0.92
    }
  ]
}
```

### 获取性能分析报告

```
GET /analytics/performance
```

获取性能分析报告。

**请求头**:

```
Authorization: Bearer {access_token}
```

**查询参数**:

| 参数 | 类型 | 描述 |
|------|------|------|
| start_time | string | 可选。开始时间（ISO 8601格式） |
| end_time | string | 可选。结束时间（ISO 8601格式） |
| device_id | string | 可选。按设备ID筛选 |
| device_type | string | 可选。按设备类型筛选 |
| metrics | string | 可选。要包含的指标，逗号分隔（例如：cpu_usage,memory_usage） |

**响应**:

```json
{
  "report_id": "perf-report-20230412",
  "generated_at": "2023-04-12T23:05:00Z",
  "period": {
    "start": "2023-04-12T00:00:00Z",
    "end": "2023-04-12T23:59:59Z"
  },
  "summary": {
    "device_count": 15,
    "avg_cpu_usage": 18.5,
    "avg_memory_usage": 256.8,
    "peak_cpu_usage": {
      "value": 45.2,
      "device_id": "gateway-001",
      "timestamp": "2023-04-12T14:30:00Z"
    },
    "peak_memory_usage": {
      "value": 512.6,
      "device_id": "gateway-001",
      "timestamp": "2023-04-12T14:35:00Z"
    }
  },
  "by_device_type": {
    "gateway": {
      "count": 5,
      "avg_cpu_usage": 22.3,
      "avg_memory_usage": 320.5
    },
    "camera": {
      "count": 6,
      "avg_cpu_usage": 15.8,
      "avg_memory_usage": 210.2
    },
    "speaker": {
      "count": 3,
      "avg_cpu_usage": 12.4,
      "avg_memory_usage": 180.6
    },
    "router": {
      "count": 1,
      "avg_cpu_usage": 25.6,
      "avg_memory_usage": 350.8
    }
  },
  "trends": {
    "hourly_cpu": [
      {"hour": 0, "value": 15.2},
      {"hour": 1, "value": 14.8},
      // ... 更多小时数据
      {"hour": 23, "value": 16.5}
    ],
    "hourly_memory": [
      {"hour": 0, "value": 245.6},
      {"hour": 1, "value": 248.2},
      // ... 更多小时数据
      {"hour": 23, "value": 260.3}
    ]
  },
  "recommendations": [
    {
      "type": "resource_optimization",
      "device_id": "gateway-001",
      "message": "考虑优化网关处理流程以减少CPU使用率",
      "confidence": 0.78
    },
    {
      "type": "memory_leak",
      "device_id": "camera-003",
      "message": "可能存在内存泄漏，建议重启设备并监控",
      "confidence": 0.65
    }
  ]
}
```

### 生成自定义报告

```
POST /analytics/reports
```

生成自定义分析报告。

**请求头**:

```
Authorization: Bearer {access_token}
```

**请求体**:

```json
{
  "report_type": "custom",
  "name": "网关设备安全与性能分析",
  "period": {
    "start": "2023-04-01T00:00:00Z",
    "end": "2023-04-12T23:59:59Z"
  },
  "filters": {
    "device_types": ["gateway"],
    "metrics": ["cpu_usage", "memory_usage", "temperature", "connected_devices"],
    "security_categories": ["data_anomaly", "authentication", "network_attack"]
  },
  "sections": ["summary", "security_analysis", "performance_analysis", "recommendations"],
  "format": "json"  // 可选值: json, pdf, csv
}
```

**响应**:

```json
{
  "report_id": "custom-report-001",
  "status": "processing",
  "estimated_completion": "2023-04-13T00:10:00Z",
  "download_url": null
}
```

### 获取报告状态

```
GET /analytics/reports/{report_id}
```

获取报告生成状态。

**请求头**:

```
Authorization: Bearer {access_token}
```

**响应**:

```json
{
  "report_id": "custom-report-001",
  "name": "网关设备安全与性能分析",
  "status": "completed",  // 可能的值: processing, completed, failed
  "progress": 100,
  "created_at": "2023-04-13T00:05:00Z",
  "completed_at": "2023-04-13T00:08:30Z",
  "download_url": "http://localhost:8080/api/v1/analytics/reports/custom-report-001/download",
  "format": "json",
  "expires_at": "2023-04-20T00:08:30Z"  // 下载链接过期时间
}
```

## 系统管理API

### 获取系统状态

```
GET /system/status
```

获取系统状态信息。

**请求头**:

```
Authorization: Bearer {access_token}
```

**响应**:

```json
{
  "status": "running",
  "version": "1.0.0",
  "uptime": 86400,  // 秒
  "started_at": "2023-04-12T00:00:00Z",
  "components": [
    {
      "name": "device_simulator",
      "status": "running",
      "version": "1.0.0",
      "health": "good"
    },
    {
      "name": "security_engine",
      "status": "running",
      "version": "1.0.0",
      "health": "good"
    },
    {
      "name": "analytics_engine",
      "status": "running",
      "version": "1.0.0",
      "health": "good"
    },
    {
      "name": "web_dashboard",
      "status": "running",
      "version": "1.0.0",
      "health": "good"
    }
  ],
  "resources": {
    "cpu_usage": 35.2,
    "memory_usage": 1024.5,  // MB
    "disk_usage": 45.6,  // 百分比
    "network": {
      "rx_bytes": 1024000,
      "tx_bytes": 512000
    }
  },
  "connections": {
    "edgex": {
      "status": "connected",
      "last_check": "2023-04-12T23:55:00Z"
    },
    "thingsboard": {
      "status": "connected",
      "last_check": "2023-04-12T23:55:00Z"
    }
  }
}
```

### 获取系统配置

```
GET /system/config
```

获取系统配置信息。

**请求头**:

```
Authorization: Bearer {access_token}
```

**响应**:

```json
{
  "platform": {
    "name": "小米AIoT边缘安全防护研究平台",
    "version": "1.0.0",
    "log_level": "INFO",
    "web_port": 8080
  },
  "simulators": {
    "gateway": {
      "count": 2,
      "properties": {
        "model": "xiaomi-gateway-v3",
        "firmware": "1.4.6_0012"
      }
    },
    "camera": {
      "count": 3,
      "properties": {
        "model": "xiaomi-camera-1080p",
        "firmware": "2.1.9_0045"
      }
    },
    "speaker": {
      "count": 2,
      "properties": {
        "model": "xiaomi-speaker-pro",
        "firmware": "3.2.1_0078"
      }
    },
    "router": {
      "count": 1,
      "properties": {
        "model": "xiaomi-router-ax6000",
        "firmware": "1.2.7_0034"
      }
    }
  },
  "edgex": {
    "enabled": true,
    "host": "localhost",
    "port": 48080,
    "device_service_name": "xiaomi-device-service"
  },
  "thingsboard": {
    "enabled": true,
    "host": "localhost",
    "port": 8080,
    "access_token": "A1_TEST_TOKEN"
  },
  "security": {
    "rules": [
      {
        "id": "data_anomaly",
        "enabled": true,
        "threshold": 10.0
      },
      {
        "id": "authentication_failure",
        "enabled": true,
        "max_attempts": 5
      },
      {
        "id": "command_injection",
        "enabled": true,
        "patterns": ["rm -rf", ";\\s*", "&&\\s*"]
      }
    ]
  },
  "analytics": {
    "storage_path": "./data/analytics",
    "report_interval": 3600
  }
}
```

### 更新系统配置

```
PUT /system/config
```

更新系统配置。

**请求头**:

```
Authorization: Bearer {access_token}
```

**请求体**:

```json
{
  "platform": {
    "log_level": "DEBUG",
    "web_port": 9090
  },
  "security": {
    "rules": [
      {
        "id": "data_anomaly",
        "threshold": 15.0
      }
    ]
  }
}
```

**响应**:

```json
{
  "success": true,
  "updated_at": "2023-04-13T00:15:00Z",
  "updated_by": "admin",
  "restart_required": true,
  "changes": [
    "platform.log_level",
    "platform.web_port",
    "security.rules[0].threshold"
  ]
}
```

### 系统控制

```
POST /system/control
```

控制系统操作。

**请求头**:

```
Authorization: Bearer {access_token}
```

**请求体**:

```json
{
  "action": "restart",  // 可选值: restart, shutdown, backup, restore
  "params": {
    "backup_path": "/backups/aiot-backup-20230413.zip"  // 如果action是backup或restore，需要提供此参数
  }
}
```

**响应**:

```json
{
  "success": true,
  "action": "restart",
  "message": "系统将在5秒后重启",
  "timestamp": "2023-04-13T00:20:00Z"
}
```

## WebSocket API

### 实时数据流

```
WS /ws/data
```

通过WebSocket接收实时数据流。

**连接参数**:

```
token={access_token}&topics=telemetry,security_events,system_events
```

**可用主题**:

- `telemetry`: 设备遥测数据
- `security_events`: 安全事件
- `system_events`: 系统事件
- `device_status`: 设备状态变化

**示例消息**:

```json
{
  "topic": "telemetry",
  "timestamp": "2023-04-13T00:25:00Z",
  "device_id": "gateway-001",
  "data": {
    "temperature": 25.8,
    "humidity": 64,
    "connected_devices": 6
  }
}
```

```json
{
  "topic": "security_events",
  "timestamp": "2023-04-13T00:26:00Z",
  "event_id": "evt-005",
  "device_id": "camera-001",
  "rule_id": "network_scan_rule",
  "severity": "medium",
  "description": "检测到网络端口扫描"
}
```

### 命令通道

```
WS /ws/command
```

通过WebSocket发送命令和接收响应。

**连接参数**:

```
token={access_token}
```

**发送命令示例**:

```json
{
  "command_id": "cmd-001",
  "device_id": "gateway-001",
  "action": "reboot",
  "params": {}
}
```

**接收响应示例**:

```json
{
  "command_id": "cmd-001",
  "device_id": "gateway-001",
  "status": "success",
  "result": {
    "message": "设备正在重启"
  },
  "timestamp": "2023-04-13T00:30:00Z"
}
```

## 错误处理

所有API错误响应都遵循以下格式：

```json
{
  "error": {
    "code": "unauthorized",
    "message": "无效的访问令牌",
    "details": "令牌已过期",
    "request_id": "req-12345"
  }
}
```

### 常见错误代码

| 错误代码 | HTTP状态码 | 描述 |
|---------|-----------|------|
| bad_request | 400 | 请求格式错误或参数无效 |
| unauthorized | 401 | 未提供认证或认证无效 |
| forbidden | 403 | 没有权限执行请求的操作 |
| not_found | 404 | 请求的资源不存在 |
| method_not_allowed | 405 | 请求方法不允许 |
| conflict | 409 | 请求与当前状态冲突 |
| too_many_requests | 429 | 请