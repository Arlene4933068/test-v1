"""
攻击检测器 - 检测针对边缘设备的攻击
"""
import time
import logging
import threading
from typing import Dict, Any, List, Optional, Callable

class AttackDetector:
    """
    攻击检测器，用于检测针对边缘设备的各种攻击
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化攻击检测器
        
        Args:
            config: 检测器配置
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.detectors = {}  # 检测器字典
        self.rules = {}  # 检测规则字典
        self.alert_callbacks = []  # 警报回调函数列表
        self.is_running = False
        self.detector_thread = None
        self.device_data = {}  # 设备数据缓存
        self.detection_interval = config.get('detection_interval', 1.0)  # 检测间隔，单位秒
        self.initialize_detectors()
    
    def initialize_detectors(self):
        """初始化各种攻击检测器"""
        # 初始化DDoS攻击检测器
        self.register_detector("ddos", self._detect_ddos_attack)
        
        # 初始化中间人攻击检测器
        self.register_detector("mitm", self._detect_mitm_attack)
        
        # 初始化固件攻击检测器
        self.register_detector("firmware", self._detect_firmware_attack)
        
        # 初始化凭证攻击检测器
        self.register_detector("credential", self._detect_credential_attack)
        
        # 初始化异常行为检测器
        self.register_detector("anomaly", self._detect_anomaly_behavior)
    
    def register_detector(self, detector_name: str, detector_func: Callable):
        """
        注册攻击检测器
        
        Args:
            detector_name: 检测器名称
            detector_func: 检测器函数
        """
        self.detectors[detector_name] = detector_func
        self.logger.info(f"注册攻击检测器: {detector_name}")
    
    def register_rule(self, rule_name: str, rule_config: Dict[str, Any]):
        """
        注册检测规则
        
        Args:
            rule_name: 规则名称
            rule_config: 规则配置
        """
        self.rules[rule_name] = rule_config
        self.logger.info(f"注册检测规则: {rule_name}")
    
    def register_alert_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """
        注册警报回调函数
        
        Args:
            callback: 回调函数，接收警报信息字典
        """
        self.alert_callbacks.append(callback)
    
    def update_device_data(self, device_id: str, data: Dict[str, Any]):
        """
        更新设备数据缓存
        
        Args:
            device_id: 设备ID
            data: 设备数据
        """
        if device_id not in self.device_data:
            self.device_data[device_id] = {
                'last_update': time.time(),
                'data_history': [],
                'connection_attempts': 0,
                'failed_auth_attempts': 0,
                'abnormal_commands': 0
            }
        
        # 更新最后更新时间
        self.device_data[device_id]['last_update'] = time.time()
        
        # 添加数据到历史记录
        data_with_timestamp = {'timestamp': time.time(), 'data': data}
        self.device_data[device_id]['data_history'].append(data_with_timestamp)
        
        # 限制历史记录大小
        max_history = self.config.get('max_history_size', 100)
        if len(self.device_data[device_id]['data_history']) > max_history:
            self.device_data[device_id]['data_history'].pop(0)
    
    def start(self):
        """启动攻击检测"""
        if self.is_running:
            self.logger.warning("攻击检测器已在运行")
            return
        
        self.is_running = True
        self.detector_thread = threading.Thread(target=self._detection_loop)
        self.detector_thread.daemon = True
        self.detector_thread.start()
        self.logger.info("攻击检测器已启动")
    
    def stop(self):
        """停止攻击检测"""
        if not self.is_running:
            self.logger.warning("攻击检测器未在运行")
            return
        
        self.is_running = False
        if self.detector_thread:
            self.detector_thread.join(timeout=5.0)
        self.logger.info("攻击检测器已停止")
    
    def _detection_loop(self):
        """检测循环"""
        while self.is_running:
            try:
                # 执行所有注册的检测器
                for detector_name, detector_func in self.detectors.items():
                    try:
                        detector_func()
                    except Exception as e:
                        self.logger.error(f"检测器 {detector_name} 执行异常: {str(e)}")
                
                # 间隔一段时间
                time.sleep(self.detection_interval)
            except Exception as e:
                self.logger.error(f"检测循环异常: {str(e)}")
    
    def trigger_alert(self, alert_info: Dict[str, Any]):
        """
        触发警报
        
        Args:
            alert_info: 警报信息
        """
        # 添加时间戳
        alert_info['timestamp'] = time.time()
        
        # 记录警报
        self.logger.warning(f"检测到攻击: {alert_info['type']} - {alert_info['description']}")
        
        # 调用所有注册的回调函数
        for callback in self.alert_callbacks:
            try:
                callback(alert_info)
            except Exception as e:
                self.logger.error(f"警报回调函数执行异常: {str(e)}")
    
    def _detect_ddos_attack(self):
        """检测DDoS攻击"""
        # 实现DDoS攻击检测逻辑
        threshold = self.config.get('ddos_threshold', 100)
        window_size = self.config.get('ddos_window', 60)  # 窗口大小，单位秒
        current_time = time.time()
        
        for device_id, device_data in self.device_data.items():
            # 计算窗口内的请求数
            request_count = 0
            for record in device_data['data_history']:
                if current_time - record['timestamp'] <= window_size:
                    request_count += 1
            
            # 如果请求数超过阈值，触发警报
            if request_count > threshold:
                self.trigger_alert({
                    'type': 'ddos',
                    'device_id': device_id,
                    'description': f"DDoS攻击: {request_count} 个请求在 {window_size} 秒内",
                    'request_count': request_count,
                    'threshold': threshold,
                    'window_size': window_size
                })
    
    def _detect_mitm_attack(self):
        """检测中间人攻击"""
        # 实现中间人攻击检测逻辑
        # 检查通信延迟异常、证书变化等
        for device_id, device_data in self.device_data.items():
            # 获取最近的数据记录
            if not device_data['data_history']:
                continue
            
            latest_data = device_data['data_history'][-1]['data']
            
            # 检查是否存在证书警告
            if latest_data.get('ssl_warning', False):
                self.trigger_alert({
                    'type': 'mitm',
                    'device_id': device_id,
                    'description': "可能存在中间人攻击: SSL证书验证失败",
                    'ssl_warning': True
                })
                
            # 检查通信延迟异常
            if 'latency' in latest_data and 'avg_latency' in device_data:
                latency = latest_data['latency']
                avg_latency = device_data['avg_latency']
                threshold = self.config.get('mitm_latency_threshold', 3.0)  # 延迟倍数阈值
                
                if latency > avg_latency * threshold:
                    self.trigger_alert({
                        'type': 'mitm',
                        'device_id': device_id,
                        'description': f"可能存在中间人攻击: 通信延迟异常 ({latency:.2f}ms > {avg_latency:.2f}ms)",
                        'latency': latency,
                        'avg_latency': avg_latency,
                        'threshold': threshold
                    })
    
    def _detect_firmware_attack(self):
        """检测固件攻击"""
        # 实现固件攻击检测逻辑
        for device_id, device_data in self.device_data.items():
            # 获取最近的数据记录
            if not device_data['data_history']:
                continue
            
            latest_data = device_data['data_history'][-1]['data']
            
            # 检查固件版本变化
            if 'firmware_version' in latest_data and 'last_firmware_version' in device_data:
                current_version = latest_data['firmware_version']
                last_version = device_data['last_firmware_version']
                
                if current_version != last_version:
                    # 检查是否为预期的更新
                    expected_update = self.config.get('expected_firmware_updates', {})
                    if device_id not in expected_update or expected_update[device_id] != current_version:
                        self.trigger_alert({
                            'type': 'firmware',
                            'device_id': device_id,
                            'description': f"可能存在固件攻击: 固件版本意外变化 ({last_version} -> {current_version})",
                            'current_version': current_version,
                            'last_version': last_version
                        })
            
            # 更新记录的固件版本
            if 'firmware_version' in latest_data:
                device_data['last_firmware_version'] = latest_data['firmware_version']
    
    def _detect_credential_attack(self):
        """检测凭证攻击"""
        # 实现凭证攻击检测逻辑
        threshold = self.config.get('failed_auth_threshold', 5)
        window_size = self.config.get('failed_auth_window', 300)  # 窗口大小，单位秒
        current_time = time.time()
        
        for device_id, device_data in self.device_data.items():
            # 如果设备记录了认证失败
            if 'auth_failures' in device_data:
                # 筛选窗口内的认证失败
                recent_failures = [f for f in device_data['auth_failures'] if current_time - f <= window_size]
                device_data['auth_failures'] = recent_failures
                
                # 如果失败次数超过阈值，触发警报
                if len(recent_failures) >= threshold:
                    self.trigger_alert({
                        'type': 'credential',
                        'device_id': device_id,
                        'description': f"可能存在凭证攻击: {len(recent_failures)} 次认证失败在 {window_size} 秒内",
                        'failure_count': len(recent_failures),
                        'threshold': threshold,
                        'window_size': window_size
                    })
    
    def _detect_anomaly_behavior(self):
        """检测异常行为"""
        # 实现异常行为检测逻辑
        for device_id, device_data in self.device_data.items():
            # 获取历史数据
            history = device_data.get('data_history', [])
            if len(history) < 2:
                continue
            
            # 分析数据变化率
            latest_data = history[-1]['data']
            previous_data = history[-2]['data']
            
            # 检查数值型数据的异常变化
            for key in latest_data:
                # 只分析数值型数据
                if isinstance(latest_data.get(key), (int, float)) and isinstance(previous_data.get(key), (int, float)):
                    current_value = latest_data[key]
                    previous_value = previous_data[key]
                    
                    # 计算变化率
                    if previous_value != 0:
                        change_rate = abs((current_value - previous_value) / previous_value)
                        
                        # 检查是否超过阈值
                        threshold = self.config.get(f'anomaly_threshold_{key}', 0.5)  # 默认变化率阈值50%
                        if change_rate > threshold:
                            self.trigger_alert({
                                'type': 'anomaly',
                                'device_id': device_id,
                                'description': f"异常行为: {key} 值变化异常 ({previous_value} -> {current_value}, 变化率 {change_rate:.2f})",
                                'field': key,
                                'previous_value': previous_value,
                                'current_value': current_value,
                                'change_rate': change_rate,
                                'threshold': threshold
                            })
    
    def record_auth_failure(self, device_id: str):
        """
        记录认证失败
        
        Args:
            device_id: 设备ID
        """
        # 确保设备数据存在
        if device_id not in self.device_data:
            self.device_data[device_id] = {
                'last_update': time.time(),
                'data_history': [],
                'auth_failures': []
            }
        
        # 确保auth_failures字段存在
        if 'auth_failures' not in self.device_data[device_id]:
            self.device_data[device_id]['auth_failures'] = []
        
        # 记录失败时间
        self.device_data[device_id]['auth_failures'].append(time.time())
        
        # 检查是否需要立即触发警报
        self._detect_credential_attack()
    
    def simulate_attack(self, attack_type: str, device_id: str, attack_params: Dict[str, Any] = None):
        """
        模拟攻击，用于测试和演示
        
        Args:
            attack_type: 攻击类型
            device_id: 目标设备ID
            attack_params: 攻击参数
        """
        if attack_params is None:
            attack_params = {}
        
        self.logger.info(f"模拟攻击: 类型={attack_type}, 设备={device_id}, 参数={attack_params}")
        
        if attack_type == "ddos":
            # 模拟DDoS攻击
            request_count = attack_params.get('request_count', 200)
            window_size = attack_params.get('window_size', 60)
            
            # 确保设备数据存在
            if device_id not in self.device_data:
                self.device_data[device_id] = {
                    'last_update': time.time(),
                    'data_history': [],
                }
            
            # 创建模拟请求历史
            current_time = time.time()
            for i in range(request_count):
                # 在窗口内均匀分布请求时间
                timestamp = current_time - (window_size * i / request_count)
                self.device_data[device_id]['data_history'].append({
                    'timestamp': timestamp,
                    'data': {'request': f'simulated_request_{i}'}
                })
            
            # 触发检测
            self._detect_ddos_attack()
            
        elif attack_type == "mitm":
            # 模拟中间人攻击
            ssl_warning = attack_params.get('ssl_warning', True)
            latency = attack_params.get('latency', 500)  # ms
            
            # 确保设备数据存在
            if device_id not in self.device_data:
                self.device_data[device_id] = {
                    'last_update': time.time(),
                    'data_history': [],
                    'avg_latency': 100  # 模拟平均延迟
                }
            
            # 设置平均延迟
            self.device_data[device_id]['avg_latency'] = attack_params.get('avg_latency', 100)
            
            # 添加模拟异常数据
            self.device_data[device_id]['data_history'].append({
                'timestamp': time.time(),
                'data': {
                    'ssl_warning': ssl_warning,
                    'latency': latency
                }
            })
            
            # 触发检测
            self._detect_mitm_attack()
            
        elif attack_type == "firmware":
            # 模拟固件攻击
            current_version = attack_params.get('current_version', '2.0.0')
            last_version = attack_params.get('last_version', '1.0.0')
            
            # 确保设备数据存在
            if device_id not in self.device_data:
                self.device_data[device_id] = {
                    'last_update': time.time(),
                    'data_history': [],
                    'last_firmware_version': last_version
                }
            else:
                self.device_data[device_id]['last_firmware_version'] = last_version
            
            # 添加模拟固件版本数据
            self.device_data[device_id]['data_history'].append({
                'timestamp': time.time(),
                'data': {'firmware_version': current_version}
            })
            
            # 触发检测
            self._detect_firmware_attack()
            
        elif attack_type == "credential":
            # 模拟凭证攻击
            failure_count = attack_params.get('failure_count', 10)
            time_span = attack_params.get('time_span', 60)  # 秒
            
            # 确保设备数据存在
            if device_id not in self.device_data:
                self.device_data[device_id] = {
                    'last_update': time.time(),
                    'data_history': [],
                    'auth_failures': []
                }
            
            # 创建模拟认证失败记录
            current_time = time.time()
            auth_failures = []
            for i in range(failure_count):
                # 在时间跨度内均匀分布失败时间
                failure_time = current_time - (time_span * i / failure_count)
                auth_failures.append(failure_time)
            
            self.device_data[device_id]['auth_failures'] = auth_failures
            
            # 触发检测
            self._detect_credential_attack()
            
        elif attack_type == "anomaly":
            # 模拟异常行为
            field = attack_params.get('field', 'temperature')
            current_value = attack_params.get('current_value', 80)
            previous_value = attack_params.get('previous_value', 25)
            
            # 确保设备数据存在
            if device_id not in self.device_data:
                self.device_data[device_id] = {
                    'last_update': time.time(),
                    'data_history': []
                }
            
            # 添加模拟历史数据
            if len(self.device_data[device_id]['data_history']) < 2:
                self.device_data[device_id]['data_history'] = [
                    {
                        'timestamp': time.time() - 60,
                        'data': {field: previous_value}
                    },
                    {
                        'timestamp': time.time(),
                        'data': {field: current_value}
                    }
                ]
            else:
                # 更新最近两条记录
                self.device_data[device_id]['data_history'][-2]['data'][field] = previous_value
                self.device_data[device_id]['data_history'][-1]['data'][field] = current_value
            
            # 触发检测
            self._detect_anomaly_behavior()
        
        else:
            self.logger.error(f"未知的攻击类型: {attack_type}")