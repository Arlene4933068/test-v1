#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
攻击防护日志记录模块
负责记录和分析安全事件和错误
"""

import os
import json
import time
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union

# 设置日志
logger = logging.getLogger(__name__)

class AttackLogger:
    """攻击防护日志记录器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.log_dir = config.get("log_dir", "data/attack_logs")
        self.db_path = os.path.join(self.log_dir, "attack_events.db")
        self.retention_days = config.get("attack_log_retention_days", 30)
        
        # 确保日志目录存在
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        # 初始化数据库
        self._initialize_database()
        logger.info(f"攻击日志记录器初始化完成，数据将保存在: {self.db_path}")
    
    def _initialize_database(self):
        """初始化SQLite数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建攻击事件表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS attack_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                device_id TEXT NOT NULL,
                attack_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                source_ip TEXT,
                destination_ip TEXT,
                description TEXT,
                raw_data TEXT,
                handled BOOLEAN DEFAULT FALSE
            )
            ''')
            
            # 创建错误日志表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS error_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                component TEXT NOT NULL,
                error_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT,
                stack_trace TEXT
            )
            ''')
            
            # 创建索引以加速查询
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_attack_timestamp ON attack_events(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_attack_device ON attack_events(device_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_attack_type ON attack_events(attack_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_error_timestamp ON error_logs(timestamp)')
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"初始化数据库失败: {str(e)}")
    
    def log_attack_event(self, event_data: Dict[str, Any]) -> int:
        """记录攻击事件
        
        参数:
            event_data: 包含攻击事件详情的字典
            
        返回:
            事件ID
        """
        required_fields = ['device_id', 'attack_type', 'severity', 'description']
        for field in required_fields:
            if field not in event_data:
                logger.error(f"攻击事件缺少必要字段: {field}")
                return -1
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 准备数据
            current_time = int(time.time())
            
            # 插入记录
            cursor.execute('''
            INSERT INTO attack_events 
            (timestamp, device_id, attack_type, severity, source_ip, destination_ip, description, raw_data, handled)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                current_time,
                event_data['device_id'],
                event_data['attack_type'],
                event_data['severity'],
                event_data.get('source_ip', ''),
                event_data.get('destination_ip', ''),
                event_data['description'],
                json.dumps(event_data.get('raw_data', {})),
                event_data.get('handled', False)
            ))
            
            event_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # 记录到标准日志
            logger.warning(
                f"攻击事件 [ID:{event_id}]: {event_data['attack_type']} "
                f"设备:{event_data['device_id']} 严重性:{event_data['severity']}"
            )
            
            return event_id
        except Exception as e:
            logger.error(f"记录攻击事件失败: {str(e)}")
            return -1
    
    def log_error(self, error_data: Dict[str, Any]) -> int:
        """记录错误信息
        
        参数:
            error_data: 包含错误详情的字典
            
        返回:
            错误ID
        """
        required_fields = ['component', 'error_type', 'severity', 'description']
        for field in required_fields:
            if field not in error_data:
                logger.error(f"错误日志缺少必要字段: {field}")
                return -1
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 准备数据
            current_time = int(time.time())
            
            # 插入记录
            cursor.execute('''
            INSERT INTO error_logs 
            (timestamp, component, error_type, severity, description, stack_trace)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                current_time,
                error_data['component'],
                error_data['error_type'],
                error_data['severity'],
                error_data['description'],
                error_data.get('stack_trace', '')
            ))
            
            error_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # 记录到标准日志
            log_method = logger.error if error_data['severity'] in ['high', 'critical'] else logger.warning
            log_method(
                f"错误 [ID:{error_id}]: {error_data['error_type']} "
                f"组件:{error_data['component']} 严重性:{error_data['severity']}"
            )
            
            return error_id
        except Exception as e:
            logger.error(f"记录错误信息失败: {str(e)}")
            return -1
    
    def get_attack_events(self, 
                         filters: Optional[Dict[str, Any]] = None, 
                         start_time: Optional[int] = None, 
                         end_time: Optional[int] = None,
                         limit: int = 50,
                         offset: int = 0) -> List[Dict[str, Any]]:
        """获取攻击事件
        
        参数:
            filters: 过滤条件
            start_time: 开始时间戳
            end_time: 结束时间戳
            limit: 最大返回条数
            offset: 偏移量
            
        返回:
            事件列表
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 构建查询
            query = "SELECT * FROM attack_events WHERE 1=1"
            params = []
            
            # 添加时间过滤
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)
                
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)
            
            # 添加其他过滤条件
            if filters:
                for key, value in filters.items():
                    if key in ['device_id', 'attack_type', 'severity', 'source_ip', 'destination_ip', 'handled']:
                        query += f" AND {key} = ?"
                        params.append(value)
            
            # 添加排序、分页
            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            # 执行查询
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # 转换结果
            results = []
            for row in rows:
                event = dict(row)
                # 解析JSON字段
                if 'raw_data' in event and event['raw_data']:
                    try:
                        event['raw_data'] = json.loads(event['raw_data'])
                    except:
                        pass
                results.append(event)
            
            conn.close()
            return results
        except Exception as e:
            logger.error(f"获取攻击事件失败: {str(e)}")
            return []
    
    def get_error_logs(self, 
                      filters: Optional[Dict[str, Any]] = None, 
                      start_time: Optional[int] = None, 
                      end_time: Optional[int] = None,
                      limit: int = 50,
                      offset: int = 0) -> List[Dict[str, Any]]:
        """获取错误日志
        
        参数:
            filters: 过滤条件
            start_time: 开始时间戳
            end_time: 结束时间戳
            limit: 最大返回条数
            offset: 偏移量
            
        返回:
            错误日志列表
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 构建查询
            query = "SELECT * FROM error_logs WHERE 1=1"
            params = []
            
            # 添加时间过滤
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)
                
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)
            
            # 添加其他过滤条件
            if filters:
                for key, value in filters.items():
                    if key in ['component', 'error_type', 'severity']:
                        query += f" AND {key} = ?"
                        params.append(value)
            
            # 添加排序、分页
            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            # 执行查询
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # 转换结果
            results = [dict(row) for row in rows]
            conn.close()
            return results
        except Exception as e:
            logger.error(f"获取错误日志失败: {str(e)}")
            return []
    
    def get_attack_statistics(self, 
                            group_by: str = 'day', 
                            start_time: Optional[int] = None, 
                            end_time: Optional[int] = None) -> Dict[str, Any]:
        """获取攻击统计信息
        
        参数:
            group_by: 分组方式 (day, hour, type, device, severity)
            start_time: 开始时间戳
            end_time: 结束时间戳
            
        返回:
            统计信息
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # 确定默认时间范围
            if not end_time:
                end_time = int(time.time())
            if not start_time:
                # 默认最近7天
                start_time = end_time - (7 * 24 * 60 * 60)
            
            # 根据分组方式构建不同查询
            if group_by == 'day':
                query = """
                SELECT 
                    strftime('%Y-%m-%d', datetime(timestamp, 'unixepoch')) as period,
                    COUNT(*) as count
                FROM attack_events
                WHERE timestamp >= ? AND timestamp <= ?
                GROUP BY period
                ORDER BY period
                """
            elif group_by == 'hour':
                query = """
                SELECT 
                    strftime('%Y-%m-%d %H:00', datetime(timestamp, 'unixepoch')) as period,
                    COUNT(*) as count
                FROM attack_events
                WHERE timestamp >= ? AND timestamp <= ?
                GROUP BY period
                ORDER BY period
                """
            elif group_by == 'type':
                query = """
                SELECT 
                    attack_type as group_value,
                    COUNT(*) as count
                FROM attack_events
                WHERE timestamp >= ? AND timestamp <= ?
                GROUP BY group_value
                ORDER BY count DESC
                """
            elif group_by == 'device':
                query = """
                SELECT 
                    device_id as group_value,
                    COUNT(*) as count
                FROM attack_events
                WHERE timestamp >= ? AND timestamp <= ?
                GROUP BY group_value
                ORDER BY count DESC
                """
            elif group_by == 'severity':
                query = """
                SELECT 
                    severity as group_value,
                    COUNT(*) as count
                FROM attack_events
                WHERE timestamp >= ? AND timestamp <= ?
                GROUP BY group_value
                ORDER BY CASE 
                    WHEN group_value = 'critical' THEN 1
                    WHEN group_value = 'high' THEN 2
                    WHEN group_value = 'medium' THEN 3
                    WHEN group_value = 'low' THEN 4
                    ELSE 5
                END
                """
            else:
                return {"error": f"不支持的分组方式: {group_by}"}
            
            # 执行查询
            cursor.execute(query, (start_time, end_time))
            rows = cursor.fetchall()
            
            # 转换结果
            results = [dict(row) for row in rows]
            
            # 获取总计
            cursor.execute("SELECT COUNT(*) as total FROM attack_events WHERE timestamp >= ? AND timestamp <= ?", 
                           (start_time, end_time))
            total = cursor.fetchone()['total']
            
            conn.close()
            
            # 构建统计结果
            return {
                "total": total,
                "period": {
                    "start": datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S'),
                    "end": datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
                },
                "group_by": group_by,
                "data": results
            }
        except Exception as e:
            logger.error(f"获取攻击统计信息失败: {str(e)}")
            return {"error": str(e)}
    
    def cleanup_old_logs(self):
        """清理过期日志"""
        try:
            # 计算截止时间
            cutoff_time = int(time.time() - (self.retention_days * 24 * 60 * 60))
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 删除旧的攻击事件
            cursor.execute("DELETE FROM attack_events WHERE timestamp < ?", (cutoff_time,))
            attack_count = cursor.rowcount
            
            # 删除旧的错误日志
            cursor.execute("DELETE FROM error_logs WHERE timestamp < ?", (cutoff_time,))
            error_count = cursor.rowcount
            
            # 压缩数据库
            cursor.execute("VACUUM")
            
            conn.commit()
            conn.close()
            
            logger.info(f"已清理过期日志: {attack_count} 条攻击事件, {error_count} 条错误日志")
            return {"attack_count": attack_count, "error_count": error_count}
        except Exception as e:
            logger.error(f"清理过期日志失败: {str(e)}")
            return {"error": str(e)}
    
    def mark_event_handled(self, event_id: int, handled: bool = True) -> bool:
        """将事件标记为已处理/未处理"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("UPDATE attack_events SET handled = ? WHERE id = ?", (handled, event_id))
            success = cursor.rowcount > 0
            
            conn.commit()
            conn.close()
            
            if success:
                logger.info(f"事件 {event_id} 已标记为{'已' if handled else '未'}处理")
            else:
                logger.warning(f"找不到事件 {event_id}")
                
            return success
        except Exception as e:
            logger.error(f"标记事件状态失败: {str(e)}")
            return False