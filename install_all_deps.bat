@echo off
chcp 65001
echo ========================================
echo 安装数据中心选址系统所有依赖包
echo ========================================
echo.

echo 🔄 正在安装AI分析依赖包...
echo.

echo 1/8 安装PyTorch (CPU版本)...
.\.venv\Scripts\python.exe -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

echo.
echo 2/8 安装OpenCV...
.\.venv\Scripts\python.exe -m pip install opencv-python

echo.
echo 3/8 安装图像处理库...
.\.venv\Scripts\python.exe -m pip install pillow numpy

echo.
echo 4/8 安装科学计算库...
.\.venv\Scripts\python.exe -m pip install scipy scikit-learn

echo.
echo 5/8 安装数据处理库...
.\.venv\Scripts\python.exe -m pip install pandas matplotlib seaborn

echo.
echo 6/8 安装异步HTTP库...
.\.venv\Scripts\python.exe -m pip install aiohttp

echo.
echo 7/8 安装Google Earth Engine...
.\.venv\Scripts\python.exe -m pip install earthengine-api

echo.
echo 8/8 安装OpenAI库...
.\.venv\Scripts\python.exe -m pip install openai

echo.
echo ========================================
echo ✅ 所有依赖包安装完成！
echo ========================================
echo.
echo 现在可以运行系统了：
echo 1. 双击 start.bat 启动系统
echo 2. 或双击 test_analysis.bat 测试分析流程
echo.
pause
