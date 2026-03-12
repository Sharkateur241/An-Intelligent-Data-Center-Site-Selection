"""
决策分析服务 - 基于AI的智能决策系统
"""

import json
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import math

class DecisionAnalysisService:
    """决策分析服务类"""
    
    def __init__(self):
        """初始化决策分析服务"""
        # 决策权重配置
        self.decision_weights = {
            "land_suitability": 0.25,      # 土地适宜性
            "energy_resources": 0.30,      # 能源资源
            "grid_capacity": 0.20,         # 电网容量
            "economic_feasibility": 0.15,  # 经济可行性
            "environmental_impact": 0.10   # 环境影响
        }
        
        # 评分标准
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
        综合分析位置适宜性
        
        Args:
            land_analysis: 土地利用分析结果
            energy_assessment: 能源资源评估结果
            
        Returns:
            综合决策分析结果
        """
        try:
            # 1. 土地适宜性评分
            land_score = await self._score_land_suitability(land_analysis)
            
            # 2. 能源资源评分
            energy_score = await self._score_energy_resources(energy_assessment)
            
            # 3. 电网容量评分
            grid_score = await self._score_grid_capacity(energy_assessment.get("grid_assessment", {}))
            
            # 4. 经济可行性评分
            economic_score = await self._score_economic_feasibility(land_analysis, energy_assessment)
            
            # 5. 环境影响评分
            environmental_score = await self._score_environmental_impact(land_analysis, energy_assessment)
            
            # 6. 计算综合评分
            overall_score = await self._calculate_overall_score({
                "land_suitability": land_score,
                "energy_resources": energy_score,
                "grid_capacity": grid_score,
                "economic_feasibility": economic_score,
                "environmental_impact": environmental_score
            })
            
            # 7. 生成决策建议
            recommendations = await self._generate_decision_recommendations(
                overall_score, land_score, energy_score, grid_score, economic_score, environmental_score
            )
            
            # 8. 风险评估
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
            print(f"决策分析失败: {e}")
            raise e
    
    async def _score_land_suitability(self, land_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        评估土地适宜性评分
        """
        suitable_areas = land_analysis.get("suitable_areas", [])
        constraints = land_analysis.get("constraints", [])
        
        # 基础评分
        base_score = 50
        
        # 根据适宜区域调整评分
        if suitable_areas:
            max_suitability = max(area.get("suitability_score", 0) for area in suitable_areas)
            area_score = max_suitability * 30  # 最高30分
        else:
            area_score = 0
        
        # 根据约束条件扣分
        constraint_penalty = len(constraints) * 5
        
        # 计算最终评分
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
        评估能源资源评分
        """
        renewable_potential = energy_assessment.get("renewable_potential", {})
        storage_assessment = energy_assessment.get("storage_assessment", {})
        
        # 基础评分
        base_score = 40
        
        # 可再生能源潜力评分
        total_renewable = renewable_potential.get("total_renewable_potential", {})
        annual_generation = total_renewable.get("annual_generation_mwh", 0)
        
        if annual_generation > 100000:  # >100GWh
            renewable_score = 30
        elif annual_generation > 50000:  # >50GWh
            renewable_score = 25
        elif annual_generation > 20000:  # >20GWh
            renewable_score = 20
        else:
            renewable_score = 10
        
        # 储能覆盖评分
        renewable_coverage = storage_assessment.get("renewable_coverage", 0)
        if renewable_coverage > 0.8:
            storage_score = 20
        elif renewable_coverage > 0.5:
            storage_score = 15
        elif renewable_coverage > 0.3:
            storage_score = 10
        else:
            storage_score = 5
        
        # 计算最终评分
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
        评估电网容量评分
        """
        available_capacity = grid_assessment.get("available_capacity", 0)
        grid_stability = grid_assessment.get("grid_stability", "未知")
        
        # 基础评分
        base_score = 50
        
        # 根据可用容量评分
        if available_capacity > 200:
            capacity_score = 30
        elif available_capacity > 100:
            capacity_score = 25
        elif available_capacity > 50:
            capacity_score = 20
        else:
            capacity_score = 10
        
        # 根据电网稳定性评分
        stability_scores = {
            "充足": 20,
            "良好": 15,
            "紧张": 5,
            "不足": 0
        }
        stability_score = stability_scores.get(grid_stability, 10)
        
        # 计算最终评分
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
        评估经济可行性评分
        """
        # 基础评分
        base_score = 60
        
        # 土地成本评分（基于土地类型）
        land_use_dist = land_analysis.get("land_use_distribution", {})
        bare_land_ratio = land_use_dist.get("裸地", 0)
        
        if bare_land_ratio > 0.5:
            land_cost_score = 20  # 裸地成本低
        elif bare_land_ratio > 0.3:
            land_cost_score = 15
        else:
            land_cost_score = 5
        
        # 能源成本评分
        renewable_coverage = energy_assessment.get("storage_assessment", {}).get("renewable_coverage", 0)
        if renewable_coverage > 0.7:
            energy_cost_score = 20  # 可再生能源比例高，成本低
        elif renewable_coverage > 0.4:
            energy_cost_score = 15
        else:
            energy_cost_score = 5
        
        # 计算最终评分
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
        评估环境影响评分
        """
        # 基础评分
        base_score = 70
        
        # 土地利用影响评分
        land_use_dist = land_analysis.get("land_use_distribution", {})
        vegetation_ratio = land_use_dist.get("植被", 0)
        
        if vegetation_ratio > 0.4:
            land_impact_score = -10  # 植被多，环境影响大
        elif vegetation_ratio > 0.2:
            land_impact_score = 0
        else:
            land_impact_score = 10  # 植被少，环境影响小
        
        # 可再生能源环境影响评分
        renewable_coverage = energy_assessment.get("storage_assessment", {}).get("renewable_coverage", 0)
        if renewable_coverage > 0.6:
            renewable_impact_score = 20  # 可再生能源比例高，环境友好
        elif renewable_coverage > 0.3:
            renewable_impact_score = 10
        else:
            renewable_impact_score = 0
        
        # 计算最终评分
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
        计算综合评分
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
            "calculation_method": "加权平均"
        }
    
    async def _generate_decision_recommendations(self, overall_score: Dict[str, Any],
                                            land_score: Dict[str, Any],
                                            energy_score: Dict[str, Any],
                                            grid_score: Dict[str, Any],
                                            economic_score: Dict[str, Any],
                                            environmental_score: Dict[str, Any]) -> List[str]:
        """
        生成决策建议
        """
        recommendations = []
        overall_level = overall_score["level"]
        
        # 基于综合评分的建议
        if overall_level == "优秀":
            recommendations.append("该位置非常适合建设数据中心，建议优先考虑")
        elif overall_level == "良好":
            recommendations.append("该位置适合建设数据中心，建议进行详细规划")
        elif overall_level == "一般":
            recommendations.append("该位置基本适合建设数据中心，需要解决一些问题")
        elif overall_level == "较差":
            recommendations.append("该位置建设数据中心存在一定困难，需要谨慎评估")
        else:
            recommendations.append("该位置不适合建设数据中心，建议寻找其他位置")
        
        # 基于各项评分的具体建议
        if land_score["score"] < 60:
            recommendations.append("土地适宜性较低，建议寻找更合适的土地")
        
        if energy_score["score"] < 60:
            recommendations.append("能源资源有限，建议考虑多种能源供应方案")
        
        if grid_score["score"] < 60:
            recommendations.append("电网容量不足，建议建设储能系统或申请电网增容")
        
        if economic_score["score"] < 60:
            recommendations.append("经济可行性较低，建议优化成本结构")
        
        if environmental_score["score"] < 60:
            recommendations.append("环境影响较大，建议采用更环保的建设方案")
        
        return recommendations
    
    async def _assess_risks(self, land_analysis: Dict[str, Any], 
                          energy_assessment: Dict[str, Any]) -> Dict[str, Any]:
        """
        风险评估
        """
        risks = []
        risk_level = "低"
        
        # 土地风险
        constraints = land_analysis.get("constraints", [])
        if len(constraints) > 2:
            risks.append("土地约束条件较多，建设风险较高")
            risk_level = "中"
        
        # 能源风险
        renewable_coverage = energy_assessment.get("storage_assessment", {}).get("renewable_coverage", 0)
        if renewable_coverage < 0.3:
            risks.append("可再生能源比例较低，能源供应风险较高")
            risk_level = "中"
        
        # 电网风险
        grid_stability = energy_assessment.get("grid_assessment", {}).get("grid_stability", "良好")
        if grid_stability in ["紧张", "不足"]:
            risks.append("电网稳定性较差，供电风险较高")
            risk_level = "高"
        
        return {
            "risk_level": risk_level,
            "risks": risks,
            "mitigation_measures": await self._get_risk_mitigation_measures(risks)
        }
    
    async def _get_risk_mitigation_measures(self, risks: List[str]) -> List[str]:
        """
        获取风险缓解措施
        """
        measures = []
        
        for risk in risks:
            if "土地约束" in risk:
                measures.append("建议进行详细的地质勘测和环境评估")
            elif "能源供应" in risk:
                measures.append("建议建设多种能源供应系统和储能设施")
            elif "电网" in risk:
                measures.append("建议建设储能系统和备用电源")
        
        return measures
    
    async def _get_score_level(self, score: float) -> str:
        """
        获取评分等级
        """
        if score >= 90:
            return "优秀"
        elif score >= 75:
            return "良好"
        elif score >= 60:
            return "一般"
        elif score >= 45:
            return "较差"
        else:
            return "很差"
    
    async def _get_decision_level(self, overall_score: Dict[str, Any]) -> str:
        """
        获取决策等级
        """
        score = overall_score["score"]
        if score >= 80:
            return "强烈推荐"
        elif score >= 70:
            return "推荐"
        elif score >= 60:
            return "可以考虑"
        elif score >= 50:
            return "不推荐"
        else:
            return "强烈不推荐"
    
