#!/bin/bash
#
# 小米AIoT边缘安全防护研究平台 - 环境设置脚本
# 用于初始化系统环境、安装依赖和配置连接
#

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印标题
echo -e "${BLUE}=====================================================${NC}"
echo -e "${BLUE}   小米AIoT边缘安全防护研究平台 - 环境初始化脚本   ${NC}"
echo -e "${BLUE}=====================================================${NC}"
echo ""

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# 获取项目根目录
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${YELLOW}项目根目录: ${PROJECT_ROOT}${NC}"
echo ""

# 检查Python环境
check_python() {
    echo -e "${YELLOW}检查Python环境...${NC}"
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        echo -e "${GREEN}Python已安装: ${PYTHON_VERSION}${NC}"
        
        # 检查Python版本是否符合要求
        PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        if (( $(echo "$PY_VER < 3.8" | bc -l) )); then
            echo -e "${RED}错误: 需要Python 3.8或更高版本${NC}"
            echo -e "${YELLOW}当前版本: ${PY_VER}${NC}"
            exit 1
        fi
    else
        echo -e "${RED}错误: 未找到Python3${NC}"
        echo -e "${YELLOW}请安装Python 3.8或更高版本${NC}"
        exit 1
    fi
    echo ""
}

# 检查Docker环境
check_docker() {
    echo -e "${YELLOW}检查Docker环境...${NC}"
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version)
        echo -e "${GREEN}Docker已安装: ${DOCKER_VERSION}${NC}"
    else
        echo -e "${RED}错误: 未找到Docker${NC}"
        echo -e "${YELLOW}请安装Docker 20.10.0或更高版本${NC}"
        exit 1
    fi
    
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version)
        echo -e "${GREEN}Docker Compose已安装: ${COMPOSE_VERSION}${NC}"
    else
        echo -e "${RED}错误: 未找到Docker Compose${NC}"
        echo -e "${YELLOW}请安装Docker Compose 1.29.0或更高版本${NC}"
        exit 1
    fi
    echo ""
}

# 检查EdgeX Foundry和ThingsBoard Edge的Docker容器
check_edge_platforms() {
    echo -e "${YELLOW}检查边缘计算平台容器...${NC}"
    
    # 检查EdgeX Foundry容器
    if docker ps | grep -q "edgex"; then
        echo -e "${GREEN}EdgeX Foundry容器正在运行${NC}"
    else
        echo -e "${RED}警告: 未检测到运行中的EdgeX Foundry容器${NC}"
        echo -e "${YELLOW}您确定要继续安装吗? 平台需要连接到EdgeX Foundry [y/N]${NC}"
        read -r response
        if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            echo -e "${YELLOW}安装已取消。请先启动EdgeX Foundry容器。${NC}"
            exit 1
        fi
    fi
    
    # 检查ThingsBoard Edge容器
    if docker ps | grep -q "thingsboard"; then
        echo -e "${GREEN}ThingsBoard Edge容器正在运行${NC}"
    else
        echo -e "${RED}警告: 未检测到运行中的ThingsBoard Edge容器${NC}"
        echo -e "${YELLOW}您确定要继续安装吗? 平台需要连接到ThingsBoard Edge [y/N]${NC}"
        read -r response
        if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            echo -e "${YELLOW}安装已取消。请先启动ThingsBoard Edge容器。${NC}"
            exit 1
        fi
    fi
    echo ""
}

# 创建Python虚拟环境
create_virtualenv() {
    echo -e "${YELLOW}创建Python虚拟环境...${NC}"
    if [ -d "${PROJECT_ROOT}/venv" ]; then
        echo -e "${YELLOW}虚拟环境已存在${NC}"
        echo -e "${YELLOW}是否重新创建虚拟环境? [y/N]${NC}"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            echo -e "${YELLOW}删除旧的虚拟环境...${NC}"
            rm -rf "${PROJECT_ROOT}/venv"
        else
            echo -e "${GREEN}使用现有虚拟环境${NC}"
            return
        fi
    fi
    
    python3 -m venv "${PROJECT_ROOT}/venv"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}虚拟环境创建成功${NC}"
    else
        echo -e "${RED}错误: 虚拟环境创建失败${NC}"
        exit 1
    fi
    echo ""
}

# 安装依赖
install_dependencies() {
    echo -e "${YELLOW}安装Python依赖...${NC}"
    # 激活虚拟环境
    source "${PROJECT_ROOT}/venv/bin/activate"
    
    # 安装依赖
    echo -e "${YELLOW}从requirements.txt安装依赖...${NC}"
    pip install --upgrade pip
    pip install -r "${PROJECT_ROOT}/requirements.txt"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}依赖安装成功${NC}"
    else
        echo -e "${RED}错误: 依赖安装失败${NC}"
        exit 1
    fi
    
    # 安装开发模式
    echo -e "${YELLOW}以开发模式安装项目...${NC}"
    pip install -e "${PROJECT_ROOT}"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}项目安装成功${NC}"
    else
        echo -e "${RED}错误: 项目安装失败${NC}"
        exit 1
    fi
    echo ""
}

