@echo off
echo =====================================
echo 🚀 Data Center Intelligent Site Selection - One-Click Install
echo =====================================
echo.

echo 📋 Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to PATH
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python OK
echo.

echo 📦 Installing Python dependencies...
echo Installing core deps...
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install pydantic==2.5.0
pip install python-multipart==0.0.6

echo Installing data-processing deps...
pip install numpy==1.24.3
pip install pandas==2.0.3
pip install scipy==1.11.4

echo Installing machine learning deps...
pip install scikit-learn==1.3.2
pip install opencv-python==4.8.1.78

echo Installing geospatial deps...
pip install earthengine-api==0.1.375
pip install geopandas==0.14.0
pip install shapely==2.0.2

echo Installing image-processing deps...
pip install Pillow==10.1.0
pip install matplotlib==3.7.2
pip install seaborn==0.12.2

echo Installing HTTP deps...
pip install requests==2.31.0
pip install httpx==0.25.2
pip install aiohttp==3.9.1

echo Installing utility deps...
pip install python-dotenv==1.0.0
pip install typing-extensions==4.8.0

echo.
echo ✅ Python dependencies installed!
echo.

echo 📋 Checking Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed
    echo Please install Node.js 16+ and add it to PATH
    echo Download: https://nodejs.org/
    echo.
    echo ⚠️  Note: frontend needs Node.js
    echo You can skip if you only need the backend API
    pause
) else (
    echo ✅ Node.js OK
    echo.
    echo 📦 Installing frontend deps...
    cd frontend
    npm install
    if %errorlevel% neq 0 (
        echo ❌ Frontend dependency install failed
        echo Please check network or run manually: cd frontend && npm install
    ) else (
        echo ✅ Frontend dependencies installed!
        echo.
        echo 🏗️  Building frontend...
        npm run build
        if %errorlevel% neq 0 (
            echo ❌ Frontend build failed
            echo Please run manually: cd frontend && npm run build
        ) else (
            echo ✅ Frontend build complete!
        )
    )
    cd ..
)

echo.
echo =====================================
echo 🎉 Installation finished!
echo =====================================
echo.
echo 📋 Next steps:
echo 1. Configure GEE auth: python setup_gee_auth.py
echo 2. Start system: python start_system.py
echo 3. Or use batch: start_simple.bat
echo.
echo 📱 Access:
echo   Frontend: http://localhost:3000
echo   Backend API: http://localhost:8000
echo   API docs: http://localhost:8000/docs
echo.
echo ⚠️  Important:
echo   - Google Earth Engine account required
echo   - Stable network connection needed
echo   - Python 3.8+ recommended
echo =====================================
pause
