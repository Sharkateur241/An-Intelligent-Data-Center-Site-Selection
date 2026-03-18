@echo off
chcp 65001 >nul
echo =====================================
echo Data Center Intelligent Site Selection & Energy Optimization
echo =====================================
echo.

echo Starting system...
echo Setting proxy...
set HTTP_PROXY=http://127.0.0.1:1082
set HTTPS_PROXY=http://127.0.0.1:1082

echo Launching full AI analysis mode...
cd frontend
call npm run build
cd ..
start "Backend Server" cmd /k "python start_system.py"

echo.
echo =====================================
echo System started!
echo =====================================
echo.
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8000
echo API docs: http://localhost:8000/docs
echo.
echo Backend server window should open automatically.
echo If not, run manually: python start_system.py
echo.
echo Press any key to close this window...
pause >nul
