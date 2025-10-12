#!/usr/bin/env python3
"""
安装项目依赖包
"""

import subprocess
import sys
import os

def install_package(package):
    """安装单个包"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {package} 安装失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 数据中心智能选址系统 - 依赖安装")
    print("=" * 60)
    print()
    
    # 依赖包列表
    packages = [
        # 核心依赖
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0", 
        "pydantic==2.5.0",
        "python-multipart==0.0.6",
        
        # 数据处理
        "numpy==1.24.3",
        "pandas==2.0.3",
        "scipy==1.11.4",
        
        # 机器学习
        "scikit-learn==1.3.2",
        "opencv-python==4.8.1.78",
        
        # 深度学习
        "torch==2.0.1",
        "torchvision==0.15.2",
        
        # 地理空间分析
        "earthengine-api==0.1.375",
        "geopandas==0.14.0",
        "shapely==2.0.2",
        
        # 图像处理
        "Pillow==10.1.0",
        "matplotlib==3.7.2",
        "seaborn==0.12.2",
        
        # HTTP请求
        "requests==2.31.0",
        "httpx==0.25.2",
        "aiohttp==3.9.1",
        
        # AI分析
        "openai==1.3.0",
        
        # 工具库
        "python-dotenv==1.0.0",
        "typing-extensions==4.8.0"
    ]
    
    print(f"📦 准备安装 {len(packages)} 个依赖包...")
    print()
    
    success_count = 0
    failed_packages = []
    
    for i, package in enumerate(packages, 1):
        print(f"[{i}/{len(packages)}] 正在安装 {package}...")
        if install_package(package):
            success_count += 1
        else:
            failed_packages.append(package)
        print()
    
    # 输出结果
    print("=" * 60)
    print("📊 安装结果")
    print("=" * 60)
    print(f"✅ 成功安装: {success_count}/{len(packages)} 个包")
    
    if failed_packages:
        print(f"❌ 安装失败: {len(failed_packages)} 个包")
        print("失败的包:")
        for package in failed_packages:
            print(f"  - {package}")
    else:
        print("🎉 所有依赖包安装成功！")
    
    print()
    print("🚀 现在可以启动系统了：")
    print("1. 双击 start.bat")
    print("2. 或运行 python start_system.py")
    print()

if __name__ == "__main__":
    main()


