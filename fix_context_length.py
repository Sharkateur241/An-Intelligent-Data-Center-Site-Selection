#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复AI分析上下文长度超限问题
"""

import os
from PIL import Image
import base64
import io

def compress_image_for_ai(image_data: str, max_size: int = 512) -> str:
    """
    压缩图像以减少AI分析的token数量
    
    Args:
        image_data: base64编码的图像数据
        max_size: 最大尺寸（像素）
    
    Returns:
        压缩后的base64图像数据
    """
    try:
        # 解码base64图像
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # 获取原始尺寸
        original_width, original_height = image.size
        print(f"原始图像尺寸: {original_width}x{original_height}")
        
        # 计算压缩比例
        if original_width > max_size or original_height > max_size:
            ratio = min(max_size / original_width, max_size / original_height)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)
            
            # 压缩图像
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            print(f"压缩后尺寸: {new_width}x{new_height}")
        
        # 转换为RGB模式（如果需要）
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 重新编码为base64
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=85, optimize=True)
        compressed_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        print(f"压缩前大小: {len(image_data)} bytes")
        print(f"压缩后大小: {len(compressed_data)} bytes")
        print(f"压缩率: {len(compressed_data) / len(image_data) * 100:.1f}%")
        
        return f"data:image/jpeg;base64,{compressed_data}"
        
    except Exception as e:
        print(f"图像压缩失败: {e}")
        return image_data

def estimate_token_count(text: str) -> int:
    """
    估算文本的token数量（粗略估算）
    1 token ≈ 4个字符（中文）或 0.75个单词（英文）
    """
    # 简单估算：中文字符数 * 1.5 + 英文字符数 * 0.25
    chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
    english_chars = len([c for c in text if c.isalpha() and ord(c) < 128])
    
    estimated_tokens = chinese_chars * 1.5 + english_chars * 0.25
    return int(estimated_tokens)

def check_ai_request_size(data: dict) -> dict:
    """
    检查AI请求的大小并优化
    """
    print("🔍 检查AI请求大小...")
    
    # 检查图像数据
    if 'image_url' in data and data['image_url']:
        image_data = data['image_url']
        if image_data.startswith('data:image'):
            # 压缩图像
            print("🔄 压缩图像数据...")
            compressed_image = compress_image_for_ai(image_data)
            data['image_url'] = compressed_image
    
    # 检查文本数据大小
    text_content = str(data)
    token_count = estimate_token_count(text_content)
    print(f"📊 估算token数量: {token_count:,}")
    
    if token_count > 100000:  # 如果超过10万token
        print("⚠️  请求过大，建议优化数据")
        
        # 移除不必要的大字段
        if 'raw_image_data' in data:
            del data['raw_image_data']
            print("   - 移除了raw_image_data字段")
        
        if 'detailed_metadata' in data:
            del data['detailed_metadata']
            print("   - 移除了detailed_metadata字段")
    
    return data

def main():
    """主函数"""
    print("🔧 AI上下文长度优化工具")
    print("=" * 50)
    
    # 测试图像压缩
    test_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    print("🖼️  测试图像压缩...")
    compressed = compress_image_for_ai(test_image)
    print(f"✅ 图像压缩完成")
    
    # 测试数据优化
    test_data = {
        "latitude": 30.2741,
        "longitude": 120.1551,
        "city_name": "杭州",
        "image_url": test_image,
        "raw_image_data": "x" * 1000000,  # 模拟大字段
        "detailed_metadata": {"key": "value" * 1000}
    }
    
    print("\n📊 测试数据优化...")
    optimized_data = check_ai_request_size(test_data)
    print(f"✅ 数据优化完成")
    
    print("\n💡 建议:")
    print("1. 在AI分析前压缩图像数据")
    print("2. 移除不必要的大字段")
    print("3. 分批处理大量数据")
    print("4. 使用更高效的图像格式")

if __name__ == "__main__":
    main()
