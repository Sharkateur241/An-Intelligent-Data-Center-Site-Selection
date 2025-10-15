"""
PROMETHEE-MCGP决策分析服务 - 基于参考文献2的多准则决策方法
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import math
from datetime import datetime

@dataclass
class CriteriaWeight:
    """准则权重"""
    name: str
    weight: float
    is_benefit: bool  # True为效益型，False为成本型

@dataclass
class AlternativeScore:
    """方案评分"""
    name: str
    scores: Dict[str, float]
    net_flow: float
    ranking: int

class PROMETHEEMCGP:
    """PROMETHEE-MCGP决策分析类"""
    
    def __init__(self):
        """初始化PROMETHEE-MCGP分析器"""
        # 根据参考文献2定义的指标体系
        self.economic_criteria = {
            "internet_penetration": {"name": "互联网普及率(%)", "weight": 0.25, "is_benefit": True},
            "transportation_density": {"name": "交通密度(km/km²)", "weight": 0.20, "is_benefit": True},
            "disaster_losses": {"name": "自然灾害直接经济损失(亿元)", "weight": 0.15, "is_benefit": False},
            "water_consumption": {"name": "万元GDP用水量(m³)", "weight": 0.20, "is_benefit": False},
            "disposable_income": {"name": "城镇居民人均可支配收入(元)", "weight": 0.20, "is_benefit": True}
        }
        
        self.environmental_criteria = {
            "annual_temperature": {"name": "年平均温度(℃)", "weight": 0.30, "is_benefit": False, "ideal": 15.0},
            "hydropower_resources": {"name": "水力资源(亿kWh/km²)", "weight": 0.25, "is_benefit": True},
            "wind_resources": {"name": "风能资源(亿kWh/km²)", "weight": 0.25, "is_benefit": True},
            "air_quality_rate": {"name": "空气质量优良率(%)", "weight": 0.20, "is_benefit": True}
        }
        
        self.energy_criteria = {
            "solar_irradiance": {"name": "太阳能年辐射量(kWh/m²)", "weight": 0.40, "is_benefit": True},
            "wind_speed": {"name": "平均风速(m/s)", "weight": 0.30, "is_benefit": True},
            "renewable_coverage": {"name": "可再生能源覆盖率(%)", "weight": 0.30, "is_benefit": True}
        }
    
    async def analyze_data_center_site_selection(self, lat: float, lon: float, 
                                               city_name: str = None) -> Dict[str, Any]:
        """
        数据中心选址PROMETHEE-MCGP分析
        
        Args:
            lat: 纬度
            lon: 经度
            city_name: 城市名称
            
        Returns:
            选址分析结果
        """
        try:
            # 1. 获取基础数据
            economic_data = await self._get_economic_data(lat, lon, city_name)
            environmental_data = await self._get_environmental_data(lat, lon, city_name)
            energy_data = await self._get_energy_data(lat, lon, city_name)
            
            # 2. 第一阶段：PROMETHEE分析经济因素
            economic_ranking = await self._promethee_analysis(
                economic_data, self.economic_criteria, "经济因素"
            )
            
            # 3. 第二阶段：MCGP综合分析
            mcgp_result = await self._mcgp_analysis(
                economic_ranking, environmental_data, energy_data
            )
            
            # 4. 生成综合评分和推荐
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
                "methodology": "PROMETHEE-MCGP集成方法"
            }
            
        except Exception as e:
            print(f"PROMETHEE-MCGP分析失败: {e}")
            return {
                "error": str(e),
                "location": {"latitude": lat, "longitude": lon, "city": city_name}
            }
    
    async def _get_economic_data(self, lat: float, lon: float, city_name: str) -> Dict[str, float]:
        """获取经济因素数据"""
        # 基于地理位置和城市特征的经济数据
        city_data = {
            "北京": {"internet_penetration": 85.0, "transportation_density": 1.2, 
                    "disaster_losses": 0.5, "water_consumption": 45.0, "disposable_income": 75000},
            "上海": {"internet_penetration": 88.0, "transportation_density": 1.5, 
                    "disaster_losses": 0.3, "water_consumption": 40.0, "disposable_income": 78000},
            "深圳": {"internet_penetration": 92.0, "transportation_density": 1.8, 
                    "disaster_losses": 0.2, "water_consumption": 35.0, "disposable_income": 82000},
            "杭州": {"internet_penetration": 87.0, "transportation_density": 1.3, 
                    "disaster_losses": 0.4, "water_consumption": 42.0, "disposable_income": 76000},
            "中卫": {"internet_penetration": 65.0, "transportation_density": 0.8, 
                    "disaster_losses": 0.1, "water_consumption": 25.0, "disposable_income": 45000},
            "贵阳": {"internet_penetration": 70.0, "transportation_density": 1.0, 
                    "disaster_losses": 0.2, "water_consumption": 30.0, "disposable_income": 50000},
            "广州": {"internet_penetration": 89.0, "transportation_density": 1.6, 
                    "disaster_losses": 0.3, "water_consumption": 38.0, "disposable_income": 80000},
            "兰州": {"internet_penetration": 68.0, "transportation_density": 0.9, 
                    "disaster_losses": 0.2, "water_consumption": 28.0, "disposable_income": 48000}
        }
        
        if city_name and city_name in city_data:
            return city_data[city_name]
        
        # 基于地理位置的估算
        base_data = {
            "internet_penetration": 70.0 + (90 - abs(lat)) * 0.5,
            "transportation_density": 0.8 + (90 - abs(lat)) * 0.02,
            "disaster_losses": 0.3 + abs(lat - 35) * 0.01,
            "water_consumption": 40.0 + abs(lat - 35) * 0.5,
            "disposable_income": 50000 + (90 - abs(lat)) * 200
        }
        
        return base_data
    
    async def _get_environmental_data(self, lat: float, lon: float, city_name: str) -> Dict[str, float]:
        """获取环境因素数据"""
        # 基于地理位置的估算
        annual_temp = 25.0 - (abs(lat) - 30) * 0.5  # 纬度越高温度越低
        
        # 水资源丰富度
        if 20 <= lat <= 35 and 110 <= lon <= 125:  # 华南
            hydropower = 0.8
        elif 25 <= lat <= 40 and 100 <= lon <= 110:  # 西南
            hydropower = 0.9
        elif 30 <= lat <= 45 and 120 <= lon <= 135:  # 华东
            hydropower = 0.6
        else:
            hydropower = 0.4
        
        # 风能资源
        wind_resources = 0.3 + (90 - abs(lat)) * 0.01
        
        # 空气质量
        if 40 <= lat <= 55 and 80 <= lon <= 100:  # 西北
            air_quality = 0.85
        elif 25 <= lat <= 40 and 100 <= lon <= 110:  # 西南
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
        """获取能源因素数据"""
        # 太阳能辐射量
        solar_irradiance = 1000 + (90 - abs(lat)) * 20
        if lon > 100:
            solar_irradiance += 200
        elif lon < 110:
            solar_irradiance -= 100
        
        # 平均风速
        wind_speed = 3.0 + (90 - abs(lat)) * 0.1
        if lon > 100:
            wind_speed += 1.0
        elif lon < 110:
            wind_speed -= 0.5
        
        # 可再生能源覆盖率
        renewable_coverage = min(solar_irradiance / 2000 + wind_speed / 6.0, 1.0)
        
        return {
            "solar_irradiance": solar_irradiance,
            "wind_speed": wind_speed,
            "renewable_coverage": renewable_coverage * 100
        }
    
    async def _promethee_analysis(self, data: Dict[str, float], 
                                criteria: Dict[str, Dict], 
                                category: str) -> Dict[str, Any]:
        """PROMETHEE分析"""
        try:
            # 数据标准化
            normalized_data = self._normalize_data(data, criteria)
            
            # 计算偏好函数
            preference_matrix = self._calculate_preference_matrix(normalized_data, criteria)
            
            # 计算流值
            leaving_flow, entering_flow, net_flow = self._calculate_flows(preference_matrix)
            
            # 生成排名
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
            print(f"PROMETHEE分析失败: {e}")
            return {"error": str(e), "category": category}
    
    def _normalize_data(self, data: Dict[str, float], 
                       criteria: Dict[str, Dict]) -> Dict[str, float]:
        """数据标准化"""
        normalized = {}
        
        for criterion, value in data.items():
            if criterion in criteria:
                # 简单的线性标准化到[0,1]
                if criteria[criterion]["is_benefit"]:
                    # 效益型：值越大越好
                    normalized[criterion] = min(value / 100, 1.0)
                else:
                    # 成本型：值越小越好
                    normalized[criterion] = max(1.0 - value / 100, 0.0)
        
        return normalized
    
    def _calculate_preference_matrix(self, data: Dict[str, float], 
                                   criteria: Dict[str, Dict]) -> np.ndarray:
        """计算偏好矩阵"""
        n_criteria = len(criteria)
        criteria_list = list(criteria.keys())
        
        # 创建偏好矩阵
        preference_matrix = np.zeros((n_criteria, n_criteria))
        
        for i, criterion_i in enumerate(criteria_list):
            for j, criterion_j in enumerate(criteria_list):
                if i != j:
                    # 使用高斯偏好函数
                    diff = data[criterion_i] - data[criterion_j]
                    weight = criteria[criterion_i]["weight"]
                    
                    if diff > 0:
                        # 高斯函数
                        sigma = 0.1  # 标准差
                        preference = 1 - math.exp(-(diff**2) / (2 * sigma**2))
                        preference_matrix[i, j] = weight * preference
                    else:
                        preference_matrix[i, j] = 0
        
        return preference_matrix
    
    def _calculate_flows(self, preference_matrix: np.ndarray) -> Tuple[float, float, float]:
        """计算流值"""
        n = preference_matrix.shape[0]
        
        # 计算流出流
        leaving_flow = np.sum(preference_matrix, axis=1) / (n - 1)
        
        # 计算流入流
        entering_flow = np.sum(preference_matrix, axis=0) / (n - 1)
        
        # 计算净流
        net_flow = leaving_flow - entering_flow
        
        return float(leaving_flow[0]), float(entering_flow[0]), float(net_flow[0])
    
    def _generate_ranking(self, net_flow: float) -> Dict[str, Any]:
        """生成排名"""
        if net_flow > 0.1:
            level = "优秀"
            score = min(net_flow * 10, 100)
        elif net_flow > 0:
            level = "良好"
            score = 70 + net_flow * 30
        elif net_flow > -0.1:
            level = "一般"
            score = 50 + (net_flow + 0.1) * 200
        else:
            level = "较差"
            score = max(net_flow * 50, 0)
        
        return {
            "level": level,
            "score": round(score, 2),
            "net_flow": round(net_flow, 4)
        }
    
    async def _mcgp_analysis(self, economic_ranking: Dict[str, Any], 
                           environmental_data: Dict[str, float],
                           energy_data: Dict[str, float]) -> Dict[str, Any]:
        """MCGP分析"""
        try:
            # 构建目标函数
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
            
            # 计算权重
            weights = {
                "economic": 0.3,
                "environmental": 0.4,
                "energy": 0.3
            }
            
            # 综合评分
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
            print(f"MCGP分析失败: {e}")
            return {"error": str(e)}
    
    def _calculate_temperature_suitability(self, temperature: float) -> float:
        """计算温度适宜性"""
        ideal_temp = 15.0  # 理想温度
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
        """生成最终排名"""
        try:
            economic_score = economic_ranking.get("score", 50)
            comprehensive_score = mcgp_result.get("comprehensive_score", 50)
            
            # 综合评分
            final_score = (economic_score * 0.4 + comprehensive_score * 0.6)
            
            # 确定等级
            if final_score >= 85:
                level = "优秀"
                recommendation = "强烈推荐"
            elif final_score >= 70:
                level = "良好"
                recommendation = "推荐"
            elif final_score >= 55:
                level = "一般"
                recommendation = "可考虑"
            else:
                level = "较差"
                recommendation = "不推荐"
            
            return {
                "final_score": round(final_score, 2),
                "level": level,
                "recommendation": recommendation,
                "economic_contribution": round(economic_score * 0.4, 2),
                "comprehensive_contribution": round(comprehensive_score * 0.6, 2)
            }
            
        except Exception as e:
            print(f"最终排名生成失败: {e}")
            return {"error": str(e)}
    
    def _generate_recommendation(self, final_ranking: Dict[str, Any]) -> Dict[str, Any]:
        """生成推荐建议"""
        try:
            level = final_ranking.get("level", "一般")
            score = final_ranking.get("final_score", 50)
            
            recommendations = []
            
            if level == "优秀":
                recommendations.extend([
                    "该地区非常适合建设数据中心",
                    "建议优先考虑此位置",
                    "可以建设大型数据中心园区"
                ])
            elif level == "良好":
                recommendations.extend([
                    "该地区适合建设数据中心",
                    "建议进行详细可行性研究",
                    "可以考虑建设中型数据中心"
                ])
            elif level == "一般":
                recommendations.extend([
                    "该地区可以建设数据中心，但需要优化",
                    "建议改善基础设施条件",
                    "适合建设小型数据中心"
                ])
            else:
                recommendations.extend([
                    "该地区不适合建设数据中心",
                    "建议寻找其他位置",
                    "如必须建设，需要大量投资改善条件"
                ])
            
            return {
                "overall_assessment": level,
                "score": score,
                "recommendations": recommendations,
                "next_steps": self._get_next_steps(level)
            }
            
        except Exception as e:
            print(f"推荐建议生成失败: {e}")
            return {"error": str(e)}
    
    def _get_next_steps(self, level: str) -> List[str]:
        """获取下一步建议"""
        if level == "优秀":
            return [
                "进行详细的环境影响评估",
                "制定具体的建设方案",
                "申请相关许可证和审批"
            ]
        elif level == "良好":
            return [
                "进行更详细的技术可行性研究",
                "评估基础设施改善需求",
                "制定风险缓解计划"
            ]
        elif level == "一般":
            return [
                "评估改善成本与收益",
                "寻找替代方案",
                "考虑分阶段建设"
            ]
        else:
            return [
                "重新评估选址标准",
                "寻找其他候选位置",
                "考虑其他建设模式"
            ]
    
    async def analyze_data_center_site_selection_with_ai(self, latitude: float, longitude: float, city_name: str, 
                                                       ai_multimodal: Dict[str, Any], ai_energy: Dict[str, Any],
                                                       ai_power_supply: Dict[str, Any], ai_energy_storage: Dict[str, Any],
                                                       ai_decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用AI分析结果进行PROMETHEE-MCGP分析
        
        Args:
            latitude: 纬度
            longitude: 经度
            city_name: 城市名称
            ai_multimodal: 多模态AI分析结果
            ai_energy: 能源AI分析结果
            ai_power_supply: 供电AI分析结果
            ai_energy_storage: 储能AI分析结果
            ai_decision: 决策AI分析结果
            
        Returns:
            综合PROMETHEE-MCGP分析结果
        """
        try:
            # 从AI分析结果中提取评分
            scores = self._extract_scores_from_ai_results(
                ai_multimodal, ai_energy, ai_power_supply, ai_energy_storage, ai_decision
            )
            
            # 使用提取的评分进行PROMETHEE-MCGP分析
            analysis_result = self._perform_promethee_mcgp_analysis(scores)
            
            # 添加AI分析结果的引用
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
                "error": f"AI集成PROMETHEE-MCGP分析失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _extract_scores_from_ai_results(self, ai_multimodal: Dict[str, Any], ai_energy: Dict[str, Any],
                                      ai_power_supply: Dict[str, Any], ai_energy_storage: Dict[str, Any],
                                      ai_decision: Dict[str, Any]) -> Dict[str, float]:
        """从AI分析结果中提取评分"""
        scores = {}
        
        # 从多模态分析中提取8个核心维度的评分
        if ai_multimodal.get("success") and "analysis" in ai_multimodal:
            try:
                analysis = ai_multimodal["analysis"]
                if isinstance(analysis, dict):
                    # 提取8个核心维度的评分
                    for key in ["energy_supply", "network_connectivity", "geographic_environment", 
                              "policy_regulations", "infrastructure", "human_resources", 
                              "socio_economic", "business_ecosystem"]:
                        if key in analysis and "score" in analysis[key]:
                            scores[f"ai_{key}"] = analysis[key]["score"]
            except Exception as e:
                print(f"⚠️ 提取多模态分析评分失败: {e}")
        
        # 从其他AI分析中提取评分
        for ai_result, prefix in [(ai_energy, "energy"), (ai_power_supply, "power_supply"), 
                                (ai_energy_storage, "energy_storage"), (ai_decision, "decision")]:
            if ai_result.get("success") and "analysis" in ai_result:
                try:
                    analysis = ai_result["analysis"]
                    if isinstance(analysis, dict):
                        # 提取总体评分
                        if "overall_score" in analysis:
                            scores[f"ai_{prefix}_overall"] = analysis["overall_score"]
                        # 提取各维度评分
                        for key, value in analysis.items():
                            if isinstance(value, dict) and "score" in value:
                                scores[f"ai_{prefix}_{key}"] = value["score"]
                except Exception as e:
                    print(f"⚠️ 提取{prefix}分析评分失败: {e}")
        
        return scores
    
    def _perform_promethee_mcgp_analysis(self, scores: Dict[str, float]) -> Dict[str, Any]:
        """执行PROMETHEE-MCGP分析"""
        try:
            # 构建综合评分矩阵
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
            
            # 计算加权总分
            total_score = 0
            weight_sum = 0
            for criterion, weight in criteria_weights.items():
                if criterion in scores:
                    total_score += scores[criterion] * weight
                    weight_sum += weight
            
            # 标准化评分
            normalized_score = total_score / weight_sum if weight_sum > 0 else 0
            
            # 生成分析结果
            return {
                "success": True,
                "analysis_type": "AI集成PROMETHEE-MCGP分析",
                "overall_score": round(normalized_score, 2),
                "detailed_scores": scores,
                "criteria_weights": criteria_weights,
                "recommendations": self._generate_ai_integrated_recommendations(scores, normalized_score),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"PROMETHEE-MCGP分析失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _generate_ai_integrated_recommendations(self, scores: Dict[str, float], overall_score: float) -> str:
        """生成基于AI分析结果的综合建议"""
        recommendations = []
        
        # 基于总体评分给出建议
        if overall_score >= 8:
            recommendations.append("该地区非常适合建设数据中心，建议优先考虑")
        elif overall_score >= 6:
            recommendations.append("该地区适合建设数据中心，但需要关注某些方面")
        elif overall_score >= 4:
            recommendations.append("该地区建设数据中心存在一定风险，需要谨慎评估")
        else:
            recommendations.append("该地区不适合建设数据中心，建议重新选址")
        
        # 基于各维度评分给出具体建议
        for criterion, score in scores.items():
            if score < 5:
                criterion_name = criterion.replace("ai_", "").replace("_", " ")
                recommendations.append(f"需要改善{criterion_name}方面（当前评分：{score}）")
        
        return "；".join(recommendations)