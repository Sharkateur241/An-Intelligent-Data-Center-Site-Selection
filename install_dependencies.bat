@echo off
chcp 65001 >nul
echo =====================================
echo 安装项目依赖包
echo =====================================
echo.

echo 正在安装Python依赖包...
echo.

echo [1/10] 安装核心依赖...
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install pydantic==2.5.0
pip install python-multipart==0.0.6

echo.
echo [2/10] 安装数据处理依赖...
pip install numpy==1.24.3
pip install pandas==2.0.3
pip install scipy==1.11.4

echo.
echo [3/10] 安装机器学习依赖...
pip install scikit-learn==1.3.2
pip install opencv-python==4.8.1.78

echo.
echo [4/10] 安装深度学习依赖...
pip install torch==2.0.1
pip install torchvision==0.15.2

echo.
echo [5/10] 安装地理空间分析依赖...
pip install earthengine-api==0.1.375
pip install geopandas==0.14.0
pip install shapely==2.0.2

echo.
echo [6/10] 安装图像处理依赖...
pip install Pillow==10.1.0
pip install matplotlib==3.7.2
pip install seaborn==0.12.2

echo.
echo [7/10] 安装HTTP请求依赖...
pip install requests==2.31.0
pip install httpx==0.25.2
pip install aiohttp==3.9.1

echo.
echo [8/10] 安装AI分析依赖...
pip install openai==1.3.0

echo.
echo [9/10] 安装工具库依赖...
pip install python-dotenv==1.0.0
pip install typing-extensions==4.8.0

echo.
echo [10/10] 安装其他必要依赖...
pip install asyncio
pip install json5
pip install base64

echo.
echo =====================================
echo 依赖安装完成！
echo =====================================
echo.
echo 现在可以运行系统了：
echo 1. 双击 start.bat 启动系统
echo 2. 或运行 python start_system.py
echo.
pause