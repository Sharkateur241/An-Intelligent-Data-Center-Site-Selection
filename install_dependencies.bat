@echo off
chcp 65001 >nul
echo =====================================
echo Install Project Dependency Packages
echo =====================================
echo.

echo Installing Python dependency packages...
echo.

echo [1/10] Installing core dependencies...
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install pydantic==2.5.0
pip install python-multipart==0.0.6

echo.
echo [2/10] Installing data processing dependencies...
pip install numpy==1.24.3
pip install pandas==2.0.3
pip install scipy==1.11.4

echo.
echo [3/10] Installing machine learning dependencies...
pip install scikit-learn==1.3.2
pip install opencv-python==4.8.1.78

echo.
echo [4/10] Installing deep learning dependencies...
pip install torch==2.0.1
pip install torchvision==0.15.2

echo.
echo [5/10] Installing geospatial analysis dependencies...
pip install earthengine-api==0.1.375
pip install geopandas==0.14.0
pip install shapely==2.0.2

echo.
echo [6/10] Installing image processing dependencies...
pip install Pillow==10.1.0
pip install matplotlib==3.7.2
pip install seaborn==0.12.2

echo.
echo [7/10] Installing HTTP request dependencies...
pip install requests==2.31.0
pip install httpx==0.25.2
pip install aiohttp==3.9.1

echo.
echo [8/10] Installing AI analysis dependencies...
pip install openai==1.3.0

echo.
echo [9/10] Installing utility library dependencies...
pip install python-dotenv==1.0.0
pip install typing-extensions==4.8.0

echo.
echo [10/10] Installing other required dependencies...
pip install asyncio
pip install json5
pip install base64

echo.
echo =====================================
echo Dependency installation complete!
echo =====================================
echo.
echo You can now run the system:
echo 1. Double-click start.bat to start the system
echo 2. Or run python start_system.py
echo.
pause