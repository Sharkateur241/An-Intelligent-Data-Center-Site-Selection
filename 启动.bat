@echo off
chcp 65001 >nul
echo =====================================
echo 数据中心智能选址与能源优化系统
echo =====================================
echo.

echo 选择启动模式：
echo 1. 基础AI分析模式
echo 2. 高级AI分析模式（时间序列、自定义指标、多维度）
echo 3. 仅启动后端API
echo.

set /p choice=请输入选择 (1-3): 

echo.
echo 设置代理...
set HTTP_PROXY=http://127.0.0.1:7897
set HTTPS_PROXY=http://127.0.0.1:7897

if "%choice%"=="1" (
    echo 启动基础AI分析模式...
    copy "frontend\src\App_simple.tsx" "frontend\src\App.tsx" >nul
    cd frontend
    npm run build
    cd ..
    python start_system.py
) else if "%choice%"=="2" (
    echo 启动高级AI分析模式...
    copy "frontend\src\App_advanced.tsx" "frontend\src\App.tsx" >nul
    cd frontend
    npm run build
    cd ..
    python start_system.py
) else if "%choice%"=="3" (
    echo 仅启动后端API...
    python start_system.py
) else (
    echo 无效选择，启动默认模式...
    copy "frontend\src\App_simple.tsx" "frontend\src\App.tsx" >nul
    cd frontend
    npm run build
    cd ..
    python start_system.py
)

echo.
echo =====================================
echo 系统启动完成！
echo 前端: http://localhost:3000
echo 后端: http://localhost:8000
echo =====================================
pause
