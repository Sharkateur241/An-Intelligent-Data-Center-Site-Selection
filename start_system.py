#!/usr/bin/env python3
"""
Startup script for Data Center Intelligent Site Selection & Energy Optimization
"""
import subprocess
import time
import os
import sys
from config import config

def start_backend():
    """Start backend service"""
    print("🚀 Starting backend service...")
    backend_dir = os.path.join(os.getcwd(), "backend")
    try:
        # Start backend - on Windows open new console window
        if os.name == 'nt':  # Windows
            cmd = f'start "Backend Server" cmd /k "cd /d {backend_dir} && python main.py"'
            process = subprocess.Popen(cmd, shell=True)
        else:  # Linux/Mac
            process = subprocess.Popen(
                [sys.executable, "main.py"],
                cwd=backend_dir
            )
        print("✅ Backend started (port 8000)")
        return process
    except Exception as e:
        print(f"❌ Backend failed to start: {e}")
        return None

def start_frontend():
    """Start frontend service"""
    print("🚀 Starting frontend service...")
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    try:
        # Start frontend - on Windows open new console window
        if os.name == 'nt':  # Windows
            cmd = f'start "Frontend Server" cmd /k "cd /d {frontend_dir} && python start_server.py"'
            process = subprocess.Popen(cmd, shell=True)
        else:  # Linux/Mac
            process = subprocess.Popen(
                [sys.executable, "start_server.py"],
                cwd=frontend_dir
            )
        print("✅ Frontend started (port 3000)")
        return process
    except Exception as e:
        print(f"❌ Frontend failed to start: {e}")
        return None

def check_gee_auth():
    """Check GEE authentication status"""
    try:
        import ee
        ee.Initialize(project='data-center-location-analysis')
        print("✅ GEE authentication OK")
        return True
    except Exception as e:
        print(f"❌ GEE authentication failed: {e}")
        print("Please run: python setup_gee_auth.py")
        return False

def main():
    """Main entry"""
    # Set proxy and API key
    config.setup_proxy()
    config.setup_openai_key()
    
    print("=" * 60)
    print("🚀 Data Center Intelligent Site Selection & Energy Optimization")
    print("=" * 60)
    
    # Check GEE auth
    if not check_gee_auth():
        print("\n❌ System cannot start, please complete GEE authentication first!")
        print("Run: python setup_gee_auth.py")
        input("\nPress Enter to exit...")
        return
    
    print("\n📋 System components:")
    print("  • Backend API (FastAPI + GEE)")
    print("  • Frontend UI (React)")
    print("  • GEE satellite imagery analysis")
    print("  • Energy resource assessment")
    print("  • Intelligent site selection decisioning")
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ Unable to start backend, please check dependencies")
        return
    
    # Wait for backend
    print("⏳ Waiting for backend to start...")
    time.sleep(3)
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ Unable to start frontend")
        return
    
    print("\n" + "=" * 60)
    print("🎉 System is up!")
    print("=" * 60)
    print("📱 Frontend: http://localhost:3000")
    print("🔧 Backend API: http://localhost:8000")
    print("📚 API docs: http://localhost:8000/docs")
    print("\n💡 Tip: keep both windows open; closing stops the services")
    print("⚠️  Note: GEE data is required")
    print("=" * 60)
    
    # Wait for user input
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
