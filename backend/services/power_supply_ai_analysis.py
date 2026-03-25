"""
Power Supply Solution AI Analysis Service - Intelligent power supply solution analysis using the official OpenAI library
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from openai import AsyncOpenAI
import os

class PowerSupplyAIAnalysisService:
    """Power Supply Solution AI Analysis Service Class"""

    def __init__(self):
        """Initialize the power supply solution AI analysis service"""
        # Do NOT mutate global proxy env vars here; they are set externally via .env / shell.
        self.client = AsyncOpenAI(
            base_url=os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1'),
            api_key=os.getenv('OPENAI_API_KEY')
        )
        self.model = "gpt-4o-2024-08-06"
        
        # Dedicated prompt template for power supply solution analysis
        self.power_supply_prompt = """
Based on the provided satellite image and geographic location information, please conduct a professional evaluation of the data center power supply solution:

1. **Grid Access Analysis**
   - Evaluate the distribution of surrounding grid infrastructure based on geographic location
   - Analyze grid access distance and construction costs
   - Assess grid capacity and power supply reliability
   - Provide a grid access feasibility score (1-10)

2. **Renewable Energy Supply Potential**
   - Assess solar power generation potential based on geographic location and terrain
   - Evaluate wind power generation feasibility based on regional wind resources
   - Analyze hydropower resource conditions
   - Calculate recommended renewable energy supply ratio

3. **Conventional Energy Supply Solutions**
   - Assess suitability for natural gas power plant construction
   - Analyze environmental impact and costs of coal-fired power generation
   - Evaluate site conditions for nuclear power plant placement
   - Compare economic viability of conventional energy supply

4. **Optimal Power Supply Combination Plan**
   - Recommend the most technically and economically optimal power supply combination
   - Analyze reliability and stability of the power supply system
   - Evaluate total power supply costs (construction + operation)
   - Provide optimization configuration recommendations for the power supply plan

5. **Power Supply Assurance & Redundancy Design**
   - Identify critical backup power configuration requirements
   - Evaluate energy storage system capacity and type selection
   - Design power supply redundancy and emergency assurance plan
   - Provide recommendations to improve power supply safety and reliability

Please provide detailed technical evaluation results and specific implementation recommendations based on professional analysis, ensuring the response is professional, practical, and actionable.
"""
    
    async def analyze_power_supply_ai(self, satellite_data: Dict[str, Any], 
                                    power_demand: float = 100,
                                    custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze power supply solutions using AI
        
        Args:
            satellite_data: Satellite data
            power_demand: Power demand (MW)
            custom_prompt: Custom analysis prompt
            
        Returns:
            AI power supply solution analysis results
        """
        try:
            image_url = satellite_data.get("url") or satellite_data.get("image_url", "")
            if not image_url:
                return {
                    "success": False,
                    "error": "Unable to retrieve satellite image URL",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Get geographic metadata
            metadata = satellite_data.get("metadata", {})
            location_info = {
                "center": metadata.get("center", []),
                "radius": metadata.get("radius", 0),
                "data_source": metadata.get("data_source", "Unknown"),
                "resolution": metadata.get("resolution", "Unknown")
            }
            
            # Build enhanced power supply analysis prompt
            enhanced_prompt = self._build_power_supply_prompt(
                location_info, power_demand, custom_prompt
            )
            
            # Call AI analysis
            ai_result = await self._call_ai_analysis(image_url, enhanced_prompt)
            
            if ai_result["success"]:
                ai_result["analysis_type"] = "AI Power Supply Solution Analysis"
                ai_result["location_info"] = location_info
                ai_result["power_demand"] = power_demand
                ai_result["gee_metadata"] = metadata
            
            return ai_result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"AI power supply solution analysis failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_power_supply_prompt(self, location_info: Dict[str, Any], 
                                  power_demand: float,
                                  custom_prompt: Optional[str] = None) -> str:
        """Build a dedicated prompt for power supply solution analysis"""
        if custom_prompt:
            base_prompt = custom_prompt
        else:
            base_prompt = self.power_supply_prompt
        
        # Add geographic location and power demand information
        context = f"""
Geographic Location and Demand Information:
- Coordinates: {location_info.get('center', [])}
- Analysis Radius: {location_info.get('radius', 0)} meters
- Data Source: {location_info.get('data_source', 'Unknown')}
- Resolution: {location_info.get('resolution', 'Unknown')}
- Power Demand: {power_demand} MW

Please combine this information to provide a more accurate analysis of the power supply solution.
"""
        
        return base_prompt + "\n\n" + context
    
    async def _call_ai_analysis(self, image_url: str, prompt: str) -> Dict[str, Any]:
        """Call the AI analysis API"""
        try:
            # Use the official OpenAI library for API calls
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
                                    "detail": "high"  # Use low to reduce context length
                                }
                            }
                        ]
                    }
                ],
                max_tokens=8000,
                temperature=0.3,
                timeout=180  # 2-minute timeout
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
                "error": f"AI analysis call failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def test_api_connection(self) -> Dict[str, Any]:
        """Test API connection"""
        try:
            # Simple API connection test
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": "Please reply with 'API connection successful'"
                    }
                ],
                max_tokens=8000,
                temperature=0.1,
                timeout=180
            )
            
            return {
                "success": True,
                "message": "API connection successful",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"API connection failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
