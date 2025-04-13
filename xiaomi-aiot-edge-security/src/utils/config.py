# src/utils/config.py
import os
import yaml
import json
from .logger import get_logger

class ConfigManager:
    """配置管理：加载和管理系统配置"""
    
    def __init__(self, config_dir='config'):
        self.logger = get_logger("ConfigManager")
        self.config_dir = config_dir
        self.configs = {}
        self._load_all_configs()
        self.logger.info("配置管理器初始化完成")

class Config(ConfigManager):
    """兼容旧版本的Config类"""
    pass

def load_config(config_dir='config'):
    """加载配置的快捷函数
    
    Args:
        config_dir: 配置目录路径
    
    Returns:
        ConfigManager实例
    """
    return ConfigManager(config_dir)
    
    def _load_all_configs(self):
        """加载所有配置文件"""
        # 确保配置目录存在
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            self.logger.info(f"创建配置目录: {self.config_dir}")
        
        # 加载所有YAML文件
        for filename in os.listdir(self.config_dir):
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                config_name = os.path.splitext(filename)[0]
                file_path = os.path.join(self.config_dir, filename)
                self._load_config(config_name, file_path)
    
    def _load_config(self, name, file_path):
        """加载单个配置文件
        
        Args:
            name: 配置名称
            file_path: 文件路径
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                self.configs[name] = config
                self.logger.info(f"加载配置文件: {file_path}")
        except Exception as e:
            self.logger.error(f"加载配置文件 {file_path} 出错: {str(e)}")
            self.configs[name] = {}
    
    def get(self, name, default=None):
        """获取配置
        
        Args:
            name: 配置名称
            default: 默认值
            
        Returns:
            配置值
        """
        # 支持点分隔的配置路径，例如 "security.rules.ddos.enabled"
        parts = name.split('.')
        
        if len(parts) == 1:
            return self.configs.get(name, default)
        else:
            config_name = parts[0]
            config = self.configs.get(config_name, {})
            
            for part in parts[1:]:
                if isinstance(config, dict) and part in config:
                    config = config[part]
                else:
                    return default
            
            return config
    
    def set(self, name, value):
        """设置配置
        
        Args:
            name: 配置名称
            value: 配置值
            
        Returns:
            bool: 是否设置成功
        """
        parts = name.split('.')
        
        if len(parts) == 1:
            self.configs[name] = value
            return True
        else:
            config_name = parts[0]
            if config_name not in self.configs:
                self.configs[config_name] = {}
            
            config = self.configs[config_name]
            for i, part in enumerate(parts[1:]):
                if i == len(parts) - 2:  # 最后一个部分
                    config[part] = value
                else:
                    if part not in config or not isinstance(config[part], dict):
                        config[part] = {}
                    config = config[part]
            
            return True
    
    def save(self, name):
        """保存配置到文件
        
        Args:
            name: 配置名称
            
        Returns:
            bool: 是否保存成功
        """
        if name not in self.configs:
            self.logger.warning(f"配置 {name} 不存在")
            return False
        
        try:
            file_path = os.path.join(self.config_dir, f"{name}.yaml")
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.configs[name], f, default_flow_style=False, allow_unicode=True)
                
            self.logger.info(f"配置保存成功: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"保存配置 {name} 出错: {str(e)}")
            return False
    
    def save_all(self):
        """保存所有配置
        
        Returns:
            bool: 是否全部保存成功
        """
        success = True
        for name in self.configs:
            if not self.save(name):
                success = False
        
        return success