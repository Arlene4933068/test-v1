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
    
    def add_alert_callback(self, callback: Callable):
        """添加告警回调函数
        
        Args:
            callback: 回调函数
        """
        self.alert_callbacks.append(callback)
    
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
                        attack_info = {'device_id': attack_info.get('device_id'), 'request_count': attack_info.get('request_count', 0), 'time_window': attack_info.get('time_window', self.config.get('detection', {}).get('ddos', {}).get('time_window', 60))}
                        detector_func(attack_info)
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
    
    def _detect_ddos_attack(self, attack_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """检测DDoS攻击
        
        Args:
            attack_info: 攻击信息
            
        Returns:
            检测结果
        """
        # 获取配置参数
        ddos_config = self.config.get('detection', {}).get('ddos', {})
        threshold = ddos_config.get('request_rate_threshold', 100)
        window_size = ddos_config.get('time_window', 60)
        
        # 获取攻击信息
        device_id = attack_info.get('device_id')
        request_count = attack_info.get('request_count', 0)
        time_window = attack_info.get('time_window', window_size)
        
        # 如果请求数超过阈值，触发警报
        if request_count > threshold:
            alert_info = {
                'type': 'ddos',
                'device_id': device_id,
                'description': f"DDoS攻击: {request_count} 个请求在 {time_window} 秒内",
                'request_count': request_count,
                'threshold': threshold,
                'time_window': time_window
            }
            self.trigger_alert(alert_info)
            return alert_info
        
        return None
    
    def _detect_mitm_attack(self, attack_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """检测中间人攻击
        
        Args:
            attack_info: 攻击信息
            
        Returns:
            检测结果
        """
        # 获取配置参数
        mitm_config = self.config.get('detection', {}).get('mitm', {})
        threshold = mitm_config.get('interception_rate_threshold', 10)
        window_size = mitm_config.get('time_window', 60)
        
        # 获取攻击信息
        device_id = attack_info.get('device_id')
        interception_count = attack_info.get('interception_count', 0)
        time_window = attack_info.get('time_window', window_size)
        
        # 如果拦截数超过阈值，触发警报
        if interception_count > threshold:
            alert_info = {
                'type': 'mitm',
                'device_id': device_id,
                'description': f"中间人攻击: {interception_count} 次拦截在 {time_window} 秒内",
                'timestamp': time.time()
            }
            self.trigger_alert(alert_info)
            return alert_info
        
        return None
    
    def _detect_firmware_attack(self, attack_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """检测固件攻击
        
        Args:
            attack_info: 攻击信息
            
        Returns:
            检测结果
        """
        # 获取配置参数
        firmware_config = self.config.get('detection', {}).get('firmware', {})
        threshold = firmware_config.get('change_rate_threshold', 10)
        window_size = firmware_config.get('time_window', 60)
        
        # 获取攻击信息
        device_id = attack_info.get('device_id')
        change_count = attack_info.get('change_count', 0)
        time_window = attack_info.get('time_window', window_size)
        
        # 如果变化数超过阈值，触发警报
        if change_count > threshold:
            alert_info = {
                'type': 'firmware',
                'device_id': device_id,
                'description': f"固件攻击: {change_count} 次变化在 {time_window} 秒内",
                'timestamp': time.time()
            }
            self.trigger_alert(alert_info)
            return alert_info
        return None
    
    def _detect_credential_attack(self, attack_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """检测凭证攻击
        
        Args:
            attack_info: 攻击信息
            
        Returns:
            检测结果
        """
        # 获取配置参数
        credential_config = self.config.get('detection', {}).get('credential', {})
        threshold = credential_config.get('failed_attempts_threshold', 5)
        window_size = credential_config.get('time_window', 60)
        
        # 获取攻击信息
        device_id = attack_info.get('device_id')
        failed_attempts = attack_info.get('failed_attempts', 0)
        time_window = attack_info.get('time_window', window_size)
        
        # 如果失败尝试数超过阈值，触发警报
        if failed_attempts > threshold:
            alert_info = {
                'type': 'credential',
                'device_id': device_id,
                'description': f"凭证攻击: {failed_attempts} 次失败尝试在 {time_window} 秒内",
                'timestamp': time.time()
            }
            self.trigger_alert(alert_info)
            return alert_info
        return None
    
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
        attack_info = {'device_id': device_id, 'failed_attempts': attack_params.get('failure_count', 0), 'time_window': attack_params.get('time_span', 60)}
        self._detect_credential_attack(attack_info)
    
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
            attack_info = {'device_id': device_id, 'request_count': request_count, 'time_window': window_size}
            self._detect_ddos_attack(attack_info)
            
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
            attack_info = {'device_id': device_id, 'interception_count': attack_params.get('interception_count', 0), 'time_window': window_size}
            self._detect_mitm_attack(attack_info)
            
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
            attack_info = {'device_id': device_id, 'change_count': attack_params.get('change_count', 0), 'time_window': window_size}
            self._detect_firmware_attack(attack_info)
            
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
            attack_info = {'device_id': device_id, 'failed_attempts': failure_count, 'time_window': time_span}
            self._detect_credential_attack(attack_info)
            
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

    def detect_attacks(self, attack_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """检测攻击
        
        Args:
            attack_info: 攻击信息
            
        Returns:
            检测结果，如果检测到攻击则返回攻击详情，否则返回None
        """
        attack_type = attack_info.get('type')
        if attack_type not in self.detectors:
            self.logger.warning(f"未知的攻击类型: {attack_type}")
            return None
            
        detector = self.detectors[attack_type]
        result = detector(attack_info)
        
        if result:
            # 触发告警回调
            for callback in self.alert_callbacks:
                try:
                    callback(result)
                except Exception as e:
                    self.logger.error(f"执行告警回调时出错: {str(e)}")
        
        return result