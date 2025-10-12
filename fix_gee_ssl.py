#!/usr/bin/env python3
"""
修复GEE SSL连接问题的脚本
"""

import os
import ssl
import urllib3
import requests
from google.auth.transport.requests import Request
import ee

def fix_ssl_and_proxy():
    """修复SSL和代理设置"""
    
    print("🔧 正在修复GEE SSL连接问题...")
    
    # 1. 禁用SSL警告
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # 2. 设置环境变量以处理SSL问题
    os.environ['PYTHONHTTPSVERIFY'] = '0'
    os.environ['CURL_CA_BUNDLE'] = ''
    os.environ['REQUESTS_CA_BUNDLE'] = ''
    
    # 3. 创建自定义SSL上下文
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    # 4. 设置代理（如果需要）
    proxy_config = {
        'http': None,
        'https': None
    }
    
    # 检查是否有代理环境变量
    http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
    https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    
    if http_proxy:
        proxy_config['http'] = http_proxy
        print(f"🌐 使用HTTP代理: {http_proxy}")
    
    if https_proxy:
        proxy_config['https'] = https_proxy
        print(f"🌐 使用HTTPS代理: {https_proxy}")
    
    # 5. 创建自定义会话
    session = requests.Session()
    session.proxies.update(proxy_config)
    session.verify = False
    
    # 6. 尝试初始化GEE
    try:
        print("🚀 尝试初始化Google Earth Engine...")
        
        # 设置认证
        try:
            # 尝试使用服务账户密钥文件
            service_account_path = os.path.join(os.getcwd(), 'gee-service-account.json')
            if os.path.exists(service_account_path):
                print(f"📁 找到服务账户文件: {service_account_path}")
                credentials = ee.ServiceAccountCredentials(None, service_account_path)
                ee.Initialize(credentials, project='data-center-location-analysis')
            else:
                # 使用默认认证
                ee.Initialize(project='data-center-location-analysis')
            
            print("✅ Google Earth Engine 初始化成功！")
            return True
            
        except Exception as auth_error:
            print(f"❌ 认证失败: {auth_error}")
            print("💡 请确保已正确设置GEE认证")
            return False
            
    except Exception as e:
        print(f"❌ GEE初始化失败: {e}")
        print("\n🔍 可能的解决方案:")
        print("1. 检查网络连接")
        print("2. 检查代理设置")
        print("3. 重新运行GEE认证: python setup_gee_auth.py")
        print("4. 检查防火墙设置")
        return False

def test_network_connectivity():
    """测试网络连接"""
    print("\n🌐 测试网络连接...")
    
    test_urls = [
        "https://www.google.com",
        "https://oauth2.googleapis.com",
        "https://earthengine.googleapis.com"
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=10, verify=False)
            print(f"✅ {url}: {response.status_code}")
        except Exception as e:
            print(f"❌ {url}: {e}")

if __name__ == "__main__":
    print("🔧 GEE SSL连接修复工具")
    print("=" * 50)
    
    # 测试网络连接
    test_network_connectivity()
    
    # 修复SSL问题
    success = fix_ssl_and_proxy()
    
    if success:
        print("\n🎉 修复完成！现在可以尝试启动后端服务。")
    else:
        print("\n⚠️  修复失败，请检查网络设置或联系管理员。")
