"""
多模态分析服务 - 使用OpenAI官方库进行卫星图像分析
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from openai import OpenAI

class MultimodalAnalysisService:
    """多模态分析服务类"""
    
    def __init__(self):
        """初始化多模态分析服务"""
        self.client = OpenAI(
            base_url='https://api.gptplus5.com/v1',
            api_key='sk-abaWwmXxZ2Mtw9GwLHKNI81Mxpsj9RVj5IapLh8mzoP4LfAR'
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
            
            # 使用OpenAI官方库进行API调用
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
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=8000,
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content
            
            # 尝试解析JSON响应
            try:
                analysis_result = json.loads(analysis_text)
                return {
                    "success": True,
                    "analysis": analysis_result,
                    "model": self.model,
                    "timestamp": datetime.now().isoformat(),
                    "image_url": image_url,
                    "api_provider": "GPTPlus5"
                }
            except json.JSONDecodeError:
                # 如果不是JSON格式，返回原始文本
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

    async def batch_analyze_images(self, image_urls: List[str], custom_prompt: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        批量分析多张图像
        
        Args:
            image_urls: 图像URL列表
            custom_prompt: 自定义提示词
            
        Returns:
            分析结果列表
        """
        tasks = []
        for image_url in image_urls:
            task = self.analyze_satellite_image(image_url, custom_prompt)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "success": False,
                    "error": str(result),
                    "image_url": image_urls[i],
                    "timestamp": datetime.now().isoformat()
                })
            else:
                processed_results.append(result)
        
        return processed_results

    async def temporal_analysis(self, image_urls: List[str], time_points: List[str]) -> Dict[str, Any]:
        """
        时间序列分析
        
        Args:
            image_urls: 不同时间点的图像URL列表
            time_points: 对应的时间点列表
            
        Returns:
            时间序列分析结果
        """
        try:
            # 构建时间序列分析提示词
            temporal_prompt = f"""
请分析这些不同时间点的卫星图像，进行数据中心选址的时间序列分析。

时间点: {', '.join(time_points)}

请从以下角度分析：
1. 土地利用变化趋势
2. 环境条件变化
3. 基础设施发展
4. 建设适宜性变化
5. 风险评估变化

请以JSON格式输出分析结果：
{{
    "temporal_analysis": {{
        "trends": "变化趋势分析",
        "recommendations": "基于时间序列的建议",
        "risks": "时间相关风险"
    }},
    "time_point_analysis": [
        {{
            "time_point": "时间点",
            "score": 分数(1-10),
            "analysis": "该时间点分析"
        }}
    ],
    "overall_recommendation": "综合建议"
}}
"""
            
            # 构建多图像消息
            content = [{"type": "text", "text": temporal_prompt}]
            for image_url in image_urls:
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": image_url,
                        "detail": "high"
                    }
                })
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": content
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
                    "time_points": time_points,
                    "api_provider": "GPTPlus5"
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "analysis": analysis_text,
                    "model": self.model,
                    "timestamp": datetime.now().isoformat(),
                    "time_points": time_points,
                    "api_provider": "GPTPlus5"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"时间序列分析异常: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    async def custom_metrics_analysis(self, image_url: str, metrics: List[str], weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        自定义指标分析
        
        Args:
            image_url: 图像URL
            metrics: 自定义指标列表
            weights: 指标权重字典
            
        Returns:
            自定义指标分析结果
        """
        try:
            weights = weights or {}
            
            # 构建自定义指标分析提示词
            custom_prompt = f"""
请分析这张卫星图像，基于以下自定义指标进行评估：

指标列表: {', '.join(metrics)}
权重设置: {weights}

请为每个指标给出1-10分的评分，并计算加权总分。

输出格式：
{{
    "custom_metrics": {{
        "指标名称": {{
            "score": 分数(1-10),
            "weight": 权重,
            "analysis": "详细分析"
        }}
    }},
    "weighted_score": 加权总分,
    "recommendations": "基于自定义指标的建议"
}}
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": custom_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url,
                                    "detail": "high"
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
                    "custom_metrics": metrics,
                    "weights": weights,
                    "api_provider": "GPTPlus5"
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "analysis": analysis_text,
                    "model": self.model,
                    "timestamp": datetime.now().isoformat(),
                    "custom_metrics": metrics,
                    "weights": weights,
                    "api_provider": "GPTPlus5"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"自定义指标分析异常: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    async def multi_dimension_scoring(self, image_url: str, dimensions: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        多维度评分分析
        
        Args:
            image_url: 图像URL
            dimensions: 维度字典，格式为 {"维度名": ["子指标1", "子指标2"]}
            
        Returns:
            多维度评分结果
        """
        try:
            # 构建多维度评分提示词
            dimension_prompt = f"""
请分析这张卫星图像，进行多维度评分分析：

维度设置: {json.dumps(dimensions, ensure_ascii=False, indent=2)}

请为每个维度的每个子指标给出1-10分的评分，并计算各维度总分。

输出格式：
{{
    "dimensions": {{
        "维度名称": {{
            "sub_metrics": {{
                "子指标名称": {{
                    "score": 分数(1-10),
                    "analysis": "详细分析"
                }}
            }},
            "dimension_score": 维度总分,
            "dimension_analysis": "维度综合分析"
        }}
    }},
    "overall_score": 总体评分,
    "recommendations": "多维度综合建议"
}}
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": dimension_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url,
                                    "detail": "high"
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
                    "dimensions": dimensions,
                    "api_provider": "GPTPlus5"
                }
            except json.JSONDecodeError:
                return {
                    "success": True,
                    "analysis": analysis_text,
                    "model": self.model,
                    "timestamp": datetime.now().isoformat(),
                    "dimensions": dimensions,
                    "api_provider": "GPTPlus5"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"多维度评分分析异常: {str(e)}",
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
            image_url = gee_data.get("image_url") or gee_data.get("url") or gee_data.get("satellite_image_url", "")
            if not image_url:
                return {
                    "success": False,
                    "error": "GEE数据中缺少图像URL",
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
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": "Hello, this is a connection test."}
                ],
                max_tokens=8000
            )
            
            return {
                "success": True,
                "message": "API连接正常",
                "model": self.model,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"API连接失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
