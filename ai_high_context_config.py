#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高上下文AI配置
"""

# 支持更大上下文的API配置
HIGH_CONTEXT_CONFIG = {
    # 模型配置
    "model": "gpt-4o-2024-08-06",  # 支持更大上下文
    "max_tokens": 8000,  # 增加输出限制
    "temperature": 0.3,
    "timeout": 180,  # 3分钟超时
    
    # 图像配置
    "image_detail": "high",  # 高质量图像分析
    "max_image_size": 2048,  # 最大图像尺寸
    
    # 上下文管理
    "max_context_tokens": 120000,  # 最大上下文token数
    "context_buffer": 8000,  # 上下文缓冲
    
    # API提供商配置
    "providers": {
        "primary": {
            "base_url": "https://api.gptplus5.com/v1",
            "api_key": "sk-abaWwmXxZ2Mtw9GwLHKNI81Mxpsj9RVj5IapLh8mzoP4LfAR"
        },
        "backup": {
            "base_url": "https://api.openai.com/v1", 
            "api_key": "your-openai-key-here"
        }
    }
}

def get_ai_config():
    """获取AI配置"""
    return HIGH_CONTEXT_CONFIG

def check_context_length(messages: list) -> dict:
    """检查上下文长度"""
    try:
        total_chars = sum(len(str(msg)) for msg in messages)
        estimated_tokens = total_chars // 4
        
        return {
            "estimated_tokens": estimated_tokens,
            "within_limit": estimated_tokens < HIGH_CONTEXT_CONFIG["max_context_tokens"],
            "usage_percentage": (estimated_tokens / HIGH_CONTEXT_CONFIG["max_context_tokens"]) * 100
        }
    except Exception as e:
        return {
            "error": str(e),
            "within_limit": True
        }
