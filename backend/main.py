"""
数据中心智能选址与能源优化系统 - 后端主程序
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from services.satellite_service import SatelliteService
from services.image_analysis import ImageAnalysisService
from services.energy_assessment import EnergyAssessmentService
from services.decision_analysis import DecisionAnalysisService
from services.power_supply_analysis import PowerSupplyAnalysisService
from services.energy_storage_analysis import EnergyStorageAnalysisService
from services.promethee_mcgp_analysis import PROMETHEEMCGP
from services.multimodal_analysis import MultimodalAnalysisService
from services.energy_ai_analysis import EnergyAIAnalysisService
from services.power_supply_ai_analysis import PowerSupplyAIAnalysisService
from services.energy_storage_ai_analysis import EnergyStorageAIAnalysisService
from services.decision_ai_analysis import DecisionAIAnalysisService
from services.regional_analysis import RegionalAnalysisService
from services.heat_utilization_analysis import HeatUtilizationAnalysisService

# 创建FastAPI应用
app = FastAPI(
    title="数据中心智能选址与能源优化系统",
    description="基于卫星图像和AI的数据中心选址分析系统",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
satellite_service = SatelliteService()
image_service = ImageAnalysisService()
energy_service = EnergyAssessmentService()
decision_service = DecisionAnalysisService()
power_supply_service = PowerSupplyAnalysisService()
energy_storage_service = EnergyStorageAnalysisService()
promethee_mcgp_service = PROMETHEEMCGP()
multimodal_service = MultimodalAnalysisService()

# 初始化AI分析服务
energy_ai_service = EnergyAIAnalysisService()
power_supply_ai_service = PowerSupplyAIAnalysisService()
energy_storage_ai_service = EnergyStorageAIAnalysisService()
decision_ai_service = DecisionAIAnalysisService()

# 初始化其他分析服务
regional_analysis_service = RegionalAnalysisService()
heat_utilization_service = HeatUtilizationAnalysisService()


# 移除不存在的服务初始化

# 数据模型
class LocationRequest(BaseModel):
    """位置请求模型"""
    latitude: float
    longitude: float
    radius: float = 1000  # 米
    city_name: Optional[str] = None

class AnalysisResult(BaseModel):
    """分析结果模型 - AI增强版"""
    location: Dict[str, float]
    land_analysis: Dict[str, Any]
    energy_assessment: Dict[str, Any]
    decision_recommendation: Dict[str, Any]
    heat_utilization: Dict[str, Any]
    geographic_environment: Dict[str, Any]
    power_supply_analysis: Dict[str, Any]
    energy_storage_analysis: Dict[str, Any]
    promethee_mcgp_analysis: Dict[str, Any]
    
    # AI分析结果
    ai_multimodal_analysis: Optional[Dict[str, Any]] = None
    ai_energy_analysis: Optional[Dict[str, Any]] = None
    ai_power_supply_analysis: Optional[Dict[str, Any]] = None
    ai_energy_storage_analysis: Optional[Dict[str, Any]] = None
    ai_decision_analysis: Optional[Dict[str, Any]] = None

class CityAnalysisRequest(BaseModel):
    """城市分析请求模型"""
    cities: List[str]

# API路由
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "数据中心智能选址与能源优化系统API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

@app.post("/analyze/location", response_model=AnalysisResult)
async def analyze_location(request: LocationRequest):
    """
    分析指定位置的数据中心选址可行性 - AI增强版
    """
    try:
        # 1. 获取卫星图像
        satellite_data = await satellite_service.get_satellite_image(
            request.latitude, 
            request.longitude, 
            radius=request.radius
        )
        
        # 2. 运行AI分析（优化版本 - 串行执行避免API限流）
        print("🔄 开始AI分析...")
        
        # 串行执行AI分析，避免API限流
        ai_results = []
        ai_services = [
            ("多模态分析", multimodal_service.analyze_with_gee_data, [satellite_data]),
            ("能源分析", energy_ai_service.analyze_energy_resources_ai, [satellite_data]),
            ("供电分析", power_supply_ai_service.analyze_power_supply_ai, [satellite_data, 100]),
            ("储能分析", energy_storage_ai_service.analyze_storage_layout_ai, [satellite_data, 100, 0.7]),
            ("决策分析", decision_ai_service.analyze_location_ai, [satellite_data])
        ]
        
        for name, service_func, args in ai_services:
            try:
                print(f"🔄 开始{name}...")
                result = await asyncio.wait_for(
                    service_func(*args),
                    timeout=60  # 每个服务60秒超时
                )
                ai_results.append(result)
                print(f"✅ {name}完成")
            except Exception as e:
                print(f"❌ {name}失败: {e}")
                ai_results.append({"success": False, "error": str(e)})
        
        # 解包结果
        ai_multimodal, ai_energy, ai_power_supply, ai_energy_storage, ai_decision = ai_results
        
        
        # 使用简化的决策分析
        try:
            promethee_mcgp_analysis = await asyncio.wait_for(
                promethee_mcgp_service.analyze_data_center_site_selection_with_ai(
                    request.latitude, request.longitude, request.city_name,
                    ai_multimodal, ai_energy, ai_power_supply, ai_energy_storage, ai_decision
                ),
                timeout=60  # 60秒超时
            )
            print("✅ 决策分析完成")
        except Exception as e:
            print(f"❌ 决策分析失败: {e}")
            promethee_mcgp_analysis = {"success": False, "error": str(e)}
        
        # 设置results变量以保持兼容性
        results = [ai_multimodal, ai_energy, ai_power_supply, ai_energy_storage, ai_decision, promethee_mcgp_analysis]
        
        # 打印详细的错误信息
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ 任务 {i} 失败: {result}")
                import traceback
                traceback.print_exc()
        
        # 处理AI分析结果
        ai_multimodal = results[0] if not isinstance(results[0], Exception) else {"success": False, "error": str(results[0])}
        ai_energy = results[1] if not isinstance(results[1], Exception) else {"success": False, "error": str(results[1])}
        ai_power_supply = results[2] if not isinstance(results[2], Exception) else {"success": False, "error": str(results[2])}
        ai_energy_storage = results[3] if not isinstance(results[3], Exception) else {"success": False, "error": str(results[3])}
        ai_decision = results[4] if not isinstance(results[4], Exception) else {"success": False, "error": str(results[4])}
        
        # PROMETHEE-MCGP分析结果
        promethee_mcgp_analysis = results[5] if not isinstance(results[5], Exception) else {"error": str(results[5])}
        
        # 获取基础土地利用分析（包含面积计算）
        image_service = ImageAnalysisService()
        try:
            print(f"🔄 开始土地利用分析...")
            land_analysis = await image_service.analyze_land_use(satellite_data)
            print(f"✅ 土地利用分析成功: {land_analysis.get('success', False)}")
        except Exception as e:
            print(f"❌ 土地利用分析失败: {e}")
            import traceback
            print(f"错误详情: {traceback.format_exc()}")
            land_analysis = {"success": False, "error": str(e)}
        
        # 使用AI分析结果作为主要分析结果
        energy_assessment = ai_energy if ai_energy.get("success") else {}
        power_supply_analysis = ai_power_supply if ai_power_supply.get("success") else {}
        energy_storage_analysis = ai_energy_storage if ai_energy_storage.get("success") else {}
        decision_recommendation = ai_decision if ai_decision.get("success") else {}
        
        # 其他分析（基于AI结果）
        heat_utilization = await energy_service.analyze_heat_utilization(
            request.latitude, request.longitude, land_analysis
        )
        geographic_environment = await energy_service.analyze_geographic_environment(
            request.latitude, request.longitude, request.radius
        )
        power_supply_analysis = ai_power_supply if ai_power_supply.get("success") else {}
        energy_storage_analysis = ai_energy_storage if ai_energy_storage.get("success") else {}
        
        # 确保geographic_environment包含卫星图像信息
        if satellite_data and satellite_data.get("url"):
            geographic_environment.update({
                "satellite_image_url": satellite_data["url"],
                "satellite_image_metadata": satellite_data.get("metadata", {})
            })
        
        return AnalysisResult(
            location={"latitude": request.latitude, "longitude": request.longitude},
            land_analysis=land_analysis,
            energy_assessment=energy_assessment,
            decision_recommendation=decision_recommendation,
            heat_utilization=heat_utilization,
            geographic_environment=geographic_environment,
            power_supply_analysis=power_supply_analysis,
            energy_storage_analysis=energy_storage_analysis,
            promethee_mcgp_analysis=promethee_mcgp_analysis,
            # 新增AI分析结果
            ai_multimodal_analysis=ai_multimodal,
            ai_energy_analysis=ai_energy,
            ai_power_supply_analysis=ai_power_supply,
            ai_energy_storage_analysis=ai_energy_storage,
            ai_decision_analysis=ai_decision
        )
        
    except Exception as e:
        print(f"❌ 分析过程中发生异常: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@app.post("/analyze/cities")
async def analyze_cities(request: CityAnalysisRequest):
    """
    批量分析多个城市的数据中心选址情况
    """
    try:
        results = {}
        for city in request.cities:
            # 获取城市坐标（这里需要城市坐标数据库）
            city_coords = await satellite_service.get_city_coordinates(city)
            if city_coords:
                analysis = await analyze_location(LocationRequest(
                    latitude=city_coords["latitude"],
                    longitude=city_coords["longitude"],
                    city_name=city
                ))
                results[city] = analysis.dict()
        
        return {"cities_analysis": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"城市分析失败: {str(e)}")

@app.get("/satellite/image/{lat}/{lon}")
async def get_satellite_image(lat: float, lon: float, zoom: int = 15, radius: float = 1000):
    """
    获取指定位置的卫星图像
    """
    try:
        image_data = await satellite_service.get_satellite_image(lat, lon, zoom, radius)
        return {"image_url": image_data["url"], "metadata": image_data["metadata"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取卫星图像失败: {str(e)}")

@app.get("/energy/resources/{lat}/{lon}")
async def get_energy_resources(lat: float, lon: float, radius: float = 1000):
    """
    获取指定位置的能源资源信息
    """
    try:
        resources = await energy_service.get_local_energy_resources(lat, lon, radius)
        return resources
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取能源资源失败: {str(e)}")

@app.post("/analyze/multimodal")
async def analyze_with_multimodal(request: LocationRequest):
    """
    使用多模态模型分析卫星图像
    """
    try:
        # 1. 获取卫星图像
        satellite_data = await satellite_service.get_satellite_image(
            request.latitude, 
            request.longitude, 
            radius=request.radius
        )
        
        # 2. 使用多模态模型分析
        multimodal_result = await multimodal_service.analyze_with_gee_data(satellite_data)
        
        return {
            "location": {"latitude": request.latitude, "longitude": request.longitude},
            "satellite_data": satellite_data,
            "multimodal_analysis": multimodal_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"多模态分析失败: {str(e)}")

@app.post("/analyze/multimodal/custom")
async def analyze_with_custom_prompt(request: LocationRequest, custom_prompt: str = None):
    """
    使用自定义提示词进行多模态分析
    """
    try:
        # 1. 获取卫星图像
        satellite_data = await satellite_service.get_satellite_image(
            request.latitude, 
            request.longitude, 
            radius=request.radius
        )
        
        # 2. 使用自定义提示词分析
        multimodal_result = await multimodal_service.analyze_with_gee_data(
            satellite_data, 
            custom_prompt
        )
        
        return {
            "location": {"latitude": request.latitude, "longitude": request.longitude},
            "satellite_data": satellite_data,
            "multimodal_analysis": multimodal_result,
            "custom_prompt": custom_prompt
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"自定义多模态分析失败: {str(e)}")

@app.get("/multimodal/test")
async def test_multimodal_api():
    """
    测试多模态API连接
    """
    try:
        test_result = await multimodal_service.test_api_connection()
        return test_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API测试失败: {str(e)}")

@app.post("/analyze/temporal")
async def analyze_temporal(request: LocationRequest, time_points: int = 3):
    """
    时间序列分析 - 多张图片动态评估
    """
    try:
        # 获取多个时间点的真实卫星图像
        temporal_data = await satellite_service.get_temporal_satellite_data(
            request.latitude, 
            request.longitude, 
            radius=request.radius,
            time_points=time_points
        )
        
        # 进行时间序列分析
        temporal_result = await multimodal_service.temporal_analysis(temporal_data)
        
        return {
            "location": {"latitude": request.latitude, "longitude": request.longitude},
            "temporal_analysis": temporal_result,
            "time_points": time_points,
            "temporal_data": temporal_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"时间序列分析失败: {str(e)}")

class CustomMetricsRequest(BaseModel):
    """自定义指标分析请求模型"""
    latitude: float
    longitude: float
    radius: float = 1000
    metrics: List[str]
    weights: Optional[Dict[str, float]] = None

@app.post("/analyze/custom-metrics")
async def analyze_custom_metrics(request: CustomMetricsRequest):
    """
    自定义指标分析
    """
    try:
        # 获取卫星图像
        satellite_data = await satellite_service.get_satellite_image(
            request.latitude, 
            request.longitude, 
            radius=request.radius
        )
        
        # 进行自定义指标分析
        custom_result = await multimodal_service.custom_metrics_analysis(
            satellite_data["url"], 
            request.metrics, 
            request.weights
        )
        
        return {
            "location": {"latitude": request.latitude, "longitude": request.longitude},
            "custom_metrics_analysis": custom_result,
            "metrics": request.metrics,
            "weights": request.weights
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"自定义指标分析失败: {str(e)}")

class MultiDimensionRequest(BaseModel):
    """多维度分析请求模型"""
    latitude: float
    longitude: float
    radius: float = 1000
    dimensions: Dict[str, List[str]]

@app.post("/analyze/multi-dimension")
async def analyze_multi_dimension(request: MultiDimensionRequest):
    """
    多维度打分评估
    """
    try:
        # 获取卫星图像
        satellite_data = await satellite_service.get_satellite_image(
            request.latitude, 
            request.longitude, 
            radius=request.radius
        )
        
        # 进行多维度分析
        multi_dim_result = await multimodal_service.multi_dimension_scoring(
            satellite_data["url"], 
            request.dimensions
        )
        
        return {
            "location": {"latitude": request.latitude, "longitude": request.longitude},
            "multi_dimension_analysis": multi_dim_result,
            "dimensions": request.dimensions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"多维度分析失败: {str(e)}")

@app.post("/analyze/ai/energy")
async def analyze_energy_ai(request: LocationRequest):
    """
    使用AI分析能源资源
    """
    try:
        # 1. 获取卫星图像
        satellite_data = await satellite_service.get_satellite_image(
            request.latitude, 
            request.longitude, 
            radius=request.radius
        )
        
        # 2. 使用AI分析能源资源
        ai_result = await energy_ai_service.analyze_energy_resources_ai(satellite_data)
        
        return {
            "location": {"latitude": request.latitude, "longitude": request.longitude},
            "satellite_data": satellite_data,
            "ai_energy_analysis": ai_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI能源分析失败: {str(e)}")

@app.post("/analyze/ai/power-supply")
async def analyze_power_supply_ai(request: LocationRequest, power_demand: float = 100):
    """
    使用AI分析供电方案
    """
    try:
        # 1. 获取卫星图像
        satellite_data = await satellite_service.get_satellite_image(
            request.latitude, 
            request.longitude, 
            radius=request.radius
        )
        
        # 2. 使用AI分析供电方案
        ai_result = await power_supply_ai_service.analyze_power_supply_ai(
            satellite_data, power_demand
        )
        
        return {
            "location": {"latitude": request.latitude, "longitude": request.longitude},
            "satellite_data": satellite_data,
            "power_demand": power_demand,
            "ai_power_supply_analysis": ai_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI供电方案分析失败: {str(e)}")

@app.post("/analyze/ai/energy-storage")
async def analyze_energy_storage_ai(request: LocationRequest, 
                                  power_demand: float = 100,
                                  renewable_ratio: float = 0.7):
    """
    使用AI分析储能布局
    """
    try:
        # 1. 获取卫星图像
        satellite_data = await satellite_service.get_satellite_image(
            request.latitude, 
            request.longitude, 
            radius=request.radius
        )
        
        # 2. 使用AI分析储能布局
        ai_result = await energy_storage_ai_service.analyze_storage_layout_ai(
            satellite_data, power_demand, renewable_ratio
        )
        
        return {
            "location": {"latitude": request.latitude, "longitude": request.longitude},
            "satellite_data": satellite_data,
            "power_demand": power_demand,
            "renewable_ratio": renewable_ratio,
            "ai_energy_storage_analysis": ai_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI储能布局分析失败: {str(e)}")

@app.post("/analyze/ai/decision")
async def analyze_decision_ai(request: LocationRequest):
    """
    使用AI进行决策分析
    """
    try:
        # 1. 获取卫星图像
        satellite_data = await satellite_service.get_satellite_image(
            request.latitude, 
            request.longitude, 
            radius=request.radius
        )
        
        # 2. 获取传统分析结果作为参考
        land_analysis = await image_service.analyze_land_use(satellite_data)
        energy_assessment = await energy_service.assess_energy_resources(
            request.latitude, 
            request.longitude,
            land_analysis
        )
        
        # 3. 使用AI进行决策分析
        ai_result = await decision_ai_service.analyze_location_ai(
            satellite_data, land_analysis, energy_assessment
        )
        
        return {
            "location": {"latitude": request.latitude, "longitude": request.longitude},
            "satellite_data": satellite_data,
            "traditional_analysis": {
                "land_analysis": land_analysis,
                "energy_assessment": energy_assessment
            },
            "ai_decision_analysis": ai_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI决策分析失败: {str(e)}")

@app.post("/analyze/ai/comprehensive")
async def analyze_comprehensive_ai(request: LocationRequest, 
                                 power_demand: float = 100,
                                 renewable_ratio: float = 0.7):
    """
    使用AI进行综合分析
    """
    try:
        # 1. 获取卫星图像
        satellite_data = await satellite_service.get_satellite_image(
            request.latitude, 
            request.longitude, 
            radius=request.radius
        )
        
        # 2. 并行执行所有AI分析
        tasks = [
            energy_ai_service.analyze_energy_resources_ai(satellite_data),
            power_supply_ai_service.analyze_power_supply_ai(satellite_data, power_demand),
            energy_storage_ai_service.analyze_storage_layout_ai(satellite_data, power_demand, renewable_ratio),
            multimodal_service.analyze_with_gee_data(satellite_data)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 3. 处理结果
        ai_energy_analysis = results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])}
        ai_power_supply_analysis = results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])}
        ai_energy_storage_analysis = results[2] if not isinstance(results[2], Exception) else {"error": str(results[2])}
        ai_multimodal_analysis = results[3] if not isinstance(results[3], Exception) else {"error": str(results[3])}
        
        return {
            "location": {"latitude": request.latitude, "longitude": request.longitude},
            "satellite_data": satellite_data,
            "analysis_parameters": {
                "power_demand": power_demand,
                "renewable_ratio": renewable_ratio
            },
            "ai_comprehensive_analysis": {
                "energy_analysis": ai_energy_analysis,
                "power_supply_analysis": ai_power_supply_analysis,
                "energy_storage_analysis": ai_energy_storage_analysis,
                "multimodal_analysis": ai_multimodal_analysis
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI综合分析失败: {str(e)}")


@app.post("/analyze/regional")
async def analyze_regional(request: LocationRequest):
    """
    分析区域特色
    """
    try:
        result = await regional_analysis_service.analyze_regional_characteristics(
            request.latitude, request.longitude, request.city_name
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"区域分析失败: {str(e)}")

@app.post("/analyze/heat-utilization")
async def analyze_heat_utilization(request: LocationRequest):
    """
    分析余热利用
    """
    try:
        result = await heat_utilization_service.analyze_heat_utilization(
            request.latitude, request.longitude, 100, request.city_name
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"余热利用分析失败: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
