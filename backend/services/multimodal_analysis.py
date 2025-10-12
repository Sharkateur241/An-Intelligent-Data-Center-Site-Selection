"""
多模态分析服务 - 使用OpenAI官方库进行卫星图像分析
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from openai import OpenAI
import os

class MultimodalAnalysisService:
    """多模态分析服务类"""
    
    def __init__(self):
        """初始化多模态分析服务"""
        # 设置代理
        os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7897'
        os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7897'
        
        # 直接使用项目中的API密钥
        api_key = os.environ.get('OPENAI_API_KEY', 'sk-abaWwmXxZ2Mtw9GwLHKNI81Mxpsj9RVj5IapLh8mzoP4LfAR')
        
        self.client = OpenAI(
            base_url='https://api.gptplus5.com/v1',
            api_key=api_key
        )
        self.model = "gpt-4o-2024-08-06"
        
        # 数据中心选址分析prompt模板 - 增强版
        self.datacenter_prompt = """
请分析这张卫星图像，从以下维度评估数据中心选址的适宜性，并给出详细的评分：

## 分析维度（每项1-10分）

### 1. 土地利用适宜性
- 地形平坦度
- 土地可用性
- 周边环境

### 2. 环境条件
- 气候条件
- 自然灾害风险
- 生态环境

### 3. 基础设施
- 交通便利性
- 电力供应
- 通信网络

### 4. 技术可行性
- 建设难度
- 维护便利性
- 扩展性

### 5. 经济性
- 土地成本
- 建设成本
- 运营成本

## 输出格式
请以JSON格式输出分析结果：
{
    "overall_score": 总分(1-10),
    "land_use": {
        "score": 分数(1-10),
        "analysis": "详细分析"
    },
    "environment": {
        "score": 分数(1-10),
        "analysis": "详细分析"
    },
    "infrastructure": {
        "score": 分数(1-10),
        "analysis": "详细分析"
    },
    "feasibility": {
        "score": 分数(1-10),
        "analysis": "详细分析"
    },
    "economics": {
        "score": 分数(1-10),
        "analysis": "详细分析"
    },
    "recommendations": "综合建议",
    "risks": "潜在风险",
    "next_steps": "后续步骤"
}
"""

    async def analyze_satellite_image(self, image_url: str, custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        分析卫星图像
        
        Args:
            image_url: 图像URL
            custom_prompt: 自定义提示词
            
        Returns:
            分析结果字典
        """
        try:
            prompt = custom_prompt or self.datacenter_prompt
            
            # 使用OpenAI官方库进行API调用，增加重试机制
            import time
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": image_url,
                                            "detail": "high"  # 使用low减少上下文长度
                                        }
                                    }
                                ]
                            }
                        ],
                        max_tokens=8000,
                        temperature=0.3,
                        timeout=180  # 2分钟超时
                    )
                    break  # 成功则跳出重试循环
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"⚠️ API调用失败，第{attempt + 1}次重试: {e}")
                        time.sleep(2)  # 等待2秒后重试
                    else:
                        raise e  # 最后一次重试失败，抛出异常
            
            analysis_text = response.choices[0].message.content
            
            # 直接返回文本分析结果
            return {
                "success": True,
                "analysis": analysis_text,
                "model": self.model,
                "timestamp": datetime.now().isoformat(),
                "image_url": image_url,
                "api_provider": "GPTPlus5"
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"API请求异常: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    async def analyze_with_gee_data(self, gee_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        结合GEE数据进行综合分析
        
        Args:
            gee_data: GEE数据字典
            
        Returns:
            综合分析结果
        """
        try:
            # 提取图像URL（支持多种字段名）
            image_url = gee_data.get("url") or gee_data.get("image_url", "")
            print(f"🔍 多模态分析 - 图像URL: {image_url[:50] if image_url else 'None'}...")
            
            if not image_url:
                return {
                    "success": False,
                    "error": "GEE数据中缺少图像URL",
                    "timestamp": datetime.now().isoformat()
                }
            
            # 检查图像URL格式
            if not (image_url.startswith("data:image/") or image_url.startswith("https://")):
                return {
                    "success": False,
                    "error": f"图像URL格式不正确: {image_url[:50]}...",
                    "timestamp": datetime.now().isoformat()
                }
            
            # 构建结合GEE数据的分析提示词
            gee_prompt = f"""
请分析这张卫星图像，结合以下GEE数据进行数据中心选址分析：

GEE数据: {json.dumps(gee_data, ensure_ascii=False, indent=2)}

请综合考虑卫星图像和GEE数据，进行以下分析：
1. 土地利用适宜性
2. 环境条件评估
3. 基础设施分析
4. 技术可行性
5. 经济性评估

输出格式：
{{
    "combined_analysis": {{
        "land_use": {{
            "score": 分数(1-10),
            "analysis": "土地利用分析",
            "gee_insights": "GEE数据洞察"
        }},
        "environment": {{
            "score": 分数(1-10),
            "analysis": "环境分析",
            "gee_insights": "GEE数据洞察"
        }},
        "infrastructure": {{
            "score": 分数(1-10),
            "analysis": "基础设施分析",
            "gee_insights": "GEE数据洞察"
        }},
        "feasibility": {{
            "score": 分数(1-10),
            "analysis": "可行性分析",
            "gee_insights": "GEE数据洞察"
        }},
        "economics": {{
            "score": 分数(1-10),
            "analysis": "经济性分析",
            "gee_insights": "GEE数据洞察"
        }}
    }},
    "overall_score": 总体评分,
    "recommendations": "综合建议",
    "risks": "潜在风险",
    "next_steps": "后续步骤"
}}
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": gee_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url,
                                    "detail": "high"  # 恢复high以获得更好的分析效果
                                }
                            }
                        ]
                    }
                ],
                max_tokens=8000,
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content
            
            try:
                analysis_result = json.loads(analysis_text)
                return {
                    "success": True,
                    "analysis": analysis_result,
                    "model": self.model,
                    "timestamp": datetime.now().isoformat(),
                    "gee_data": gee_data,
                    "api_provider": "GPTPlus5"
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "analysis": analysis_text,
                    "model": self.model,
                    "timestamp": datetime.now().isoformat(),
                    "gee_data": gee_data,
                    "api_provider": "GPTPlus5"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"GEE数据分析异常: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    async def test_api_connection(self) -> Dict[str, Any]:
        """
        测试API连接
        
        Returns:
            连接测试结果
        """
        # 尝试不同模型
        models_to_try = [
            "gpt-4o",          # 首选
            "gpt-4o-mini",    # 备选
            "qwen-vl-max"     # 兼容
        ]
        
        for model in models_to_try:
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": "ping"}
                    ],
                    max_tokens=8000
                )
                
                # 如果成功，更新模型
                self.model = model
                
                return {
                    "success": True,
                    "message": f"API连接正常，使用模型: {model}",
                    "model": model,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                print(f"模型 {model} 不可用: {e}")
                continue
        
        return {
            "success": False,
            "error": "所有模型都不可用，请检查配额或联系服务提供商",
            "timestamp": datetime.now().isoformat()
        }