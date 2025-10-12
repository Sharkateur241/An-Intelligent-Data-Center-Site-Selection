"""
增强版数据中心选址分析服务
基于专业评估维度的全面分析，替代原有AI分析
"""

import os
import asyncio
from typing import Dict, Any, List
from datetime import datetime

class EnhancedDataCenterAnalysisService:
    """增强版数据中心选址分析服务"""
    
    def __init__(self):
        # 设置代理
        os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7897'
        os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7897'
        
        self.analysis_dimensions = {
            "能源供应与成本": {
                "权重": 0.25,
                "子维度": [
                    "电网稳定性", "电价水平", "绿色能源可用性", 
                    "备用电源支持", "能源政策支持"
                ]
            },
            "网络连接性": {
                "权重": 0.20,
                "子维度": [
                    "骨干网络接入", "运营商丰富度", "国际连接质量",
                    "互联网交换中心距离", "网络延迟"
                ]
            },
            "地理与环境条件": {
                "权重": 0.15,
                "子维度": [
                    "自然灾害风险", "气候条件", "地形适宜性",
                    "海拔高度", "环境稳定性"
                ]
            },
            "政策与法规环境": {
                "权重": 0.15,
                "子维度": [
                    "政府支持政策", "数据合规要求", "土地获取便利性",
                    "税收优惠政策", "安全法规合规性"
                ]
            },
            "基础设施与配套": {
                "权重": 0.10,
                "子维度": [
                    "交通运输便利性", "水资源供应", "消防系统",
                    "周边产业配套", "基础设施完善度"
                ]
            },
            "人力资源与人才池": {
                "权重": 0.10,
                "子维度": [
                    "技术人才可用性", "劳动力成本", "培训资源",
                    "人才流动性", "教育水平"
                ]
            },
            "社会经济稳定性": {
                "权重": 0.05,
                "子维度": [
                    "政治稳定性", "经济健康度", "社会安全",
                    "政策连续性", "投资环境"
                ]
            },
            "商业生态与市场临近度": {
                "权重": 0.05,
                "子维度": [
                    "客户距离", "产业集群", "市场竞争",
                    "业务合作机会", "市场发展潜力"
                ]
            }
        }
    
    async def analyze_comprehensive(self, lat: float, lon: float, city_name: str, radius: float = 1000) -> Dict[str, Any]:
        """综合数据中心选址分析 - 替代原有AI分析"""
        print(f"🔍 开始综合数据中心选址分析: {city_name}")
        print("=" * 60)
        
        analysis_result = {
            "success": True,
            "analysis_type": "增强版数据中心选址分析",
            "location": {"latitude": lat, "longitude": lon, "city_name": city_name, "radius": radius},
            "analysis_time": datetime.now().isoformat(),
            "dimensions": {},
            "overall_score": 0,
            "recommendation": "",
            "key_strengths": [],
            "key_risks": [],
            "improvement_suggestions": [],
            "detailed_analysis": ""
        }
        
        total_weighted_score = 0
        total_weight = 0
        
        # 分析每个维度
        for dimension, config in self.analysis_dimensions.items():
            print(f"\n📊 分析维度: {dimension}")
            print(f"   权重: {config['权重']*100}%")
            
            dimension_score = await self._analyze_dimension(dimension, lat, lon, city_name)
            analysis_result["dimensions"][dimension] = dimension_score
            
            # 计算加权分数
            weighted_score = dimension_score["score"] * config["权重"]
            total_weighted_score += weighted_score
            total_weight += config["权重"]
            
            print(f"   ✅ {dimension} 得分: {dimension_score['score']:.1f}/10")
        
        # 计算总体得分
        analysis_result["overall_score"] = total_weighted_score / total_weight if total_weight > 0 else 0
        
        # 生成建议和详细分析
        analysis_result.update(self._generate_recommendations(analysis_result))
        analysis_result["detailed_analysis"] = self._generate_detailed_analysis(analysis_result)
        
        print(f"\n🎯 总体得分: {analysis_result['overall_score']:.1f}/10")
        print(f"📋 建议: {analysis_result['recommendation']}")
        
        return analysis_result
    
    async def _analyze_dimension(self, dimension: str, lat: float, lon: float, city_name: str) -> Dict[str, Any]:
        """分析单个维度"""
        
        if dimension == "能源供应与成本":
            return await self._analyze_energy_supply(lat, lon, city_name)
        elif dimension == "网络连接性":
            return await self._analyze_network_connectivity(lat, lon, city_name)
        elif dimension == "地理与环境条件":
            return await self._analyze_geographic_conditions(lat, lon, city_name)
        elif dimension == "政策与法规环境":
            return await self._analyze_policy_environment(lat, lon, city_name)
        elif dimension == "基础设施与配套":
            return await self._analyze_infrastructure(lat, lon, city_name)
        elif dimension == "人力资源与人才池":
            return await self._analyze_human_resources(lat, lon, city_name)
        elif dimension == "社会经济稳定性":
            return await self._analyze_social_economic_stability(lat, lon, city_name)
        elif dimension == "商业生态与市场临近度":
            return await self._analyze_business_ecology(lat, lon, city_name)
        else:
            return {"score": 5.0, "details": "未实现的分析维度", "factors": []}
    
    async def _analyze_energy_supply(self, lat: float, lon: float, city_name: str) -> Dict[str, Any]:
        """分析能源供应与成本"""
        try:
            from .energy_assessment import EnergyAssessmentService
            
            energy_service = EnergyAssessmentService()
            
            # 获取能源数据
            energy_data = {
                "latitude": lat,
                "longitude": lon,
                "city_name": city_name
            }
            
            # 基础能源评估
            basic_assessment = energy_service.assess_energy_resources(energy_data)
            
            # 计算得分
            score = 5.0  # 基础分
            factors = []
            
            if basic_assessment.get("solar_potential", 0) > 6:
                score += 1.5
                factors.append("太阳能资源丰富")
            elif basic_assessment.get("solar_potential", 0) > 4:
                score += 0.5
                factors.append("太阳能资源一般")
            
            if basic_assessment.get("wind_potential", 0) > 6:
                score += 1.5
                factors.append("风能资源丰富")
            elif basic_assessment.get("wind_potential", 0) > 4:
                score += 0.5
                factors.append("风能资源一般")
            
            if basic_assessment.get("renewable_energy_ratio", 0) > 0.6:
                score += 1.0
                factors.append("可再生能源比例高")
            
            # 基于城市特点调整
            if city_name in ["北京", "上海", "深圳", "杭州"]:
                score += 0.5
                factors.append("一线城市电网稳定")
            
            return {
                "score": min(score, 10.0),
                "details": f"能源供应分析完成，可再生能源比例: {basic_assessment.get('renewable_energy_ratio', 0):.1%}",
                "factors": factors,
                "data": basic_assessment
            }
            
        except Exception as e:
            return {
                "score": 5.0,
                "details": f"能源分析失败: {e}",
                "factors": ["分析失败"],
                "error": str(e)
            }
    
    async def _analyze_network_connectivity(self, lat: float, lon: float, city_name: str) -> Dict[str, Any]:
        """分析网络连接性"""
        # 基于城市特点的网络分析
        network_scores = {
            "北京": 9.5, "上海": 9.5, "深圳": 9.0, "广州": 8.5,
            "杭州": 8.0, "南京": 7.5, "成都": 7.0, "武汉": 7.0,
            "西安": 6.5, "重庆": 6.5
        }
        
        base_score = network_scores.get(city_name, 5.0)
        factors = []
        
        if base_score >= 8.0:
            factors.extend(["国家级网络节点", "多运营商覆盖", "国际连接优秀"])
        elif base_score >= 6.0:
            factors.extend(["区域网络中心", "运营商覆盖良好", "国内连接稳定"])
        else:
            factors.extend(["网络基础设施一般", "需要进一步评估"])
        
        return {
            "score": base_score,
            "details": f"{city_name}网络连接性分析",
            "factors": factors,
            "note": "基于城市网络基础设施水平评估"
        }
    
    async def _analyze_geographic_conditions(self, lat: float, lon: float, city_name: str) -> Dict[str, Any]:
        """分析地理与环境条件"""
        try:
            from .satellite_service import SatelliteService
            
            satellite_service = SatelliteService()
            land_data = await satellite_service.get_satellite_data(lat, lon, 1000)
            
            score = 5.0
            factors = []
            
            # 基于土地利用分析
            if land_data and "land_use_distribution" in land_data:
                land_use = land_data["land_use_distribution"]
                
                # 裸地和建设用地比例
                suitable_land = land_use.get("裸地", 0) + land_use.get("建设用地", 0)
                if suitable_land > 0.3:
                    score += 2.0
                    factors.append("适宜建设用地充足")
                elif suitable_land > 0.2:
                    score += 1.0
                    factors.append("适宜建设用地一般")
                
                # 水体风险
                water_ratio = land_use.get("水体", 0)
                if water_ratio > 0.2:
                    score -= 1.0
                    factors.append("水体较多，需防洪考虑")
            
            # 基于地理位置的风险评估
            if 20 <= lat <= 45 and 100 <= lon <= 125:  # 中国东部
                score += 1.0
                factors.append("地理位置相对安全")
            
            # 气候条件（简化评估）
            if 25 <= lat <= 35:  # 亚热带
                score += 0.5
                factors.append("气候条件适宜")
            
            return {
                "score": min(max(score, 0), 10),
                "details": "地理环境条件分析",
                "factors": factors,
                "data": land_data
            }
            
        except Exception as e:
            return {
                "score": 5.0,
                "details": f"地理分析失败: {e}",
                "factors": ["分析失败"]
            }
    
    async def _analyze_policy_environment(self, lat: float, lon: float, city_name: str) -> Dict[str, Any]:
        """分析政策与法规环境"""
        # 基于城市政策环境评估
        policy_scores = {
            "北京": 8.5, "上海": 9.0, "深圳": 9.5, "杭州": 8.0,
            "南京": 7.5, "成都": 7.0, "武汉": 7.0, "西安": 6.5,
            "重庆": 7.5, "广州": 8.0
        }
        
        base_score = policy_scores.get(city_name, 6.0)
        factors = []
        
        if base_score >= 8.0:
            factors.extend(["政策支持力度大", "数据合规环境良好", "税收优惠丰富"])
        elif base_score >= 6.0:
            factors.extend(["政策环境一般", "需要进一步了解具体政策"])
        else:
            factors.extend(["政策环境需要改善", "建议深入了解"])
        
        return {
            "score": base_score,
            "details": f"{city_name}政策环境分析",
            "factors": factors,
            "note": "基于城市政策支持水平评估"
        }
    
    async def _analyze_infrastructure(self, lat: float, lon: float, city_name: str) -> Dict[str, Any]:
        """分析基础设施与配套"""
        # 基于城市基础设施水平评估
        infra_scores = {
            "北京": 9.0, "上海": 9.5, "深圳": 9.0, "杭州": 8.5,
            "南京": 8.0, "成都": 7.5, "武汉": 7.5, "西安": 7.0,
            "重庆": 7.0, "广州": 8.5
        }
        
        base_score = infra_scores.get(city_name, 6.0)
        factors = []
        
        if base_score >= 8.0:
            factors.extend(["基础设施完善", "交通便利", "配套产业成熟"])
        elif base_score >= 6.0:
            factors.extend(["基础设施一般", "需要评估具体条件"])
        else:
            factors.extend(["基础设施需要改善"])
        
        return {
            "score": base_score,
            "details": f"{city_name}基础设施分析",
            "factors": factors
        }
    
    async def _analyze_human_resources(self, lat: float, lon: float, city_name: str) -> Dict[str, Any]:
        """分析人力资源与人才池"""
        # 基于城市人才资源评估
        talent_scores = {
            "北京": 9.5, "上海": 9.5, "深圳": 9.0, "杭州": 8.5,
            "南京": 8.0, "成都": 7.5, "武汉": 8.0, "西安": 7.5,
            "重庆": 7.0, "广州": 8.0
        }
        
        base_score = talent_scores.get(city_name, 6.0)
        factors = []
        
        if base_score >= 8.0:
            factors.extend(["技术人才丰富", "高校资源充足", "人才流动性好"])
        elif base_score >= 6.0:
            factors.extend(["人才资源一般", "需要吸引外部人才"])
        else:
            factors.extend(["人才资源有限", "需要重点考虑"])
        
        return {
            "score": base_score,
            "details": f"{city_name}人力资源分析",
            "factors": factors
        }
    
    async def _analyze_social_economic_stability(self, lat: float, lon: float, city_name: str) -> Dict[str, Any]:
        """分析社会经济稳定性"""
        # 基于城市稳定性评估
        stability_scores = {
            "北京": 9.0, "上海": 9.0, "深圳": 8.5, "杭州": 8.5,
            "南京": 8.0, "成都": 8.0, "武汉": 7.5, "西安": 7.5,
            "重庆": 7.5, "广州": 8.0
        }
        
        base_score = stability_scores.get(city_name, 7.0)
        factors = []
        
        if base_score >= 8.0:
            factors.extend(["政治稳定", "经济健康", "社会安全"])
        elif base_score >= 6.0:
            factors.extend(["稳定性一般", "需要持续关注"])
        else:
            factors.extend(["稳定性需要改善"])
        
        return {
            "score": base_score,
            "details": f"{city_name}社会经济稳定性分析",
            "factors": factors
        }
    
    async def _analyze_business_ecology(self, lat: float, lon: float, city_name: str) -> Dict[str, Any]:
        """分析商业生态与市场临近度"""
        # 基于城市商业生态评估
        business_scores = {
            "北京": 9.0, "上海": 9.5, "深圳": 9.0, "杭州": 8.5,
            "南京": 7.5, "成都": 7.5, "武汉": 7.0, "西安": 6.5,
            "重庆": 7.0, "广州": 8.0
        }
        
        base_score = business_scores.get(city_name, 6.0)
        factors = []
        
        if base_score >= 8.0:
            factors.extend(["产业集群发达", "客户集中度高", "合作机会多"])
        elif base_score >= 6.0:
            factors.extend(["商业生态一般", "需要培育市场"])
        else:
            factors.extend(["商业生态需要发展"])
        
        return {
            "score": base_score,
            "details": f"{city_name}商业生态分析",
            "factors": factors
        }
    
    def _generate_recommendations(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成建议和总结"""
        overall_score = analysis_result["overall_score"]
        dimensions = analysis_result["dimensions"]
        
        # 找出优势和风险
        strengths = []
        risks = []
        
        for dim_name, dim_data in dimensions.items():
            if dim_data["score"] >= 8.0:
                strengths.append(f"{dim_name}: {dim_data['score']:.1f}分")
            elif dim_data["score"] <= 5.0:
                risks.append(f"{dim_name}: {dim_data['score']:.1f}分")
        
        # 生成总体建议
        if overall_score >= 8.0:
            recommendation = "强烈推荐：该地区非常适合建设数据中心"
        elif overall_score >= 6.0:
            recommendation = "推荐：该地区适合建设数据中心，但需要关注某些方面"
        elif overall_score >= 4.0:
            recommendation = "谨慎考虑：该地区建设数据中心存在一定风险"
        else:
            recommendation = "不推荐：该地区不适合建设数据中心"
        
        # 改进建议
        improvements = []
        for dim_name, dim_data in dimensions.items():
            if dim_data["score"] < 6.0:
                improvements.append(f"改善{dim_name}：{dim_data['details']}")
        
        return {
            "recommendation": recommendation,
            "key_strengths": strengths,
            "key_risks": risks,
            "improvement_suggestions": improvements
        }
    
    def _generate_detailed_analysis(self, analysis_result: Dict[str, Any]) -> str:
        """生成详细分析报告"""
        overall_score = analysis_result["overall_score"]
        dimensions = analysis_result["dimensions"]
        
        report = f"""
# 数据中心选址综合分析报告

## 总体评估
**综合得分：{overall_score:.1f}/10**
**建议：{analysis_result['recommendation']}**

## 各维度详细分析

"""
        
        for dim_name, dim_data in dimensions.items():
            report += f"### {dim_name} ({dim_data['score']:.1f}/10)\n"
            report += f"**分析结果：** {dim_data['details']}\n\n"
            
            if dim_data.get('factors'):
                report += "**关键因素：**\n"
                for factor in dim_data['factors']:
                    report += f"- {factor}\n"
                report += "\n"
        
        if analysis_result['key_strengths']:
            report += "## 主要优势\n"
            for strength in analysis_result['key_strengths']:
                report += f"- {strength}\n"
            report += "\n"
        
        if analysis_result['key_risks']:
            report += "## 主要风险\n"
            for risk in analysis_result['key_risks']:
                report += f"- {risk}\n"
            report += "\n"
        
        if analysis_result['improvement_suggestions']:
            report += "## 改进建议\n"
            for improvement in analysis_result['improvement_suggestions']:
                report += f"- {improvement}\n"
        
        return report.strip()
