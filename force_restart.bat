@echo off
chcp 65001
echo ========================================
echo 强制重启系统 - 清除所有缓存
echo ========================================
echo.

echo 🔄 正在停止所有相关进程...
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul

echo.
echo ⏳ 等待5秒确保进程完全停止...
timeout /t 5 /nobreak >nul

echo.
echo 🧹 清除Python缓存...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul

echo.
echo 🔄 重新启动系统...
echo 设置代理...
set HTTP_PROXY=http://127.0.0.1:7897
set HTTPS_PROXY=http://127.0.0.1:7897

echo 启动AI分析模式...
cd frontend
call npm run build
cd ..

echo.
echo 🚀 启动后端服务器...
start "Backend Server" cmd /k "python start_system.py"

echo.
echo ========================================
echo ✅ 强制重启完成！
echo ========================================
echo.
echo 等待后端启动完成后再测试...
echo 后端控制台应该显示新的调试信息
echo.
pause
