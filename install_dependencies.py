#!/usr/bin/env python3
"""
Install project dependency packages
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a single package"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {package} installation failed: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("🚀 Data Center Intelligent Site Selection System - Dependency Installation")
    print("=" * 60)
    print()
    
    # Dependency package list
    packages = [
        # Core dependencies
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0", 
        "pydantic==2.5.0",
        "python-multipart==0.0.6",
        
        # Data processing
        "numpy==1.24.3",
        "pandas==2.0.3",
        "scipy==1.11.4",
        
        # Machine learning
        "scikit-learn==1.3.2",
        "opencv-python==4.8.1.78",
        
        # Deep learning
        "torch==2.0.1",
        "torchvision==0.15.2",
        
        # Geospatial analysis
        "earthengine-api==0.1.375",
        "geopandas==0.14.0",
        "shapely==2.0.2",
        
        # Image processing
        "Pillow==10.1.0",
        "matplotlib==3.7.2",
        "seaborn==0.12.2",
        
        # HTTP requests
        "requests==2.31.0",
        "httpx==0.25.2",
        "aiohttp==3.9.1",
        
        # AI analysis
        "openai==1.3.0",
        
        # Utility libraries
        "python-dotenv==1.0.0",
        "typing-extensions==4.8.0"
    ]
    
    print(f"📦 Preparing to install {len(packages)} dependency packages...")
    print()
    
    success_count = 0
    failed_packages = []
    
    for i, package in enumerate(packages, 1):
        print(f"[{i}/{len(packages)}] Installing {package}...")
        if install_package(package):
            success_count += 1
        else:
            failed_packages.append(package)
        print()
    
    # Output results
    print("=" * 60)
    print("📊 Installation Results")
    print("=" * 60)
    print(f"✅ Successfully installed: {success_count}/{len(packages)} packages")
    
    if failed_packages:
        print(f"❌ Installation failed: {len(failed_packages)} packages")
        print("Failed packages:")
        for package in failed_packages:
            print(f"  - {package}")
    else:
        print("🎉 All dependency packages installed successfully!")
    
    print()
    print("🚀 You can now start the system:")
    print("1. Double-click start.bat")
    print("2. Or run python start_system.py")
    print()

if __name__ == "__main__":
    main()