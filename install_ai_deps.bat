@echo off
chcp 65001
echo 安装AI分析所需的依赖包...
echo.

echo 安装PyTorch...
.\.venv\Scripts\python.exe -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

echo.
echo 安装其他AI依赖...
.\.venv\Scripts\python.exe -m pip install opencv-python pillow numpy

echo.
echo 安装完成！
pause
