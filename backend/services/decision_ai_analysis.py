"""
Decision analysis AI service - uses OpenAI SDK for intelligent decision analysis
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from openai import AsyncOpenAI
import os

class DecisionAIAnalysisService:
    """Decision analysis AI service"""

    def __init__(self):
        """Initialize decision analysis AI service"""
        # Use project-level API key (proxy picked up from env if provided)
        api_key = os.getenv('OPENAI_API_KEY')

        self.client = AsyncOpenAI(
            base_url=os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1'),
            api_key=api_key
        )
        self.model = "gpt-4o-2024-08-06"
        
        # Decision-analysis prompt template
        self.decision_prompt = """
Please analyze this satellite image and deliver a comprehensive decision assessment for data-center siting:

1. **Site suitability**
   - Evaluate land suitability (terrain, geology, environment)
   - Analyze construction conditions (transportation, infrastructure)
   - Assess operating conditions (climate, safety)
   - Provide a suitability score (1–10)

2. **Economic analysis**
   - Evaluate land cost
   - Analyze construction cost
   - Assess operating cost
   - Analyze return on investment

3. **Technical feasibility**
   - Evaluate implementation difficulty
   - Analyze technical risks
   - Assess technological maturity
   - Analyze development potential

4. **Environmental impact**
   - Evaluate environmental impact
   - Analyze ecological protection requirements
   - Assess environmental compliance
   - Analyze sustainability potential

5. **Risk analysis**
   - Identify natural disaster risks
   - Analyze policy risks
   - Assess market risks
   - Analyze technical risks

6. **Overall recommendation**
   - Provide an overall score (1–10)
   - Provide decision recommendations
   - Identify key success factors
   - Provide implementation suggestions

Please provide detailed analysis and specific recommendations in English.
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
            # image_url may be None when satellite fetch failed — proceed text-only
            if not image_url:
                image_url = None  # handled below in _call_ai_analysis
            
            # Get geographical metadata
            metadata = satellite_data.get("metadata", {})
            location_info = {
                "center": metadata.get("center", []),
                "radius": metadata.get("radius", 0),
                "data_source": metadata.get("data_source", "Unknown"),
                "resolution": metadata.get("resolution", "Unknown")
            }
            
            # Get geographical metadata
            enhanced_prompt = self._build_decision_prompt(
                location_info, land_analysis, energy_assessment, custom_prompt
            )
            
            # Call AI analysis
            ai_result = await self._call_ai_analysis(image_url, enhanced_prompt)
            
            if ai_result["success"]:
                ai_result["analysis_type"] = "AI Decision Analysis"
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
                "error": f"AI decision analysis failed: {str(e)}",
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
        
        # Add location information
        context = f"""
Geolocation information：
- coordinate: {location_info.get('center', [])}
- analysis radius: {location_info.get('radius', 0)} m
- data source: {location_info.get('data_source', 'Unknown')}
- resolution: {location_info.get('resolution', 'Unknown')}
"""
        
        # Add land use analysis information
        if land_analysis:
            context += f"""
Land use analysis results：
- total area: {land_analysis.get('total_area', 'Unknown')} m²
- land use distribution: {land_analysis.get('land_use_distribution', {})}
- suitability level: {land_analysis.get('empty_land_analysis', {}).get('suitability_level', 'Unknown')}
"""
        
        # 添加能源评估信息
        if energy_assessment:
            context += f"""
Energy assessment results：
- Solar data: {energy_assessment.get('solar_data', {})}
- Wind energy data: {energy_assessment.get('wind_data', {})}
- Renewable energy potential: {energy_assessment.get('renewable_potential', {})}
"""
        
        context += "\nPlease combine this information to conduct a more accurate decision analysis."
        
        return base_prompt + "\n\n" + context
    
    async def _call_ai_analysis(self, image_url: str, prompt: str) -> Dict[str, Any]:
        """Calling AI Analysis API"""
        try:
            # Build message content — include image only when URL is available
            if image_url:
                content = [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url, "detail": "high"}
                    }
                ]
            else:
                content = [{"type": "text", "text": prompt}]

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": content}],
                max_tokens=8000,
                temperature=0.3,
                timeout=180
            )

            analysis_text = response.choices[0].message.content

            return {
                "success": True,
                "analysis": analysis_text,
                "model": self.model,
                "timestamp": datetime.now().isoformat(),
                "image_url": image_url,
                "api_provider": "OpenAI",
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"AI analysis call failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
