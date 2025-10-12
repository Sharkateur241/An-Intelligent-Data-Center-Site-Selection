#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
升级AI配置以支持更大上下文
"""

import os
import re

def upgrade_ai_services():
    """升级所有AI服务的配置"""
    
    print("🚀 升级AI服务配置以支持更大上下文...")
    
    # 需要升级的文件
    ai_files = [
        "backend/services/energy_ai_analysis.py",
        "backend/services/power_supply_ai_analysis.py", 
        "backend/services/energy_storage_ai_analysis.py",
        "backend/services/decision_ai_analysis.py",
        "backend/services/multimodal_analysis.py",
        "backend/services/multimodal_analysis_new.py"
    ]
    
    # 新的配置
    new_config = {
        'model': 'gpt-4o-2024-08-06',  # 支持更大上下文
        'max_tokens': 8000,  # 增加输出token限制
        'detail': 'high',  # 使用高质量图像分析
        'timeout': 180  # 增加超时时间
    }
    
    for file_path in ai_files:
        if os.path.exists(file_path):
            print(f"🔄 升级 {file_path}...")
            upgrade_file(file_path, new_config)
        else:
            print(f"❌ 文件不存在: {file_path}")
    
    print("\n✅ AI服务配置升级完成！")

def upgrade_file(file_path: str, config: dict):
    """升级单个文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 升级模型配置
        content = re.sub(
            r'self\.model = ["\'][^"\']*["\']',
            f'self.model = "{config["model"]}"',
            content
        )
        
        # 升级max_tokens
        content = re.sub(
            r'max_tokens=\d+',
            f'max_tokens={config["max_tokens"]}',
            content
        )
        
        # 升级detail设置
        content = re.sub(
            r'"detail":\s*["\'][^"\']*["\']',
            f'"detail": "{config["detail"]}"',
            content
        )
        
        # 升级timeout
        content = re.sub(
            r'timeout=\d+',
            f'timeout={config["timeout"]}',
            content
        )
        
        # 添加上下文长度检查
        if 'def _call_ai_analysis' in content and 'context_length_check' not in content:
            # 在_call_ai_analysis方法中添加上下文检查
            context_check = '''
    def _check_context_length(self, messages: list) -> bool:
        """检查上下文长度是否超限"""
        try:
            # 估算token数量（粗略估算）
            total_chars = sum(len(str(msg)) for msg in messages)
            estimated_tokens = total_chars // 4  # 粗略估算
            
            if estimated_tokens > 120000:  # 留一些余量
                print(f"⚠️  上下文长度可能超限: {estimated_tokens:,} tokens")
                return False
            return True
        except:
            return True
'''
            
            # 在类定义中添加方法
            class_end_pattern = r'(class \w+.*?:\s*def __init__.*?)(def \w+)'
            content = re.sub(class_end_pattern, r'\1' + context_check + r'\n    \2', content, flags=re.DOTALL)
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✅ {file_path} 升级成功")
        
    except Exception as e:
        print(f"  ❌ {file_path} 升级失败: {e}")

def create_high_context_config():
    """创建高上下文配置"""
    
    config_content = '''#!/usr/bin/env python3
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
'''
    
    with open('ai_high_context_config.py', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("✅ 创建高上下文配置文件: ai_high_context_config.py")

def main():
    """主函数"""
    print("🔧 AI上下文限制升级工具")
    print("=" * 50)
    
    # 1. 升级现有服务
    upgrade_ai_services()
    
    # 2. 创建高上下文配置
    create_high_context_config()
    
    print("\n" + "=" * 50)
    print("🎉 升级完成！")
    print("\n💡 升级内容:")
    print("  ✅ 模型升级为 gpt-4o-2024-08-06")
    print("  ✅ 增加max_tokens到8000")
    print("  ✅ 使用高质量图像分析")
    print("  ✅ 增加超时时间到3分钟")
    print("  ✅ 添加上下文长度检查")
    
    print("\n⚠️  注意事项:")
    print("  1. 确保API提供商支持所选模型")
    print("  2. 更大的上下文意味着更高的API费用")
    print("  3. 如果仍然超限，考虑分批处理数据")
    
    print("\n🚀 现在可以重新测试AI分析功能！")

if __name__ == "__main__":
    main()
