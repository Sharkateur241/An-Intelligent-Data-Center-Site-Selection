"""
Multimodal analysis service - satellite image analysis via OpenAI-compatible API
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
import os

class MultimodalAnalysisService:
    """Multimodal analysis service"""

    def __init__(self):
        """Initialize multimodal analysis service"""
        # Use project-level API settings; do not force a proxy
        api_key = os.environ.get('OPENAI_API_KEY', '')
        base_url = os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1')
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        self.model = os.environ.get("OPENAI_MULTIMODAL_MODEL", "gpt-4o-2024-08-06")
        # Derive provider label from base_url
        self.api_provider = "OpenAI" if "openai" in base_url else "GPTPlus5"
        
        # Datacenter siting prompt template (core dimensions)
        self.datacenter_prompt = """
Analyze this satellite image for data center siting across the core dimensions and provide detailed scores.

## Core dimensions (each 1–10)

1) Energy supply & cost
- Grid stability/reliability
- Power cost
- Green energy access
- Onsite generation feasibility

2) Network connectivity
- Distance to backbone
- Latency
- Carrier diversity
- International bandwidth quality

3) Geography & environment
- Natural hazard risk
- Climate suitability
- Terrain stability
- Environmental compliance

4) Policy & regulatory environment
- Government support
- Data compliance requirements
- Land acquisition ease
- Safety/security regulations

5) Infrastructure & utilities
- Transport access
- Water supply
- Fire safety support
- Nearby industry/ecosystem

6) Human resources & talent pool
- Technical talent availability
- Labor cost
- Training resources
- Talent mobility

7) Socioeconomic stability
- Political stability
- Economic health
- Public safety
- Policy consistency

8) Business ecosystem & market proximity
- Distance to target markets
- Industrial clustering
- Competitive landscape
- Partnership opportunities

## Output format
Provide a human-readable text result including:
- Overall score X/10
- Per-dimension details (score + analysis)
- Overall recommendation
- Key risks
- Next actions

Important: plain text only; do not return JSON or code blocks.
"""

    async def analyze_satellite_image(self, image_url: str, custom_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a satellite image.
        
        Args:
            image_url: image URL
            custom_prompt: optional prompt override
            
        Returns:
            Analysis result dict
        """
        try:
            prompt = custom_prompt or self.datacenter_prompt
            
            # Call API with retry
            import time
            max_retries = 3
            for attempt in range(max_retries):
                try:
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
                                            "detail": "low"  # use low to reduce context length
                                        }
                                    }
                                ]
                            }
                        ],
                        max_tokens=8000,
                        temperature=0.3,
                        timeout=180  # 2-minute timeout
                    )
                    break  # success
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"⚠️ API call failed, retry {attempt + 1}: {e}")
                        time.sleep(2)  # wait 2s then retry
                    else:
                        raise e
            
            analysis_text = response.choices[0].message.content
            
            # Return text analysis
            return {
                "success": True,
                "analysis": analysis_text,
                "model": self.model,
                "timestamp": datetime.now().isoformat(),
                "image_url": image_url,
                "api_provider": self.api_provider
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"API request error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

    async def analyze_with_gee_data(self, gee_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze location-only data (no image) for data center siting.
        
        Args:
            gee_data: dict with location metadata
            
        Returns:
            Analysis result
        """
        try:
            # Extract location info
            location_info = gee_data.get("metadata", {})
            center = location_info.get("center", [])
            radius = location_info.get("radius", 1000)
            
            if not center or len(center) < 2:
                return {
                    "success": False,
                    "error": "Missing location info",
                    "timestamp": datetime.now().isoformat()
                }
            
            lat, lon = center[0], center[1]
            print(f"🔍 Multimodal analysis - location: ({lat}, {lon}), radius: {radius}m")
            
            # Build city/region info
            city_name = self._get_city_name_from_coords(lat, lon)
            region_info = self._get_region_info(lat, lon)
            
            # Build 8-dimension prompt based on location
            location_prompt = f"""
Evaluate this location for data center siting across the core dimensions and provide detailed scores.

Important: reply in plain text; do not use JSON or code blocks.

## Location info
- Coordinates: ({lat}, {lon})
- City/Region: {city_name}
- Analysis radius: {radius} m
- Regional traits: {region_info}

## Core dimensions (each 1–10)

1) Energy supply & cost
- Grid stability/reliability
- Power cost
- Green energy access
- Onsite generation feasibility

2) Network connectivity
- Distance to backbone
- Latency
- Carrier diversity
- International bandwidth quality

3) Geography & environment
- Natural hazard risk
- Climate suitability
- Terrain stability
- Environmental compliance

4) Policy & regulatory environment
- Government support
- Data compliance requirements
- Land acquisition ease
- Safety/security regulations

