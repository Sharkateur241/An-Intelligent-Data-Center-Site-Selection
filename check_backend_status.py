#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 检查后端状态和代码版本
"""

import requests
import json

def check_backend_status():
    """检查后端状态"""
    try:
        # 检查健康状态
        response = requests.get('http://localhost:8000/health')
        if response.status_code == 200:
            print("✅ 后端服务器运行正常")
            print(f"健康状态: {response.json()}")
        else:
            print(f"❌ 后端服务器异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到后端服务器: {e}")
        return False
    
    # 测试分析接口
    try:
        test_data = {
            "latitude": 39.9042,
            "longitude": 116.4074,
            "city_name": "北京",
            "radius": 1000
        }
        
        print("\n🔄 测试分析接口...")
        response = requests.post(
            'http://localhost:8000/analyze/location',
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=180  # 3分钟超时
        )
        
        if response.status_code == 200:
            print("✅ 分析接口正常")
            result = response.json()
            print(f"返回字段: {list(result.keys())}")
        else:
            print(f"❌ 分析接口异常: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 分析接口测试失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("🔍 检查后端状态")
    print("=" * 50)
    
    success = check_backend_status()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 后端状态正常！")
    else:
        print("❌ 后端状态异常！")
    print("=" * 50)
