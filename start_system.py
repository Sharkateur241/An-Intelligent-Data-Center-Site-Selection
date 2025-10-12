#!/usr/bin/env python3
"""
数据中心智能选址与能源优化系统启动脚本
"""
import subprocess
import time
import os
import sys
from config import config

def start_backend():
    """启动后端服务"""
    print("🚀 启动后端服务...")
    backend_dir = os.path.join(os.getcwd(), "backend")
    try:
        # 启动后端服务 - 使用Windows的start命令打开新窗口
        if os.name == 'nt':  # Windows
            cmd = f'start "Backend Server" cmd /k "cd /d {backend_dir} && python main.py"'
            process = subprocess.Popen(cmd, shell=True)
        else:  # Linux/Mac
            process = subprocess.Popen(
                [sys.executable, "main.py"],
                cwd=backend_dir
            )
        print("✅ 后端服务已启动 (端口8000)")
        return process
    except Exception as e:
        print(f"❌ 后端服务启动失败: {e}")
        return None

def start_frontend():
    """启动前端服务"""
    print("🚀 启动前端服务...")
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    try:
        # 启动前端服务 - 使用Windows的start命令打开新窗口
        if os.name == 'nt':  # Windows
            cmd = f'start "Frontend Server" cmd /k "cd /d {frontend_dir} && python start_server.py"'
            process = subprocess.Popen(cmd, shell=True)
        else:  # Linux/Mac
            process = subprocess.Popen(
                [sys.executable, "start_server.py"],
                cwd=frontend_dir
            )
        print("✅ 前端服务已启动 (端口3000)")
        return process
    except Exception as e:
        print(f"❌ 前端服务启动失败: {e}")
        return None

def check_gee_auth():
    """检查GEE认证状态"""
    try:
        import ee
        ee.Initialize(project='data-center-location-analysis')
        print("✅ GEE认证正常")
        return True
    except Exception as e:
        print(f"❌ GEE认证失败: {e}")
        print("请先运行: python setup_gee_auth.py")
        return False

def main():
    """主函数"""
    # 设置代理和API密钥
    config.setup_proxy()
    config.setup_openai_key()
    
    print("=" * 60)
    print("🚀 数据中心智能选址与能源优化系统")
    print("=" * 60)
    
    # 检查GEE认证
    if not check_gee_auth():
        print("\n❌ 系统无法启动，请先完成GEE认证！")
        print("运行命令: python setup_gee_auth.py")
        input("\n按回车键退出...")
        return
    
    print("\n📋 系统组件:")
    print("  • 后端API服务 (FastAPI + GEE)")
    print("  • 前端界面 (React)")
    print("  • GEE卫星图像分析")
    print("  • 能源资源评估")
    print("  • 智能选址决策")
    
    # 启动后端
    backend_process = start_backend()
    if not backend_process:
        print("❌ 无法启动后端服务，请检查依赖是否安装")
        return
    
    # 等待后端启动
    print("⏳ 等待后端服务启动...")
    time.sleep(3)
    
    # 启动前端
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ 无法启动前端服务")
        return
    
    print("\n" + "=" * 60)
    print("🎉 系统启动完成！")
    print("=" * 60)
    print("📱 前端界面: http://localhost:3000")
    print("🔧 后端API: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    print("\n💡 提示: 保持这两个窗口打开，关闭窗口会停止服务")
    print("⚠️  注意: 系统必须使用GEE数据")
    print("=" * 60)
    
    # 等待用户输入
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
