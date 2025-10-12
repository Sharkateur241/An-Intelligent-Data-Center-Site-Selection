"""
决策分析AI服务 - 使用OpenAI官方库进行智能决策分析
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from openai import OpenAI
import os

class DecisionAIAnalysisService:
    """决策分析AI服务类"""
    
    def __init__(self):
        """初始化决策分析AI服务"""
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
        
        # 决策分析专用prompt模板
        self.decision_prompt = """
请分析这张卫星图像，进行数据中心选址的综合决策分析：

1. **选址适宜性评估**
   - 评估土地适宜性（地形、地质、环境）
   - 分析建设条件（交通、基础设施）
   - 评估运营条件（气候、安全）
   - 给出选址适宜性评分（1-10分）

2. **经济性分析**
   - 评估土地成本
   - 分析建设成本
   - 评估运营成本
   - 分析投资回报率

3. **技术可行性分析**
   - 评估技术实现难度
   - 分析技术风险
   - 评估技术成熟度
   - 分析技术发展潜力

4. **环境影响评估**
   - 评估环境影响
   - 分析生态保护要求
   - 评估环境合规性
   - 分析可持续发展潜力

5. **风险分析**
   - 识别自然灾害风险
   - 分析政策风险
   - 评估市场风险
   - 分析技术风险

6. **综合决策建议**
   - 给出综合评分（1-10分）
   - 提供决策建议
   - 识别关键成功因素
   - 给出实施建议

请提供详细的分析结果和具体建议，使用中文回答。
"""
    
    async def analyze_location_ai(self, satellite_data: Dict[str, Any], 
                                land_analysis: Dict[str, Any] = None,
                                energy_assessment: Dict[str, Any] = None,
                                custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        使用AI进行选址决策分析
        
        Args:
            satellite_data: 卫星数据
            land_analysis: 土地利用分析结果
            energy_assessment: 能源评估结果
            custom_prompt: 自定义分析提示词
            
        Returns:
            AI决策分析结果
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
            
            # 构建增强的决策分析prompt
            enhanced_prompt = self._build_decision_prompt(
                location_info, land_analysis, energy_assessment, custom_prompt
            )
            
            # 调用AI分析
            ai_result = await self._call_ai_analysis(image_url, enhanced_prompt)
            
            if ai_result["success"]:
                ai_result["analysis_type"] = "AI决策分析"
                ai_result["location_info"] = location_info
                ai_result["gee_metadata"] = metadata
                if land_analysis:
                    ai_result["land_analysis"] = land_analysis
                if energy_assessment:
                    ai_result["energy_assessment"] = energy_assessment
            
            return ai_result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"AI决策分析失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_decision_prompt(self, location_info: Dict[str, Any], 
                             land_analysis: Dict[str, Any] = None,
                             energy_assessment: Dict[str, Any] = None,
                             custom_prompt: Optional[str] = None) -> str:
        """构建决策分析专用prompt"""
        if custom_prompt:
            base_prompt = custom_prompt
        else:
            base_prompt = self.decision_prompt
        
        # 添加地理位置信息
        context = f"""
地理位置信息：
- 坐标: {location_info.get('center', [])}
- 分析半径: {location_info.get('radius', 0)}米
- 数据源: {location_info.get('data_source', 'Unknown')}
- 分辨率: {location_info.get('resolution', 'Unknown')}
"""
        
        # 添加土地利用分析信息
        if land_analysis:
            context += f"""
土地利用分析结果：
- 总面积: {land_analysis.get('total_area', 'Unknown')}平方米
- 土地利用分布: {land_analysis.get('land_use_distribution', {})}
- 适宜性等级: {land_analysis.get('empty_land_analysis', {}).get('suitability_level', 'Unknown')}
"""
        
        # 添加能源评估信息
        if energy_assessment:
            context += f"""
能源评估结果：
- 太阳能数据: {energy_assessment.get('solar_data', {})}
- 风能数据: {energy_assessment.get('wind_data', {})}
- 可再生能源潜力: {energy_assessment.get('renewable_potential', {})}
"""
        
        context += "\n请结合这些信息，进行更准确的决策分析。"
        
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
