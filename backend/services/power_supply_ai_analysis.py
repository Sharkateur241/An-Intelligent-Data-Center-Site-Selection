"""
供电方案AI分析服务 - 使用OpenAI官方库进行智能供电方案分析
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from openai import OpenAI
import os

class PowerSupplyAIAnalysisService:
    """供电方案AI分析服务类"""
    
    def __init__(self):
        """初始化供电方案AI分析服务"""
        # 设置代理
        os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7897'
        os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7897'
        
        self.client = OpenAI(
            base_url='https://api.gptplus5.com/v1',
            api_key=os.environ.get('OPENAI_API_KEY', 'sk-abaWwmXxZ2Mtw9GwLHKNI81Mxpsj9RVj5IapLh8mzoP4LfAR')
        )
        self.model = "gpt-4o-2024-08-06"
        
        # 供电方案分析专用prompt模板
        self.power_supply_prompt = """
请分析这张卫星图像，评估数据中心供电方案的技术经济性：

1. **电网接入分析**
   - 识别周边电网设施和变电站
   - 评估电网接入距离和成本
   - 分析电网容量和可靠性
   - 评估电网接入可行性（1-10分）

2. **可再生能源供电**
   - 评估太阳能发电潜力
   - 评估风能发电潜力
   - 评估水能发电潜力
   - 分析可再生能源供电比例

3. **传统能源供电**
   - 评估天然气发电可行性
   - 分析燃煤发电环境影响
   - 评估核能发电适宜性
   - 分析传统能源成本

4. **混合供电方案**
   - 推荐最佳供电组合
   - 分析供电可靠性
   - 评估供电成本
   - 提供供电方案优化建议

5. **供电保障措施**
   - 识别备用电源需求
   - 评估储能系统配置
   - 分析供电冗余设计
   - 提供供电保障建议

请提供详细的分析结果和具体建议，使用中文回答。
"""
    
    async def analyze_power_supply_ai(self, satellite_data: Dict[str, Any], 
                                    power_demand: float = 100,
                                    custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        使用AI分析供电方案
        
        Args:
            satellite_data: 卫星数据
            power_demand: 电力需求（MW）
            custom_prompt: 自定义分析提示词
            
        Returns:
            AI供电方案分析结果
        """
        try:
            image_url = satellite_data.get("url") or satellite_data.get("image_url", "")
            if not image_url:
                return {
                    "success": False,
                    "error": "无法获取卫星图像URL",
                    "timestamp": datetime.now().isoformat()
                }
            
            # 获取地理元数据
            metadata = satellite_data.get("metadata", {})
            location_info = {
                "center": metadata.get("center", []),
                "radius": metadata.get("radius", 0),
                "data_source": metadata.get("data_source", "Unknown"),
                "resolution": metadata.get("resolution", "Unknown")
            }
            
            # 构建增强的供电分析prompt
            enhanced_prompt = self._build_power_supply_prompt(
                location_info, power_demand, custom_prompt
            )
            
            # 调用AI分析
            ai_result = await self._call_ai_analysis(image_url, enhanced_prompt)
            
            if ai_result["success"]:
                ai_result["analysis_type"] = "AI供电方案分析"
                ai_result["location_info"] = location_info
                ai_result["power_demand"] = power_demand
                ai_result["gee_metadata"] = metadata
            
            return ai_result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"AI供电方案分析失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_power_supply_prompt(self, location_info: Dict[str, Any], 
                                  power_demand: float,
                                  custom_prompt: Optional[str] = None) -> str:
        """构建供电方案分析专用prompt"""
        if custom_prompt:
            base_prompt = custom_prompt
        else:
            base_prompt = self.power_supply_prompt
        
        # 添加地理位置和电力需求信息
        context = f"""
地理位置和需求信息：
- 坐标: {location_info.get('center', [])}
- 分析半径: {location_info.get('radius', 0)}米
- 数据源: {location_info.get('data_source', 'Unknown')}
- 分辨率: {location_info.get('resolution', 'Unknown')}
- 电力需求: {power_demand}MW

请结合这些信息，对供电方案进行更准确的分析。
"""
        
        return base_prompt + "\n\n" + context
    
    async def _call_ai_analysis(self, image_url: str, prompt: str) -> Dict[str, Any]:
        """调用AI分析API"""
        try:
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
                "error": f"AI分析调用失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def test_api_connection(self) -> Dict[str, Any]:
        """测试API连接"""
        try:
            # 简单的API连接测试
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": "请回复'API连接正常'"
                    }
                ],
                max_tokens=8000,
                temperature=0.1,
                timeout=180
            )
            
            return {
                "success": True,
                "message": "API连接正常",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"API连接失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
