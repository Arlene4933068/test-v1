#!/bin/bash

# 小米AIoT边缘安全防护研究平台 - 停止仿真脚本
# 此脚本用于停止仿真平台的各个组件

# 设置颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  小米AIoT边缘安全防护研究平台停止脚本  ${NC}"
echo -e "${GREEN}=========================================${NC}"

# 停止控制面板
if [ -f .dashboard.pid ]; then
    DASHBOARD_PID=$(cat .dashboard.pid)
    echo -e "${YELLOW}停止控制面板 (PID: $DASHBOARD_PID)...${NC}"
    if ps -p $DASHBOARD_PID > /dev/null; then
        kill $DASHBOARD_PID
        echo -e "${GREEN}✓ 控制面板已停止${NC}"
    else
        echo -e "${RED}! 控制面板进程不存在${NC}"
    fi
    rm .dashboard.pid
else
    echo -e "${YELLOW}! 未找到控制面板PID文件${NC}"
fi

# 停止数据分析模块
if [ -f .analytics.pid ]; then
    ANALYTICS_PID=$(cat .analytics.pid)
    echo -e "${YELLOW}停止数据分析模块 (PID: $ANALYTICS_PID)...${NC}"
    if ps -p $ANALYTICS_PID > /dev/null; then
        kill $ANALYTICS_PID
        echo -e "${GREEN}✓ 数据分析模块已停止${NC}"
    else
        echo -e "${RED}! 数据分析模块进程不存在${NC}"
    fi
    rm .analytics.pid
else
    echo -e "${YELLOW}! 未找到数据分析模块PID文件${NC}"
fi

# 停止安全防护模块
if [ -f .security.pid ]; then
    SECURITY_PID=$(cat .security.pid)
    echo -e "${YELLOW}停止安全防护模块 (PID: $SECURITY_PID)...${NC}"
    if ps -p $SECURITY_PID > /dev/null; then
        kill $SECURITY_PID
        echo -e "${GREEN}✓ 安全防护模块已停止${NC}"
    else
        echo -e "${RED}! 安全防护模块进程不存在${NC}"
    fi
    rm .security.pid
else
    echo -e "${YELLOW}! 未找到安全防护模块PID文件${NC}"
fi

# 停止设备模拟器
if [ -f .simulator.pid ]; then
    SIMULATOR_PID=$(cat .simulator.pid)
    echo -e "${YELLOW}停止设备模拟器 (PID: $SIMULATOR_PID)...${NC}"
    if ps -p $SIMULATOR_PID > /dev/null; then
        kill $SIMULATOR_PID
        echo -e "${GREEN}✓ 设备模拟器已停止${NC}"
    else
        echo -e "${RED}! 设备模拟器进程不存在${NC}"
    fi
    rm .simulator.pid
else
    echo -e "${YELLOW}! 未找到设备模拟器PID文件${NC}"
fi

# 检查是否有任何组件进程仍在运行
echo -e "\n${YELLOW}检查是否还有组件进程运行...${NC}"
PROCESSES=$(ps aux | grep "python -m src\." | grep -v grep)
if [ -n "$PROCESSES" ]; then
    echo -e "${RED}! 检测到以下进程可能仍在运行:${NC}"
    echo "$PROCESSES"
    echo -e "${YELLOW}是否强制终止所有相关进程? (y/n)${NC}"
    read -r answer
    if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
        pkill -f "python -m src\."
        echo -e "${GREEN}✓ 已强制终止所有相关进程${NC}"
    else
        echo -e "${YELLOW}跳过强制终止${NC}"
    fi
else
    echo -e "${GREEN}✓ 没有检测到运行中的组件进程${NC}"
fi

echo -e "\n${GREEN}=========================================${NC}"
echo -e "${GREEN}  所有组件已成功停止!  ${NC}"
echo -e "${GREEN}=========================================${NC}"
echo -e "重新启动平台: ${YELLOW}./scripts/start_simulation.sh${NC}"