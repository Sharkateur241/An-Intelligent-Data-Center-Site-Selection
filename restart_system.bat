@echo off
chcp 65001
echo ========================================
echo 强制重启数据中心选址系统
echo ========================================
echo.

echo 🔄 正在停止所有相关进程...
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul

echo.
echo ⏳ 等待3秒...
timeout /t 3 /nobreak >nul

echo.
echo 🔄 重新启动系统...
echo 设置代理...
set HTTP_PROXY=http://127.0.0.1:1082
set HTTPS_PROXY=http://127.0.0.1:1082

echo 启动基础AI分析模式...
copy "frontend\src\App_simple.tsx" "frontend\src\App.tsx" >nul
cd frontend
call npm run build
cd ..

echo.
echo 🚀 启动后端服务器...
start "Backend Server" cmd /k "python start_system.py"

echo.
echo ========================================
echo ✅ 系统重启完成！
echo ========================================
echo.
echo 前端界面: http://localhost:3000
echo 后端API: http://localhost:8000
echo.
echo 等待后端启动完成后再测试...
echo.
pause
