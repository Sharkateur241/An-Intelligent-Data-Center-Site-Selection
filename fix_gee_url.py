#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复GEE URL解析问题
"""

def fix_gee_url(original_url):
    """修复GEE URL"""
    print(f"原始URL: {original_url}")
    
    if 'getPixels' in original_url and 'thumbnails' in original_url:
        # 解析URL
        parts = original_url.split('/')
        print(f"URL部分: {parts}")
        
        if len(parts) >= 8:
            project_id = parts[5]  # 正确的项目ID位置
            image_id = parts[7].split(':')[0]  # 正确的图像ID位置
            print(f"项目ID: {project_id}")
            print(f"图像ID: {image_id}")
            
            # 构造正确的URL
            fixed_url = f"https://earthengine.googleapis.com/v1/projects/{project_id}/thumbnails/{image_id}:getPixels"
            print(f"修复URL: {fixed_url}")
            return fixed_url
    
    return original_url

# 测试URL修复
test_urls = [
    "https://earthengine.googleapis.com/v1/projects/data-center-location-analysis/thumbnails/e7d3931df416ef00c3ff48b7bda0e03e-63dfa5c7c9ab55359eb1e5df3593442b:getPixels",
    "https://earthengine.googleapis.com/v1/projects/data-center-location-analysis/thumbnails/b6d482875c441e1537e575b0ea6561fb-48f6b40ba742b18b100cc373ea09b484:getPixels"
]

for url in test_urls:
    print("\n" + "="*50)
    fixed = fix_gee_url(url)
    print(f"最终URL: {fixed}")
