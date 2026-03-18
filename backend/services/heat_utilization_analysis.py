#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Waste heat utilization analysis service - data center waste heat recovery and utilization analysis
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from config import config

class HeatUtilizationAnalysisService:
    """Waste heat utilization analysis service class"""
    
    def __init__(self):
        """Initialize waste heat utilization analysis service"""
        config.setup_proxy()
        
    async def analyze_heat_utilization(self, latitude: float, longitude: float, 
                                     data_center_power: float = 100, 
                                     city_name: str = None) -> Dict[str, Any]:
        """
        Analyze waste heat utilization potential for a data center
        
        Args:
            latitude: Latitude
            longitude: Longitude
            data_center_power: Data center power (MW)
            city_name: City name
            
        Returns:
            Waste heat utilization analysis result
        """
        try:
            # Identify region type
            region_type = await self._identify_region_type(latitude, longitude, city_name)
            
            # Calculate waste heat generation
            heat_generation = await self._calculate_heat_generation(data_center_power)
            
            # Analyze waste heat utilization schemes
            utilization_schemes = await self._analyze_utilization_schemes(
                region_type, heat_generation, latitude, longitude
            )
            
            # Analyze economic benefits
            economic_analysis = await self._analyze_economic_benefits(
                utilization_schemes, data_center_power
            )
            
            # Analyze environmental impact
            environmental_impact = await self._analyze_environmental_impact(
                utilization_schemes, data_center_power
            )
            
            # Generate implementation recommendations
            implementation_recommendations = await self._generate_implementation_recommendations(
                region_type, utilization_schemes, economic_analysis
            )
            
            return {
                "success": True,
                "analysis_type": "Waste heat utilization analysis",
                "region_type": region_type,
                "heat_generation": heat_generation,
                "utilization_schemes": utilization_schemes,
                "economic_analysis": economic_analysis,
                "environmental_impact": environmental_impact,
                "implementation_recommendations": implementation_recommendations,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Waste heat utilization analysis failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _identify_region_type(self, latitude: float, longitude: float, city_name: str) -> str:
        """Identify region type"""
        try:
            # Identify based on city name
            if city_name:
                if any(c in city_name for c in ["Beijing", "Tianjin", "Hebei"]):
                    return "north"
                elif any(c in city_name for c in ["Guangdong", "Guangxi", "Hainan"]):
                    return "south"
                elif any(c in city_name for c in ["Shanghai", "Jiangsu", "Zhejiang"]):
                    return "east"
                elif any(c in city_name for c in ["Sichuan", "Chongqing", "Guizhou"]):
                    return "southwest"
                else:
                    return "other"
            
            # Identify based on coordinates
            if 35.0 <= latitude <= 45.0:
                return "north"  # Northern region
            elif 20.0 <= latitude <= 35.0:
                return "south"  # Southern region
            else:
                return "other"
                
        except Exception as e:
            print(f"⚠️ Region type identification failed: {e}")
            return "unknown"
    
    async def _calculate_heat_generation(self, data_center_power: float) -> Dict[str, Any]:
        """Calculate waste heat generation"""
        try:
            # Waste heat generation calculation
            # Assumes data center PUE of 1.5, where 0.5 is cooling system consumption
            # Waste heat mainly comes from servers and cooling systems
            
            total_power = data_center_power  # MW
            pue = 1.5  # Power Usage Effectiveness (PUE)
            it_power = total_power / pue  # IT equipment power
            cooling_power = total_power - it_power  # Cooling system power
            
            # Waste heat generation (assumes 80% of IT power and 20% of cooling power converted to waste heat)
            heat_from_it = it_power * 0.8  # IT equipment waste heat
            heat_from_cooling = cooling_power * 0.2  # Cooling system waste heat
            total_heat = heat_from_it + heat_from_cooling  # Total waste heat
            
            # Waste heat temperature (assumes average temperature of 40-60°C)
            heat_temperature = 50  # °C
            
            return {
                "total_heat_mw": round(total_heat, 2),
                "heat_from_it_mw": round(heat_from_it, 2),
                "heat_from_cooling_mw": round(heat_from_cooling, 2),
                "heat_temperature_c": heat_temperature,
                "heat_utilization_potential": "high" if total_heat > 50 else "medium" if total_heat > 20 else "low"
            }
            
        except Exception as e:
            return {"error": f"Waste heat generation calculation failed: {str(e)}"}
    
    async def _analyze_utilization_schemes(self, region_type: str, heat_generation: Dict[str, Any],
                                         latitude: float, longitude: float) -> List[Dict[str, Any]]:
        """Analyze waste heat utilization schemes"""
        try:
            schemes = []
            total_heat = heat_generation.get("total_heat_mw", 0)
            heat_temperature = heat_generation.get("heat_temperature_c", 50)
            
            if region_type == "north":
                # Northern region: primarily used for heating
                schemes.append({
                    "scheme_name": "district_heating",
                    "description": "Use waste heat for district heating systems",
                    "applicable_heat": total_heat * 0.8,  # 80% of waste heat available for heating
                    "target_users": "Residents, schools, hospitals, etc.",
                    "implementation_difficulty": "medium",
                    "economic_benefit": "high",
                    "environmental_benefit": "high"
                })
                
                schemes.append({
                    "scheme_name": "industrial_heat",
                    "description": "Use waste heat for industrial heating",
                    "applicable_heat": total_heat * 0.6,  # 60% of waste heat available for industry
                    "target_users": "Factories, manufacturing, etc.",
                    "implementation_difficulty": "low",
                    "economic_benefit": "medium",
                    "environmental_benefit": "medium"
                })
                
            elif region_type == "south":
                # Southern region: primarily used for industrial heating
                schemes.append({
                    "scheme_name": "industrial_heat",
                    "description": "Use waste heat for industrial heating",
                    "applicable_heat": total_heat * 0.7,  # 70% of waste heat available for industry
                    "target_users": "Factories, manufacturing, etc.",
                    "implementation_difficulty": "low",
                    "economic_benefit": "high",
                    "environmental_benefit": "high"
                })
                
                schemes.append({
                    "scheme_name": "hot_water_supply",
                    "description": "Use waste heat for hot water supply",
                    "applicable_heat": total_heat * 0.5,  # 50% of waste heat available for hot water
                    "target_users": "Hotels, hospitals, schools, etc.",
                    "implementation_difficulty": "medium",
                    "economic_benefit": "medium",
                    "environmental_benefit": "medium"
                })
                
            else:
                # Other regions: general plan
                schemes.append({
                    "scheme_name": "industrial_heat",
                    "description": "Use waste heat for industrial heating",
                    "applicable_heat": total_heat * 0.6,
                    "target_users": "Factories, manufacturing, etc.",
                    "implementation_difficulty": "low",
                    "economic_benefit": "medium",
                    "environmental_benefit": "medium"
                })
            
            # General option: waste heat power generation
            if total_heat > 10:  # Only consider power generation when waste heat is sufficient
                schemes.append({
                    "scheme_name": "waste_heat_power_generation",
                    "description": "Use waste heat for power generation",
                    "applicable_heat": total_heat * 0.4,  # 40% of waste heat available for power generation
                    "target_users": "Self-use or grid connection",
                    "implementation_difficulty": "high",
                    "economic_benefit": "high",
                    "environmental_benefit": "high"
                })
            
            return schemes
            
        except Exception as e:
            return [{"error": f"Waste heat utilization scheme analysis failed: {str(e)}"}]
    
    async def _analyze_economic_benefits(self, utilization_schemes: List[Dict[str, Any]], 
                                       data_center_power: float) -> Dict[str, Any]:
        """Analyze economic benefits"""
        try:
            total_investment = 0
            annual_revenue = 0
            payback_period = 0
            
            for scheme in utilization_schemes:
                if "error" in scheme:
                    continue
                    
                # Investment cost estimate (10k CNY/MW)
                investment_per_mw = 1000  # Assumed 10M CNY investment per MW of waste heat utilization
                scheme_investment = scheme.get("applicable_heat", 0) * investment_per_mw
                total_investment += scheme_investment
                
                # Annual revenue estimate (10k CNY/MW)
                revenue_per_mw = 200  # Assumed 2M CNY annual revenue per MW of waste heat utilization
                scheme_revenue = scheme.get("applicable_heat", 0) * revenue_per_mw
                annual_revenue += scheme_revenue
            
            # Calculate payback period
            if annual_revenue > 0:
                payback_period = total_investment / annual_revenue
            
            return {
                "total_investment_10k_cny": round(total_investment, 2),
                "annual_revenue_10k_cny": round(annual_revenue, 2),
                "payback_period_years": round(payback_period, 2),
                "economic_feasibility": "high" if payback_period < 5 else "medium" if payback_period < 10 else "low"
            }
            
        except Exception as e:
            return {"error": f"Economic benefit analysis failed: {str(e)}"}
    
    async def _analyze_environmental_impact(self, utilization_schemes: List[Dict[str, Any]], 
                                          data_center_power: float) -> Dict[str, Any]:
        """Analyze environmental impact"""
        try:
            co2_reduction = 0
            energy_saving = 0
            
            for scheme in utilization_schemes:
                if "error" in scheme:
                    continue
                    
                # CO2 reduction estimate (tons/year/MW)
                co2_per_mw = 1000  # Assumed 1000 tons CO2 reduction per MW per year
                scheme_co2 = scheme.get("applicable_heat", 0) * co2_per_mw
                co2_reduction += scheme_co2
                
                # Energy saving estimate (MWh/year/MW)
                energy_per_mw = 5000  # Assumed 5000 MWh energy saving per MW per year
                scheme_energy = scheme.get("applicable_heat", 0) * energy_per_mw
                energy_saving += scheme_energy
            
            return {
                "co2_reduction_tons_year": round(co2_reduction, 2),
                "energy_saving_mwh_year": round(energy_saving, 2),
                "environmental_benefit": "high" if co2_reduction > 5000 else "medium" if co2_reduction > 1000 else "low"
            }
            
        except Exception as e:
            return {"error": f"Environmental impact analysis failed: {str(e)}"}
    
    async def _generate_implementation_recommendations(self, region_type: str, 
                                                     utilization_schemes: List[Dict[str, Any]],
                                                     economic_analysis: Dict[str, Any]) -> List[str]:
        """Generate implementation recommendations"""
        try:
            recommendations = []
            
            # Recommendations based on region type
            if region_type == "north":
                recommendations.append("Prioritize district heating scheme to fully utilize waste heat resources")
                recommendations.append("Partner with local heating companies to establish a waste heat utilization network")
            elif region_type == "south":
                recommendations.append("Prioritize industrial heat scheme and identify suitable industrial users")
                recommendations.append("Consider hot water supply scheme to serve local commercial users")
            else:
                recommendations.append("Select an appropriate waste heat utilization scheme based on local conditions")
            
            # Recommendations based on economic benefits
            if economic_analysis.get("economic_feasibility") == "high":
                recommendations.append("Good economic feasibility — recommend implementing as soon as possible")
            elif economic_analysis.get("economic_feasibility") == "medium":
                recommendations.append("Moderate economic feasibility — further scheme optimization needed")
            else:
                recommendations.append("Low economic feasibility — recommend re-evaluating the scheme")
            
            # Recommendations based on waste heat utilization schemes
            for scheme in utilization_schemes:
                if "error" in scheme:
                    continue
                    
                if scheme.get("implementation_difficulty") == "low":
                    recommendations.append(f"Recommend prioritizing the {scheme.get('scheme_name')} scheme")
                elif scheme.get("implementation_difficulty") == "medium":
                    recommendations.append(f"Consider implementing the {scheme.get('scheme_name')} scheme — detailed planning required")
                else:
                    recommendations.append(f"The {scheme.get('scheme_name')} scheme has high implementation difficulty — thorough preparation needed")
            
            return recommendations
            
        except Exception as e:
            return [f"Implementation recommendation generation failed: {str(e)}"]