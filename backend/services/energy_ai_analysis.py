"""
能源资源AI分析服务 - 使用OpenAI官方库进行智能能源评估
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from openai import OpenAI
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from config import config

class EnergyAIAnalysisService:
    """能源资源AI分析服务类"""
    
    def __init__(self):
        """初始化能源AI分析服务"""
        # 设置代理和API密钥
        config.setup_proxy()
        config.setup_openai_key()
        
        self.client = OpenAI(
            base_url=config.OPENAI_BASE_URL,
            api_key=config.OPENAI_API_KEY
        )
        self.model = "gpt-4o-2024-08-06"
        
        # 能源分析专用prompt模板
        self.energy_prompt = """
请分析这张卫星图像，从能源资源角度评估数据中心的可再生能源潜力：

1. **太阳能资源评估**
   - 识别地形平坦度，评估光伏板安装适宜性
   - 分析云层覆盖情况，评估日照条件
   - 识别阴影区域（山脉、建筑等）
   - 评估太阳能发电潜力（1-10分）

2. **风能资源评估**
   - 识别地形特征，评估风力条件
   - 分析海拔高度对风能的影响
   - 识别风力发电适宜区域
   - 评估风能发电潜力（1-10分）

3. **水能资源评估**
   - 识别河流、湖泊等水体
   - 分析水体规模和水能潜力
   - 评估水力发电可行性
   - 评估水能发电潜力（1-10分）

4. **地热能评估**
   - 分析地质构造特征
   - 识别地热资源潜力区域
   - 评估地热能利用可行性
   - 评估地热能潜力（1-10分）

5. **综合能源建议**
   - 推荐最佳能源组合方案
   - 提供具体的能源配置建议
   - 评估能源自给自足能力
   - 给出能源成本预估

请提供详细的分析结果和具体建议，使用中文回答。
"""
    
    async def analyze_energy_resources_ai(self, satellite_data: Dict[str, Any], 
                                        custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        使用AI分析能源资源
        
        Args:
            satellite_data: 卫星数据
            custom_prompt: 自定义分析提示词
            
        Returns:
            AI能源分析结果
        """
        try:
            image_url = satellite_data.get("url") or satellite_data.get("image_url", "")
            print(f"🔍 能源AI分析 - 图像URL: {image_url[:50] if image_url else 'None'}...")
            
            if not image_url:
                return {
                    "success": False,
                    "error": "无法获取卫星图像URL",
                    "timestamp": datetime.now().isoformat()
                }
            
            # 检查图像URL格式
            if not (image_url.startswith("data:image/") or image_url.startswith("https://")):
                return {
                    "success": False,
                    "error": f"图像URL格式不正确: {image_url[:50]}...",
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
            
            # 构建增强的能源分析prompt
            enhanced_prompt = self._build_energy_prompt(location_info, custom_prompt)
            
            # 调用AI分析
            ai_result = await self._call_ai_analysis(image_url, enhanced_prompt)
            
            if ai_result["success"]:
                ai_result["analysis_type"] = "AI能源资源分析"
                ai_result["location_info"] = location_info
                ai_result["gee_metadata"] = metadata
            
            return ai_result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"AI能源分析失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_energy_prompt(self, location_info: Dict[str, Any], 
                           custom_prompt: Optional[str] = None) -> str:
        """构建能源分析专用prompt"""
        if custom_prompt:
            base_prompt = custom_prompt
        else:
            base_prompt = self.energy_prompt
        
        # 添加地理位置信息
        location_context = f"""
地理位置信息：
- 坐标: {location_info.get('center', [])}
- 分析半径: {location_info.get('radius', 0)}米
- 数据源: {location_info.get('data_source', 'Unknown')}
- 分辨率: {location_info.get('resolution', 'Unknown')}

请结合这些地理信息，对能源资源进行更准确的分析。
"""
        
        return base_prompt + "\n\n" + location_context
    
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
    
    async def analyze_heat_utilization_ai(self, satellite_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI分析余热利用"""
        heat_prompt = """
请分析这张卫星图像，评估数据中心余热利用潜力：

1. **余热回收评估**
   - 识别周边工业设施和热需求区域
   - 分析热传输距离和可行性
   - 评估余热利用的经济价值

2. **热网建设分析**
   - 分析热网建设的地形条件
   - 评估热网投资成本
   - 识别潜在的热用户

3. **综合建议**
   - 推荐最佳余热利用方案
   - 提供经济效益分析
   - 给出实施建议

请提供详细的分析结果，使用中文回答。
"""
        
        return await self.analyze_energy_resources_ai(satellite_data, heat_prompt)
    
    async def analyze_geographic_environment_ai(self, satellite_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI分析地理环境"""
        geo_prompt = """
请分析这张卫星图像，评估地理环境对数据中心建设的影响：

1. **地形分析**
   - 评估地形平坦度和稳定性
   - 识别地质灾害风险区域
   - 分析海拔高度影响

2. **水文分析**
   - 识别河流、湖泊等水体
   - 评估洪水风险
   - 分析水资源供应条件

3. **气候分析**
   - 评估气候条件对数据中心的影响
   - 分析温度、湿度等环境因素
   - 识别极端天气风险

4. **环境约束**
   - 识别环境敏感区域
   - 评估生态保护要求
   - 分析环境合规性

请提供详细的分析结果，使用中文回答。
"""
        
        return await self.analyze_energy_resources_ai(satellite_data, geo_prompt)
