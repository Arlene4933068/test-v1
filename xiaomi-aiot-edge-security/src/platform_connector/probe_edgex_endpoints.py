#!/usr/bin/env python3
# 探测 EdgeX 端点

import requests
import sys

def probe_endpoint(url):
    try:
        print(f"尝试: {url}")
        response = requests.get(url, timeout=5)
        print(f"  状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"  响应: {response.text[:100]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"  错误: {str(e)}")
        return False

# EdgeX Foundry 服务基础 URL
host = "localhost"
ports = [59880, 59881, 59882]
endpoints = [
    "/ping", 
    "/api/v2/ping", 
    "/api/v2/version", 
    "/api/v2/health/check",
    "/api/v2/info"
]

success = False

for port in ports:
    print(f"\n检查端口 {port}:")
    for path in endpoints:
        url = f"http://{host}:{port}{path}"
        if probe_endpoint(url):
            print(f"\n✅ 成功: 找到有效端点 {url}")
            success = True

if not success:
    print("\n⚠️ 警告: 未找到任何有效的 EdgeX 端点")