5) Infrastructure & utilities
- Transport access
- Water supply
- Fire safety support
- Nearby industry/ecosystem

6) Human resources & talent pool
- Technical talent availability
- Labor cost
- Training resources
- Talent mobility

7) Socioeconomic stability
- Political stability
- Economic health
- Public safety
- Policy consistency

8) Business ecosystem & market proximity
- Distance to target markets
- Industrial clustering
- Competitive landscape
- Partnership opportunities

## Output format
Return analysis as JSON:
{{
  "overall_score": (1-10),
  "energy_supply": {{"score": (1-10), "analysis": "text"}},
  "network_connectivity": {{"score": (1-10), "analysis": "text"}},
  "geographic_environment": {{"score": (1-10), "analysis": "text"}},
  "policy_regulations": {{"score": (1-10), "analysis": "text"}},
  "infrastructure": {{"score": (1-10), "analysis": "text"}},
  "human_resources": {{"score": (1-10), "analysis": "text"}},
  "socio_economic": {{"score": (1-10), "analysis": "text"}},
  "business_ecosystem": {{"score": (1-10), "analysis": "text"}},
  "recommendations": "overall advice",
  "key_risks": "key risks",
  "next_steps": "action items"
}}
"""
            
            # Text-only analysis, no image included here
            response = await self.client.chat.completions.create(
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
            
            # If AI returns JSON, convert to human-readable text
            if analysis_text.strip().startswith('{') and analysis_text.strip().endswith('}'):
                try:
                    analysis_json = json.loads(analysis_text)
                    # Convert JSON to human text
                    human_text = self._convert_json_to_human_text(analysis_json)
                    analysis_text = human_text
                except json.JSONDecodeError:
                    pass  # keep original text if parsing fails
            
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
                "error": f"Location data analysis error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_city_name_from_coords(self, lat: float, lon: float) -> str:
        """Return coordinate string — no hardcoded city lookup."""
        return f"{lat:.4f}°, {lon:.4f}°"
    
    def _get_region_info(self, lat: float, lon: float) -> str:
        """Get region info from coordinates"""
        if 20 <= lat <= 50 and 100 <= lon <= 130:
            return "East China region"
        elif 20 <= lat <= 50 and 70 <= lon <= 100:
            return "West China region"
        elif 20 <= lat <= 50 and 110 <= lon <= 125:
            return "Southeast coastal China"
        else:
            return "Other region"
    
    def _convert_json_to_human_text(self, analysis_json: dict) -> str:
        """Convert JSON-formatted analysis to human-readable text"""
        try:
            overall_score = analysis_json.get('overall_score', 0)
            
            human_text = f"**Overall score**: {overall_score}/10\n\n"
            human_text += "**Dimension details**:\n\n"
            
            dimensions = [
                ('energy_supply', 'Energy supply & cost'),
                ('network_connectivity', 'Network connectivity'),
                ('geographic_environment', 'Geography & environment'),
                ('policy_regulations', 'Policy & regulation'),
                ('infrastructure', 'Infrastructure & utilities'),
                ('human_resources', 'Human resources'),
                ('socio_economic', 'Socioeconomic stability'),
                ('business_ecosystem', 'Business ecosystem & proximity')
            ]
            
            for i, (key, name) in enumerate(dimensions, 1):
                if key in analysis_json:
                    dim_data = analysis_json[key]
                    score = dim_data.get('score', 0)
                    analysis = dim_data.get('analysis', 'No analysis')
                    human_text += f"{i}. **{name}** ({score}/10): {analysis}\n\n"
            
            if 'recommendations' in analysis_json:
                human_text += f"**Recommendations**: {analysis_json['recommendations']}\n\n"
            
            if 'key_risks' in analysis_json:
                human_text += f"**Key risks**: {analysis_json['key_risks']}\n\n"
            
            if 'next_steps' in analysis_json:
                human_text += f"**Next steps**: {analysis_json['next_steps']}\n"
            
            return human_text
            
        except Exception as e:
            return f"Failed to convert analysis: {str(e)}"

    async def test_api_connection(self) -> Dict[str, Any]:
        """
        Test API connectivity
        
        Returns:
            Connectivity result
        """
        models_to_try = [
            "gpt-4o",          # preferred
            "gpt-4o-mini",    # fallback
            "qwen-vl-max"     # compatible
        ]
        
        for model in models_to_try:
            try:
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": "ping"}
                    ],
                    max_tokens=8000
                )
                
                # On success, update model
                self.model = model
                
                return {
                    "success": True,
                    "message": f"API connection OK, using model: {model}",
                    "model": model,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                print(f"Model {model} unavailable: {e}")
                continue
        
        return {
            "success": False,
            "error": "All models unavailable; check quota or provider",
            "timestamp": datetime.now().isoformat()
        }
