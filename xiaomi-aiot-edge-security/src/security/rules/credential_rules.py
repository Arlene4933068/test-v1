"""
小米AIoT边缘安全防护研究平台 - 凭证攻击防护规则
定义针对身份认证和凭证的攻击防护规则
"""

def get_rules():
    """
    获取凭证攻击防护规则
    
    Returns:
        凭证攻击防护规则字典
    """
    return {
        # 暴力破解攻击
        'credential_brute_force': {
            'name': '暴力破解防护',
            'description': '防止通过暴力破解方式猜测密码或PIN码',
            'actions': [
                {
                    'type': 'account_lockout',
                    'params': {
                        'account_id': '{account_id}',
                        'duration': 1800,  # 30分钟
                        'reason': 'multiple_failed_attempts'
                    }
                },
                {
                    'type': 'increase_delay',
                    'params': {
                        'base_delay': 1000,  # 毫秒
                        'multiplier': 2,
                        'max_delay': 30000  # 最大30秒
                    }
                },
                {
                    'type': 'notify_admin',
                    'params': {
                        'message': '检测到针对账号的暴力破解尝试，已临时锁定',
                        'method': 'email'
                    }
                }
            ],
            'recovery_action': {
                'type': 'unlock_account',
                'params': {
                    'require_verification': True
                }
            },
            'duration': 1800  # 30分钟
        },
        
        # 凭证重放攻击
        'credential_replay': {
            'name': '凭证重放防护',
            'description': '防止截获和重放认证凭证的攻击',
            'actions': [
                {
                    'type': 'invalidate_session',
                    'params': {
                        'session_id': '{session_id}',
                        'reason': 'replay_detected'
                    }
                },
                {
                    'type': 'enforce_nonce',
                    'params': {
                        'timeout': 60,  # 秒
                        'force_unique': True
                    }
                },
                {
                    'type': 'notify_admin',
                    'params': {
                        'message': '检测到凭证重放攻击，已强制使用一次性令牌',
                        'method': 'email'
                    }
                }
            ],
            'recovery_action': None,
            'duration': 0
        },
        
        # 凭证泄露
        'credential_leak': {
            'name': '凭证泄露防护',
            'description': '检测和应对凭证泄露事件',
            'actions': [
                {
                    'type': 'reset_credentials',
                    'params': {
                        'account_id': '{account_id}',
                        'notify_user': True,
                        'force_change': True
                    }
                },
                {
                    'type': 'invalidate_sessions',
                    'params': {
                        'account_id': '{account_id}',
                        'all_sessions': True
                    }
                },
                {
                    'type': 'notify_admin',
                    'params': {
                        'message': '检测到凭证泄露，已重置凭证并终止所有会话',
                        'method': 'sms',
                        'priority': 'high'
                    }
                }
            ],
            'recovery_action': {
                'type': 'audit_access_logs',
                'params': {
                    'time_period': 86400,  # 过去24小时
                    'detailed': True
                }
            },
            'duration': 3600  # 1小时
        },
        
        # 默认/弱密码攻击
        'credential_default_weak': {
            'name': '默认/弱密码防护',
            'description': '防止使用默认或弱密码的风险',
            'actions': [
                {
                    'type': 'force_password_change',
                    'params': {
                        'account_id': '{account_id}',
                        'min_strength': 'high',
                        'block_until_changed': True
                    }
                },
                {
                    'type': 'apply_password_policy',
                    'params': {
                        'min_length': 12,
                        'require_mixed_case': True,
                        'require_numbers': True,
                        'require_special': True
                    }
                },
                {
                    'type': 'notify_admin',
                    'params': {
                        'message': '检测到设备使用默认/弱密码，已强制更改',
                        'method': 'email'
                    }
                }
            ],
            'recovery_action': None,
            'duration': 0
        },
        
        # 凭证嗅探攻击
        'credential_sniffing': {
            'name': '凭证嗅探防护',
            'description': '防止通过网络嗅探捕获明文凭证',
            'actions': [
                {
                    'type': 'enforce_encryption',
                    'params': {
                        'protocol': 'https',
                        'min_tls_version': '1.2'
                    }
                },
                {
                    'type': 'implement_hsts',
                    'params': {
                        'max_age': 31536000,  # 1年
                        'include_subdomains': True
                    }
                },
                {
                    'type': 'notify_admin',
                    'params': {
                        'message': '检测到凭证嗅探尝试，已强制使用加密传输',
                        'method': 'email'
                    }
                }
            ],
            'recovery_action': None,
            'duration': 604800  # 7天
        },
        
        # OAuth令牌盗用
        'credential_token_theft': {
            'name': 'OAuth令牌盗用防护',
            'description': '防止OAuth或其他授权令牌被盗用',
            'actions': [
                {
                    'type': 'revoke_token',
                    'params': {
                        'token_id': '{token_id}',
                        'revoke_related': True
                    }
                },
                {
                    'type': 'reduce_token_lifetime',
                    'params': {
                        'access_token_lifetime': 900,  # 15分钟
                        'refresh_token_lifetime': 86400  # 1天
                    }
                },
                {
                    'type': 'notify_admin',
                    'params': {
                        'message': '检测到OAuth令牌可能被盗用，已吊销并缩短有效期',
                        'method': 'email'
                    }
                }
            ],
            'recovery_action': {
                'type': 'audit_authorization_logs',
                'params': {
                    'detailed': True
                }
            },
            'duration': 86400  # 1天
        },
        
        # 会话固定攻击
        'credential_session_fixation': {
            'name': '会话固定防护',
            'description': '防止会话固定攻击',
            'actions': [
                {
                    'type': 'regenerate_session_id',
                    'params': {
                        'on_authentication': True,
                        'on_privilege_change': True
                    }
                },
                {
                    'type': 'implement_session_timeout',
                    'params': {
                        'idle_timeout': 1800,  # 30分钟
                        'absolute_timeout': 28800  # 8小时
                    }
                },
                {
                    'type': 'notify_admin',
                    'params': {
                        'message': '检测到会话固定尝试，已重新生成会话标识',
                        'method': 'email'
                    }
                }
            ],
            'recovery_action': None,
            'duration': 3600  # 1小时
        }
    }