"""
储能布局AI分析服务 - 使用OpenAI官方库进行智能储能布局分析
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from openai import OpenAI
import os

class EnergyStorageAIAnalysisService:
    """储能布局AI分析服务类"""
    
    def __init__(self):
        """初始化储能布局AI分析服务"""
        # 设置代理
        os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7897'
        os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7897'
        
        self.client = OpenAI(
            base_url='https://api.gptplus5.com/v1',
            api_key=os.environ.get('OPENAI_API_KEY', 'sk-abaWwmXxZ2Mtw9GwLHKNI81Mxpsj9RVj5IapLh8mzoP4LfAR')
        )
        self.model = "gpt-4o-2024-08-06"
        
        # 储能布局分析专用prompt模板
        self.storage_prompt = """
请分析这张卫星图像，评估数据中心储能系统布局优化：

1. **储能技术选择**
   - 评估锂离子电池布局适宜性
   - 分析抽水蓄能可行性
   - 评估压缩空气储能条件
   - 分析液流电池布局空间

2. **储能容量规划**
   - 分析储能容量需求
   - 评估储能系统规模
   - 识别储能设备安装区域
   - 评估储能系统效率

3. **储能布局优化**
   - 识别最佳储能设备位置
   - 分析储能系统间距要求
   - 评估储能设备维护便利性
   - 分析储能系统安全性

4. **储能经济性分析**
   - 评估储能系统投资成本
   - 分析储能系统运营成本
   - 评估储能系统经济效益
   - 提供储能投资建议

5. **储能系统集成**
   - 分析储能与电网集成方案
   - 评估储能与可再生能源集成
   - 分析储能系统控制策略
   - 提供储能系统优化建议

请提供详细的分析结果和具体建议，使用中文回答。
"""
    
    async def analyze_storage_layout_ai(self, satellite_data: Dict[str, Any], 
                                      power_demand: float = 100,
                                      renewable_ratio: float = 0.7,
                                      custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        使用AI分析储能布局
        
        Args:
            satellite_data: 卫星数据
            power_demand: 电力需求（MW）
            renewable_ratio: 可再生能源比例
            custom_prompt: 自定义分析提示词
            
        Returns:
            AI储能布局分析结果
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
            
            # 构建增强的储能分析prompt
            enhanced_prompt = self._build_storage_prompt(
                location_info, power_demand, renewable_ratio, custom_prompt
            )
            
            # 调用AI分析
            ai_result = await self._call_ai_analysis(image_url, enhanced_prompt)
            
            if ai_result["success"]:
                ai_result["analysis_type"] = "AI储能布局分析"
                ai_result["location_info"] = location_info
                ai_result["power_demand"] = power_demand
                ai_result["renewable_ratio"] = renewable_ratio
                ai_result["gee_metadata"] = metadata
            
            return ai_result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"AI储能布局分析失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_storage_prompt(self, location_info: Dict[str, Any], 
                            power_demand: float,
                            renewable_ratio: float,
                            custom_prompt: Optional[str] = None) -> str:
        """构建储能布局分析专用prompt"""
        if custom_prompt:
            base_prompt = custom_prompt
        else:
            base_prompt = self.storage_prompt
        
        # 添加地理位置和储能需求信息
        context = f"""
地理位置和储能需求信息：
- 坐标: {location_info.get('center', [])}
- 分析半径: {location_info.get('radius', 0)}米
- 数据源: {location_info.get('data_source', 'Unknown')}
- 分辨率: {location_info.get('resolution', 'Unknown')}
- 电力需求: {power_demand}MW
- 可再生能源比例: {renewable_ratio*100}%

请结合这些信息，对储能布局进行更准确的分析。
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
