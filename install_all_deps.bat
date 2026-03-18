@echo off
chcp 65001
echo ========================================
echo Install All Dependencies for Data Center Site Selection System
echo ========================================
echo.

echo 🔄 Installing AI analysis dependency packages...
echo.

echo 1/8 Installing PyTorch (CPU version)...
.\.venv\Scripts\python.exe -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

echo.
echo 2/8 Installing OpenCV...
.\.venv\Scripts\python.exe -m pip install opencv-python

echo.
echo 3/8 Installing image processing libraries...
.\.venv\Scripts\python.exe -m pip install pillow numpy

echo.
echo 4/8 Installing scientific computing libraries...
.\.venv\Scripts\python.exe -m pip install scipy scikit-learn

echo.
echo 5/8 Installing data processing libraries...
.\.venv\Scripts\python.exe -m pip install pandas matplotlib seaborn

echo.
echo 6/8 Installing async HTTP library...
.\.venv\Scripts\python.exe -m pip install aiohttp

echo.
echo 7/8 Installing Google Earth Engine...
.\.venv\Scripts\python.exe -m pip install earthengine-api

echo.
echo 8/8 Installing OpenAI library...
.\.venv\Scripts\python.exe -m pip install openai

echo.
echo ========================================
echo ✅ All dependency packages installed successfully!
echo ========================================
echo.
echo You can now run the system:
echo 1. Double-click start.bat to start the system
echo 2. Or double-click test_analysis.bat to test the analysis workflow
echo.
pause