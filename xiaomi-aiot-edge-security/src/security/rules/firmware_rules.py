"""
小米AIoT边缘安全防护研究平台 - 固件攻击防护规则
定义针对固件漏洞和攻击的防护规则
"""

def get_rules():
    """
    获取固件攻击防护规则
    
    Returns:
        固件攻击防护规则字典
    """
    return {
        # 固件篡改检测
        'firmware_tampering': {
            'name': '固件篡改防护',
            'description': '检测和防护对设备固件的未授权修改',
            'actions': [
                {
                    'type': 'isolate_device',
                    'params': {
                        'level': 'network',
                        'allow_recovery': True
                    }
                },
                {
                    'type': 'restore_firmware',
                    'params': {
                        'from_backup': True,
                        'verify_integrity': True
                    }
                },
                {
                    'type': 'notify_admin',
                    'params': {
                        'message': '检测到固件篡改，设备已隔离并尝试恢复',
                        'method': 'email',
                        'priority': 'critical'
                    }
                }
            ],
            'recovery_action': {
                'type': 'verify_firmware',
                'params': {
                    'deep_check': True
                }
            },
            'duration': 7200  # 2小时
        },
        
        # 未签名固件更新攻击
        'unsigned_firmware_update': {
            'name': '未签名固件防护',
            'description': '防止安装未经签名或签名无效的固件更新',
            'actions': [
                {
                    'type': 'block_update',
                    'params': {
                        'update_id': '{update_id}',
                        'reason': 'invalid_signature'
                    }
                },
                {
                    'type': 'log_update_attempt',
                    'params': {
                        'details': True,
                        'source_info': True
                    }
                },
                {
                    'type': 'notify_admin',
                    'params': {
                        'message': '阻止了未签名固件更新尝试',
                        'method': 'email',
                        'include_details': True
                    }
                }
            ],
            'recovery_action': None,  # 不需要恢复操作
            'duration': 0  # 一次性操作，不需要持续时间
        },
        
        # 固件降级攻击
        'firmware_downgrade': {
            'name': '固件降级防护',
            'description': '防止将设备固件降级到存在已知漏洞的旧版本',
            'actions': [
                {
                    'type': 'block_update',
                    'params': {
                        'update_id': '{update_id}',
                        'reason': 'version_downgrade'
                    }
                },
                {
                    'type': 'enforce_version_check',
                    'params': {
                        'min_version': '{min_secure_version}',
                        'strict': True
                    }
                },
                {
                    'type': 'notify_admin',
                    'params': {
                        'message': '检测到固件降级尝试，已阻止',
                        'method': 'email'
                    }
                }
            ],
            'recovery_action': None,
            'duration': 0
        },
        
        # 固件提取攻击
        'firmware_extraction': {
            'name': '固件提取防护',
            'description': '防止未授权读取或提取设备固件',
            'actions': [
                {
                    'type': 'block_interface',
                    'params': {
                        'interface': '{extraction_interface}',
                        'duration': 3600
                    }
                },
                {
                    'type': 'enable_encryption',
                    'params': {
                        'storage_areas': ['firmware', 'bootloader'],
                        'strength': 'high'
                    }
                },
                {
                    'type': 'notify_admin',
                    'params': {
                        'message': '检测到固件提取尝试，已加强保护',
                        'method': 'email',
                        'priority': 'high'
                    }
                }
            ],
            'recovery_action': {
                'type': 'restore_interfaces',
                'params': {
                    'after_verification': True
                }
            },
            'duration': 3600  # 1小时
        },
        
        # 固件内存注入
        'firmware_memory_injection': {
            'name': '固件内存注入防护',
            'description': '防止通过内存操作向固件执行区域注入恶意代码',
            'actions': [
                {
                    'type': 'reset_device',
                    'params': {
                        'type': 'hard',
                        'preserve_config': False
                    }
                },
                {
                    'type': 'enable_memory_protection',
                    'params': {
                        'use_aslr': True,
                        'use_nx': True,
                        'use_canaries': True
                    }
                },
                {
                    'type': 'notify_admin',
                    'params': {
                        'message': '检测到固件内存注入攻击，已重置设备并加强内存保护',
                        'method': 'sms',
                        'priority': 'critical'
                    }
                }
            ],
            'recovery_action': {
                'type': 'verify_memory_integrity',
                'params': {
                    'scan_depth': 'full'
                }
            },
            'duration': 1800  # 30分钟
        },
        
        # 引导加载程序漏洞攻击
        'bootloader_vulnerability': {
            'name': '引导加载程序防护',
            'description': '防止利用引导加载程序漏洞的攻击',
            'actions': [
                {
                    'type': 'enable_secure_boot',
                    'params': {
                        'verify_chain': True,
                        'lock_bootloader': True
                    }
                },
                {
                    'type': 'update_bootloader',
                    'params': {
                        'to_version': '{latest_secure_version}',
                        'verify_signature': True
                    }
                },
                {
                    'type': 'notify_admin',
                    'params': {
                        'message': '检测到引导加载程序漏洞攻击，已启用安全启动',
                        'method': 'email',
                        'priority': 'critical'
                    }
                }
            ],
            'recovery_action': {
                'type': 'verify_boot_process',
                'params': {
                    'full_chain': True
                }
            },
            'duration': 3600  # 1小时
        },
        
        # 调试接口攻击
        'debug_interface_attack': {
            'name': '调试接口防护',
            'description': '防止通过JTAG、UART等调试接口进行的攻击',
            'actions': [
                {
                    'type': 'disable_interface',
                    'params': {
                        'interfaces': ['jtag', 'uart', 'swd'],
                        'permanent': False
                    }
                },
                {
                    'type': 'log_access_attempt',
                    'params': {
                        'interface': '{interface_name}',
                        'with_timing': True
                    }
                },
                {
                    'type': 'notify_admin',
                    'params': {
                        'message': '检测到调试接口访问尝试，已禁用接口',
                        'method': 'email'
                    }
                }
            ],
            'recovery_action': {
                'type': 'enable_interfaces',
                'params': {
                    'with_authentication': True
                }
            },
            'duration': 86400  # 24小时
        }
    }