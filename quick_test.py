#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试 - 跳过GEE，直接测试AI功能
"""

import os
import requests
import time

# 设置代理
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7897'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7897'

def test_simple_analysis():
    """测试简单分析（不依赖GEE）"""
    print("🚀 快速测试 - 跳过GEE数据获取")
    print("=" * 50)
    
    # 测试数据（使用小图片）
    test_data = {
        "latitude": 30.2741,
        "longitude": 120.1551,
        "city_name": "杭州",
        "radius": 1000,
        "image_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    }
    
    print("📡 发送分析请求...")
    start_time = time.time()
    
    try:
        response = requests.post(
            'http://localhost:8000/analyze/location',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30  # 30秒超时
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        print(f"⏱️  响应时间: {response_time:.2f}秒")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 分析成功！")
            print(f"   返回字段: {list(result.keys())}")
            
            # 检查AI字段
            ai_fields = ['ai_multimodal_analysis', 'ai_energy_analysis']
            for field in ai_fields:
                if field in result:
                    print(f"   ✅ {field}: 包含")
                else:
                    print(f"   ❌ {field}: 缺失")
            
            return True
        else:
            print(f"❌ 分析失败: {response.status_code}")
            print(f"   错误: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时 - 可能是网络问题")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败 - 后端可能未运行")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def test_network_speed():
    """测试网络速度"""
    print("\n🌐 测试网络速度...")
    
    test_urls = [
        ("百度", "https://www.baidu.com"),
        ("Google", "https://www.google.com"),
        ("GEE API", "https://earthengine.googleapis.com")
    ]
    
    for name, url in test_urls:
        try:
            start = time.time()
            response = requests.get(url, timeout=10)
            end = time.time()
            
            speed = end - start
            status = "✅" if response.status_code == 200 else "❌"
            print(f"   {status} {name}: {speed:.2f}秒 ({response.status_code})")
            
        except Exception as e:
            print(f"   ❌ {name}: 失败 - {e}")

def main():
    """主函数"""
    print("🔧 快速诊断工具")
    print("=" * 50)
    
    # 1. 测试网络速度
    test_network_speed()
    
    # 2. 测试简单分析
    success = test_simple_analysis()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 系统正常！网络慢可能是GEE数据获取导致的")
        print("\n💡 建议:")
        print("  1. 使用国内位置测试（减少GEE数据量）")
        print("  2. 检查代理服务器状态")
        print("  3. 尝试在非高峰时段使用")
    else:
        print("❌ 系统有问题，需要进一步诊断")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
