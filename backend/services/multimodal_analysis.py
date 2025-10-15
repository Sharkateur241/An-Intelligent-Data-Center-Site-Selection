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
        
        # 数据中心选址分析prompt模板 - 核心维度版
        self.datacenter_prompt = """
请分析这张卫星图像，从数据中心选址的核心维度进行评估，并给出详细的评分：

## 核心分析维度（每项1-10分）

### 1. 能源供应与成本
- 电网稳定性和可靠性
- 电力成本分析
- 绿色能源接入便利性
- 自备发电条件

### 2. 网络连接性
- 骨干网络接入距离
- 网络延迟评估
- 运营商丰富度
- 国际出口带宽质量

### 3. 地理与环境条件
- 自然灾害风险评估
- 气候条件适宜性
- 地形稳定性
- 环境合规性

### 4. 政策与法规环境
- 政府支持政策
- 数据合规要求
- 土地获取便利性
- 安全法规影响

### 5. 基础设施与配套
- 交通运输便利性
- 水资源供应
- 消防系统支持
- 周边产业配套

### 6. 人力资源与人才池
- 技术人才可用性
- 劳动力成本
- 培训资源
- 人才流动性

### 7. 社会经济稳定性
- 政治稳定性
- 经济健康度
- 社会安全状况
- 政策连续性

### 8. 商业生态与市场临近度
- 目标市场距离
- 产业集群效应
- 市场竞争状况
- 业务合作机会

## 输出格式
请以人类可读的文本格式输出分析结果，包含以下内容：

**综合评分**: X/10分

**各维度详细分析**:
1. **能源供应与成本** (X/10分): 详细分析内容
2. **网络连接性** (X/10分): 详细分析内容  
3. **地理与环境条件** (X/10分): 详细分析内容
4. **政策与法规环境** (X/10分): 详细分析内容
5. **基础设施与配套** (X/10分): 详细分析内容
6. **人力资源与人才池** (X/10分): 详细分析内容
7. **社会经济稳定性** (X/10分): 详细分析内容
8. **商业生态与市场临近度** (X/10分): 详细分析内容

**综合建议**: 基于以上分析的总体建议
**关键风险**: 需要重点关注的风险点
**下一步行动**: 具体的后续行动建议

**重要提醒**: 请务必以纯文本格式输出，不要使用JSON格式，不要使用代码块，不要使用任何编程语言语法！
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
                                            "detail": "low"  # 使用low减少上下文长度
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
        基于地理位置信息进行数据中心选址分析（不依赖图像）
        
        Args:
            gee_data: GEE数据字典，包含位置信息
            
        Returns:
            综合分析结果
        """
        try:
            # 提取位置信息
            location_info = gee_data.get("metadata", {})
            center = location_info.get("center", [])
            radius = location_info.get("radius", 1000)
            
            if not center or len(center) < 2:
                return {
                    "success": False,
                    "error": "缺少位置信息",
                    "timestamp": datetime.now().isoformat()
                }
            
            lat, lon = center[0], center[1]
            print(f"🔍 多模态分析 - 位置: ({lat}, {lon}), 半径: {radius}m")
            
            # 基于位置信息生成城市名和地区信息
            city_name = self._get_city_name_from_coords(lat, lon)
            region_info = self._get_region_info(lat, lon)
            
            # 创建基于位置的8维度分析prompt
            location_prompt = f"""
请基于以下地理位置信息，从数据中心选址的核心维度进行评估，并给出详细的评分。

**重要**: 请以纯文本格式回答，不要使用JSON、代码块或任何编程语言语法！

## 分析位置信息
- 坐标: ({lat}, {lon})
- 城市/地区: {city_name}
- 分析半径: {radius}米
- 地区特征: {region_info}

## 核心分析维度（每项1-10分）

### 1. 能源供应与成本
- 电网稳定性和可靠性
- 电力成本分析
- 绿色能源接入便利性
- 自备发电条件

### 2. 网络连接性
- 骨干网络接入距离
- 网络延迟评估
- 运营商丰富度
- 国际出口带宽质量

### 3. 地理与环境条件
- 自然灾害风险评估
- 气候条件适宜性
- 地形稳定性
- 环境合规性

### 4. 政策与法规环境
- 政府支持政策
- 数据合规要求
- 土地获取便利性
- 安全法规影响

### 5. 基础设施与配套
- 交通运输便利性
- 水资源供应
- 消防系统支持
- 周边产业配套

### 6. 人力资源与人才池
- 技术人才可用性
- 劳动力成本
- 培训资源
- 人才流动性

### 7. 社会经济稳定性
- 政治稳定性
- 经济健康度
- 社会安全状况
- 政策连续性

### 8. 商业生态与市场临近度
- 目标市场距离
- 产业集群效应
- 市场竞争状况
- 业务合作机会

## 输出格式
请以JSON格式输出分析结果：
{{
    "overall_score": 总分(1-10),
    "energy_supply": {{
        "score": 分数(1-10),
        "analysis": "能源供应分析"
    }},
    "network_connectivity": {{
        "score": 分数(1-10),
        "analysis": "网络连接性分析"
    }},
    "geographic_environment": {{
        "score": 分数(1-10),
        "analysis": "地理环境分析"
    }},
    "policy_regulations": {{
        "score": 分数(1-10),
        "analysis": "政策法规分析"
    }},
    "infrastructure": {{
        "score": 分数(1-10),
        "analysis": "基础设施分析"
    }},
    "human_resources": {{
        "score": 分数(1-10),
        "analysis": "人力资源分析"
    }},
    "socio_economic": {{
        "score": 分数(1-10),
        "analysis": "社会经济分析"
    }},
    "business_ecosystem": {{
        "score": 分数(1-10),
        "analysis": "商业生态分析"
    }},
    "recommendations": "综合建议",
    "key_risks": "关键风险",
    "next_steps": "后续步骤"
}}
"""
            
            # 只使用文本分析，不包含图像
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": location_prompt
                    }
                ],
                max_tokens=8000,
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content
            
            # 如果AI返回的是JSON格式，转换为人类语言
            if analysis_text.strip().startswith('{') and analysis_text.strip().endswith('}'):
                try:
                    analysis_json = json.loads(analysis_text)
                    # 将JSON转换为人类语言
                    human_text = self._convert_json_to_human_text(analysis_json)
                    analysis_text = human_text
                except json.JSONDecodeError:
                    pass  # 如果解析失败，使用原始文本
            
            return {
                "success": True,
                "analysis": analysis_text,
                "model": self.model,
                "timestamp": datetime.now().isoformat(),
                "location_info": {
                    "city": city_name,
                    "coordinates": [lat, lon],
                    "radius": radius,
                    "region": region_info
                },
                "api_provider": "GPTPlus5"
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"位置数据分析异常: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_city_name_from_coords(self, lat: float, lon: float) -> str:
        """根据坐标获取城市名"""
        # 简单的坐标到城市名映射
        city_mapping = {
            (30.2741, 120.1551): "杭州",
            (39.9042, 116.4074): "北京", 
            (31.2304, 121.4737): "上海",
            (22.3193, 114.1694): "香港",
            (23.1291, 113.2644): "广州",
            (29.5647, 106.5507): "重庆",
            (30.5728, 104.0668): "成都",
            (36.0611, 120.3785): "青岛",
            (38.0428, 114.5149): "石家庄",
            (34.3416, 108.9398): "西安"
        }
        
        # 查找最接近的城市
        for (city_lat, city_lon), city_name in city_mapping.items():
            if abs(lat - city_lat) < 0.5 and abs(lon - city_lon) < 0.5:
                return city_name
        
        # 如果没找到精确匹配，返回坐标信息
        return f"位置({lat:.4f}, {lon:.4f})"
    
    def _get_region_info(self, lat: float, lon: float) -> str:
        """根据坐标获取地区信息"""
        if 20 <= lat <= 50 and 100 <= lon <= 130:
            return "中国东部地区"
        elif 20 <= lat <= 50 and 70 <= lon <= 100:
            return "中国西部地区"
        elif 20 <= lat <= 50 and 110 <= lon <= 125:
            return "中国东南沿海地区"
        else:
            return "其他地区"
    
    def _convert_json_to_human_text(self, analysis_json: dict) -> str:
        """将JSON格式的分析结果转换为人类语言"""
        try:
            overall_score = analysis_json.get('overall_score', 0)
            
            # 构建人类语言描述
            human_text = f"**综合评分**: {overall_score}/10分\n\n"
            human_text += "**各维度详细分析**:\n\n"
            
            # 处理各个维度
            dimensions = [
                ('energy_supply', '能源供应与成本'),
                ('network_connectivity', '网络连接性'),
                ('geographic_environment', '地理与环境条件'),
                ('policy_regulations', '政策与法规环境'),
                ('infrastructure', '基础设施与配套'),
                ('human_resources', '人力资源与人才池'),
                ('socio_economic', '社会经济稳定性'),
                ('business_ecosystem', '商业生态与市场临近度')
            ]
            
            for i, (key, name) in enumerate(dimensions, 1):
                if key in analysis_json:
                    dim_data = analysis_json[key]
                    score = dim_data.get('score', 0)
                    analysis = dim_data.get('analysis', '暂无分析')
                    human_text += f"{i}. **{name}** ({score}/10分): {analysis}\n\n"
            
            # 添加建议和风险
            if 'recommendations' in analysis_json:
                human_text += f"**综合建议**: {analysis_json['recommendations']}\n\n"
            
            if 'key_risks' in analysis_json:
                human_text += f"**关键风险**: {analysis_json['key_risks']}\n\n"
            
            if 'next_steps' in analysis_json:
                human_text += f"**下一步行动**: {analysis_json['next_steps']}\n"
            
            return human_text
            
        except Exception as e:
            return f"分析结果转换失败: {str(e)}"

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