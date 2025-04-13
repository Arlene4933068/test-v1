#!/bin/bash

# 小米AIoT边缘安全防护研究平台 - 启动仿真脚本
# 此脚本用于启动仿真平台的各个组件

# 设置颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  小米AIoT边缘安全防护研究平台启动脚本  ${NC}"
echo -e "${GREEN}=========================================${NC}"

# 激活虚拟环境
if [ -d "venv" ]; then
    echo -e "${YELLOW}激活虚拟环境...${NC}"
    source venv/bin/activate
else
    echo -e "${RED}未找到虚拟环境，请先运行 setup.sh${NC}"
    exit 1
fi

# 检查配置文件是否存在
echo -e "\n${YELLOW}检查配置文件...${NC}"
CONFIG_FILES=("config/simulator.yaml" "config/edgex.yaml" "config/thingsboard.yaml" "config/security.yaml" "config/logging.yaml")
CONFIG_MISSING=false

for config_file in "${CONFIG_FILES[@]}"; do
    if [ ! -f "$config_file" ]; then
        echo -e "${RED}✗ 配置文件 $config_file 不存在${NC}"
        CONFIG_MISSING=true
    else
        echo -e "${GREEN}✓ 配置文件 $config_file 已找到${NC}"
    fi
done

if [ "$CONFIG_MISSING" = true ]; then
    echo -e "${RED}请确保所有配置文件都存在后再启动${NC}"
    exit 1
fi

# 检查Docker容器
echo -e "\n${YELLOW}检查Docker容器...${NC}"
if command -v docker &>/dev/null; then
    # 检查EdgeX和ThingsBoard容器是否运行
    if ! docker ps | grep -q "edgex-core-metadata"; then
        echo -e "${YELLOW}! EdgeX容器未运行，请确保已启动EdgeX Foundry${NC}"
    else
        echo -e "${GREEN}✓ EdgeX容器正在运行${NC}"
    fi
    
    if ! docker ps | grep -q "thingsboard-edge"; then
        echo -e "${YELLOW}! ThingsBoard Edge容器未运行，请确保已启动ThingsBoard Edge${NC}"
    else
        echo -e "${GREEN}✓ ThingsBoard Edge容器正在运行${NC}"
    fi
fi

# 启动设备模拟器
echo -e "\n${YELLOW}启动设备模拟器...${NC}"
mkdir -p logs
python -m src.device_simulator.__init__ > logs/simulator.log 2>&1 &
SIMULATOR_PID=$!
echo $SIMULATOR_PID > .simulator.pid
echo -e "${GREEN}✓ 设备模拟器已启动 (PID: $SIMULATOR_PID)${NC}"

# 启动安全防护模块
echo -e "\n${YELLOW}启动安全防护模块...${NC}"
python -m src.security.__init__ > logs/security.log 2>&1 &
SECURITY_PID=$!
echo $SECURITY_PID > .security.pid
echo -e "${GREEN}✓ 安全防护模块已启动 (PID: $SECURITY_PID)${NC}"

# 启动分析模块
echo -e "\n${YELLOW}启动数据分析模块...${NC}"
python -m src.analytics.__init__ > logs/analytics.log 2>&1 &
ANALYTICS_PID=$!
echo $ANALYTICS_PID > .analytics.pid
echo -e "${GREEN}✓ 数据分析模块已启动 (PID: $ANALYTICS_PID)${NC}"

# 启动控制面板
echo -e "\n${YELLOW}启动控制面板...${NC}"
python -m src.dashboard.app > logs/dashboard.log 2>&1 &
DASHBOARD_PID=$!
echo $DASHBOARD_PID > .dashboard.pid
echo -e "${GREEN}✓ 控制面板已启动 (PID: $DASHBOARD_PID)${NC}"

echo -e "\n${GREEN}=========================================${NC}"
echo -e "${GREEN}  所有组件已成功启动!  ${NC}"
echo -e "${GREEN}=========================================${NC}"
echo -e "控制面板地址: ${YELLOW}http://localhost:5000${NC}"
echo -e "查看日志: ${YELLOW}tail -f logs/*.log${NC}"
echo -e "停止平台: ${YELLOW}./scripts/stop_simulation.sh${NC}"

# 退出虚拟环境
deactivate