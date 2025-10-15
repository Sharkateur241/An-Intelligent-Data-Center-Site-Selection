@echo off
chcp 65001 >nul
echo =====================================
echo 数据中心智能选址与能源优化系统
echo =====================================
echo.

echo 正在启动系统...
echo 设置代理...
set HTTP_PROXY=http://127.0.0.1:7897
set HTTPS_PROXY=http://127.0.0.1:7897

echo 启动完整AI分析模式...
cd frontend
call npm run build
cd ..
start "Backend Server" cmd /k "python start_system.py"

echo.
echo =====================================
echo 系统启动完成！
echo =====================================
echo.
echo 前端界面: http://localhost:3000
echo 后端API: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.
echo 后端服务器窗口应该会自动打开
echo 如果没有打开，请手动运行: python start_system.py
echo.
echo 按任意键关闭此窗口...
pause >nul