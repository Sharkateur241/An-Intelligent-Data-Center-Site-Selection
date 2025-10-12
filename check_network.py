#!/usr/bin/env python3
"""
检查Python网络环境和代理设置
"""

import os
import requests
import urllib3
import ssl
from urllib.parse import urlparse

def check_network_environment():
    """检查网络环境"""
    print("🔍 检查Python网络环境...")
    print("=" * 50)
    
    # 1. 检查环境变量
    print("📋 环境变量:")
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']
    for var in proxy_vars:
        value = os.environ.get(var)
        if value:
            print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: 未设置")
    
    # 2. 检查SSL设置
    print("\n🔒 SSL设置:")
    print(f"  SSL版本: {ssl.OPENSSL_VERSION}")
    print(f"  Python SSL验证: {os.environ.get('PYTHONHTTPSVERIFY', '默认')}")
    
    # 3. 测试网络连接
    print("\n🌐 网络连接测试:")
    test_urls = [
        ("Google", "https://www.google.com"),
        ("Google OAuth", "https://oauth2.googleapis.com"),
        ("GEE API", "https://earthengine.googleapis.com"),
        ("百度", "https://www.baidu.com"),
        ("GitHub", "https://github.com")
    ]
    
    session = requests.Session()
    session.verify = False  # 临时禁用SSL验证
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    for name, url in test_urls:
        try:
            response = session.get(url, timeout=10)
            print(f"  ✅ {name}: {response.status_code} (响应时间: {response.elapsed.total_seconds():.2f}s)")
        except requests.exceptions.ProxyError as e:
            print(f"  ❌ {name}: 代理错误 - {e}")
        except requests.exceptions.SSLError as e:
            print(f"  ❌ {name}: SSL错误 - {e}")
        except requests.exceptions.ConnectionError as e:
            print(f"  ❌ {name}: 连接错误 - {e}")
        except requests.exceptions.Timeout as e:
            print(f"  ❌ {name}: 超时 - {e}")
        except Exception as e:
            print(f"  ❌ {name}: 其他错误 - {e}")
    
    # 4. 检查requests库的代理设置
    print("\n🔧 requests库配置:")
    print(f"  默认代理: {session.proxies}")
    print(f"  SSL验证: {session.verify}")
    
    # 5. 检查系统代理
    print("\n💻 系统代理检查:")
    try:
        import winreg
        # 检查Windows代理设置
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Internet Settings") as key:
            proxy_enable = winreg.QueryValueEx(key, "ProxyEnable")[0]
            if proxy_enable:
                proxy_server = winreg.QueryValueEx(key, "ProxyServer")[0]
                print(f"  ✅ Windows代理已启用: {proxy_server}")
            else:
                print(f"  ❌ Windows代理未启用")
    except Exception as e:
        print(f"  ⚠️  无法检查Windows代理设置: {e}")
    
    # 6. 检查是否有翻墙软件
    print("\n🚀 翻墙软件检查:")
    common_vpn_ports = [1080, 1087, 7890, 7891, 8080, 8118]
    for port in common_vpn_ports:
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            if result == 0:
                print(f"  ✅ 发现本地代理端口 {port} 正在监听")
            sock.close()
        except:
            pass
    
    print("\n" + "=" * 50)
    print("💡 建议:")
    print("1. 如果看到代理设置，说明有翻墙软件")
    print("2. 如果Google相关网站连接失败，可能需要配置代理")
    print("3. 如果所有网站都连接失败，可能是网络问题")

if __name__ == "__main__":
    check_network_environment()
