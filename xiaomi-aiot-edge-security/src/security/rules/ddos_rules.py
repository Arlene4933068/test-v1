"""
小米AIoT边缘安全防护研究平台 - DDoS防护规则
定义DDoS攻击防护规则
"""

def get_rules():
    """
    获取DDoS防护规则
    
    Returns:
        DDoS防护规则字典
    """
    return {
        # SYN Flood攻击
        'ddos_syn_flood': {
            'name': 'SYN Flood防护',
            'description': '防止TCP SYN Flood攻击，通过监控短时间内的大量SYN请求',
            'actions': [
                {
                    'type': 'block_traffic',
                    'params': {
                        'direction': 'inbound',
                        'duration': 300,  # 5分钟
                        'protocol': 'tcp'
                    }
                },
                {
                    'type': 'notify_admin',
                    'params': {
                        'message': 'SYN Flood攻击检测到，已临时阻断入站TCP流量',
                        'method': 'email'
                    }
                }
            ],
            'recovery_action': {
                'type': 'unblock_traffic',
                'params': {
                    'protocol': 'tcp'
                }
            },
            'duration': 300  # 防护持续5分钟
        },
        
        # UDP Flood攻击
        'ddos_udp_flood': {
            'name': 'UDP Flood防护',
            'description': '防止UDP Flood攻击，通过监控短时间内的大量UDP数据包',
            'actions': [
                {
                    'type': 'block_traffic',
                    'params': {
                        'direction': 'inbound',
                        'duration': 300,
                        'protocol': 'udp'
                    }
                },
                {
                    'type': 'rate_limit',
                    'params': {
                        'protocol': 'udp',
                        'max_packets_per_second': 100
                    }
                },
                {
                    'type': 'notify_admin',
                    'params': {
                        'message': 'UDP Flood攻击检测到，已限制UDP流量',
                        'method': 'email'
                    }
                }
            ],
            'recovery_action': {
                'type': 'unblock_traffic',
                'params': {
                    'protocol': 'udp'
                }
            },
            'duration': 300
        },
        
        # HTTP Flood攻击
        'ddos_http_flood': {
            'name': 'HTTP Flood防护',
            'description': '防止HTTP Flood攻击，通过监控短时间内来自相同来源的大量HTTP请求',
            'actions': [
                {
                    'type': 'rate_limit',
                    'params': {
                        'protocol': 'http',
                        'max_requests_per_minute': 60
                    }
                },
                {
                    'type': 'implement_captcha',
                    'params': {
                        'threshold': 30  # 当请求超过30/分钟时启用验证码
                    }
                },
                {
                    'type': 'notify_admin',
                    'params': {
                        'message': 'HTTP Flood攻击检测到，已实施流量限制',
                        'method': 'email'
                    }
                }
            ],
            'recovery_action': {
                'type': 'remove_rate_limit',
                'params': {
                    'protocol': 'http'
                }
            },
            'duration': 600  # 10分钟
        },
        
        # ICMP Flood攻击
        'ddos_icmp_flood': {
            'name': 'ICMP Flood防护',
            'description': '防止ICMP Flood攻击（例如Ping Flood），通过限制ICMP数据包',
            'actions': [
                {
                    'type': 'block_traffic',
                    'params': {
                        'direction': 'inbound',
                        'protocol': 'icmp',
                        'duration': 300
                    }
                },
                {
                    'type': 'notify_admin',
                    'params': {
                        'message': 'ICMP Flood攻击检测到，已阻断ICMP流量',
                        'method': 'email'
                    }
                }
            ],
            'recovery_action': {
                'type': 'unblock_traffic',
                'params': {
                    'protocol': 'icmp'
                }
            },
            'duration': 300
        },
        
        # 分布式反射放大攻击 (如NTP放大、DNS放大)
        'ddos_amplification': {
            'name': '放大攻击防护',
            'description': '防止反射放大攻击，如NTP放大、DNS放大、SSDP放大等',
            'actions': [
                {
                    'type': 'block_traffic',
                    'params': {
                        'direction': 'inbound',
                        'ports': [53, 123, 1900],  # DNS, NTP, SSDP
                        'duration': 600
                    }
                },
                {
                    'type': 'validate_source',
                    'params': {
                        'protocols': ['dns', 'ntp', 'ssdp']
                    }
                },
                {
                    'type': 'notify_admin',
                    'params': {
                        'message': '检测到放大攻击尝试，已阻断相关端口流量',
                        'method': 'email'
                    }
                }
            ],
            'recovery_action': {
                'type': 'unblock_traffic',
                'params': {
                    'ports': [53, 123, 1900]
                }
            },
            'duration': 600  # 10分钟
        },
        
        # IoT僵尸网络协同攻击
        'ddos_iot_botnet': {
            'name': 'IoT僵尸网络防护',
            'description': '防止来自受感染IoT设备组成的僵尸网络的协同攻击',
            'actions': [
                {
                    'type': 'isolate_device',
                    'params': {
                        'level': 'network'
                    }
                },
                {
                    'type': 'scan_firmware',
                    'params': {
                        'scan_type': 'deep',
                        'check_signatures': True
                    }
                },
                {
                    'type': 'reset_device',
                    'params': {
                        'type': 'hard',
                        'preserve_config': False
                    }
                },
                {
                    'type': 'notify_admin',
                    'params': {
                        'message': '检测到设备可能成为僵尸网络一部分，已隔离并扫描',
                        'method': 'sms',
                        'priority': 'high'
                    }
                }
            ],
            'recovery_action': {
                'type': 'reconnect_device',
                'params': {
                    'verify_first': True
                }
            },
            'duration': 3600  # 1小时
        }
    }