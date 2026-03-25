"""
Decision analysis service - AI-based intelligent decision system
"""

import json
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import math

class DecisionAnalysisService:
    """Decision analysis service class"""
    
    def __init__(self):
        """Initialize decision analysis service"""
        # Decision weight configuration
        self.decision_weights = {
            "land_suitability": 0.25,      # Land suitability
            "energy_resources": 0.30,      # Energy resources
            "grid_capacity": 0.20,         # Grid capacity
            "economic_feasibility": 0.15,  # Economic feasibility
            "environmental_impact": 0.10   # Environmental impact
        }
        
        # Scoring criteria
        self.scoring_criteria = {
            "excellent": 90,
            "good": 75,
            "fair": 60,
            "poor": 45,
            "very_poor": 30
        }
    
    async def analyze_location(self, land_analysis: Dict[str, Any], 
                            energy_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive location suitability analysis
        
        Args:
            land_analysis: Land use analysis result
            energy_assessment: Energy resource assessment result
            
        Returns:
            Comprehensive decision analysis result
        """
        try:
            # 1. Land suitability score
            land_score = await self._score_land_suitability(land_analysis)
            
            # 2. Energy resources score
            energy_score = await self._score_energy_resources(energy_assessment)
            
            # 3. Grid capacity score
            grid_score = await self._score_grid_capacity(energy_assessment.get("grid_assessment", {}))
            
            # 4. Economic feasibility score
            economic_score = await self._score_economic_feasibility(land_analysis, energy_assessment)
            
            # 5. Environmental impact score
            environmental_score = await self._score_environmental_impact(land_analysis, energy_assessment)
            
            # 6. Calculate overall score
            overall_score = await self._calculate_overall_score({
                "land_suitability": land_score,
                "energy_resources": energy_score,
                "grid_capacity": grid_score,
                "economic_feasibility": economic_score,
                "environmental_impact": environmental_score
            })
            
            # 7. Generate decision recommendations
            recommendations = await self._generate_decision_recommendations(
                overall_score, land_score, energy_score, grid_score, economic_score, environmental_score
            )
            
            # 8. Risk assessment
            risk_assessment = await self._assess_risks(land_analysis, energy_assessment)
            
            return {
                "overall_score": overall_score,
                "detailed_scores": {
                    "land_suitability": land_score,
                    "energy_resources": energy_score,
                    "grid_capacity": grid_score,
                    "economic_feasibility": economic_score,
                    "environmental_impact": environmental_score
                },
                "recommendations": recommendations,
                "risk_assessment": risk_assessment,
                "decision_level": await self._get_decision_level(overall_score),
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Decision analysis failed: {e}")
            raise e
    
    async def _score_land_suitability(self, land_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate land suitability score
        """
        suitable_areas = land_analysis.get("suitable_areas", [])
        constraints = land_analysis.get("constraints", [])
        
        # Base score
        base_score = 50
        
        # Adjust score based on suitable areas
        if suitable_areas:
            max_suitability = max(area.get("suitability_score", 0) for area in suitable_areas)
            area_score = max_suitability * 30  # max 30 points
        else:
            area_score = 0
        
        # Deduct points for constraints
        constraint_penalty = len(constraints) * 5
        
        # Calculate final score
        final_score = base_score + area_score - constraint_penalty
        final_score = max(0, min(100, final_score))
        
        return {
            "score": final_score,
            "details": {
                "base_score": base_score,
                "area_score": area_score,
                "constraint_penalty": constraint_penalty,
                "suitable_areas_count": len(suitable_areas),
                "constraints_count": len(constraints)
            },
            "level": await self._get_score_level(final_score)
        }
    
    async def _score_energy_resources(self, energy_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate energy resources score
        """
        renewable_potential = energy_assessment.get("renewable_potential", {})
        storage_assessment = energy_assessment.get("storage_assessment", {})
        
        # Base score
        base_score = 40
        
        # Renewable energy potential score
        total_renewable = renewable_potential.get("total_renewable_potential", {})
        annual_generation = total_renewable.get("annual_generation_mwh", 0)
        
        if annual_generation > 100000:  # >100 GWh
            renewable_score = 30
        elif annual_generation > 50000:  # >50 GWh
            renewable_score = 25
        elif annual_generation > 20000:  # >20 GWh
            renewable_score = 20
        else:
            renewable_score = 10
        
        # Storage coverage score
        renewable_coverage = storage_assessment.get("renewable_coverage", 0)
        if renewable_coverage > 0.8:
            storage_score = 20
        elif renewable_coverage > 0.5:
            storage_score = 15
        elif renewable_coverage > 0.3:
            storage_score = 10
        else:
            storage_score = 5
        
        # Calculate final score
        final_score = base_score + renewable_score + storage_score
        final_score = max(0, min(100, final_score))
        
        return {
            "score": final_score,
            "details": {
                "base_score": base_score,
                "renewable_score": renewable_score,
                "storage_score": storage_score,
                "annual_generation_mwh": annual_generation,
                "renewable_coverage": renewable_coverage
            },
            "level": await self._get_score_level(final_score)
        }
    
    async def _score_grid_capacity(self, grid_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate grid capacity score
        """
        available_capacity = grid_assessment.get("available_capacity", 0)
        grid_stability = grid_assessment.get("grid_stability", "unknown")
        
        # Base score
        base_score = 50
        
        # Score based on available capacity
        if available_capacity > 200:
            capacity_score = 30
        elif available_capacity > 100:
            capacity_score = 25
        elif available_capacity > 50:
            capacity_score = 20
        else:
            capacity_score = 10
        
        # Score based on grid stability
        stability_scores = {
            "sufficient": 20,
            "good": 15,
            "tight": 5,
            "insufficient": 0
        }
        stability_score = stability_scores.get(grid_stability, 10)
        
        # Calculate final score
        final_score = base_score + capacity_score + stability_score
        final_score = max(0, min(100, final_score))
        
        return {
            "score": final_score,
            "details": {
                "base_score": base_score,
                "capacity_score": capacity_score,
                "stability_score": stability_score,
                "available_capacity_mw": available_capacity,
                "grid_stability": grid_stability
            },
            "level": await self._get_score_level(final_score)
        }
    
    async def _score_economic_feasibility(self, land_analysis: Dict[str, Any], 
                                        energy_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate economic feasibility score
        """
        # Base score
        base_score = 60
        
        # Land cost score (based on land type)
        land_use_dist = land_analysis.get("land_use_distribution", {})
        bare_land_ratio = land_use_dist.get("Bare / sparse vegetation", 0)
        
        if bare_land_ratio > 0.5:
            land_cost_score = 20  # Bare land has low cost
        elif bare_land_ratio > 0.3:
            land_cost_score = 15
        else:
            land_cost_score = 5
        
        # Energy cost score
        renewable_coverage = energy_assessment.get("storage_assessment", {}).get("renewable_coverage", 0)
        if renewable_coverage > 0.7:
            energy_cost_score = 20  # High renewable ratio means lower cost
        elif renewable_coverage > 0.4:
            energy_cost_score = 15
        else:
            energy_cost_score = 5
        
        # Calculate final score
        final_score = base_score + land_cost_score + energy_cost_score
        final_score = max(0, min(100, final_score))
        
        return {
            "score": final_score,
            "details": {
                "base_score": base_score,
                "land_cost_score": land_cost_score,
                "energy_cost_score": energy_cost_score,
                "bare_land_ratio": bare_land_ratio,
                "renewable_coverage": renewable_coverage
            },
            "level": await self._get_score_level(final_score)
        }
    
    async def _score_environmental_impact(self, land_analysis: Dict[str, Any], 
                                        energy_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate environmental impact score
        """
        # Base score
        base_score = 70
        
        # Land use impact score
        land_use_dist = land_analysis.get("land_use_distribution", {})
        vegetation_ratio = (
            land_use_dist.get("Tree cover", 0) +
            land_use_dist.get("Shrubland", 0) +
            land_use_dist.get("Grassland", 0)
        )
        
        if vegetation_ratio > 0.4:
            land_impact_score = -10  # High vegetation means greater environmental impact
        elif vegetation_ratio > 0.2:
            land_impact_score = 0
        else:
            land_impact_score = 10  # Low vegetation means smaller environmental impact
        
        # Renewable energy environmental impact score
        renewable_coverage = energy_assessment.get("storage_assessment", {}).get("renewable_coverage", 0)
        if renewable_coverage > 0.6:
            renewable_impact_score = 20  # High renewable ratio is environmentally friendly
        elif renewable_coverage > 0.3:
            renewable_impact_score = 10
        else:
            renewable_impact_score = 0
        
        # Calculate final score
        final_score = base_score + land_impact_score + renewable_impact_score
        final_score = max(0, min(100, final_score))
        
        return {
            "score": final_score,
            "details": {
                "base_score": base_score,
                "land_impact_score": land_impact_score,
                "renewable_impact_score": renewable_impact_score,
                "vegetation_ratio": vegetation_ratio,
                "renewable_coverage": renewable_coverage
            },
            "level": await self._get_score_level(final_score)
        }
    
    async def _calculate_overall_score(self, scores: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate overall score
        """
        weighted_sum = 0
        total_weight = 0
        
        for criterion, weight in self.decision_weights.items():
            if criterion in scores:
                score_value = scores[criterion]["score"]
                weighted_sum += score_value * weight
                total_weight += weight
        
        overall_score = weighted_sum / total_weight if total_weight > 0 else 0
        
        return {
            "score": overall_score,
            "level": await self._get_score_level(overall_score),
            "weights": self.decision_weights,
            "calculation_method": "Weighted average"
        }
    
    async def _generate_decision_recommendations(self, overall_score: Dict[str, Any],
                                            land_score: Dict[str, Any],
                                            energy_score: Dict[str, Any],
                                            grid_score: Dict[str, Any],
                                            economic_score: Dict[str, Any],
                                            environmental_score: Dict[str, Any]) -> List[str]:
        """
        Generate decision recommendations
        """
        recommendations = []
        overall_level = overall_score["level"]
        
        # Recommendations based on overall score
        if overall_level == "excellent":
            recommendations.append("This location is highly suitable for a data center — prioritize it")
        elif overall_level == "good":
            recommendations.append("This location is suitable for a data center — proceed with detailed planning")
        elif overall_level == "fair":
            recommendations.append("This location is marginally suitable for a data center — some issues need resolving")
        elif overall_level == "poor":
            recommendations.append("Building a data center here presents difficulties — careful evaluation required")
        else:
            recommendations.append("This location is not suitable for a data center — consider alternative sites")
        
        # Specific recommendations based on individual scores
        if land_score["score"] < 60:
            recommendations.append("Low land suitability — consider finding more appropriate land")
        
        if energy_score["score"] < 60:
            recommendations.append("Limited energy resources — consider diversified energy supply options")
        
        if grid_score["score"] < 60:
            recommendations.append("Insufficient grid capacity — consider building storage systems or applying for grid expansion")
        
        if economic_score["score"] < 60:
            recommendations.append("Low economic feasibility — consider optimizing cost structure")
        
        if environmental_score["score"] < 60:
            recommendations.append("High environmental impact — consider adopting a greener construction approach")
        
        return recommendations
    
    async def _assess_risks(self, land_analysis: Dict[str, Any], 
                          energy_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Risk assessment
        """
        risks = []
        risk_level = "low"
        
        # Land risk
        constraints = land_analysis.get("constraints", [])
        if len(constraints) > 2:
            risks.append("Multiple land constraints — construction risk is elevated")
            risk_level = "medium"
        
        # Energy risk
        renewable_coverage = energy_assessment.get("storage_assessment", {}).get("renewable_coverage", 0)
        if renewable_coverage < 0.3:
            risks.append("Low renewable energy ratio — energy supply risk is elevated")
            risk_level = "medium"
        
        # Grid risk
        grid_stability = energy_assessment.get("grid_assessment", {}).get("grid_stability", "good")
        if grid_stability in ["tight", "insufficient"]:
            risks.append("Poor grid stability — power supply risk is high")
            risk_level = "high"
        
        return {
            "risk_level": risk_level,
            "risks": risks,
            "mitigation_measures": await self._get_risk_mitigation_measures(risks)
        }
    
    async def _get_risk_mitigation_measures(self, risks: List[str]) -> List[str]:
        """
        Get risk mitigation measures
        """
        measures = []
        
        for risk in risks:
            if "land constraints" in risk:
                measures.append("Conduct detailed geological surveys and environmental assessments")
            elif "energy supply" in risk:
                measures.append("Build diversified energy supply systems and storage facilities")
            elif "grid" in risk:
                measures.append("Build energy storage systems and backup power supplies")
        
        return measures
    
    async def _get_score_level(self, score: float) -> str:
        """
        Get score level
        """
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 60:
            return "fair"
        elif score >= 45:
            return "poor"
        else:
            return "very_poor"
    
    async def _get_decision_level(self, overall_score: Dict[str, Any]) -> str:
        """
        Get decision level
        """
        score = overall_score["score"]
        if score >= 80:
            return "Strongly recommended"
        elif score >= 70:
            return "Recommended"
        elif score >= 60:
            return "Worth considering"
        elif score >= 50:
            return "Not recommended"
        else:
            return "Strongly not recommended"