#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查GEE图像质量
"""

import os
import asyncio
import base64
import requests
from PIL import Image
import io

# 设置代理
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7897'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7897'

async def check_image_quality():
    """检查GEE图像质量"""
    print("🔍 检查GEE图像质量")
    print("=" * 50)
    
    try:
        from backend.services.satellite_service import SatelliteService
        
        satellite_service = SatelliteService()
        
        # 测试多个位置
        test_locations = [
            {"lat": 30.2741, "lon": 120.1551, "name": "杭州"},
            {"lat": 39.9042, "lon": 116.4074, "name": "北京"},
            {"lat": 31.2304, "lon": 121.4737, "name": "上海"}
        ]
        
        for location in test_locations:
            print(f"\n🌍 检查位置: {location['name']}")
            
            try:
                # 获取图像
                result = await satellite_service.get_satellite_image(
                    location['lat'], 
                    location['lon'], 
                    10, 
                    1000
                )
                
                if result and result.get('url'):
                    image_url = result['url']
                    print(f"   ✅ 图像获取成功")
                    print(f"   📊 URL长度: {len(image_url)}")
                    
                    # 检查图像质量
                    if image_url.startswith('data:image'):
                        # Base64图像
                        try:
                            # 解码图像
                            if ',' in image_url:
                                image_data = image_url.split(',')[1]
                            else:
                                image_data = image_url
                            
                            image_bytes = base64.b64decode(image_data)
                            image = Image.open(io.BytesIO(image_bytes))
                            
                            print(f"   📐 图像尺寸: {image.size}")
                            print(f"   🎨 图像模式: {image.mode}")
                            
                            # 检查图像是否太暗
                            if image.mode == 'RGB':
                                # 计算平均亮度
                                pixels = list(image.getdata())
                                avg_brightness = sum(sum(pixel) for pixel in pixels) / (len(pixels) * 3)
                                print(f"   💡 平均亮度: {avg_brightness:.1f}/255")
                                
                                if avg_brightness < 50:
                                    print(f"   ⚠️  图像太暗，可能是夜间图像")
                                elif avg_brightness > 200:
                                    print(f"   ⚠️  图像过亮，可能曝光过度")
                                else:
                                    print(f"   ✅ 图像亮度正常")
                            
                            # 检查图像是否太小
                            if image.size[0] < 100 or image.size[1] < 100:
                                print(f"   ⚠️  图像尺寸太小，可能影响AI分析")
                            else:
                                print(f"   ✅ 图像尺寸合适")
                                
                        except Exception as e:
                            print(f"   ❌ 图像解析失败: {e}")
                    
                    elif image_url.startswith('http'):
                        # HTTP图像
                        print(f"   🌐 HTTP图像URL: {image_url[:100]}...")
                        
                        try:
                            response = requests.get(image_url, timeout=10)
                            if response.status_code == 200:
                                print(f"   ✅ 图像下载成功")
                                print(f"   📊 图像大小: {len(response.content)} bytes")
                                
                                # 尝试解析图像
                                image = Image.open(io.BytesIO(response.content))
                                print(f"   📐 图像尺寸: {image.size}")
                                print(f"   🎨 图像模式: {image.mode}")
                            else:
                                print(f"   ❌ 图像下载失败: {response.status_code}")
                        except Exception as e:
                            print(f"   ❌ 图像处理失败: {e}")
                    
                    else:
                        print(f"   ❌ 未知图像格式")
                
                else:
                    print(f"   ❌ 图像获取失败")
                    
            except Exception as e:
                print(f"   ❌ 检查失败: {e}")
        
        print(f"\n💡 建议:")
        print(f"   1. 如果图像太暗，尝试不同时间的数据")
        print(f"   2. 如果图像太小，增加缩放级别")
        print(f"   3. 如果图像质量差，尝试不同的数据源")
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")

if __name__ == "__main__":
    asyncio.run(check_image_quality())
