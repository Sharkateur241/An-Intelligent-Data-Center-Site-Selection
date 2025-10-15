#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
余热利用分析服务 - 数据中心余热回收利用分析
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from config import config

class HeatUtilizationAnalysisService:
    """余热利用分析服务类"""
    
    def __init__(self):
        """初始化余热利用分析服务"""
        config.setup_proxy()
        
    async def analyze_heat_utilization(self, latitude: float, longitude: float, 
                                     data_center_power: float = 100, 
                                     city_name: str = None) -> Dict[str, Any]:
        """
        分析数据中心余热利用潜力
        
        Args:
            latitude: 纬度
            longitude: 经度
            data_center_power: 数据中心功率（MW）
            city_name: 城市名称
            
        Returns:
            余热利用分析结果
        """
        try:
            # 识别区域类型
            region_type = await self._identify_region_type(latitude, longitude, city_name)
            
            # 计算余热产生量
            heat_generation = await self._calculate_heat_generation(data_center_power)
            
            # 分析余热利用方案
            utilization_schemes = await self._analyze_utilization_schemes(
                region_type, heat_generation, latitude, longitude
            )
            
            # 分析经济效益
            economic_analysis = await self._analyze_economic_benefits(
                utilization_schemes, data_center_power
            )
            
            # 分析环境影响
            environmental_impact = await self._analyze_environmental_impact(
                utilization_schemes, data_center_power
            )
            
            # 生成实施建议
            implementation_recommendations = await self._generate_implementation_recommendations(
                region_type, utilization_schemes, economic_analysis
            )
            
            return {
                "success": True,
                "analysis_type": "余热利用分析",
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
                "error": f"余热利用分析失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _identify_region_type(self, latitude: float, longitude: float, city_name: str) -> str:
        """识别区域类型"""
        try:
            # 基于城市名称识别
            if city_name:
                if "北京" in city_name or "天津" in city_name or "河北" in city_name:
                    return "北方"
                elif "广东" in city_name or "广西" in city_name or "海南" in city_name:
                    return "南方"
                elif "上海" in city_name or "江苏" in city_name or "浙江" in city_name:
                    return "华东"
                elif "四川" in city_name or "重庆" in city_name or "贵州" in city_name:
                    return "西南"
                else:
                    return "其他"
            
            # 基于坐标识别
            if 35.0 <= latitude <= 45.0:
                return "北方"  # 北方地区
            elif 20.0 <= latitude <= 35.0:
                return "南方"  # 南方地区
            else:
                return "其他"
                
        except Exception as e:
            print(f"⚠️ 区域类型识别失败: {e}")
            return "未知"
    
    async def _calculate_heat_generation(self, data_center_power: float) -> Dict[str, Any]:
        """计算余热产生量"""
        try:
            # 数据中心余热产生量计算
            # 假设数据中心PUE为1.5，其中0.5为冷却系统消耗
            # 余热主要来自服务器和冷却系统
            
            total_power = data_center_power  # MW
            pue = 1.5  # 电源使用效率
            it_power = total_power / pue  # IT设备功率
            cooling_power = total_power - it_power  # 冷却系统功率
            
            # 余热产生量（假设80%的IT功率和20%的冷却功率转化为余热）
            heat_from_it = it_power * 0.8  # IT设备余热
            heat_from_cooling = cooling_power * 0.2  # 冷却系统余热
            total_heat = heat_from_it + heat_from_cooling  # 总余热
            
            # 余热温度（假设平均温度为40-60°C）
            heat_temperature = 50  # °C
            
            return {
                "total_heat_mw": round(total_heat, 2),
                "heat_from_it_mw": round(heat_from_it, 2),
                "heat_from_cooling_mw": round(heat_from_cooling, 2),
                "heat_temperature_c": heat_temperature,
                "heat_utilization_potential": "high" if total_heat > 50 else "medium" if total_heat > 20 else "low"
            }
            
        except Exception as e:
            return {"error": f"余热产生量计算失败: {str(e)}"}
    
    async def _analyze_utilization_schemes(self, region_type: str, heat_generation: Dict[str, Any],
                                         latitude: float, longitude: float) -> List[Dict[str, Any]]:
        """分析余热利用方案"""
        try:
            schemes = []
            total_heat = heat_generation.get("total_heat_mw", 0)
            heat_temperature = heat_generation.get("heat_temperature_c", 50)
            
            if region_type == "北方":
                # 北方地区：主要用于供热
                schemes.append({
                    "scheme_name": "区域供热",
                    "description": "将余热用于区域供热系统",
                    "applicable_heat": total_heat * 0.8,  # 80%的余热可用于供热
                    "target_users": "居民、学校、医院等",
                    "implementation_difficulty": "medium",
                    "economic_benefit": "high",
                    "environmental_benefit": "high"
                })
                
                schemes.append({
                    "scheme_name": "工业用热",
                    "description": "将余热用于工业用热",
                    "applicable_heat": total_heat * 0.6,  # 60%的余热可用于工业
                    "target_users": "工厂、制造业等",
                    "implementation_difficulty": "low",
                    "economic_benefit": "medium",
                    "environmental_benefit": "medium"
                })
                
            elif region_type == "南方":
                # 南方地区：主要用于工业用热
                schemes.append({
                    "scheme_name": "工业用热",
                    "description": "将余热用于工业用热",
                    "applicable_heat": total_heat * 0.7,  # 70%的余热可用于工业
                    "target_users": "工厂、制造业等",
                    "implementation_difficulty": "low",
                    "economic_benefit": "high",
                    "environmental_benefit": "high"
                })
                
                schemes.append({
                    "scheme_name": "热水供应",
                    "description": "将余热用于热水供应",
                    "applicable_heat": total_heat * 0.5,  # 50%的余热可用于热水
                    "target_users": "酒店、医院、学校等",
                    "implementation_difficulty": "medium",
                    "economic_benefit": "medium",
                    "environmental_benefit": "medium"
                })
                
            else:
                # 其他地区：通用方案
                schemes.append({
                    "scheme_name": "工业用热",
                    "description": "将余热用于工业用热",
                    "applicable_heat": total_heat * 0.6,
                    "target_users": "工厂、制造业等",
                    "implementation_difficulty": "low",
                    "economic_benefit": "medium",
                    "environmental_benefit": "medium"
                })
            
            # 通用方案：余热发电
            if total_heat > 10:  # 只有余热量足够大时才考虑发电
                schemes.append({
                    "scheme_name": "余热发电",
                    "description": "将余热用于发电",
                    "applicable_heat": total_heat * 0.4,  # 40%的余热可用于发电
                    "target_users": "自用或并网",
                    "implementation_difficulty": "high",
                    "economic_benefit": "high",
                    "environmental_benefit": "high"
                })
            
            return schemes
            
        except Exception as e:
            return [{"error": f"余热利用方案分析失败: {str(e)}"}]
    
    async def _analyze_economic_benefits(self, utilization_schemes: List[Dict[str, Any]], 
                                       data_center_power: float) -> Dict[str, Any]:
        """分析经济效益"""
        try:
            total_investment = 0
            annual_revenue = 0
            payback_period = 0
            
            for scheme in utilization_schemes:
                if "error" in scheme:
                    continue
                    
                # 投资成本估算（万元/MW）
                investment_per_mw = 1000  # 假设每MW余热利用投资1000万元
                scheme_investment = scheme.get("applicable_heat", 0) * investment_per_mw
                total_investment += scheme_investment
                
                # 年收入估算（万元/MW）
                revenue_per_mw = 200  # 假设每MW余热利用年收入200万元
                scheme_revenue = scheme.get("applicable_heat", 0) * revenue_per_mw
                annual_revenue += scheme_revenue
            
            # 投资回收期计算
            if annual_revenue > 0:
                payback_period = total_investment / annual_revenue
            
            return {
                "total_investment_万元": round(total_investment, 2),
                "annual_revenue_万元": round(annual_revenue, 2),
                "payback_period_年": round(payback_period, 2),
                "economic_feasibility": "high" if payback_period < 5 else "medium" if payback_period < 10 else "low"
            }
            
        except Exception as e:
            return {"error": f"经济效益分析失败: {str(e)}"}
    
    async def _analyze_environmental_impact(self, utilization_schemes: List[Dict[str, Any]], 
                                          data_center_power: float) -> Dict[str, Any]:
        """分析环境影响"""
        try:
            co2_reduction = 0
            energy_saving = 0
            
            for scheme in utilization_schemes:
                if "error" in scheme:
                    continue
                    
                # CO2减排量估算（吨/年/MW）
                co2_per_mw = 1000  # 假设每MW余热利用年减排1000吨CO2
                scheme_co2 = scheme.get("applicable_heat", 0) * co2_per_mw
                co2_reduction += scheme_co2
                
                # 节能量估算（MWh/年/MW）
                energy_per_mw = 5000  # 假设每MW余热利用年节能5000MWh
                scheme_energy = scheme.get("applicable_heat", 0) * energy_per_mw
                energy_saving += scheme_energy
            
            return {
                "co2_reduction_吨年": round(co2_reduction, 2),
                "energy_saving_mwh年": round(energy_saving, 2),
                "environmental_benefit": "high" if co2_reduction > 5000 else "medium" if co2_reduction > 1000 else "low"
            }
            
        except Exception as e:
            return {"error": f"环境影响分析失败: {str(e)}"}
    
    async def _generate_implementation_recommendations(self, region_type: str, 
                                                     utilization_schemes: List[Dict[str, Any]],
                                                     economic_analysis: Dict[str, Any]) -> List[str]:
        """生成实施建议"""
        try:
            recommendations = []
            
            # 基于区域类型给出建议
            if region_type == "北方":
                recommendations.append("优先考虑区域供热方案，充分利用余热资源")
                recommendations.append("与当地供热公司合作，建立余热利用网络")
            elif region_type == "南方":
                recommendations.append("优先考虑工业用热方案，寻找合适的工业用户")
                recommendations.append("考虑热水供应方案，服务当地商业用户")
            else:
                recommendations.append("根据当地实际情况选择合适的余热利用方案")
            
            # 基于经济效益给出建议
            if economic_analysis.get("economic_feasibility") == "high":
                recommendations.append("经济效益良好，建议尽快实施")
            elif economic_analysis.get("economic_feasibility") == "medium":
                recommendations.append("经济效益一般，需要进一步优化方案")
            else:
                recommendations.append("经济效益较低，建议重新评估方案")
            
            # 基于余热利用方案给出建议
            for scheme in utilization_schemes:
                if "error" in scheme:
                    continue
                    
                if scheme.get("implementation_difficulty") == "low":
                    recommendations.append(f"建议优先实施{scheme.get('scheme_name')}方案")
                elif scheme.get("implementation_difficulty") == "medium":
                    recommendations.append(f"考虑实施{scheme.get('scheme_name')}方案，需要详细规划")
                else:
                    recommendations.append(f"{scheme.get('scheme_name')}方案实施难度较大，需要充分准备")
            
            return recommendations
            
        except Exception as e:
            return [f"实施建议生成失败: {str(e)}"]
