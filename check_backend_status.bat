@echo off
chcp 65001
echo Checking backend status...
.\.venv\Scripts\python.exe check_backend_status.py
pause
