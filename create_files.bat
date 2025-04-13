@echo off
setlocal enabledelayedexpansion

:: 创建src目录下的空文件
mkdir "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\device_simulator"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\device_simulator\gateway.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\device_simulator\router.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\device_simulator\speaker.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\device_simulator\camera.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\device_simulator\simulator_base.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\device_simulator\__init__.py"

mkdir "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\platform_connector"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\platform_connector\edgex_connector.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\platform_connector\thingsboard_connector.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\platform_connector\connector_base.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\platform_connector\__init__.py"

mkdir "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\security\rules"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\security\attack_detector.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\security\protection_engine.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\security\security_logger.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\security\rules\ddos_rules.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\security\rules\mitm_rules.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\security\rules\firmware_rules.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\security\rules\credential_rules.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\security\rules\__init__.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\security\__init__.py"

mkdir "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\analytics"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\analytics\data_collector.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\analytics\statistical_analyzer.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\analytics\report_generator.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\analytics\__init__.py"

mkdir "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\dashboard\static"
mkdir "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\dashboard\templates"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\dashboard\app.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\dashboard\device_manager.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\dashboard\security_config.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\dashboard\visualization.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\dashboard\__init__.py"

mkdir "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\utils"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\utils\config.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\utils\logger.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\utils\crypto.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\utils\protocol.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\utils\__init__.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\src\__init__.py"

:: 创建config目录下的空文件
mkdir "d:\0pj\test-v1\xiaomi-aiot-edge-security\config"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\config\simulator.yaml"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\config\edgex.yaml"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\config\thingsboard.yaml"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\config\security.yaml"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\config\logging.yaml"

:: 创建tests目录下的空文件
mkdir "d:\0pj\test-v1\xiaomi-aiot-edge-security\tests"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\tests\test_simulator.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\tests\test_connector.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\tests\test_security.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\tests\test_analytics.py"

:: 创建docs目录下的空文件
mkdir "d:\0pj\test-v1\xiaomi-aiot-edge-security\docs"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\docs\setup.md"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\docs\usage.md"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\docs\architecture.md"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\docs\api.md"

:: 创建scripts目录下的空文件
mkdir "d:\0pj\test-v1\xiaomi-aiot-edge-security\scripts"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\scripts\setup.sh"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\scripts\start_simulation.sh"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\scripts\stop_simulation.sh"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\scripts\generate_report.sh"

:: 创建根目录下的空文件
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\.gitignore"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\README.md"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\requirements.txt"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\setup.py"
type nul > "d:\0pj\test-v1\xiaomi-aiot-edge-security\docker-compose.yml"

echo 所有空文件已创建完成
pause