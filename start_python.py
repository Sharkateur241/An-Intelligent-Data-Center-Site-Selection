#!/usr/bin/env python3
"""
Python startup script - avoid PowerShell issues
"""
import os
import subprocess
import sys
import time

def main():
    print("🚀 Starting Data Center Intelligent Site Selection System...")
    
    # Set proxy environment variables
    os.environ['HTTP_PROXY'] = 'http://127.0.0.1:1082'
    os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:1082'
    
    print("📋 Setting proxy environment variables...")
    print(f"HTTP_PROXY: {os.environ.get('HTTP_PROXY')}")
    print(f"HTTPS_PROXY: {os.environ.get('HTTPS_PROXY')}")
    
    print("\nSelect startup mode:")
    print("1. Basic AI analysis mode")
    print("2. Advanced AI analysis mode")
    print("3. Backend API only")
    
    choice = input("Please enter your choice (1-3): ").strip()
    
    if choice == "1":
        print("🔧 Starting Basic AI analysis mode...")
        # Copy frontend files
        try:
            import shutil
            shutil.copy("frontend/src/App_simple.tsx", "frontend/src/App.tsx")
            print("✅ Frontend file configuration complete")
        except Exception as e:
            print(f"⚠️ Frontend file configuration failed: {e}")
        
        # Build frontend
        print("🔨 Building frontend...")
        try:
            subprocess.run(["npm", "run", "build"], cwd="frontend", check=True)
            print("✅ Frontend build complete")
        except Exception as e:
            print(f"⚠️ Frontend build failed: {e}")
        
        # Start backend
        print("🚀 Starting backend service...")
        subprocess.Popen([sys.executable, "start_system.py"])
        
    elif choice == "2":
        print("🔧 Starting Advanced AI analysis mode...")
        # Copy frontend files
        try:
            import shutil
            shutil.copy("frontend/src/App_advanced.tsx", "frontend/src/App.tsx")
            print("✅ Frontend file configuration complete")
        except Exception as e:
            print(f"⚠️ Frontend file configuration failed: {e}")
        
        # Build frontend
        print("🔨 Building frontend...")
        try:
            subprocess.run(["npm", "run", "build"], cwd="frontend", check=True)
            print("✅ Frontend build complete")
        except Exception as e:
            print(f"⚠️ Frontend build failed: {e}")
        
        # Start backend
        print("🚀 Starting backend service...")
        subprocess.Popen([sys.executable, "start_system.py"])
        
    elif choice == "3":
        print("🔧 Starting Backend API only mode...")
        subprocess.Popen([sys.executable, "start_system.py"])
        
    else:
        print("❌ Invalid choice, starting default mode...")
        subprocess.Popen([sys.executable, "start_system.py"])
    
    print("\n" + "="*50)
    print("🎉 System startup complete!")
    print("Frontend: http://localhost:3000")
    print("Backend: http://localhost:8000")
    print("="*50)
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()