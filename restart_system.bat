@echo off
chcp 65001
echo ========================================
echo Force Restart Data Center Site Selection System
echo ========================================
echo.

echo 🔄 Stopping all related processes...
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul

echo.
echo ⏳ Waiting 3 seconds...
timeout /t 3 /nobreak >nul

echo.
echo 🔄 Restarting system...
echo Setting proxy...
set HTTP_PROXY=http://127.0.0.1:1082
set HTTPS_PROXY=http://127.0.0.1:1082

echo Starting Basic AI analysis mode...
copy "frontend\src\App_simple.tsx" "frontend\src\App.tsx" >nul
cd frontend
call npm run build
cd ..

echo.
echo 🚀 Starting backend server...
start "Backend Server" cmd /k "python start_system.py"

echo.
echo ========================================
echo ✅ System restart complete!
echo ========================================
echo.
echo Frontend interface: http://localhost:3000
echo Backend API: http://localhost:8000
echo.
echo Wait for the backend to finish starting before testing...
echo.
pause