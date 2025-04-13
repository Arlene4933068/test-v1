#!/bin/bash

# 小米AIoT边缘安全防护研究平台 - 生成报告脚本
# 此脚本用于生成安全防护分析报告

# 设置颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# 获取当前日期和时间
DATETIME=$(date +"%Y%m%d_%H%M%S")
REPORT_FILE="reports/security_report_${DATETIME}.pdf"

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  小米AIoT边缘安全防护研究平台报告生成脚本  ${NC}"
echo -e "${GREEN}=========================================${NC}"

# 激活虚拟环境
if [ -d "venv" ]; then
    echo -e "${YELLOW}激活虚拟环境...${NC}"
    source venv/bin/activate
else
    echo -e "${RED}未找到虚拟环境，请先运行 setup.sh${NC}"
    exit 1
fi

# 检查报告目录是否存在
echo -e "\n${YELLOW}检查报告目录...${NC}"
if [ ! -d "reports" ]; then
    echo -e "${YELLOW}创建报告目录...${NC}"
    mkdir -p reports
fi

# 设置报告类型
echo -e "\n${YELLOW}请选择报告类型:${NC}"
echo -e "1) 完整安全分析报告 (包含所有攻击检测和防护数据)"
echo -e "2) 性能分析报告 (关注系统响应时间和资源占用)"
echo -e "3) 漏洞分析报告 (专注于已检测到的漏洞)"
echo -e "4) 攻击模式分析报告 (分析攻击行为模式)"
echo -e "5) 所有报告"

read -r option

# 根据选择设置报告参数
case $option in
    1)
        REPORT_TYPE="full"
        echo -e "${GREEN}已选择: 完整安全分析报告${NC}"
        ;;
    2)
        REPORT_TYPE="performance"
        echo -e "${GREEN}已选择: 性能分析报告${NC}"
        ;;
    3)
        REPORT_TYPE="vulnerability"
        echo -e "${GREEN}已选择: 漏洞分析报告${NC}"
        ;;
    4)
        REPORT_TYPE="attack_pattern"
        echo -e "${GREEN}已选择: 攻击模式分析报告${NC}"
        ;;
    5)
        REPORT_TYPE="all"
        echo -e "${GREEN}已选择: 所有报告${NC}"
        ;;
    *)
        echo -e "${RED}无效选项，默认生成完整安全分析报告${NC}"
        REPORT_TYPE="full"
        ;;
esac

# 设置报告时间范围
echo -e "\n${YELLOW}请选择报告时间范围:${NC}"
echo -e "1) 最近24小时"
echo -e "2) 最近7天"
echo -e "3) 最近30天"
echo -e "4) 全部数据"
echo -e "5) 自定义时间范围"

read -r time_option

# 根据选择设置时间范围
case $time_option in
    1)
        TIME_RANGE="24h"
        echo -e "${GREEN}已选择: 最近24小时${NC}"
        ;;
    2)
        TIME_RANGE="7d"
        echo -e "${GREEN}已选择: 最近7天${NC}"
        ;;
    3)
        TIME_RANGE="30d"
        echo -e "${GREEN}已选择: 最近30天${NC}"
        ;;
    4)
        TIME_RANGE="all"
        echo -e "${GREEN}已选择: 全部数据${NC}"
        ;;
    5)
        echo -e "${YELLOW}请输入起始日期 (格式: YYYY-MM-DD):${NC}"
        read -r start_date
        echo -e "${YELLOW}请输入结束日期 (格式: YYYY-MM-DD):${NC}"
        read -r end_date
        TIME_RANGE="${start_date}_${end_date}"
        echo -e "${GREEN}已选择: 自定义时间范围 ${start_date} 至 ${end_date}${NC}"
        ;;
    *)
        echo -e "${RED}无效选项，默认使用全部数据${NC}"
        TIME_RANGE="all"
        ;;
esac

# 生成报告
echo -e "\n${YELLOW}正在生成报告...${NC}"
echo -e "类型: ${REPORT_TYPE}"
echo -e "时间范围: ${TIME_RANGE}"
echo -e "输出文件: ${REPORT_FILE}"

# 生成报告的Python命令
python -m src.analytics.report_generator --type "${REPORT_TYPE}" --time-range "${TIME_RANGE}" --output "${REPORT_FILE}"

# 检查命令执行结果
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}报告生成成功!${NC}"
    echo -e "报告保存在: ${YELLOW}${REPORT_FILE}${NC}"
    
    # 询问是否在浏览器中打开报告
    echo -e "\n${YELLOW}是否打开报告? (y/n)${NC}"
    read -r open_option
    if [ "$open_option" = "y" ] || [ "$open_option" = "Y" ]; then
        if command -v xdg-open > /dev/null; then
            xdg-open "${REPORT_FILE}"
        elif command -v open > /dev/null; then
            open "${REPORT_FILE}"
        else
            echo -e "${RED}无法自动打开报告，请手动打开${NC}"
        fi
    fi
else
    echo -e "\n${RED}报告生成失败!${NC}"
    echo -e "请检查日志文件以获取更多信息: ${YELLOW}logs/analytics.log${NC}"
fi

echo -e "\n${GREEN}=========================================${NC}"
echo -e "${GREEN}  报告生成脚本完成  ${NC}"
echo -e "${GREEN}=========================================${NC}"

# 退出虚拟环境
deactivate