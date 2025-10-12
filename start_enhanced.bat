@echo off
chcp 65001 >nul
echo =====================================
echo 数据中心智能选址系统 - 增强版
echo =====================================
echo.

echo 设置代理环境变量...
set HTTP_PROXY=http://127.0.0.1:7897
set HTTPS_PROXY=http://127.0.0.1:7897
set http_proxy=http://127.0.0.1:7897
set https_proxy=http://127.0.0.1:7897
set ALL_PROXY=http://127.0.0.1:7897
set all_proxy=http://127.0.0.1:7897

echo 代理设置完成: http://127.0.0.1:7897
echo.

echo 启动增强版后端服务...
cd backend
start "Enhanced Backend Server" cmd /k "python main_enhanced.py"
cd ..

echo.
echo =====================================
echo 系统启动完成！
echo =====================================
echo.
echo 前端界面: http://localhost:3000
echo 后端API: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.
echo 增强版特性:
echo   ✅ 专业8维度评估框架
echo   ✅ 无AI超时问题
echo   ✅ 快速响应分析
echo   ✅ 全面选址建议
echo.
echo 后端服务器窗口应该会自动打开
echo 如果没有打开，请手动运行: cd backend && python main_enhanced.py
echo.
echo 按任意键关闭此窗口...
pause >nul