# 配置系统
configure_system() {
    echo -e "${YELLOW}配置系统...${NC}"
    
    # 创建日志目录
    mkdir -p "${PROJECT_ROOT}/logs"
    
    # 创建数据目录
    mkdir -p "${PROJECT_ROOT}/data"
    
    # 创建报告目录
    mkdir -p "${PROJECT_ROOT}/reports"
    
    # 检查配置文件
    echo -e "${YELLOW}检查配置文件...${NC}"
    
    # 检查EdgeX配置
    if [ ! -f "${PROJECT_ROOT}/config/edgex.yaml" ]; then
        if [ -f "${PROJECT_ROOT}/config/edgex.yaml.example" ]; then
            echo -e "${YELLOW}创建EdgeX配置文件...${NC}"
            cp "${PROJECT_ROOT}/config/edgex.yaml.example" "${PROJECT_ROOT}/config/edgex.yaml"
            echo -e "${GREEN}已创建EdgeX配置文件，请根据您的环境修改${NC}"
            echo -e "${YELLOW}配置文件位置: ${PROJECT_ROOT}/config/edgex.yaml${NC}"
        else
            echo -e "${RED}错误: EdgeX配置模板文件不存在${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}EdgeX配置文件已存在${NC}"
    fi
    
    # 检查ThingsBoard配置
    if [ ! -f "${PROJECT_ROOT}/config/thingsboard.yaml" ]; then
        if [ -f "${PROJECT_ROOT}/config/thingsboard.yaml.example" ]; then
            echo -e "${YELLOW}创建ThingsBoard配置文件...${NC}"
            cp "${PROJECT_ROOT}/config/thingsboard.yaml.example" "${PROJECT_ROOT}/config/thingsboard.yaml"
            echo -e "${GREEN}已创建ThingsBoard配置文件，请根据您的环境修改${NC}"
            echo -e "${YELLOW}配置文件位置: ${PROJECT_ROOT}/config/thingsboard.yaml${NC}"
        else
            echo -e "${RED}错误: ThingsBoard配置模板文件不存在${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}ThingsBoard配置文件已存在${NC}"
    fi
    
    # 检查模拟器配置
    if [ ! -f "${PROJECT_ROOT}/config/simulator.yaml" ]; then
        if [ -f "${PROJECT_ROOT}/config/simulator.yaml.example" ]; then
            echo -e "${YELLOW}创建模拟器配置文件...${NC}"
            cp "${PROJECT_ROOT}/config/simulator.yaml.example" "${PROJECT_ROOT}/config/simulator.yaml"
            echo -e "${GREEN}已创建模拟器配置文件${NC}"
        else
            echo -e "${RED}错误: 模拟器配置模板文件不存在${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}模拟器配置文件已存在${NC}"
    fi
    
    # 检查安全配置
    if [ ! -f "${PROJECT_ROOT}/config/security.yaml" ]; then
        if [ -f "${PROJECT_ROOT}/config/security.yaml.example" ]; then
            echo -e "${YELLOW}创建安全配置文件...${NC}"
            cp "${PROJECT_ROOT}/config/security.yaml.example" "${PROJECT_ROOT}/config/security.yaml"
            echo -e "${GREEN}已创建安全配置文件${NC}"
        else
            echo -e "${RED}错误: 安全配置模板文件不存在${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}安全配置文件已存在${NC}"
    fi
    
    # 检查日志配置
    if [ ! -f "${PROJECT_ROOT}/config/logging.yaml" ]; then
        if [ -f "${PROJECT_ROOT}/config/logging.yaml.example" ]; then
            echo -e "${YELLOW}创建日志配置文件...${NC}"
            cp "${PROJECT_ROOT}/config/logging.yaml.example" "${PROJECT_ROOT}/config/logging.yaml"
            echo -e "${GREEN}已创建日志配置文件${NC}"
        else
            echo -e "${RED}错误: 日志配置模板文件不存在${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}日志配置文件已存在${NC}"
    fi
    
    echo -e "${GREEN}系统配置完成${NC}"
    echo ""
}

# 运行测试
run_tests() {
    echo -e "${YELLOW}运行基本测试...${NC}"
    
    # 激活虚拟环境
    source "${PROJECT_ROOT}/venv/bin/activate"
    
    # 运行单元测试
    python -m unittest discover -s "${PROJECT_ROOT}/tests" -p "test_*.py"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}测试通过${NC}"
    else
        echo -e "${RED}警告: 测试未通过${NC}"
        echo -e "${YELLOW}您确定要继续吗? [y/N]${NC}"
        read -r response
        if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            echo -e "${YELLOW}设置已取消。请修复测试错误后重试。${NC}"
            exit 1
        fi
    fi
    echo ""
}

# 设置权限
set_permissions() {
    echo -e "${YELLOW}设置执行权限...${NC}"
    
    # 设置脚本执行权限
    chmod +x "${PROJECT_ROOT}/scripts/"*.sh
    
    echo -e "${GREEN}权限设置完成${NC}"
    echo ""
}

# 完成设置
finish_setup() {
    echo -e "${GREEN}=====================================================${NC}"
    echo -e "${GREEN}   小米AIoT边缘安全防护研究平台环境设置已完成!   ${NC}"
    echo -e "${GREEN}=====================================================${NC}"
    echo ""
    echo -e "${YELLOW}要启动平台, 请运行:${NC}"
    echo -e "${BLUE}source ${PROJECT_ROOT}/venv/bin/activate${NC}"
    echo -e "${BLUE}bash ${PROJECT_ROOT}/scripts/start_simulation.sh${NC}"
    echo ""
    echo -e "${YELLOW}平台控制面板将在启动后可访问:${NC}"
    echo -e "${BLUE}http://localhost:5000${NC}"
    echo ""
    echo -e "${YELLOW}请确保您已根据自己的环境修改配置文件:${NC}"
    echo -e "${BLUE}${PROJECT_ROOT}/config/edgex.yaml${NC}"
    echo -e "${BLUE}${PROJECT_ROOT}/config/thingsboard.yaml${NC}"
    echo ""
}

# 主函数
main() {
    check_python
    check_docker
    check_edge_platforms
    create_virtualenv
    install_dependencies
    configure_system
    run_tests
    set_permissions
    finish_setup
}

# 执行主函数
main