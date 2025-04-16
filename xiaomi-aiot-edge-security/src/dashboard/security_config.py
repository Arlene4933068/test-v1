# src/dashboard/security_config.py
import os
import yaml
import json
import time
from utils.logger import get_logger

class SecurityConfig:
    """安全配置管理：管理安全防护规则和配置"""
    
    def __init__(self, config=None):
        self.logger = get_logger("SecurityConfig")
        self.config = config
        
        # 配置文件路径
        self.config_file = os.path.join(os.getcwd(), 'config', 'security.yaml')
        
        # 默认配置
        self.default_config = {
            "protection": {
                "enabled": True,
                "auto_update": True,
                "log_level": "info"
            },
            "rules": {
                "ddos": {
                    "enabled": True,
                    "threshold": 100,
                    "window": 60
                },
                "mitm": {
                    "enabled": True,
                    "certificate_verification": True
                },
                "firmware": {
                    "enabled": True,
                    "verify_signature": True,
                    "verify_checksum": True
                },
                "credential": {
                    "enabled": True,
                    "lockout_threshold": 5,
                    "lockout_time": 300
                }
            },
            "response": {
                "alert": True,
                "block": True,
                "quarantine": False
            }
        }
        
        # 统计数据
        self.stats = {
            "total_attacks": 0,
            "blocked_attacks": 0,
            "by_type": {},
            "by_device": {}
        }
        
        # 加载配置
        self._load_config()
        self.logger.info("安全配置管理器初始化完成")
    
    def _load_config(self):
        """从配置文件加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                
                # 合并配置
                for key, value in self.default_config.items():
                    if key not in config:
                        config[key] = value
                    elif isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            if sub_key not in config[key]:
                                config[key][sub_key] = sub_value
                
                self.current_config = config
                self.logger.info(f"从 {self.config_file} 加载配置成功")
            else:
                self.current_config = self.default_config.copy()
                self._save_config()
                self.logger.info(f"创建默认配置文件: {self.config_file}")
        except Exception as e:
            self.logger.error(f"加载配置出错: {str(e)}")
            self.current_config = self.default_config.copy()
    
    def _save_config(self):
        """保存配置到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.current_config, f, default_flow_style=False, allow_unicode=True)
                
            self.logger.info(f"配置保存成功: {self.config_file}")
            return True
        except Exception as e:
            self.logger.error(f"保存配置出错: {str(e)}")
            return False
    
    def get_config(self):
        """获取当前配置
        
        Returns:
            dict: 当前配置
        """
        return self.current_config
    
    def update_config(self, new_config):
        """更新配置
        
        Args:
            new_config: 新配置
            
        Returns:
            dict: 更新结果
        """
        try:
            # 递归更新配置
            def update_dict(d, u):
                for k, v in u.items():
                    if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                        update_dict(d[k], v)
                    else:
                        d[k] = v
            
            update_dict(self.current_config, new_config)
            
            # 保存配置
            if self._save_config():
                return {
                    "success": True,
                    "config": self.current_config
                }
            else:
                raise Exception("保存配置失败")
        except Exception as e:
            self.logger.error(f"更新配置出错: {str(e)}")
            raise
    
    def get_security_status(self):
        """获取安全状态
        
        Returns:
            dict: 安全状态信息
        """
        # 这里可以从安全防护引擎获取实时状态
        # 暂时使用静态数据
        return {
            "enabled": self.current_config["protection"]["enabled"],
            "status": "active" if self.current_config["protection"]["enabled"] else "disabled",
            "rules_active": sum(1 for rule, config in self.current_config["rules"].items() if config["enabled"]),
            "rules_total": len(self.current_config["rules"]),
            "last_updated": time.time()
        }
    
    def get_security_stats(self):
        """获取安全统计数据
        
        Returns:
            dict: 安全统计数据
        """
        # 这里可以从安全日志中读取统计数据
        # 暂时使用模拟数据
        self.stats = {
            "total_attacks": 247,
            "blocked_attacks": 235,
            "by_type": {
                "ddos": {"total": 102, "blocked": 99, "timestamp": time.time()},
                "mitm": {"total": 64, "blocked": 61, "timestamp": time.time()},
                "firmware": {"total": 35, "blocked": 32, "timestamp": time.time()},
                "credential": {"total": 46, "blocked": 43, "timestamp": time.time()}
            },
            "by_device": {
                "gateway": {"total": 78, "blocked": 75, "timestamp": time.time()},
                "router": {"total": 92, "blocked": 89, "timestamp": time.time()},
                "speaker": {"total": 33, "blocked": 31, "timestamp": time.time()},
                "camera": {"total": 44, "blocked": 40, "timestamp": time.time()}
            },
            "timeline": [
                {"time": time.time() - 3600 * 24, "count": 42},
                {"time": time.time() - 3600 * 18, "count": 53},
                {"time": time.time() - 3600 * 12, "count": 68},
                {"time": time.time() - 3600 * 6, "count": 84}
            ]
        }
        
        return self.stats