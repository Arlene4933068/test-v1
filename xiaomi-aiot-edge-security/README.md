# 小米AIoT边缘安全防护研究平台

这是一个用于研究小米AIoT边缘设备安全防护能力的仿真平台。平台支持模拟各种边缘设备，连接EdgeX Foundry和ThingsBoard Edge边缘计算平台，并提供安全防护和分析功能。

## 项目概述

小米AIoT边缘安全防护研究平台是一个针对边缘计算场景下IoT设备安全问题的仿真研究系统。本平台通过模拟网关、路由器、小爱音箱和摄像头等常见边缘设备，研究它们在与EdgeX Foundry和ThingsBoard Edge连接时可能面临的安全威胁，并测试相应的防御策略。

## 功能特点

- **设备模拟**: 模拟网关、路由器、小爱音箱（蓝牙网关）和摄像头等边缘设备
- **平台连接**: 支持连接EdgeX Foundry和ThingsBoard Edge边缘计算平台
- **分布式安全防护**: 实现分布式安全防护框架，具备攻击检测和防护能力
- **场景模拟**: 模拟AIoT设备在实际运行中的典型场景，包括数据通信、身份认证、攻击防护等
- **性能分析**: 对实验过程中产生的性能数据进行统计分析，包括攻击检测率、响应延迟、资源占用等
- **可视化界面**: 提供直观的分析报告和可视化图表

## 系统架构

本系统由以下主要组件构成：

1. **设备模拟器** - 模拟各类边缘设备的行为和通信
2. **平台连接器** - 对接EdgeX Foundry和ThingsBoard Edge平台
3. **安全防护模块** - 检测和防御各类攻击
4. **数据分析模块** - 收集性能数据并进行统计分析
5. **控制面板** - 提供配置和监控功能

## 目录结构
xiaomi-aiot-edge-security/ ├── config/ # 配置文件 │ └── platform.yaml # 平台主配置 ├── data/ # 数据文件 │ ├── device_data/ # 设备数据 │ ├── security_data/ # 安全数据 │ └── performance_data/ # 性能数据 ├── output/ # 输出文件 │ ├── reports/ # 分析报告 │ └── visualizations/ # 可视化图表 ├── src/ # 源代码 │ ├── analytics/ # 数据分析模块 │ ├── dashboard/ # 控制面板 │ ├── device_simulator/ # 设备模拟器 │ │ └── devices/ # 设备模型 │ ├── platform_connector/ # 平台连接器 │ ├── security/ # 安全防护模块 │ └── utils/ # 工具类 ├── tests/ # 测试代码 ├── README.md # 项目介绍 ├── requirements.txt # 依赖项 └── setup.py # 安装配置

Code

## 快速开始

### 环境要求

- Python 3.8或更高版本
- Docker和Docker Compose
- EdgeX Foundry (已部署在Docker中)
- ThingsBoard Edge (已部署在Docker中)

### 安装步骤

1. 克隆代码仓库：
   ```bash
   git clone https://github.com/your-username/xiaomi-aiot-edge-security.git
   cd xiaomi-aiot-edge-security
安装依赖：

bash
pip install -r requirements.txt
修改配置：

bash
# 编辑config/platform.yaml文件，配置EdgeX和ThingsBoard连接参数
nano config/platform.yaml
启动平台：

bash
python src/main.py
使用指南
设备模拟：

平台启动后会自动创建并模拟配置的边缘设备
设备将连接到EdgeX Foundry和ThingsBoard Edge
可以在EdgeX UI (http://localhost:4000) 和ThingsBoard UI (http://localhost:8080) 中查看设备状态
攻击模拟：

平台会自动模拟各种攻击场景
可以在日志中观察攻击事件和防护措施
数据分析：

平台会收集性能数据并在output目录生成分析报告和可视化图表
报告包括攻击检测率、响应延迟、资源占用等指标
自定义场景：

修改config/platform.yaml文件可以自定义设备类型、攻击场景等
安全防护分析
本平台实现了以下安全防护功能：

DDoS攻击防护：检测和缓解针对边缘设备的DDoS攻击
中间人攻击检测：识别通信中的中间人攻击
凭证保护：防御凭证盗取和暴力破解
固件安全：检测恶意固件更新
协议漏洞防护：防御针对IoT通信协议的攻击
数据窃取防护：检测和阻止数据窃取行为
僵尸网络防护：防御IoT设备被纳入僵尸网络
物理篡改检测：检测设备物理篡改行为
性能数据分析
平台可以生成以下性能数据分析：

攻击检测率统计：按攻击类型的检测成功率
响应延迟分析：从检测到响应的时间分析
资源占用统计：安全措施对系统资源的影响
设备性能影响：安全措施对设备正常功能的影响
故障排除
如果您在使用平台时遇到问题，可以尝试以下方法：

连接问题：

确认EdgeX Foundry和ThingsBoard Edge服务正在运行
检查配置文件中的连接参数是否正确
设备创建失败：

检查日志了解具体错误
确保EdgeX和ThingsBoard有足够的权限创建设备
数据分析问题：

确保data和output目录有写入权限
贡献指南
欢迎为小米AIoT边缘安全防护研究平台做出贡献！请遵循以下步骤：

Fork本仓库
创建您的特性分支 (git checkout -b feature/amazing-feature)
提交您的更改 (git commit -m 'Add some amazing feature')
推送到分支 (git push origin feature/amazing-feature)
创建一个Pull Request
许可证
本项目采用MIT许可证。请参阅LICENSE文件了解详情。

联系方式
如有任何问题或建议，请通过以下方式联系我们：

项目主页：GitHub Issue
电子邮件：your-email@example.com