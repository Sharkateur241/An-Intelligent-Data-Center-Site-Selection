#!/usr/bin/env python3
"""
Python启动脚本 - 避免PowerShell问题
"""
import os
import subprocess
import sys
import time

def main():
    print("🚀 启动数据中心智能选址系统...")
    
    # 设置代理环境变量
    os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7897'
    os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7897'
    
    print("📋 设置代理环境变量...")
    print(f"HTTP_PROXY: {os.environ.get('HTTP_PROXY')}")
    print(f"HTTPS_PROXY: {os.environ.get('HTTPS_PROXY')}")
    
    print("\n选择启动模式:")
    print("1. 基础AI分析模式")
    print("2. 高级AI分析模式")
    print("3. 仅后端API")
    
    choice = input("请输入选择 (1-3): ").strip()
    
    if choice == "1":
        print("🔧 启动基础AI分析模式...")
        # 复制前端文件
        try:
            import shutil
            shutil.copy("frontend/src/App_simple.tsx", "frontend/src/App.tsx")
            print("✅ 前端文件配置完成")
        except Exception as e:
            print(f"⚠️ 前端文件配置失败: {e}")
        
        # 构建前端
        print("🔨 构建前端...")
        try:
            subprocess.run(["npm", "run", "build"], cwd="frontend", check=True)
            print("✅ 前端构建完成")
        except Exception as e:
            print(f"⚠️ 前端构建失败: {e}")
        
        # 启动后端
        print("🚀 启动后端服务...")
        subprocess.Popen([sys.executable, "start_system.py"])
        
    elif choice == "2":
        print("🔧 启动高级AI分析模式...")
        # 复制前端文件
        try:
            import shutil
            shutil.copy("frontend/src/App_advanced.tsx", "frontend/src/App.tsx")
            print("✅ 前端文件配置完成")
        except Exception as e:
            print(f"⚠️ 前端文件配置失败: {e}")
        
        # 构建前端
        print("🔨 构建前端...")
        try:
            subprocess.run(["npm", "run", "build"], cwd="frontend", check=True)
            print("✅ 前端构建完成")
        except Exception as e:
            print(f"⚠️ 前端构建失败: {e}")
        
        # 启动后端
        print("🚀 启动后端服务...")
        subprocess.Popen([sys.executable, "start_system.py"])
        
    elif choice == "3":
        print("🔧 启动仅后端API模式...")
        subprocess.Popen([sys.executable, "start_system.py"])
        
    else:
        print("❌ 无效选择，启动默认模式...")
        subprocess.Popen([sys.executable, "start_system.py"])
    
    print("\n" + "="*50)
    print("🎉 系统启动完成！")
    print("前端: http://localhost:3000")
    print("后端: http://localhost:8000")
    print("="*50)
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
