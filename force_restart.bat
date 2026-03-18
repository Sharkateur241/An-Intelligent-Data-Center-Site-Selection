@echo off
chcp 65001
echo ========================================
echo Force Restart System - Clear All Cache
echo ========================================
echo.

echo 🔄 Stopping all related processes...
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul

echo.
echo ⏳ Waiting 5 seconds to ensure processes are fully stopped...
timeout /t 5 /nobreak >nul

echo.
echo 🧹 Clearing Python cache...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul

echo.
echo 🔄 Restarting system...
echo Setting proxy...
set HTTP_PROXY=http://127.0.0.1:1082
set HTTPS_PROXY=http://127.0.0.1:1082

echo Starting AI analysis mode...
cd frontend
call npm run build
cd ..

echo.
echo 🚀 Starting backend server...
start "Backend Server" cmd /k "python start_system.py"

echo.
echo ========================================
echo ✅ Force restart complete!
echo ========================================
echo.
echo Wait for the backend to finish starting before testing...
echo The backend console should display new debug information
echo.
pause