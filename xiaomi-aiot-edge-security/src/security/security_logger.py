"""
小米AIoT边缘安全防护研究平台 - 安全日志记录
负责记录和保存安全相关事件
"""

import logging
import os
import json
import time
import yaml
from datetime import datetime
from typing import Dict, Any, List, Optional

class SecurityLogger:
    """安全日志记录器，负责记录和管理安全相关事件"""
    
    def __init__(self, config_path: str = "../config/security.yaml"):
        """
        初始化安全日志记录器
        
        Args:
            config_path: 安全配置文件路径
        """
        self.logger = logging.getLogger("security.logger")
        self.config = self._load_config(config_path)
        self.log_dir = self.config.get('log_dir', '../logs/security')
        self.event_log_file = os.path.join(self.log_dir, 'security_events.log')
        self.alert_log_file = os.path.join(self.log_dir, 'security_alerts.log')
        self.action_log_file = os.path.join(self.log_dir, 'security_actions.log')
        
        # 确保日志目录存在
        os.makedirs(self.log_dir, exist_ok=True)
    
    def _load_config(self, config_path: str) -> Dict:
        """
        加载安全配置
        
        Args:
            config_path: 安全配置文件路径
            
        Returns:
            配置字典
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config.get('security_logger', {})
        except Exception as e:
            self.logger.error(f"加载安全配置文件失败: {str(e)}")
            return {}
    
    def log_event(self, event_type: str, device_id: str, details: Dict[str, Any], severity: str = 'info') -> str:
        """
        记录安全事件
        
        Args:
            event_type: 事件类型
            device_id: 设备ID
            details: 事件详情
            severity: 事件严重程度 (info, warning, critical)
            
        Returns:
            事件ID
        """
        event_id = f"evt_{int(time.time())}_{device_id}"
        timestamp = datetime.now().isoformat()
        
        event = {
            'id': event_id,
            'timestamp': timestamp,
            'type': event_type,
            'device_id': device_id,
            'severity': severity,
            'details': details
        }
        
        try:
            with open(self.event_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(event) + '\n')
            
            self.logger.info(f"安全事件已记录: {event_id} - {event_type} - {device_id}")
        except Exception as e:
            self.logger.error(f"记录安全事件失败: {str(e)}")
        
        return event_id
    
    def log_alert(self, alert_type: str, device_id: str, threat_info: Dict[str, Any], 
                  confidence: float, severity: str = 'high') -> str:
        """
        记录安全警报
        
        Args:
            alert_type: 警报类型
            device_id: 设备ID
            threat_info: 威胁信息
            confidence: 置信度 (0.0-1.0)
            severity: 警报严重程度 (low, medium, high, critical)
            
        Returns:
            警报ID
        """
        alert_id = f"alt_{int(time.time())}_{device_id}"
        timestamp = datetime.now().isoformat()
        
        alert = {
            'id': alert_id,
            'timestamp': timestamp,
            'type': alert_type,
            'device_id': device_id,
            'threat_info': threat_info,
            'confidence': confidence,
            'severity': severity,
            'status': 'new'
        }
        
        try:
            with open(self.alert_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(alert) + '\n')
            
            self.logger.warning(f"安全警报已记录: {alert_id} - {alert_type} - {device_id} - 严重程度: {severity}")
        except Exception as e:
            self.logger.error(f"记录安全警报失败: {str(e)}")
        
        return alert_id
    
    def log_action(self, action_type: str, device_id: str, action_details: Dict[str, Any], 
                   alert_id: Optional[str] = None, result: str = 'success') -> str:
        """
        记录安全操作
        
        Args:
            action_type: 操作类型
            device_id: 设备ID
            action_details: 操作详情
            alert_id: 关联的警报ID（如果有）
            result: 操作结果 (success, failure, partial)
            
        Returns:
            操作ID
        """
        action_id = f"act_{int(time.time())}_{device_id}"
        timestamp = datetime.now().isoformat()
        
        action = {
            'id': action_id,
            'timestamp': timestamp,
            'type': action_type,
            'device_id': device_id,
            'details': action_details,
            'alert_id': alert_id,
            'result': result
        }
        
        try:
            with open(self.action_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(action) + '\n')
            
            self.logger.info(f"安全操作已记录: {action_id} - {action_type} - {device_id} - 结果: {result}")
        except Exception as e:
            self.logger.error(f"记录安全操作失败: {str(e)}")
        
        return action_id
    
    def get_recent_events(self, limit: int = 100, device_id: Optional[str] = None, 
                         event_type: Optional[str] = None) -> List[Dict]:
        """
        获取最近的安全事件
        
        Args:
            limit: 返回的最大事件数
            device_id: 过滤指定设备ID（可选）
            event_type: 过滤指定事件类型（可选）
            
        Returns:
            事件列表
        """
        events = []
        
        try:
            if os.path.exists(self.event_log_file):
                with open(self.event_log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            event = json.loads(line.strip())
                            
                            # 应用过滤条件
                            if device_id and event.get('device_id') != device_id:
                                continue
                            if event_type and event.get('type') != event_type:
                                continue
                                
                            events.append(event)
                            if len(events) >= limit:
                                break
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            self.logger.error(f"获取安全事件失败: {str(e)}")
        
        # 按时间戳排序，最新的在前
        events.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return events[:limit]
    
    def get_recent_alerts(self, limit: int = 100, status: Optional[str] = None, 
                         severity: Optional[str] = None) -> List[Dict]:
        """
        获取最近的安全警报
        
        Args:
            limit: 返回的最大警报数
            status: 过滤指定状态（可选）：new, acknowledged, resolved
            severity: 过滤指定严重程度（可选）：low, medium, high, critical
            
        Returns:
            警报列表
        """
        alerts = []
        
        try:
            if os.path.exists(self.alert_log_file):
                with open(self.alert_log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            alert = json.loads(line.strip())
                            
                            # 应用过滤条件
                            if status and alert.get('status') != status:
                                continue
                            if severity and alert.get('severity') != severity:
                                continue
                                
                            alerts.append(alert)
                            if len(alerts) >= limit:
                                break
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            self.logger.error(f"获取安全警报失败: {str(e)}")
        
        # 按时间戳排序，最新的在前
        alerts.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return alerts[:limit]
    
    def update_alert_status(self, alert_id: str, new_status: str) -> bool:
        """
        更新警报状态
        
        Args:
            alert_id: 警报ID
            new_status: 新状态 (new, acknowledged, resolved)
            
        Returns:
            是否更新成功
        """
        if new_status not in ['new', 'acknowledged', 'resolved']:
            self.logger.error(f"无效的警报状态: {new_status}")
            return False
            
        alerts = []
        updated = False
        
        try:
            # 读取所有警报
            if os.path.exists(self.alert_log_file):
                with open(self.alert_log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            alert = json.loads(line.strip())
                            if alert.get('id') == alert_id:  # 找到要更新的警报
                                alert['status'] = new_status
                                alert['updated_at'] = datetime.now().isoformat()
                                updated = True
                            alerts.append(alert)
                        except json.JSONDecodeError:
                            continue
            
            # 如果找到并更新了警报，重写警报文件
            if updated:
                with open(self.alert_log_file, 'w', encoding='utf-8') as f:
                    for alert in alerts:
                        f.write(json.dumps(alert) + '\n')
                
                self.logger.info(f"警报 {alert_id} 状态已更新为 {new_status}")
                return True
            else:
                self.logger.warning(f"未找到警报: {alert_id}")
                return False
        except Exception as e:
            self.logger.error(f"更新警报状态失败: {str(e)}")
            return False
    
    def generate_daily_summary(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        生成每日安全摘要
        
        Args:
            date: 日期字符串 (YYYY-MM-DD)，默认为当天
            
        Returns:
            安全摘要数据
        """
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # 当天开始和结束的时间戳
        date_start = f"{date}T00:00:00"
        date_end = f"{date}T23:59:59"
        
        summary = {
            'date': date,
            'events': {
                'total': 0,
                'by_type': {},
                'by_severity': {}
            },
            'alerts': {
                'total': 0,
                'by_type': {},
                'by_severity': {},
                'by_status': {}
            },
            'actions': {
                'total': 0,
                'by_type': {},
                'by_result': {}
            }
        }
        
        # 处理事件日志
        try:
            if os.path.exists(self.event_log_file):
                with open(self.event_log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            event = json.loads(line.strip())
                            timestamp = event.get('timestamp', '')
                            
                            # 检查事件是否在指定日期内
                            if date_start <= timestamp <= date_end:
                                summary['events']['total'] += 1
                                
                                # 按类型统计
                                event_type = event.get('type', 'unknown')
                                summary['events']['by_type'][event_type] = summary['events']['by_type'].get(event_type, 0) + 1
                                
                                # 按严重程度统计
                                severity = event.get('severity', 'info')
                                summary['events']['by_severity'][severity] = summary['events']['by_severity'].get(severity, 0) + 1
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            self.logger.error(f"处理事件日志失败: {str(e)}")
        
        # 处理警报日志
        try:
            if os.path.exists(self.alert_log_file):
                with open(self.alert_log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            alert = json.loads(line.strip())
                            timestamp = alert.get('timestamp', '')
                            
                            # 检查警报是否在指定日期内
                            if date_start <= timestamp <= date_end:
                                summary['alerts']['total'] += 1
                                
                                # 按类型统计
                                alert_type = alert.get('type', 'unknown')
                                summary['alerts']['by_type'][alert_type] = summary['alerts']['by_type'].get(alert_type, 0) + 1
                                
                                # 按严重程度统计
                                severity = alert.get('severity', 'medium')
                                summary['alerts']['by_severity'][severity] = summary['alerts']['by_severity'].get(severity, 0) + 1
                                
                                # 按状态统计
                                status = alert.get('status', 'new')
                                summary['alerts']['by_status'][status] = summary['alerts']['by_status'].get(status, 0) + 1
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            self.logger.error(f"处理警报日志失败: {str(e)}")
        
        # 处理操作日志
        try:
            if os.path.exists(self.action_log_file):
                with open(self.action_log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            action = json.loads(line.strip())
                            timestamp = action.get('timestamp', '')
                            
                            # 检查操作是否在指定日期内
                            if date_start <= timestamp <= date_end:
                                summary['actions']['total'] += 1
                                
                                # 按类型统计
                                action_type = action.get('type', 'unknown')
                                summary['actions']['by_type'][action_type] = summary['actions']['by_type'].get(action_type, 0) + 1
                                
                                # 按结果统计
                                result = action.get('result', 'unknown')
                                summary['actions']['by_result'][result] = summary['actions']['by_result'].get(result, 0) + 1
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            self.logger.error(f"处理操作日志失败: {str(e)}")
        
        return summary