# src/analytics/report_generator.py
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from ..utils.logger import get_logger

class ReportGenerator:
    """报告生成器：生成实验数据分析报告"""
    
    def __init__(self, output_dir="reports"):
        self.logger = get_logger("ReportGenerator")
        self.output_dir = output_dir
        
        # 确保输出目录存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        self.logger.info(f"报告生成器初始化完成，输出目录: {output_dir}")
        
    def generate_detection_report(self, detection_data, filename=None):
        """生成攻击检测报告
        
        Args:
            detection_data: 攻击检测分析数据
            filename: 输出文件名
            
        Returns:
            str: 报告文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"detection_report_{timestamp}"
            
        # 生成图表
        try:
            if isinstance(detection_data, dict) and "by_attack_type" in detection_data:
                # 创建检测率条形图
                plt.figure(figsize=(10, 6))
                attack_types = list(detection_data["by_attack_type"].keys())
                rates = [data["rate"] for data in detection_data["by_attack_type"].values()]
                
                plt.bar(attack_types, rates)
                plt.xlabel('攻击类型')
                plt.ylabel('检测率 (%)')
                plt.title('各类攻击检测率对比')
                plt.ylim(0, 100)
                plt.grid(axis='y', linestyle='--', alpha=0.7)
                plt.tight_layout()
                
                chart_path = os.path.join(self.output_dir, f"{filename}_chart.png")
                plt.savefig(chart_path)
                plt.close()
                
                # 生成文本报告
                with open(os.path.join(self.output_dir, f"{filename}.txt"), 'w', encoding='utf-8') as f:
                    f.write("=== 攻击检测率分析报告 ===\n")
                    f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(f"总体检测率: {detection_data['overall_detection_rate']:.2f}%\n")
                    f.write(f"样本总数: {detection_data['sample_size']}\n\n")
                    f.write("各类攻击检测率:\n")
                    
                    for attack_type, data in detection_data["by_attack_type"].items():
                        f.write(f"- {attack_type}: {data['rate']:.2f}% (样本数: {data['sample_size']})\n")
                
                # 生成JSON报告
                with open(os.path.join(self.output_dir, f"{filename}.json"), 'w', encoding='utf-8') as f:
                    json.dump(detection_data, f, indent=2)
                    
                self.logger.info(f"攻击检测报告生成完成: {filename}")
                return os.path.join(self.output_dir, f"{filename}.txt")
            else:
                self.logger.error("无效的检测数据格式")
                return None
        except Exception as e:
            self.logger.error(f"生成检测报告时出错: {str(e)}")
            return None
    
    def generate_performance_report(self, response_data, resource_data, filename=None):
        """生成性能分析报告
        
        Args:
            response_data: 响应时间分析数据
            resource_data: 资源使用分析数据
            filename: 输出文件名
            
        Returns:
            str: 报告文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_report_{timestamp}"
            
        try:
            # 生成响应时间图表
            if isinstance(response_data, dict) and "by_device_type" in response_data:
                plt.figure(figsize=(12, 10))
                
                # 响应时间图表
                plt.subplot(2, 1, 1)
                devices = list(response_data["by_device_type"].keys())
                means = [data["mean"] for data in response_data["by_device_type"].values()]
                
                plt.bar(devices, means)
                plt.xlabel('设备类型')
                plt.ylabel('平均响应时间 (ms)')
                plt.title('各类设备平均响应时间')
                plt.grid(axis='y', linestyle='--', alpha=0.7)
                
                # 资源使用图表
                if isinstance(resource_data, dict) and "by_device_type" in resource_data:
                    plt.subplot(2, 1, 2)
                    devices = list(resource_data["by_device_type"].keys())
                    cpu_usage = [data["cpu"] for data in resource_data["by_device_type"].values()]
                    memory_usage = [data["memory"] for data in resource_data["by_device_type"].values()]
                    
                    x = range(len(devices))
                    width = 0.35
                    
                    plt.bar([i - width/2 for i in x], cpu_usage, width, label='CPU使用率 (%)')
                    plt.bar([i + width/2 for i in x], memory_usage, width, label='内存使用率 (%)')
                    plt.xlabel('设备类型')
                    plt.ylabel('资源使用率 (%)')
                    plt.title('各类设备资源使用情况')
                    plt.xticks(x, devices)
                    plt.legend()
                    plt.grid(axis='y', linestyle='--', alpha=0.7)
                
                plt.tight_layout()
                chart_path = os.path.join(self.output_dir, f"{filename}_chart.png")
                plt.savefig(chart_path)
                plt.close()
                
                # 生成文本报告
                with open(os.path.join(self.output_dir, f"{filename}.txt"), 'w', encoding='utf-8') as f:
                    f.write("=== 性能分析报告 ===\n")
                    f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    
                    f.write("== 响应时间分析 ==\n")
                    f.write(f"整体平均响应时间: {response_data['overall_stats']['mean']:.2f} ms\n")
                    f.write(f"最小响应时间: {response_data['overall_stats']['min']:.2f} ms\n")
                    f.write(f"最大响应时间: {response_data['overall_stats']['max']:.2f} ms\n")
                    f.write(f"标准差: {response_data['overall_stats']['std_dev']:.2f} ms\n\n")
                    
                    f.write("各设备响应时间:\n")
                    for device, data in response_data["by_device_type"].items():
                        f.write(f"- {device}: 平均 {data['mean']:.2f} ms, 中位数 {data['median']:.2f} ms (样本数: {data['sample_size']})\n")
                    
                    f.write("\n== 资源使用分析 ==\n")
                    f.write(f"整体平均CPU使用率: {resource_data['overall_usage']['cpu']:.2f}%\n")
                    f.write(f"整体平均内存使用率: {resource_data['overall_usage']['memory']:.2f}%\n")
                    
                    if resource_data['overall_usage']['network'] is not None:
                        f.write(f"整体平均网络使用率: {resource_data['overall_usage']['network']:.2f} KB/s\n\n")
                    
                    f.write("各设备资源使用情况:\n")
                    for device, data in resource_data["by_device_type"].items():
                        f.write(f"- {device}: CPU {data['cpu']:.2f}%, 内存 {data['memory']:.2f}% (样本数: {data['sample_size']})\n")
                    
                    if resource_data['protection_impact'] is not None:
                        f.write("\n安全防护影响分析:\n")
                        with_data = resource_data['protection_impact']['with_protection']
                        without_data = resource_data['protection_impact']['without_protection']
                        
                        if with_data['cpu'] is not None and without_data['cpu'] is not None:
                            cpu_impact = with_data['cpu'] - without_data['cpu']
                            memory_impact = with_data['memory'] - without_data['memory']
                            
                            f.write(f"防护开启时CPU增加: {cpu_impact:.2f}% (相对增加: {(cpu_impact/without_data['cpu']*100):.2f}%)\n")
                            f.write(f"防护开启时内存增加: {memory_impact:.2f}% (相对增加: {(memory_impact/without_data['memory']*100):.2f}%)\n")
                
                # 生成JSON报告
                combined_data = {
                    "response_time": response_data,
                    "resource_usage": resource_data
                }
                
                with open(os.path.join(self.output_dir, f"{filename}.json"), 'w', encoding='utf-8') as f:
                    json.dump(combined_data, f, indent=2)
                    
                self.logger.info(f"性能分析报告生成完成: {filename}")
                return os.path.join(self.output_dir, f"{filename}.txt")
            else:
                self.logger.error("无效的性能数据格式")
                return None
        except Exception as e:
            self.logger.error(f"生成性能报告时出错: {str(e)}")
            return None
    
    def generate_comprehensive_report(self, data, filename=None):
        """生成综合分析报告
        
        Args:
            data: 包含所有分析数据的字典
            filename: 输出文件名
            
        Returns:
            str: 报告文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comprehensive_report_{timestamp}"
            
        try:
            # 创建多个图表
            plt.figure(figsize=(15, 12))
            
            # 1. 检测率图表
            if "detection" in data and "by_attack_type" in data["detection"]:
                plt.subplot(2, 2, 1)
                attack_types = list(data["detection"]["by_attack_type"].keys())
                rates = [d["rate"] for d in data["detection"]["by_attack_type"].values()]
                
                plt.bar(attack_types, rates, color='skyblue')
                plt.xlabel('攻击类型')
                plt.ylabel('检测率 (%)')
                plt.title('不同攻击类型检测率')
                plt.ylim(0, 100)
                plt.xticks(rotation=45, ha='right')
                plt.grid(axis='y', linestyle='--', alpha=0.7)
            
            # 2. 响应时间图表
            if "response_time" in data and "by_device_type" in data["response_time"]:
                plt.subplot(2, 2, 2)
                
                devices = list(data["response_time"]["by_device_type"].keys())
                response_times = [d["mean"] for d in data["response_time"]["by_device_type"].values()]
                
                # 创建柱状图
                bars = plt.bar(devices, response_times, color='lightgreen')
                
                # 添加数值标签
                for bar in bars:
                    height = bar.get_height()
                    plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                            f'{height:.1f}',
                            ha='center', va='bottom', rotation=0)
                
                plt.xlabel('设备类型')
                plt.ylabel('平均响应时间 (ms)')
                plt.title('设备响应时间分析')
                plt.grid(axis='y', linestyle='--', alpha=0.7)
            
            # 3. 资源使用对比图
            if "resource_usage" in data and "protection_impact" in data["resource_usage"]:
                plt.subplot(2, 2, 3)
                
                impact = data["resource_usage"]["protection_impact"]
                if (impact["with_protection"]["cpu"] is not None and 
                    impact["without_protection"]["cpu"] is not None):
                    
                    categories = ['CPU使用率', '内存使用率']
                    with_protection = [impact["with_protection"]["cpu"], 
                                      impact["with_protection"]["memory"]]
                    without_protection = [impact["without_protection"]["cpu"], 
                                         impact["without_protection"]["memory"]]
                    
                    x = range(len(categories))
                    width = 0.35
                    
                    plt.bar([i - width/2 for i in x], without_protection, width, 
                           label='防护关闭', color='lightgray')
                    plt.bar([i + width/2 for i in x], with_protection, width, 
                           label='防护开启', color='salmon')
                    
                    plt.xlabel('资源类型')
                    plt.ylabel('使用率 (%)')
                    plt.title('安全防护对资源使用的影响')
                    plt.xticks(x, categories)
                    plt.legend()
                    plt.grid(axis='y', linestyle='--', alpha=0.7)
            
            # 4. 设备资源使用情况
            if "resource_usage" in data and "by_device_type" in data["resource_usage"]:
                plt.subplot(2, 2, 4)
                
                devices = list(data["resource_usage"]["by_device_type"].keys())
                cpu_usage = [d["cpu"] for d in data["resource_usage"]["by_device_type"].values()]
                memory_usage = [d["memory"] for d in data["resource_usage"]["by_device_type"].values()]
                
                x = range(len(devices))
                width = 0.35
                
                plt.bar([i - width/2 for i in x], cpu_usage, width, label='CPU', color='lightblue')
                plt.bar([i + width/2 for i in x], memory_usage, width, label='内存', color='lightpink')
                
                plt.xlabel('设备类型')
                plt.ylabel('使用率 (%)')
                plt.title('设备资源使用情况')
                plt.xticks(x, devices)
                plt.legend()
                plt.grid(axis='y', linestyle='--', alpha=0.7)
            
            plt.tight_layout()
            chart_path = os.path.join(self.output_dir, f"{filename}_chart.png")
            plt.savefig(chart_path)
            plt.close()
            
            # 生成文本报告
            with open(os.path.join(self.output_dir, f"{filename}.txt"), 'w', encoding='utf-8') as f:
                f.write("======= 小米AIoT边缘安全防护研究综合报告 =======\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # 检测效果部分
                if "detection" in data:
                    detection = data["detection"]
                    f.write("=== 一、攻击检测效果分析 ===\n\n")
                    f.write(f"1. 总体检测率: {detection['overall_detection_rate']:.2f}% (样本数: {detection['sample_size']})\n\n")
                    f.write("2. 各类攻击检测效果:\n")
                    
                    for attack_type, type_data in detection["by_attack_type"].items():
                        f.write(f"   - {attack_type}: {type_data['rate']:.2f}% (样本数: {type_data['sample_size']})\n")
                    
                    f.write("\n")
                
                # 性能分析部分
                if "response_time" in data:
                    response = data["response_time"]
                    f.write("=== 二、系统响应性能分析 ===\n\n")
                    f.write(f"1. 整体响应时间: 平均 {response['overall_stats']['mean']:.2f} ms, 中位数 {response['overall_stats']['median']:.2f} ms\n")
                    f.write(f"   - 最小值: {response['overall_stats']['min']:.2f} ms\n")
                    f.write(f"   - 最大值: {response['overall_stats']['max']:.2f} ms\n")
                    f.write(f"   - 标准差: {response['overall_stats']['std_dev']:.2f} ms\n\n")
                    
                    f.write("2. 各设备响应时间分析:\n")
                    for device, device_data in response["by_device_type"].items():
                        f.write(f"   - {device}: 平均 {device_data['mean']:.2f} ms, 中位数 {device_data['median']:.2f} ms\n")
                    
                    f.write("\n")
                
                # 资源使用分析
                if "resource_usage" in data:
                    resource = data["resource_usage"]
                    f.write("=== 三、资源占用分析 ===\n\n")
                    f.write(f"1. 整体资源使用情况:\n")
                    f.write(f"   - CPU平均使用率: {resource['overall_usage']['cpu']:.2f}%\n")
                    f.write(f"   - 内存平均使用率: {resource['overall_usage']['memory']:.2f}%\n")
                    
                    if resource['overall_usage']['network'] is not None:
                        f.write(f"   - 网络平均使用率: {resource['overall_usage']['network']:.2f} KB/s\n")
                    
                    f.write("\n2. 各设备资源使用情况:\n")
                    for device, device_data in resource["by_device_type"].items():
                        f.write(f"   - {device}: CPU {device_data['cpu']:.2f}%, 内存 {device_data['memory']:.2f}%\n")
                    
                    if resource['protection_impact'] is not None:
                        with_data = resource['protection_impact']['with_protection']
                        without_data = resource['protection_impact']['without_protection']
                        
                        if with_data['cpu'] is not None and without_data['cpu'] is not None:
                            cpu_impact = with_data['cpu'] - without_data['cpu']
                            memory_impact = with_data['memory'] - without_data['memory']
                            
                            f.write("\n3. 安全防护资源消耗影响:\n")
                            f.write(f"   - 防护关闭时: CPU {without_data['cpu']:.2f}%, 内存 {without_data['memory']:.2f}%\n")
                            f.write(f"   - 防护开启时: CPU {with_data['cpu']:.2f}%, 内存 {with_data['memory']:.2f}%\n")
                            f.write(f"   - 资源增加量: CPU +{cpu_impact:.2f}%, 内存 +{memory_impact:.2f}%\n")
                            f.write(f"   - 相对增幅: CPU {(cpu_impact/without_data['cpu']*100):.2f}%, 内存 {(memory_impact/without_data['memory']*100):.2f}%\n")
                
                # 结论与建议
                f.write("\n=== 四、结论与建议 ===\n\n")
                
                # 根据数据生成一些结论
                if "detection" in data and data["detection"]["overall_detection_rate"] > 90:
                    f.write("1. 检测效果分析结论: 系统整体检测效果良好，能够有效识别大多数常见攻击。\n")
                elif "detection" in data:
                    f.write("1. 检测效果分析结论: 系统检测效果有待提高，应加强以下类型攻击的检测能力：\n")
                    for attack_type, type_data in data["detection"]["by_attack_type"].items():
                        if type_data['rate'] < 80:
                            f.write(f"   - {attack_type}: 当前检测率仅为 {type_data['rate']:.2f}%\n")
                
                if "resource_usage" in data and "protection_impact" in data["resource_usage"]:
                    impact = data["resource_usage"]["protection_impact"]
                    if (impact["with_protection"]["cpu"] is not None and 
                        impact["without_protection"]["cpu"] is not None):
                        
                        cpu_impact = impact["with_protection"]["cpu"] - impact["without_protection"]["cpu"]
                        relative_impact = cpu_impact / impact["without_protection"]["cpu"] * 100
                        
                        if relative_impact > 50:
                            f.write("\n2. 资源占用分析结论: 安全防护模块资源占用较高，建议优化代码效率。特别是CPU使用增加了")
                            f.write(f"{relative_impact:.2f}%，已超过系统资源预算。\n")
                        else:
                            f.write("\n2. 资源占用分析结论: 安全防护模块资源占用在可接受范围内，对系统性能影响有限。\n")
                
                if "response_time" in data:
                    response = data["response_time"]
                    if response['overall_stats']['mean'] > 200:  # 假设200ms为阈值
                        f.write("\n3. 响应性能分析结论: 系统整体响应时间较长，可能影响用户体验，建议进一步优化处理流程。\n")
                    else:
                        f.write("\n3. 响应性能分析结论: 系统响应时间表现良好，各设备类型均保持在可接受范围内。\n")