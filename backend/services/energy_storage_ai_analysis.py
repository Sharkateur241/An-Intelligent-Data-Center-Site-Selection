"""
Energy storage layout AI analysis service - intelligent storage layout analysis using the OpenAI SDK
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from openai import AsyncOpenAI
import os

class EnergyStorageAIAnalysisService:
    """Energy storage layout AI analysis service class"""

    def __init__(self):
        """Initialize energy storage layout AI analysis service"""
        self.client = AsyncOpenAI(
            base_url=os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1'),
            api_key=os.environ.get('OPENAI_API_KEY')
        )
        self.model = "gpt-4o-2024-08-06"
        
        # Energy storage layout analysis prompt template
        self.storage_prompt = """
Analyze this satellite image and evaluate energy storage system layout optimization for a data center:

1. **Storage technology selection**
   - Assess suitability of lithium-ion battery layout
   - Analyze feasibility of pumped hydro storage
   - Evaluate conditions for compressed air energy storage
   - Analyze available space for flow battery layout

2. **Storage capacity planning**
   - Analyze storage capacity requirements
   - Evaluate energy storage system scale
   - Identify installation areas for storage equipment
   - Assess energy storage system efficiency

3. **Storage layout optimization**
   - Identify optimal locations for storage equipment
   - Analyze spacing requirements for storage systems
   - Evaluate maintenance accessibility of storage equipment
   - Analyze safety of storage systems

4. **Storage economic analysis**
   - Evaluate capital cost of storage systems
   - Analyze operating cost of storage systems
   - Assess economic benefits of storage systems
   - Provide storage investment recommendations

5. **Storage system integration**
   - Analyze grid integration plan for storage systems
   - Evaluate integration of storage with renewable energy
   - Analyze control strategies for storage systems
   - Provide storage system optimization recommendations

Please provide detailed analysis results and specific recommendations in English.
"""
    
    async def analyze_storage_layout_ai(self, satellite_data: Dict[str, Any], 
                                      power_demand: float = 100,
                                      renewable_ratio: float = 0.7,
                                      custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze energy storage layout using AI
        
        Args:
            satellite_data: Satellite data
            power_demand: Power demand (MW)
            renewable_ratio: Renewable energy ratio
            custom_prompt: Custom analysis prompt
            
        Returns:
            AI energy storage layout analysis result
        """
        try:
            image_url = satellite_data.get("url") or satellite_data.get("image_url", "")
            if not image_url:
                return {
                    "success": False,
                    "error": "Unable to retrieve satellite image URL",
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
            
            # Build enhanced storage analysis prompt
            enhanced_prompt = self._build_storage_prompt(
                location_info, power_demand, renewable_ratio, custom_prompt
            )
            
            # Call AI analysis
            ai_result = await self._call_ai_analysis(image_url, enhanced_prompt)
            
            if ai_result["success"]:
                ai_result["analysis_type"] = "AI energy storage layout analysis"
                ai_result["location_info"] = location_info
                ai_result["power_demand"] = power_demand
                ai_result["renewable_ratio"] = renewable_ratio
                ai_result["gee_metadata"] = metadata
            
            return ai_result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"AI energy storage layout analysis failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_storage_prompt(self, location_info: Dict[str, Any], 
                            power_demand: float,
                            renewable_ratio: float,
                            custom_prompt: Optional[str] = None) -> str:
        """Build energy storage layout analysis prompt"""
        if custom_prompt:
            base_prompt = custom_prompt
        else:
            base_prompt = self.storage_prompt
        
        # Add geographic location and storage requirement info
        context = f"""
Geographic location and storage requirement info:
- Coordinates: {location_info.get('center', [])}
- Analysis radius: {location_info.get('radius', 0)} meters
- Data source: {location_info.get('data_source', 'Unknown')}
- Resolution: {location_info.get('resolution', 'Unknown')}
- Power demand: {power_demand} MW
- Renewable energy ratio: {renewable_ratio*100}%

Please use this information for a more accurate storage layout analysis.
"""
        
        return base_prompt + "\n\n" + context
    
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