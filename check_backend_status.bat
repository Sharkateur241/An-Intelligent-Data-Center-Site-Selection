@echo off
chcp 65001
echo 检查后端状态...
.\.venv\Scripts\python.exe check_backend_status.py
pause
