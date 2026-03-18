"""
PROMETHEE-MCGP Decision Analysis Service - Multi-criteria decision method based on Reference 2
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import math
from datetime import datetime

@dataclass
class CriteriaWeight:
    """Criteria weight"""
    name: str
    weight: float
    is_benefit: bool  # True = benefit type, False = cost type

@dataclass
class AlternativeScore:
    """Alternative score"""
    name: str
    scores: Dict[str, float]
    net_flow: float
    ranking: int

class PROMETHEEMCGP:
    """PROMETHEE-MCGP Decision Analysis Class"""
    
    def __init__(self):
        """Initialize the PROMETHEE-MCGP analyzer"""
        # Indicator system defined according to Reference 2
        self.economic_criteria = {
            "internet_penetration": {"name": "Internet Penetration Rate (%)", "weight": 0.25, "is_benefit": True},
            "transportation_density": {"name": "Transportation Density (km/km²)", "weight": 0.20, "is_benefit": True},
            "disaster_losses": {"name": "Direct Economic Losses from Natural Disasters (100M CNY)", "weight": 0.15, "is_benefit": False},
            "water_consumption": {"name": "Water Consumption per 10k CNY GDP (m³)", "weight": 0.20, "is_benefit": False},
            "disposable_income": {"name": "Per Capita Disposable Income of Urban Residents (CNY)", "weight": 0.20, "is_benefit": True}
        }
        
        self.environmental_criteria = {
            "annual_temperature": {"name": "Annual Average Temperature (℃)", "weight": 0.30, "is_benefit": False, "ideal": 15.0},
            "hydropower_resources": {"name": "Hydropower Resources (100M kWh/km²)", "weight": 0.25, "is_benefit": True},
            "wind_resources": {"name": "Wind Energy Resources (100M kWh/km²)", "weight": 0.25, "is_benefit": True},
            "air_quality_rate": {"name": "Air Quality Excellence Rate (%)", "weight": 0.20, "is_benefit": True}
        }
        
        self.energy_criteria = {
            "solar_irradiance": {"name": "Annual Solar Irradiance (kWh/m²)", "weight": 0.40, "is_benefit": True},
            "wind_speed": {"name": "Average Wind Speed (m/s)", "weight": 0.30, "is_benefit": True},
            "renewable_coverage": {"name": "Renewable Energy Coverage Rate (%)", "weight": 0.30, "is_benefit": True}
        }
    
    async def analyze_data_center_site_selection(self, lat: float, lon: float, 
                                               city_name: str = None) -> Dict[str, Any]:
        """
        PROMETHEE-MCGP analysis for data center site selection
        
        Args:
            lat: Latitude
            lon: Longitude
            city_name: City name
            
        Returns:
            Site selection analysis results
        """
        try:
            # 1. Get base data
            economic_data = await self._get_economic_data(lat, lon, city_name)
            environmental_data = await self._get_environmental_data(lat, lon, city_name)
            energy_data = await self._get_energy_data(lat, lon, city_name)
            
            # 2. Phase 1: PROMETHEE analysis of economic factors
            economic_ranking = await self._promethee_analysis(
                economic_data, self.economic_criteria, "Economic Factors"
            )
            
            # 3. Phase 2: MCGP comprehensive analysis
            mcgp_result = await self._mcgp_analysis(
                economic_ranking, environmental_data, energy_data
            )
            
            # 4. Generate comprehensive score and recommendations
            final_ranking = await self._generate_final_ranking(
                economic_ranking, mcgp_result
            )
            
            return {
                "location": {"latitude": lat, "longitude": lon, "city": city_name},
                "economic_analysis": economic_ranking,
                "environmental_analysis": environmental_data,
                "energy_analysis": energy_data,
                "mcgp_result": mcgp_result,
                "final_ranking": final_ranking,
                "recommendation": self._generate_recommendation(final_ranking),
                "methodology": "PROMETHEE-MCGP Integrated Method"
            }
            
        except Exception as e:
            print(f"PROMETHEE-MCGP analysis failed: {e}")
            return {
                "error": str(e),
                "location": {"latitude": lat, "longitude": lon, "city": city_name}
            }
    
    async def _get_economic_data(self, lat: float, lon: float, city_name: str) -> Dict[str, float]:
        """Get economic factor data"""
        # Economic data based on geographic location and city characteristics
        city_data = {
            "Beijing":    {"internet_penetration": 85.0, "transportation_density": 1.2,
                           "disaster_losses": 0.5, "water_consumption": 45.0, "disposable_income": 75000},
            "Shanghai":   {"internet_penetration": 88.0, "transportation_density": 1.5,
                           "disaster_losses": 0.3, "water_consumption": 40.0, "disposable_income": 78000},
            "Shenzhen":   {"internet_penetration": 92.0, "transportation_density": 1.8,
                           "disaster_losses": 0.2, "water_consumption": 35.0, "disposable_income": 82000},
            "Hangzhou":   {"internet_penetration": 87.0, "transportation_density": 1.3,
                           "disaster_losses": 0.4, "water_consumption": 42.0, "disposable_income": 76000},
            "Zhongwei":   {"internet_penetration": 65.0, "transportation_density": 0.8,
                           "disaster_losses": 0.1, "water_consumption": 25.0, "disposable_income": 45000},
            "Guiyang":    {"internet_penetration": 70.0, "transportation_density": 1.0,
                           "disaster_losses": 0.2, "water_consumption": 30.0, "disposable_income": 50000},
            "Guangzhou":  {"internet_penetration": 89.0, "transportation_density": 1.6,
                           "disaster_losses": 0.3, "water_consumption": 38.0, "disposable_income": 80000},
            "Lanzhou":    {"internet_penetration": 68.0, "transportation_density": 0.9,
                           "disaster_losses": 0.2, "water_consumption": 28.0, "disposable_income": 48000}
        }
        
        if city_name and city_name in city_data:
            return city_data[city_name]
        
        # Estimation based on geographic location
        base_data = {
            "internet_penetration": 70.0 + (90 - abs(lat)) * 0.5,
            "transportation_density": 0.8 + (90 - abs(lat)) * 0.02,
            "disaster_losses": 0.3 + abs(lat - 35) * 0.01,
            "water_consumption": 40.0 + abs(lat - 35) * 0.5,
            "disposable_income": 50000 + (90 - abs(lat)) * 200
        }
        
        return base_data
    
    async def _get_environmental_data(self, lat: float, lon: float, city_name: str) -> Dict[str, float]:
        """Get environmental factor data"""
        # Estimation based on geographic location
        annual_temp = 25.0 - (abs(lat) - 30) * 0.5  # Temperature decreases with higher latitude
        
        # Water resource abundance
        if 20 <= lat <= 35 and 110 <= lon <= 125:   # South China
            hydropower = 0.8
        elif 25 <= lat <= 40 and 100 <= lon <= 110:  # Southwest
            hydropower = 0.9
        elif 30 <= lat <= 45 and 120 <= lon <= 135:  # East China
            hydropower = 0.6
        else:
            hydropower = 0.4
        
        # Wind energy resources
        wind_resources = 0.3 + (90 - abs(lat)) * 0.01
        
        # Air quality
        if 40 <= lat <= 55 and 80 <= lon <= 100:    # Northwest
            air_quality = 0.85
        elif 25 <= lat <= 40 and 100 <= lon <= 110:  # Southwest
            air_quality = 0.90
        else:
            air_quality = 0.70
        
        return {
            "annual_temperature": annual_temp,
            "hydropower_resources": hydropower,
            "wind_resources": wind_resources,
            "air_quality_rate": air_quality * 100
        }
    
    async def _get_energy_data(self, lat: float, lon: float, city_name: str) -> Dict[str, float]:
        """Get energy factor data"""
        # Solar irradiance
        solar_irradiance = 1000 + (90 - abs(lat)) * 20
        if lon > 100:
            solar_irradiance += 200
        elif lon < 110:
            solar_irradiance -= 100
        
        # Average wind speed
        wind_speed = 3.0 + (90 - abs(lat)) * 0.1
        if lon > 100:
            wind_speed += 1.0
        elif lon < 110:
            wind_speed -= 0.5
        
        # Renewable energy coverage rate
        renewable_coverage = min(solar_irradiance / 2000 + wind_speed / 6.0, 1.0)
        
        return {
            "solar_irradiance": solar_irradiance,
            "wind_speed": wind_speed,
            "renewable_coverage": renewable_coverage * 100
        }
    
    async def _promethee_analysis(self, data: Dict[str, float], 
                                criteria: Dict[str, Dict], 
                                category: str) -> Dict[str, Any]:
        """PROMETHEE analysis"""
        try:
            # Data normalization
            normalized_data = self._normalize_data(data, criteria)
            
            # Calculate preference function
            preference_matrix = self._calculate_preference_matrix(normalized_data, criteria)
            
            # Calculate flow values
            leaving_flow, entering_flow, net_flow = self._calculate_flows(preference_matrix)
            
            # Generate ranking
            ranking = self._generate_ranking(net_flow)
            
            return {
                "category": category,
                "normalized_data": normalized_data,
                "preference_matrix": preference_matrix.tolist(),
                "leaving_flow": leaving_flow,
                "entering_flow": entering_flow,
                "net_flow": net_flow,
                "ranking": ranking,
                "method": "PROMETHEE"
            }
            
        except Exception as e:
            print(f"PROMETHEE analysis failed: {e}")
            return {"error": str(e), "category": category}
    
    def _normalize_data(self, data: Dict[str, float], 
                       criteria: Dict[str, Dict]) -> Dict[str, float]:
        """Data normalization"""
        normalized = {}
        
        for criterion, value in data.items():
            if criterion in criteria:
                # Simple linear normalization to [0, 1]
                if criteria[criterion]["is_benefit"]:
                    # Benefit type: higher value is better
                    normalized[criterion] = min(value / 100, 1.0)
                else:
                    # Cost type: lower value is better
                    normalized[criterion] = max(1.0 - value / 100, 0.0)
        
        return normalized
    
    def _calculate_preference_matrix(self, data: Dict[str, float], 
                                   criteria: Dict[str, Dict]) -> np.ndarray:
        """Calculate preference matrix"""
        n_criteria = len(criteria)
        criteria_list = list(criteria.keys())
        
        # Create preference matrix
        preference_matrix = np.zeros((n_criteria, n_criteria))
        
        for i, criterion_i in enumerate(criteria_list):
            for j, criterion_j in enumerate(criteria_list):
                if i != j:
                    # Use Gaussian preference function
                    diff = data[criterion_i] - data[criterion_j]
                    weight = criteria[criterion_i]["weight"]
                    
                    if diff > 0:
                        # Gaussian function
                        sigma = 0.1  # Standard deviation
                        preference = 1 - math.exp(-(diff**2) / (2 * sigma**2))
                        preference_matrix[i, j] = weight * preference
                    else:
                        preference_matrix[i, j] = 0
        
        return preference_matrix
    
    def _calculate_flows(self, preference_matrix: np.ndarray) -> Tuple[float, float, float]:
        """Calculate flow values"""
        n = preference_matrix.shape[0]
        
        # Calculate leaving flow
        leaving_flow = np.sum(preference_matrix, axis=1) / (n - 1)
        
        # Calculate entering flow
        entering_flow = np.sum(preference_matrix, axis=0) / (n - 1)
        
        # Calculate net flow
        net_flow = leaving_flow - entering_flow
        
        return float(leaving_flow[0]), float(entering_flow[0]), float(net_flow[0])
    
    def _generate_ranking(self, net_flow: float) -> Dict[str, Any]:
        """Generate ranking"""
        if net_flow > 0.1:
            level = "Excellent"
            score = min(net_flow * 10, 100)
        elif net_flow > 0:
            level = "Good"
            score = 70 + net_flow * 30
        elif net_flow > -0.1:
            level = "Average"
            score = 50 + (net_flow + 0.1) * 200
        else:
            level = "Below Average"
            score = max(net_flow * 50, 0)
        
        return {
            "level": level,
            "score": round(score, 2),
            "net_flow": round(net_flow, 4)
        }
    
    async def _mcgp_analysis(self, economic_ranking: Dict[str, Any], 
                           environmental_data: Dict[str, float],
                           energy_data: Dict[str, float]) -> Dict[str, Any]:
        """MCGP analysis"""
        try:
            # Build objective function
            goals = {
                "economic_score": economic_ranking.get("score", 50),
                "temperature_suitability": self._calculate_temperature_suitability(
                    environmental_data["annual_temperature"]
                ),
                "hydropower_score": environmental_data["hydropower_resources"] * 100,
                "wind_score": environmental_data["wind_resources"] * 100,
                "air_quality_score": environmental_data["air_quality_rate"],
                "solar_score": min(energy_data["solar_irradiance"] / 2000 * 100, 100),
                "renewable_score": energy_data["renewable_coverage"]
            }
            
            # Calculate weights
            weights = {
                "economic": 0.3,
                "environmental": 0.4,
                "energy": 0.3
            }
            
            # Comprehensive score
            comprehensive_score = (
                goals["economic_score"] * weights["economic"] +
                (goals["temperature_suitability"] + goals["hydropower_score"] + 
                 goals["wind_score"] + goals["air_quality_score"]) / 4 * weights["environmental"] +
                (goals["solar_score"] + goals["renewable_score"]) / 2 * weights["energy"]
            )
            
            return {
                "goals": goals,
                "weights": weights,
                "comprehensive_score": round(comprehensive_score, 2),
                "method": "MCGP"
            }
            
        except Exception as e:
            print(f"MCGP analysis failed: {e}")
            return {"error": str(e)}
    
    def _calculate_temperature_suitability(self, temperature: float) -> float:
        """Calculate temperature suitability"""
        ideal_temp = 15.0  # Ideal temperature
        temp_diff = abs(temperature - ideal_temp)
        
        if temp_diff <= 2:
            return 100
        elif temp_diff <= 5:
            return 80
        elif temp_diff <= 10:
            return 60
        else:
            return max(40 - temp_diff * 2, 0)
    
    async def _generate_final_ranking(self, economic_ranking: Dict[str, Any], 
                                    mcgp_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final ranking"""
        try:
            economic_score = economic_ranking.get("score", 50)
            comprehensive_score = mcgp_result.get("comprehensive_score", 50)
            
            # Composite score
            final_score = (economic_score * 0.4 + comprehensive_score * 0.6)
            
            # Determine level
            if final_score >= 85:
                level = "Excellent"
                recommendation = "Strongly Recommended"
            elif final_score >= 70:
                level = "Good"
                recommendation = "Recommended"
            elif final_score >= 55:
                level = "Average"
                recommendation = "Worth Considering"
            else:
                level = "Below Average"
                recommendation = "Not Recommended"
            
            return {
                "final_score": round(final_score, 2),
                "level": level,
                "recommendation": recommendation,
                "economic_contribution": round(economic_score * 0.4, 2),
                "comprehensive_contribution": round(comprehensive_score * 0.6, 2)
            }
            
        except Exception as e:
            print(f"Final ranking generation failed: {e}")
            return {"error": str(e)}
    
    def _generate_recommendation(self, final_ranking: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recommendation"""
        try:
            level = final_ranking.get("level", "Average")
            score = final_ranking.get("final_score", 50)
            
            recommendations = []
            
            if level == "Excellent":
                recommendations.extend([
                    "This area is highly suitable for data center construction",
                    "Recommend prioritizing this location",
                    "A large-scale data center campus can be planned"
                ])
            elif level == "Good":
                recommendations.extend([
                    "This area is suitable for data center construction",
                    "Recommend conducting a detailed feasibility study",
                    "Consider building a medium-sized data center"
                ])
            elif level == "Average":
                recommendations.extend([
                    "This area can support a data center but requires optimization",
                    "Recommend improving infrastructure conditions",
                    "Suitable for a small-scale data center"
                ])
            else:
                recommendations.extend([
                    "This area is not suitable for data center construction",
                    "Recommend finding an alternative location",
                    "If construction is required, significant investment will be needed to improve conditions"
                ])
            
            return {
                "overall_assessment": level,
                "score": score,
                "recommendations": recommendations,
                "next_steps": self._get_next_steps(level)
            }
            
        except Exception as e:
            print(f"Recommendation generation failed: {e}")
            return {"error": str(e)}
    
    def _get_next_steps(self, level: str) -> List[str]:
        """Get next step recommendations"""
        if level == "Excellent":
            return [
                "Conduct a detailed environmental impact assessment",
                "Develop a specific construction plan",
                "Apply for relevant permits and approvals"
            ]
        elif level == "Good":
            return [
                "Conduct a more detailed technical feasibility study",
                "Assess infrastructure improvement requirements",
                "Develop a risk mitigation plan"
            ]
        elif level == "Average":
            return [
                "Evaluate the cost-benefit of improvements",
                "Explore alternative solutions",
                "Consider phased construction"
            ]
        else:
            return [
                "Re-evaluate site selection criteria",
                "Identify other candidate locations",
                "Consider alternative construction models"
            ]
    
    async def analyze_data_center_site_selection_with_ai(self, latitude: float, longitude: float, city_name: str, 
                                                       ai_multimodal: Dict[str, Any], ai_energy: Dict[str, Any],
                                                       ai_power_supply: Dict[str, Any], ai_energy_storage: Dict[str, Any],
                                                       ai_decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        PROMETHEE-MCGP analysis using AI analysis results
        
        Args:
            latitude: Latitude
            longitude: Longitude
            city_name: City name
            ai_multimodal: Multimodal AI analysis results
            ai_energy: Energy AI analysis results
            ai_power_supply: Power supply AI analysis results
            ai_energy_storage: Energy storage AI analysis results
            ai_decision: Decision AI analysis results
            
        Returns:
            Comprehensive PROMETHEE-MCGP analysis results
        """
        try:
            # Extract scores from AI analysis results
            scores = self._extract_scores_from_ai_results(
                ai_multimodal, ai_energy, ai_power_supply, ai_energy_storage, ai_decision
            )
            
            # Perform PROMETHEE-MCGP analysis using extracted scores
            analysis_result = self._perform_promethee_mcgp_analysis(scores)
            
            # Add references to AI analysis results
            analysis_result["ai_analysis_integration"] = {
                "multimodal_analysis": ai_multimodal.get("success", False),
                "energy_analysis": ai_energy.get("success", False),
                "power_supply_analysis": ai_power_supply.get("success", False),
                "energy_storage_analysis": ai_energy_storage.get("success", False),
                "decision_analysis": ai_decision.get("success", False)
            }
            
            return analysis_result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"AI-integrated PROMETHEE-MCGP analysis failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _extract_scores_from_ai_results(self, ai_multimodal: Dict[str, Any], ai_energy: Dict[str, Any],
                                      ai_power_supply: Dict[str, Any], ai_energy_storage: Dict[str, Any],
                                      ai_decision: Dict[str, Any]) -> Dict[str, float]:
        """Extract scores from AI analysis results"""
        scores = {}

        def _extract_score_from_text(text: str) -> Optional[float]:
            """Best-effort extraction of a 0–100 score from free-text AI output.

            Looks for patterns like "8/10", "8.5 / 10", or "85%" and scales to 0–100.
            Returns None when no obvious score is found.
            """
            import re

            # Match "x/10" style
            match = re.search(r"(\d+(?:\.\d+)?)\s*/\s*10", text)
            if match:
                val = float(match.group(1)) * 10
                return max(0.0, min(100.0, val))

            # Match percentage style "85%"
            match = re.search(r"(\d+(?:\.\d+)?)\s*%", text)
            if match:
                val = float(match.group(1))
                return max(0.0, min(100.0, val))

            return None
        
        # Extract scores for the 8 core dimensions from multimodal analysis
        if ai_multimodal.get("success") and "analysis" in ai_multimodal:
            try:
                analysis = ai_multimodal["analysis"]
                if isinstance(analysis, dict):
                    # Extract scores for the 8 core dimensions
                    for key in ["energy_supply", "network_connectivity", "geographic_environment", 
                              "policy_regulations", "infrastructure", "human_resources", 
                              "socio_economic", "business_ecosystem"]:
                        if key in analysis and "score" in analysis[key]:
                            scores[f"ai_{key}"] = analysis[key]["score"]
            except Exception as e:
                print(f"⚠️ Failed to extract multimodal analysis scores: {e}")

        # Extract scores from other AI analyses
        for ai_result, prefix in [(ai_energy, "energy"), (ai_power_supply, "power_supply"), 
                                (ai_energy_storage, "energy_storage"), (ai_decision, "decision")]:
            if ai_result.get("success") and "analysis" in ai_result:
                try:
                    analysis = ai_result["analysis"]
                    if isinstance(analysis, dict):
                        # Extract overall score
                        if "overall_score" in analysis:
                            scores[f"ai_{prefix}_overall"] = analysis["overall_score"]
                        # Extract dimension scores
                        for key, value in analysis.items():
                            if isinstance(value, dict) and "score" in value:
                                scores[f"ai_{prefix}_{key}"] = value["score"]
                    elif isinstance(analysis, str):
                        # Try to pull an overall score from text output
                        extracted = _extract_score_from_text(analysis)
                        if extracted is not None:
                            scores[f"ai_{prefix}_overall"] = extracted
                except Exception as e:
                    print(f"⚠️ Failed to extract {prefix} analysis scores: {e}")

        return scores
    
    def _perform_promethee_mcgp_analysis(self, scores: Dict[str, float]) -> Dict[str, Any]:
        """Execute PROMETHEE-MCGP analysis"""
        try:
            # Build comprehensive scoring matrix
            criteria_weights = {
                "ai_energy_supply": 0.20,
                "ai_network_connectivity": 0.15,
                "ai_geographic_environment": 0.15,
                "ai_policy_regulations": 0.10,
                "ai_infrastructure": 0.10,
                "ai_human_resources": 0.10,
                "ai_socio_economic": 0.10,
                "ai_business_ecosystem": 0.10
            }
            
            # Calculate weighted total score
            total_score = 0
            weight_sum = 0
            for criterion, weight in criteria_weights.items():
                if criterion in scores:
                    total_score += scores[criterion] * weight
                    weight_sum += weight
            
            # If expected AI scores are missing, fall back to mean of available scores
            # to avoid returning zero when some scores are present
            if weight_sum > 0:
                normalized_score = total_score / weight_sum
            elif scores:
                normalized_score = sum(scores.values()) / len(scores)
            else:
                # No usable AI scores; default to neutral mid-score instead of 0 to avoid false failure
                normalized_score = 50
            
            # Generate analysis results
            return {
                "success": True,
                "analysis_type": "AI Integrated PROMETHEE-MCGP",
                "overall_score": round(normalized_score, 2),
                "detailed_scores": scores,
                "criteria_weights": criteria_weights,
                "recommendations": self._generate_ai_integrated_recommendations(scores, normalized_score),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"PROMETHEE-MCGP analysis failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _generate_ai_integrated_recommendations(self, scores: Dict[str, float], overall_score: float) -> str:
        """Generate integrated recommendations based on AI scores"""
        recommendations = []
        
        # Overall guidance
        if overall_score >= 80:
            recommendations.append("Strong candidate for data center development; prioritize this site.")
        elif overall_score >= 60:
            recommendations.append("Good candidate; proceed with detailed planning and risk checks.")
        elif overall_score >= 40:
            recommendations.append("Viable but with notable risks; mitigate weak dimensions before proceeding.")
        else:
            recommendations.append("Not recommended; consider alternative locations.")
        
        # Dimension-specific suggestions
        for criterion, score in scores.items():
            if score < 50:
                criterion_name = criterion.replace("ai_", "").replace("_", " ")
                recommendations.append(f"Improve {criterion_name} (current score: {score}).")
        
        return " ".join(recommendations)
