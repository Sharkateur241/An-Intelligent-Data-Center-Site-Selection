@echo off
echo =====================================
echo 🚀 数据中心智能选址系统 - 一键安装
echo =====================================
echo.

echo 📋 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装或未添加到PATH
    echo 请先安装Python 3.8+并添加到系统PATH
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python环境正常
echo.

echo 📦 安装Python依赖包...
echo 正在安装核心依赖...
pip install fastapi==0.104.1
pip install uvicorn[standard]==0.24.0
pip install pydantic==2.5.0
pip install python-multipart==0.0.6

echo 正在安装数据处理依赖...
pip install numpy==1.24.3
pip install pandas==2.0.3
pip install scipy==1.11.4

echo 正在安装机器学习依赖...
pip install scikit-learn==1.3.2
pip install opencv-python==4.8.1.78

echo 正在安装地理空间分析依赖...
pip install earthengine-api==0.1.375
pip install geopandas==0.14.0
pip install shapely==2.0.2

echo 正在安装图像处理依赖...
pip install Pillow==10.1.0
pip install matplotlib==3.7.2
pip install seaborn==0.12.2

echo 正在安装HTTP请求依赖...
pip install requests==2.31.0
pip install httpx==0.25.2
pip install aiohttp==3.9.1

echo 正在安装工具库依赖...
pip install python-dotenv==1.0.0
pip install typing-extensions==4.8.0

echo.
echo ✅ Python依赖安装完成！
echo.

echo 📋 检查Node.js环境...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js未安装
    echo 请先安装Node.js 16+并添加到系统PATH
    echo 下载地址: https://nodejs.org/
    echo.
    echo ⚠️  注意: 前端需要Node.js环境
    echo 如果只需要后端API，可以跳过此步骤
    pause
) else (
    echo ✅ Node.js环境正常
    echo.
    echo 📦 安装前端依赖...
    cd frontend
    npm install
    if %errorlevel% neq 0 (
        echo ❌ 前端依赖安装失败
        echo 请检查网络连接或手动运行: cd frontend && npm install
    ) else (
        echo ✅ 前端依赖安装完成！
        echo.
        echo 🏗️  构建前端...
        npm run build
        if %errorlevel% neq 0 (
            echo ❌ 前端构建失败
            echo 请手动运行: cd frontend && npm run build
        ) else (
            echo ✅ 前端构建完成！
        )
    )
    cd ..
)

echo.
echo =====================================
echo 🎉 安装完成！
echo =====================================
echo.
echo 📋 下一步操作:
echo 1. 配置GEE认证: python setup_gee_auth.py
echo 2. 启动系统: python start_system.py
echo 3. 或使用批处理: start_simple.bat
echo.
echo 📱 访问地址:
echo   前端界面: http://localhost:3000
echo   后端API: http://localhost:8000
echo   API文档: http://localhost:8000/docs
echo.
echo ⚠️  重要提醒:
echo   - 需要Google Earth Engine账号
echo   - 需要稳定的网络连接
echo   - 建议使用Python 3.8+
echo =====================================
pause
