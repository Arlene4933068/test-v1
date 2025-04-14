#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全节点模块
实现分布式安全防护框架中的安全节点
"""

import logging
import threading
import time
import json
import uuid
import socket
import hashlib
from typing import Dict, List, Any, Callable, Optional, Set, Tuple
import zmq
from .attack_detector import AttackDetector
from .protection_engine import ProtectionEngine
from .security_logger import SecurityLogger

class SecurityNode:
    """安全节点类，表示分布式安全框架中的一个节点"""
    
    def __init__(self, config: Dict[str, Any], node_id: str = None):
        """
        初始化安全节点
        
        Args:
            config: 节点配置
            node_id: 节点ID，如果未提供则自动生成
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.node_id = node_id or f"node_{uuid.uuid4().hex[:8]}"
        
        # 节点类型：'coordinator' 或 'worker'
        self.node_type = config.get("node_type", "worker")
        
        # 节点角色：可以是多个，如 ["detector", "protector", "logger"]
        self.roles = config.get("roles", ["detector", "protector"])
        
        # 节点状态
        self.state = {
            "status": "initializing",  # initializing, active, degraded, inactive
            "last_heartbeat": 0,
            "connected_nodes": 0
        }
        
        # 关联的设备ID
        self.associated_devices = config.get("associated_devices", [])
        
                # 网络配置
        self.network_config = config.get("network", {})
        self.host = self.network_config.get("host", "127.0.0.1")
        self.port = self.network_config.get("port", 5555)
        self.discovery_port = self.network_config.get("discovery_port", 5556)
        
        # 已知的其他节点
        self.known_nodes = {}  # {node_id: {"address": "ip:port", "type": "coordinator/worker", "last_seen": timestamp}}
        
        # 组件实例
        self.detector = None
        self.protection_engine = None
        self.security_logger = None
        
        # 防护策略
        self.protection_policies = config.get("protection_policies", {})
        
        # 通信上下文
        self.zmq_context = zmq.Context()
        self.message_socket = None
        self.discovery_socket = None
        
        # 线程
        self.discovery_thread = None
        self.message_thread = None
        self.heartbeat_thread = None
        self._stop_event = threading.Event()
        
        # 消息处理函数
        self.message_handlers = {
            "alert": self._handle_alert_message,
            "policy_update": self._handle_policy_update,
            "node_status": self._handle_node_status,
            "heartbeat": self._handle_heartbeat,
            "command": self._handle_command
        }
        
        self.logger.info(f"安全节点 {self.node_id} 已初始化，类型: {self.node_type}")
    
    def initialize_components(self):
        """初始化安全组件"""
        # 根据角色初始化必要的组件
        if "detector" in self.roles:
            detector_config = self.config.get("detector", {})
            self.detector = AttackDetector(detector_config)
            # 添加告警回调
            self.detector.add_alert_callback(self._on_attack_detected)
        
        if "protector" in self.roles:
            protection_config = self.config.get("protection", {})
            self.protection_engine = ProtectionEngine(protection_config)
        
        if "logger" in self.roles or True:  # 始终初始化日志记录器
            logger_config = self.config.get("logger", {})
            self.security_logger = SecurityLogger(logger_config)
    
    def start(self) -> bool:
        """
        启动安全节点
        
        Returns:
            bool: 启动成功返回True，否则返回False
        """
        try:
            # 初始化组件
            self.initialize_components()
            
            # 设置通信
            self._setup_communication()
            
            # 启动线程
            self._start_threads()
            
            # 更新状态
            self.state["status"] = "active"
            self.state["last_heartbeat"] = time.time()
            
            # 启动组件
            if self.detector:
                self.detector.start()
            if self.protection_engine:
                self.protection_engine.start()
            
            self.logger.info(f"安全节点 {self.node_id} 已启动")
            return True
        except Exception as e:
            self.logger.error(f"启动安全节点失败: {str(e)}")
            self.state["status"] = "inactive"
            return False
    
    def stop(self) -> bool:
        """
        停止安全节点
        
        Returns:
            bool: 停止成功返回True，否则返回False
        """
        try:
            # 发送离开通知
            self._broadcast_status("leaving")
            
            # 停止线程
            self._stop_event.set()
            
            # 停止组件
            if self.detector:
                self.detector.stop()
            if self.protection_engine:
                self.protection_engine.stop()
            
            # 等待线程结束
            if self.discovery_thread and self.discovery_thread.is_alive():
                self.discovery_thread.join(timeout=2.0)
            if self.message_thread and self.message_thread.is_alive():
                self.message_thread.join(timeout=2.0)
            if self.heartbeat_thread and self.heartbeat_thread.is_alive():
                self.heartbeat_thread.join(timeout=2.0)
            
            # 关闭套接字
            if self.message_socket:
                self.message_socket.close()
            if self.discovery_socket:
                self.discovery_socket.close()
            
            # 终止ZMQ上下文
            self.zmq_context.term()
            
            # 更新状态
            self.state["status"] = "inactive"
            
            self.logger.info(f"安全节点 {self.node_id} 已停止")
            return True
        except Exception as e:
            self.logger.error(f"停止安全节点失败: {str(e)}")
            return False
    
    def _setup_communication(self):
        """设置节点间通信"""
        # 设置消息套接字
        self.message_socket = self.zmq_context.socket(zmq.ROUTER if self.node_type == "coordinator" else zmq.DEALER)
        
        if self.node_type == "coordinator":
            # 协调器绑定端口等待连接
            self.message_socket.bind(f"tcp://{self.host}:{self.port}")
        else:
            # 工作节点连接到协调器
            coordinator_address = self.network_config.get("coordinator", f"127.0.0.1:{self.port}")
            self.message_socket.connect(f"tcp://{coordinator_address}")
            # 设置节点ID作为套接字标识
            self.message_socket.setsockopt_string(zmq.IDENTITY, self.node_id)
        
        # 设置发现套接字
        self.discovery_socket = self.zmq_context.socket(zmq.PUB if self.node_type == "coordinator" else zmq.SUB)
        
        if self.node_type == "coordinator":
            # 协调器广播发现信息
            self.discovery_socket.bind(f"tcp://{self.host}:{self.discovery_port}")
        else:
            # 工作节点监听发现信息
            coordinator_address = self.network_config.get("coordinator", f"127.0.0.1:{self.discovery_port}")
            self.discovery_socket.connect(f"tcp://{coordinator_address}")
            self.discovery_socket.setsockopt_string(zmq.SUBSCRIBE, "")
    
    def _start_threads(self):
        """启动工作线程"""
        # 启动发现线程
        self.discovery_thread = threading.Thread(target=self._discovery_loop)
        self.discovery_thread.daemon = True
        self.discovery_thread.start()
        
        # 启动消息处理线程
        self.message_thread = threading.Thread(target=self._message_loop)
        self.message_thread.daemon = True
        self.message_thread.start()
        
        # 启动心跳线程
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop)
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()
    
    def _discovery_loop(self):
        """节点发现循环"""
        while not self._stop_event.is_set():
            try:
                if self.node_type == "coordinator":
                    # 协调器广播网络信息
                    network_info = {
                        "type": "network_info",
                        "coordinator_id": self.node_id,
                        "message_port": self.port,
                        "discovery_port": self.discovery_port,
                        "timestamp": time.time()
                    }
                    self.discovery_socket.send_string(json.dumps(network_info))
                    self._stop_event.wait(10.0)  # 每10秒广播一次
                else:
                    # 工作节点处理发现消息
                    try:
                        message = self.discovery_socket.recv_string(flags=zmq.NOBLOCK)
                        data = json.loads(message)
                        if data.get("type") == "network_info":
                            coordinator_id = data.get("coordinator_id")
                            if coordinator_id and coordinator_id not in self.known_nodes:
                                self.known_nodes[coordinator_id] = {
                                    "address": f"{self.host}:{data.get('message_port', self.port)}",
                                    "type": "coordinator",
                                    "last_seen": time.time()
                                }
                                self.logger.info(f"发现协调器节点: {coordinator_id}")
                    except zmq.Again:
                        pass  # 没有消息，继续
                    self._stop_event.wait(0.1)  # 检查频率
            except Exception as e:
                self.logger.error(f"发现循环错误: {str(e)}")
                self._stop_event.wait(5.0)  # 错误后等待再次尝试
    
    def _message_loop(self):
        """消息处理循环"""
        while not self._stop_event.is_set():
            try:
                if self.node_type == "coordinator":
                    # 协调器处理来自工作节点的消息
                    try:
                        frames = self.message_socket.recv_multipart(flags=zmq.NOBLOCK)
                        if len(frames) >= 3:  # [sender_id, empty, message]
                            sender_id = frames[0].decode("utf-8")
                            message_data = json.loads(frames[2].decode("utf-8"))
                            self._process_message(sender_id, message_data)
                    except zmq.Again:
                        pass  # 没有消息，继续
                else:
                    # 工作节点处理来自协调器的消息
                    try:
                        frames = self.message_socket.recv_multipart(flags=zmq.NOBLOCK)
                        if len(frames) >= 2:  # [empty, message]
                            message_data = json.loads(frames[1].decode("utf-8"))
                            self._process_message("coordinator", message_data)
                    except zmq.Again:
                        pass  # 没有消息，继续
                
                self._stop_event.wait(0.01)  # 检查频率
            except Exception as e:
                self.logger.error(f"消息循环错误: {str(e)}")
                self._stop_event.wait(1.0)  # 错误后等待再次尝试
    
    def _heartbeat_loop(self):
        """心跳循环"""
        while not self._stop_event.is_set():
            try:
                # 发送心跳消息
                heartbeat_message = {
                    "type": "heartbeat",
                    "sender_id": self.node_id,
                    "sender_type": self.node_type,
                    "status": self.state["status"],
                    "roles": self.roles,
                    "timestamp": time.time()
                }
                
                if self.node_type == "coordinator":
                    # 协调器向所有工作节点广播心跳
                    for node_id in list(self.known_nodes.keys()):
                        try:
                            self.message_socket.send_multipart([
                                node_id.encode("utf-8"),
                                b"",
                                json.dumps(heartbeat_message).encode("utf-8")
                            ])
                        except Exception as e:
                            self.logger.warning(f"向节点 {node_id} 发送心跳失败: {str(e)}")
                else:
                    # 工作节点向协调器发送心跳
                    self.message_socket.send_multipart([
                        b"",
                        json.dumps(heartbeat_message).encode("utf-8")
                    ])
                
                # 更新自己的心跳时间
                self.state["last_heartbeat"] = time.time()
                
                # 检查其他节点的心跳
                current_time = time.time()
                for node_id in list(self.known_nodes.keys()):
                    last_seen = self.known_nodes[node_id].get("last_seen", 0)
                    if current_time - last_seen > 30.0:  # 30秒无响应认为节点离线
                        self.logger.warning(f"节点 {node_id} 可能已离线")
                        if self.node_type == "coordinator":
                            self._handle_node_offline(node_id)
                
                self._stop_event.wait(5.0)  # 每5秒发送一次心跳
            except Exception as e:
                self.logger.error(f"心跳循环错误: {str(e)}")
                self._stop_event.wait(5.0)  # 错误后等待再次尝试
    
    def _process_message(self, sender_id: str, message: Dict[str, Any]):
        """
        处理接收到的消息
        
        Args:
            sender_id: 发送者ID
            message: 消息数据
        """
        try:
            message_type = message.get("type")
            
            # 更新节点的最后可见时间
            if sender_id != "coordinator" and sender_id not in self.known_nodes:
                self.known_nodes[sender_id] = {
                    "address": "unknown",
                    "type": message.get("sender_type", "worker"),
                    "last_seen": time.time()
                }
            elif sender_id in self.known_nodes:
                self.known_nodes[sender_id]["last_seen"] = time.time()
            
            # 调用对应的消息处理函数
            if message_type in self.message_handlers:
                self.message_handlers[message_type](sender_id, message)
            else:
                self.logger.warning(f"收到未知类型的消息: {message_type}")
        except Exception as e:
            self.logger.error(f"处理消息时出错: {str(e)}")
    
    def _handle_alert_message(self, sender_id: str, message: Dict[str, Any]):
        """处理告警消息"""
        try:
            alert_data = message.get("alert_data", {})
            self.logger.info(f"收到来自 {sender_id} 的告警: {alert_data.get('type')}")
            
            # 记录告警
            if self.security_logger:
                self.security_logger.log_alert(alert_data)
            
            # 如果是协调器，广播给其他节点
            if self.node_type == "coordinator" and "broadcast" in message:
                self._broadcast_alert(alert_data, skip_node_id=sender_id)
            
            # 如果是保护者角色，处理告警
            if self.protection_engine and "protector" in self.roles:
                self.protection_engine.handle_alert(alert_data)
        except Exception as e:
            self.logger.error(f"处理告警消息时出错: {str(e)}")
    
    def _handle_policy_update(self, sender_id: str, message: Dict[str, Any]):
        """处理策略更新消息"""
        try:
            policies = message.get("policies", {})
            self.logger.info(f"收到来自 {sender_id} 的策略更新")
            
            # 更新本地策略
            self.protection_policies.update(policies)
            
            # 如果有保护引擎，更新其策略
            if self.protection_engine:
                self.protection_engine.update_policies(policies)
            
            # 如果是协调器，广播给其他节点
            if self.node_type == "coordinator" and "broadcast" in message:
                self._broadcast_policy_update(policies, skip_node_id=sender_id)
        except Exception as e:
            self.logger.error(f"处理策略更新消息时出错: {str(e)}")
    
    def _handle_node_status(self, sender_id: str, message: Dict[str, Any]):
        """处理节点状态消息"""
        try:
            status = message.get("status")
            if status == "leaving":
                self.logger.info(f"节点 {sender_id} 正在离开网络")
                if sender_id in self.known_nodes:
                    del self.known_nodes[sender_id]
            else:
                # 更新节点信息
                roles = message.get("roles", [])
                address = message.get("address", "unknown")
                
                self.logger.info(f"收到节点 {sender_id} 的状态更新: {status}")
                
                if sender_id not in self.known_nodes:
                    self.known_nodes[sender_id] = {
                        "address": address,
                        "type": message.get("node_type", "worker"),
                        "roles": roles,
                        "last_seen": time.time(),
                        "status": status
                    }
                else:
                    self.known_nodes[sender_id].update({
                        "roles": roles,
                        "address": address,
                        "last_seen": time.time(),
                        "status": status
                    })
                
                # 如果是协调器，广播给其他节点
                if self.node_type == "coordinator" and "broadcast" in message:
                    self._broadcast_node_status(sender_id, status, roles, address, skip_node_id=sender_id)
        except Exception as e:
            self.logger.error(f"处理节点状态消息时出错: {str(e)}")
    
    def _handle_heartbeat(self, sender_id: str, message: Dict[str, Any]):
        """处理心跳消息"""
        try:
            timestamp = message.get("timestamp")
            status = message.get("status")
            node_type = message.get("sender_type")
            roles = message.get("roles", [])
            
            if sender_id not in self.known_nodes:
                self.known_nodes[sender_id] = {
                    "address": "unknown",
                    "type": node_type,
                    "roles": roles,
                    "last_seen": timestamp,
                    "status": status
                }
            else:
                self.known_nodes[sender_id].update({
                    "last_seen": timestamp,
                    "status": status,
                    "type": node_type,
                    "roles": roles
                })
        except Exception as e:
            self.logger.error(f"处理心跳消息时出错: {str(e)}")
    
    def _handle_command(self, sender_id: str, message: Dict[str, Any]):
        """处理命令消息"""
        try:
            command = message.get("command")
            params = message.get("params", {})
            command_id = message.get("command_id", "unknown")
            
            self.logger.info(f"收到来自 {sender_id} 的命令: {command}")
            
            result = {"success": False, "message": "未知命令"}
            
            if command == "update_config":
                # 更新配置
                new_config = params.get("config", {})
                for key, value in new_config.items():
                    if key in self.config:
                        self.config[key] = value
                result = {"success": True, "message": "配置已更新"}
            
            elif command == "change_role":
                # 更改角色
                new_roles = params.get("roles", [])
                if new_roles:
                    old_roles = self.roles.copy()
                    self.roles = new_roles
                    result = {"success": True, "message": f"角色已从 {old_roles} 更改为 {new_roles}"}
                else:
                    result = {"success": False, "message": "未提供新角色"}
            
            elif command == "restart":
                # 重启节点
                threading.Thread(target=self._delayed_restart).start()
                result = {"success": True, "message": "节点正在重启"}
            
            # 发送命令响应
            response = {
                "type": "command_response",
                "command_id": command_id,
                "sender_id": self.node_id,
                "result": result
            }
            
            if self.node_type == "coordinator":
                self.message_socket.send_multipart([
                    sender_id.encode("utf-8"),
                    b"",
                    json.dumps(response).encode("utf-8")
                ])
            else:
                self.message_socket.send_multipart([
                    b"",
                    json.dumps(response).encode("utf-8")
                ])
        except Exception as e:
            self.logger.error(f"处理命令消息时出错: {str(e)}")
    
    def _delayed_restart(self):
        """延迟重启节点"""
        time.sleep(1.0)  # 等待1秒让响应先发出
        self.stop()
        time.sleep(1.0)
        self.start()
    
    def _handle_node_offline(self, node_id: str):
        """
        处理节点离线事件
        
        Args:
            node_id: 离线节点的ID
        """
        if node_id in self.known_nodes:
            self.logger.warning(f"节点 {node_id} 已标记为离线")
            
            # 如果是协调器，通知其他节点
            if self.node_type == "coordinator":
                offline_message = {
                    "type": "node_status",
                    "sender_id": node_id,
                    "status": "offline",
                    "timestamp": time.time()
                }
                
                for other_node_id in list(self.known_nodes.keys()):
                    if other_node_id != node_id:
                        try:
                            self.message_socket.send_multipart([
                                other_node_id.encode("utf-8"),
                                b"",
                                json.dumps(offline_message).encode("utf-8")
                            ])
                        except Exception as e:
                            self.logger.warning(f"通知节点 {other_node_id} 关于 {node_id} 离线状态失败: {str(e)}")
            
            # 从已知节点中移除
            del self.known_nodes[node_id]
            self.state["connected_nodes"] = len(self.known_nodes)
    
    def _on_attack_detected(self, alert_data: Dict[str, Any]):
        """
        攻击检测回调函数
        
        Args:
            alert_data: 告警数据
        """
        # 记录告警
        if self.security_logger:
            self.security_logger.log_alert(alert_data)
        
        # 如果有保护引擎，处理告警
        if self.protection_engine and "protector" in self.roles:
            self.protection_engine.handle_alert(alert_data)
        
        # 发送告警消息
        alert_message = {
            "type": "alert",
            "sender_id": self.node_id,
            "sender_type": self.node_type,
            "alert_data": alert_data,
            "broadcast": True,
            "timestamp": time.time()
        }
        
        if self.node_type == "coordinator":
            # 广播给所有工作节点
            for node_id in self.known_nodes:
                try:
                    self.message_socket.send_multipart([
                        node_id.encode("utf-8"),
                        b"",
                        json.dumps(alert_message).encode("utf-8")
                    ])
                except Exception as e:
                    self.logger.warning(f"向节点 {node_id} 发送告警失败: {str(e)}")
        else:
            # 发送给协调器
            self.message_socket.send_multipart([
                b"",
                json.dumps(alert_message).encode("utf-8")
            ])
    
    def _broadcast_alert(self, alert_data: Dict[str, Any], skip_node_id: str = None):
        """
        广播告警到所有节点
        
        Args:
            alert_data: 告警数据
            skip_node_id: 跳过的节点ID
        """
        if self.node_type != "coordinator":
            self.logger.warning("只有协调器可以广播告警")
            return
        
        alert_message = {
            "type": "alert",
            "sender_id": self.node_id,
            "sender_type": self.node_type,
            "alert_data": alert_data,
            "timestamp": time.time()
        }
        
        for node_id in list(self.known_nodes.keys()):
            if node_id != skip_node_id:
                try:
                    self.message_socket.send_multipart([
                        node_id.encode("utf-8"),
                        b"",
                        json.dumps(alert_message).encode("utf-8")
                    ])
                except Exception as e:
                    self.logger.warning(f"向节点 {node_id} 广播告警失败: {str(e)}")
    
    def _broadcast_policy_update(self, policies: Dict[str, Any], skip_node_id: str = None):
        """
        广播策略更新到所有节点
        
        Args:
            policies: 策略数据
            skip_node_id: 跳过的节点ID
        """
        if self.node_type != "coordinator":
            self.logger.warning("只有协调器可以广播策略更新")
            return
        
        policy_message = {
            "type": "policy_update",
            "sender_id": self.node_id,
            "sender_type": self.node_type,
            "policies": policies,
            "timestamp": time.time()
        }
        
        for node_id in list(self.known_nodes.keys()):
            if node_id != skip_node_id:
                try:
                    self.message_socket.send_multipart([
                        node_id.encode("utf-8"),
                        b"",
                        json.dumps(policy_message).encode("utf-8")
                    ])
                except Exception as e:
                    self.logger.warning(f"向节点 {node_id} 广播策略更新失败: {str(e)}")
    
    def _broadcast_node_status(self, target_node_id: str, status: str, roles: List[str], 
                              address: str, skip_node_id: str = None):
        """
        广播节点状态到所有节点
        
        Args:
            target_node_id: 目标节点ID
            status: 节点状态
            roles: 节点角色
            address: 节点地址
            skip_node_id: 跳过的节点ID
        """
        if self.node_type != "coordinator":
            self.logger.warning("只有协调器可以广播节点状态")
            return
        
        status_message = {
            "type": "node_status",
            "sender_id": self.node_id,
            "sender_type": self.node_type,
            "target_id": target_node_id,
            "status": status,
            "roles": roles,
            "address": address,
            "timestamp": time.time()
        }
        
        for node_id in list(self.known_nodes.keys()):
            if node_id != skip_node_id:
                try:
                    self.message_socket.send_multipart([
                        node_id.encode("utf-8"),
                        b"",
                        json.dumps(status_message).encode("utf-8")
                    ])
                except Exception as e:
                    self.logger.warning(f"向节点 {node_id} 广播节点状态失败: {str(e)}")
    
    def _broadcast_status(self, status: str):
        """
        广播自身状态
        
        Args:
            status: 状态值
        """
        status_message = {
            "type": "node_status",
            "sender_id": self.node_id,
            "sender_type": self.node_type,
            "status": status,
            "roles": self.roles,
            "address": f"{self.host}:{self.port}",
            "broadcast": True,
            "timestamp": time.time()
        }
        
        if self.node_type == "coordinator":
            # 广播给所有工作节点
            for node_id in list(self.known_nodes.keys()):
                try:
                    self.message_socket.send_multipart([
                        node_id.encode("utf-8"),
                        b"",
                        json.dumps(status_message).encode("utf-8")
                    ])
                except Exception:
                    pass  # 忽略错误
        else:
            # 发送给协调器
            try:
                self.message_socket.send_multipart([
                    b"",
                    json.dumps(status_message).encode("utf-8")
                ])
            except Exception:
                pass  # 忽略错误