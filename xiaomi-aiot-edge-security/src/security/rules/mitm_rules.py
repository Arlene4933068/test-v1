"""
小米AIoT边缘安全防护研究平台 - 中间人攻击防护规则
定义防护规则以应对中间人(MITM)攻击
"""

def get_rules():
    """
    获取中间人攻击防护规则
    
    Returns:
        中间人攻击防护规则字典
    """
    return {
        # ARP欺骗攻击
        'mitm_arp_spoofing': {
            'name': 'ARP欺骗防护',
            'description': '防止ARP欺骗攻击，通过监控和验证ARP请求和响应',
            'actions': [
                {
                    'type': 'block_device',
                    'params': {
                        'mac_address': '{attacker_mac}',
                        'duration': 600  # 10分钟
                    }
                },
                {
                    'type': 'restore_arp_table',
                    'params': {
                        'verify': True
                    }
                },
                {
                    'type': 'notify_admin',
                    'params': {
                        'message': '检测到ARP欺骗攻击，已阻止可疑设备并恢复ARP表',
                        'method': 'email'
                    }
                }
            ],
            'recovery_action': {
                'type': 'verify_network',
                'params': {
                    'scan_type': 'arp_scan'
                }
            },
            'duration': 600
        },
        
        # SSL/TLS中间人攻击
        'mitm_ssl_interception': {
            'name': 'SSL/TLS拦截防护',
            'description': '防止SSL/TLS中间人攻击，通过证书验证和握手分析',
            'actions': [
                {
                    'type': 'terminate_connection',
                    'params': {
                        'connection_id': '{connection_id}'
                    }
                },
                {
                    'type': 'blacklist_certificate',
                    'params': {
                        'certificate_hash': '{certificate_hash}',
                        'duration': 86400  # 24小时
                    }
                },
                {
                    'type': 'notify_admin',
                    'params': {
                        'message': '检测到SSL/TLS中间人攻击尝试，已终止连接并列入黑名单',
                        'method': 'email',
                        'priority': 'high'
                    }
                }
            ],
            'recovery_action': {
                'type': 'update_certificate_store',
                'params': {
                    'check_revocation': True
                }
            },
            'duration': 3600  # 1小时
        },
        
        # DNS欺骗攻击
        'mitm_dns_spoofing': {
            'name': 'DNS欺骗防护',
            'description': '防止DNS欺骗攻击，通过验证DNS响应的真实性',
            'actions': [
                {
                    'type': 'block_traffic',
                    'params': {
                        'direction': 'outbound',
                        'destination': '{malicious_ip}',
                        'duration': 3600
                    }
                },
                {
                    'type': 'use_secure_dns',
                    'params': {
                        'dns_servers': ['8.8.8.8', '1.1.1.1'],
                        'use_dnssec': True
                    }
                },
                {
                    'type': 'notify_admin',
                    'params': {
                        'message': '检测到DNS欺骗攻击，已切换到安全DNS服务器',
                        'method': 'email'
                    }
                }
            ],
            'recovery_action': {
                'type': 'restore_dns_settings',
                'params': {
                    'verify_first': True
                }
            },
            'duration': 3600
        },
        
        # WiFi邪恶双胞胎攻击
        'mitm_evil_twin': {
            'name': 'WiFi邪恶双胞胎防护',
            'description': '防止假冒合法WiFi接入点的攻击',
            'actions': [
                {
                    'type': 'disconnect_wifi',
                    'params': {
                        'ssid': '{evil_ssid}',
                        'bssid': '{evil_bssid}'
                    }
                },
                {
                    'type': 'blacklist_wifi',
                    'params': {
                        'bssid': '{evil_bssid}',
                        'duration': 86400  # 24小时
                    }
                },
                {
                    'type': 'notify_admin',
                    'params': {
                        'message': '检测到WiFi邪恶双胞胎攻击，已断开可疑网络连接',
                        'method': 'sms',
                        'priority': 'high'
                    }
                }
            ],
            'recovery_action': {
                'type': 'scan_wifi_networks',
                'params': {
                    'verify_legitimate': True
                }
            },
            'duration': 3600
        },
        
        # BGP劫持攻击 (对于边缘路由器)
        'mitm_bgp_hijacking': {
            'name': 'BGP劫持防护',
            'description': '防止边缘路由器的BGP路由劫持攻击',
            'actions': [
                {
                    'type': 'validate_routes',
                    'params': {
                        'check_rpki': True,
                        'check_bgpsec': True
                    }
                },
                {
                    'type': 'reject_invalid_routes',
                    'params': {
                        'origin_asn': '{malicious_asn}'
                    }
                },
                {
                    'type': 'notify_admin',
                    'params': {
                        'message': '检测到可能的BGP劫持尝试，已拒绝可疑路由',
                        'method': 'email',
                        'priority': 'critical'
                    }
                }
            ],
            'recovery_action': {
                'type': 'reload_routing_table',
                'params': {
                    'from_trusted_source': True
                }
            },
            'duration': 7200  # 2小时
        },
        
        # MQTT中间人攻击 (针对IoT设备)
        'mitm_mqtt_interception': {
            'name': 'MQTT中间人防护',
            'description': '防止针对MQTT协议的中间人攻击',
            'actions': [
                {
                    'type': 'terminate_connection',
                    'params': {
                        'broker_address': '{suspicious_broker}',
                        'client_id': '{client_id}'
                    }
                },
                {
                    'type': 'enforce_tls',
                    'params': {
                        'min_tls_version': '1.2',
                        'verify_cert': True
                    }
                },
                {
                    'type': 'notify_admin',
                    'params': {
                        'message': '检测到MQTT中间人攻击，已终止连接并强制使用TLS',
                        'method': 'email'
                    }
                }
            ],
            'recovery_action': {
                'type': 'reconnect_mqtt',
                'params': {
                    'to_trusted_broker': True,
                    'with_authentication': True
                }
            },
            'duration': 1800  # 30分钟
        }
    }