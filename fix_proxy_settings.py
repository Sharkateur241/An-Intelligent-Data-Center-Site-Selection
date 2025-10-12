#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复代理设置 - 让Python程序使用系统代理
"""

import os
import subprocess
import sys

def set_proxy_environment():
    """设置代理环境变量"""
    print("🔧 设置代理环境变量...")
    
    # 设置代理环境变量
    proxy_url = "http://127.0.0.1:7897"
    
    os.environ['HTTP_PROXY'] = proxy_url
    os.environ['HTTPS_PROXY'] = proxy_url
    os.environ['http_proxy'] = proxy_url
    os.environ['https_proxy'] = proxy_url
    os.environ['ALL_PROXY'] = proxy_url
    os.environ['all_proxy'] = proxy_url
    
    print(f"✅ 已设置代理: {proxy_url}")
    
    # 验证设置
    print("\n📋 当前环境变量:")
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    for var in proxy_vars:
        value = os.environ.get(var)
        print(f"  {var}: {value}")

def test_gee_connection():
    """测试GEE连接"""
    print("\n🌐 测试GEE连接...")
    
    try:
        import ee
        import requests
        
        # 设置requests使用代理
        session = requests.Session()
        session.proxies = {
            'http': 'http://127.0.0.1:7897',
            'https': 'http://127.0.0.1:7897'
        }
        
        # 测试GEE API连接
        test_url = "https://earthengine.googleapis.com/v1/projects/data-center-location-analysis"
        response = session.get(test_url, timeout=10)
        print(f"✅ GEE API连接成功: {response.status_code}")
        
        # 尝试初始化GEE
        print("🚀 尝试初始化GEE...")
        ee.Initialize(project='data-center-location-analysis')
        print("✅ GEE初始化成功！")
        
        return True
        
    except Exception as e:
        print(f"❌ GEE连接失败: {e}")
        return False

def create_proxy_startup_script():
    """创建带代理的启动脚本"""
    print("\n📝 创建代理启动脚本...")
    
    script_content = '''@echo off
chcp 65001 >nul
echo =====================================
echo 数据中心智能选址与能源优化系统 (代理版)
echo =====================================
echo.

echo 设置代理环境变量...
set HTTP_PROXY=http://127.0.0.1:7897
set HTTPS_PROXY=http://127.0.0.1:7897
set http_proxy=http://127.0.0.1:7897
set https_proxy=http://127.0.0.1:7897
set ALL_PROXY=http://127.0.0.1:7897
set all_proxy=http://127.0.0.1:7897

echo 代理设置完成: http://127.0.0.1:7897
echo.

echo 启动基础AI分析模式...
copy "frontend\\src\\App_simple.tsx" "frontend\\src\\App.tsx" >nul
cd frontend
call npm run build
cd ..
start "Backend Server" cmd /k "python start_system.py"

echo.
echo =====================================
echo 系统启动完成！
echo =====================================
echo.
echo 前端界面: http://localhost:3000
echo 后端API: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo.
echo 后端服务器窗口应该会自动打开
echo 如果没有打开，请手动运行: python start_system.py
echo.
echo 按任意键关闭此窗口...
pause >nul
'''
    
    with open('start_with_proxy.bat', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✅ 已创建 start_with_proxy.bat")

def main():
    """主函数"""
    print("🔧 代理设置修复工具")
    print("=" * 50)
    
    # 1. 设置环境变量
    set_proxy_environment()
    
    # 2. 测试GEE连接
    gee_success = test_gee_connection()
    
    # 3. 创建代理启动脚本
    create_proxy_startup_script()
    
    print("\n" + "=" * 50)
    if gee_success:
        print("🎉 修复成功！GEE现在可以正常工作了！")
        print("\n💡 使用方法:")
        print("1. 直接运行: python start_system.py")
        print("2. 或使用代理启动脚本: start_with_proxy.bat")
    else:
        print("⚠️  部分修复完成，但GEE连接仍有问题")
        print("\n💡 建议:")
        print("1. 检查代理软件是否正常运行")
        print("2. 尝试重启代理软件")
        print("3. 使用 start_with_proxy.bat 启动系统")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
