@echo off
chcp 65001 >nul
echo Starting Enhanced Data Center Location System...

REM Switch to script directory
cd /d "%~dp0"

REM Set proxy environment variables
set HTTP_PROXY=http://127.0.0.1:7897
set HTTPS_PROXY=http://127.0.0.1:7897
set http_proxy=http://127.0.0.1:7897
set https_proxy=http://127.0.0.1:7897

echo Current directory: %CD%
echo Proxy set to: %HTTP_PROXY%

REM Switch to backend directory
cd backend
echo Switched to backend directory: %CD%

REM 运行增强版后端
echo Starting enhanced backend service...
python main_enhanced.py

pause
