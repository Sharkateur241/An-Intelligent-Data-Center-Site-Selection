"""
Energy resource AI analysis service - intelligent energy assessment using the OpenAI SDK
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from openai import AsyncOpenAI
import os

class EnergyAIAnalysisService:
    """Energy resource AI analysis service class"""

    def __init__(self):
        """Initialize energy AI analysis service"""
        # Proxy and API key are read from environment; no global mutation here.
        self.client = AsyncOpenAI(
            base_url=os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1'),
            api_key=os.environ.get('OPENAI_API_KEY', '')
        )
        self.model = "gpt-4o-2024-08-06"
        
        # Energy analysis prompt template
        self.energy_prompt = """
Analyze this satellite image and assess the renewable energy potential for data center siting from an energy resource perspective:

1. **Solar energy assessment**
   - Identify terrain flatness and assess suitability for photovoltaic panel installation
   - Analyze cloud cover and evaluate solar irradiance conditions
   - Identify shadow areas (mountains, buildings, etc.)
   - Rate solar generation potential (1–10)

2. **Wind energy assessment**
   - Identify terrain features and evaluate wind conditions
   - Analyze the effect of altitude on wind energy
   - Identify suitable areas for wind power generation
   - Rate wind generation potential (1–10)

3. **Hydro energy assessment**
   - Identify rivers, lakes and other water bodies
   - Analyze water body scale and hydro potential
   - Evaluate feasibility of hydroelectric generation
   - Rate hydro generation potential (1–10)

4. **Geothermal energy assessment**
   - Analyze geological structural features
   - Identify areas with geothermal resource potential
   - Evaluate feasibility of geothermal energy utilization
   - Rate geothermal potential (1–10)

5. **Comprehensive energy recommendations**
   - Recommend the optimal energy mix
   - Provide specific energy configuration advice
   - Assess energy self-sufficiency capability
   - Estimate energy costs

Please provide detailed analysis results and specific recommendations in English.
"""
    
    async def analyze_energy_resources_ai(self, satellite_data: Dict[str, Any], 
                                        custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze energy resources using AI
        
        Args:
            satellite_data: Satellite data
            custom_prompt: Custom analysis prompt
            
        Returns:
            AI energy analysis result
        """
        try:
            image_url = satellite_data.get("url") or satellite_data.get("image_url", "")
            print(f"🔍 Energy AI analysis - image URL: {image_url[:50] if image_url else 'None'}...")
            
            if not image_url:
                return {
                    "success": False,
                    "error": "Unable to retrieve satellite image URL",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Validate image URL format
            if not (image_url.startswith("data:image/") or image_url.startswith("https://")):
                return {
                    "success": False,
                    "error": f"Invalid image URL format: {image_url[:50]}...",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Retrieve geographic metadata
            metadata = satellite_data.get("metadata", {})
            location_info = {
                "center": metadata.get("center", []),
                "radius": metadata.get("radius", 0),
                "data_source": metadata.get("data_source", "Unknown"),
                "resolution": metadata.get("resolution", "Unknown")
            }
            
            # Build enhanced energy analysis prompt
            enhanced_prompt = self._build_energy_prompt(location_info, custom_prompt)
            
            # Call AI analysis
            ai_result = await self._call_ai_analysis(image_url, enhanced_prompt)
            
            if ai_result["success"]:
                ai_result["analysis_type"] = "AI energy resource analysis"
                ai_result["location_info"] = location_info
                ai_result["gee_metadata"] = metadata
            
            return ai_result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"AI energy analysis failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_energy_prompt(self, location_info: Dict[str, Any], 
                           custom_prompt: Optional[str] = None) -> str:
        """Build energy analysis prompt"""
        if custom_prompt:
            base_prompt = custom_prompt
        else:
            base_prompt = self.energy_prompt
        
        # Add geographic location info
        location_context = f"""
Geographic location info:
- Coordinates: {location_info.get('center', [])}
- Analysis radius: {location_info.get('radius', 0)} meters
- Data source: {location_info.get('data_source', 'Unknown')}
- Resolution: {location_info.get('resolution', 'Unknown')}

Please use this geographic information for a more accurate energy resource analysis.
"""
        
        return base_prompt + "\n\n" + location_context
    
    async def _call_ai_analysis(self, image_url: str, prompt: str) -> Dict[str, Any]:
        """Call AI analysis API"""
        try:
            # Call API using AsyncOpenAI to avoid blocking the event loop
            response = await self.client.chat.completions.create(
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
                temperature=0.3,
                timeout=180  # 3 minute timeout
            )
            
            analysis_text = response.choices[0].message.content
            
            return {
                "success": True,
                "analysis": analysis_text,
                "model": self.model,
                "timestamp": datetime.now().isoformat(),
                "image_url": image_url,
                "api_provider": "OpenAI"
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"AI analysis call failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def analyze_heat_utilization_ai(self, satellite_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI analysis of waste heat utilization"""
        heat_prompt = """
Analyze this satellite image and evaluate the waste heat utilization potential for a data center:

1. **Waste heat recovery assessment**
   - Identify surrounding industrial facilities and heat demand areas
   - Analyze heat transmission distance and feasibility
   - Evaluate the economic value of waste heat utilization

2. **District heating network analysis**
   - Analyze terrain conditions for heating network construction
   - Evaluate heating network investment cost
   - Identify potential heat consumers

3. **Comprehensive recommendations**
   - Recommend the optimal waste heat utilization plan
   - Provide economic benefit analysis
   - Give implementation advice

Please provide detailed analysis results in English.
"""
        
        return await self.analyze_energy_resources_ai(satellite_data, heat_prompt)
    
    async def analyze_geographic_environment_ai(self, satellite_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI analysis of geographic environment"""
        geo_prompt = """
Analyze this satellite image and assess the impact of the geographic environment on data center construction:

1. **Terrain analysis**
   - Assess terrain flatness and stability
   - Identify geological hazard risk areas
   - Analyze the impact of altitude

2. **Hydrological analysis**
   - Identify rivers, lakes and other water bodies
   - Evaluate flood risk
   - Analyze water supply conditions

3. **Climate analysis**
   - Assess the impact of climate conditions on the data center
   - Analyze environmental factors such as temperature and humidity
   - Identify extreme weather risks

4. **Environmental constraints**
   - Identify environmentally sensitive areas
   - Evaluate ecological protection requirements
   - Analyze environmental compliance

Please provide detailed analysis results in English.
"""
        
        return await self.analyze_energy_resources_ai(satellite_data, geo_prompt)