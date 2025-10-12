"""
数据中心智能选址与能源优化系统 - 增强版后端主程序
使用专业评估框架替代原有AI分析
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

from services.satellite_service import SatelliteService
from services.image_analysis import ImageAnalysisService
from services.energy_assessment import EnergyAssessmentService
from services.decision_analysis import DecisionAnalysisService
from services.power_supply_analysis import PowerSupplyAnalysisService
from services.energy_storage_analysis import EnergyStorageAnalysisService
from services.promethee_mcgp_analysis import PROMETHEEMCGP
from services.enhanced_data_center_analysis import EnhancedDataCenterAnalysisService

# 创建FastAPI应用
app = FastAPI(
    title="数据中心智能选址与能源优化系统",
    description="基于专业评估框架的数据中心选址分析系统",
    version="2.0.0"
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
enhanced_analysis_service = EnhancedDataCenterAnalysisService()

# 数据模型
class LocationRequest(BaseModel):
    """位置请求模型"""
    latitude: float
    longitude: float
    city_name: str
    radius: float = 1000

class AnalysisResult(BaseModel):
    """分析结果模型"""
    location: Dict[str, Any]
    land_analysis: Dict[str, Any]
    energy_assessment: Dict[str, Any]
    decision_recommendation: Dict[str, Any]
    heat_utilization: Dict[str, Any]
    geographic_environment: Dict[str, Any]
    power_supply_analysis: Dict[str, Any]
    energy_storage_analysis: Dict[str, Any]
    promethee_mcgp_analysis: Dict[str, Any]
    enhanced_analysis: Dict[str, Any]  # 新增：增强版分析结果

# 静态文件服务
if os.path.exists("frontend/build"):
    app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

@app.get("/")
async def root():
    """根路径"""
    return {"message": "数据中心智能选址与能源优化系统 API", "version": "2.0.0"}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "version": "2.0.0"}

@app.post("/analyze/location", response_model=AnalysisResult)
async def analyze_location(request: LocationRequest):
    """
    分析指定位置的数据中心选址可行性 - 增强版专业分析
    """
    try:
        print(f"🔍 开始分析位置: {request.city_name} ({request.latitude}, {request.longitude})")
        
        # 1. 获取卫星图像（用于地理分析）
        satellite_data = await satellite_service.get_satellite_image(
            request.latitude, 
            request.longitude, 
            radius=request.radius
        )
        
        # 2. 获取土地利用分析
        land_analysis = await satellite_service.get_satellite_data(
            request.latitude, 
            request.longitude, 
            request.radius
        )
        
        # 3. 运行增强版综合分析（替代原有AI分析）
        print("🚀 运行增强版专业分析...")
        enhanced_analysis = await enhanced_analysis_service.analyze_comprehensive(
            request.latitude, 
            request.longitude, 
            request.city_name,
            request.radius
        )
        
        # 4. 运行传统分析（保留）
        print("🔄 运行传统分析...")
        tasks = [
            energy_service.assess_energy_resources({
                "latitude": request.latitude,
                "longitude": request.longitude,
                "city_name": request.city_name
            }),
            decision_service.analyze_location({
                "latitude": request.latitude,
                "longitude": request.longitude,
                "city_name": request.city_name,
                "land_analysis": land_analysis
            }),
            power_supply_service.analyze_power_supply_schemes({
                "latitude": request.latitude,
                "longitude": request.longitude,
                "city_name": request.city_name
            }),
            energy_storage_service.analyze_storage_layout({
                "latitude": request.latitude,
                "longitude": request.longitude,
                "city_name": request.city_name
            }),
            promethee_mcgp_service.analyze_data_center_site_selection(
                request.latitude, request.longitude, request.city_name
            )
        ]
        
        # 并行运行传统分析
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=120  # 2分钟超时
            )
        except asyncio.TimeoutError:
            print("❌ 传统分析任务超时，使用默认结果")
            results = [{"success": False, "error": "分析超时"}] * len(tasks)
        
        # 处理传统分析结果
        energy_assessment = results[0] if not isinstance(results[0], Exception) else {"success": False, "error": str(results[0])}
        decision_recommendation = results[1] if not isinstance(results[1], Exception) else {"success": False, "error": str(results[1])}
        power_supply_analysis = results[2] if not isinstance(results[2], Exception) else {"success": False, "error": str(results[2])}
        energy_storage_analysis = results[3] if not isinstance(results[3], Exception) else {"success": False, "error": str(results[3])}
        promethee_mcgp_analysis = results[4] if not isinstance(results[4], Exception) else {"success": False, "error": str(results[4])}
        
        # 5. 生成余热利用和地理环境分析（简化版）
        heat_utilization = {
            "success": True,
            "analysis": "基于增强版分析结果，该地区数据中心余热利用潜力评估",
            "recommendation": "建议采用热回收系统，提高能源利用效率"
        }
        
        geographic_environment = {
            "success": True,
            "analysis": "基于卫星数据分析的地理环境评估",
            "land_use": land_analysis.get("land_use_distribution", {}),
            "environmental_factors": enhanced_analysis.get("dimensions", {}).get("地理与环境条件", {})
        }
        
        print("✅ 分析完成！")
        
        return AnalysisResult(
            location={
                "latitude": request.latitude,
                "longitude": request.longitude,
                "city_name": request.city_name,
                "radius": request.radius
            },
            land_analysis=land_analysis,
            energy_assessment=energy_assessment,
            decision_recommendation=decision_recommendation,
            heat_utilization=heat_utilization,
            geographic_environment=geographic_environment,
            power_supply_analysis=power_supply_analysis,
            energy_storage_analysis=energy_storage_analysis,
            promethee_mcgp_analysis=promethee_mcgp_analysis,
            enhanced_analysis=enhanced_analysis  # 新增：增强版分析结果
        )
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@app.get("/analyze/energy/{latitude}/{longitude}")
async def analyze_energy(latitude: float, longitude: float):
    """分析指定位置的能源资源"""
    try:
        result = energy_service.assess_energy_resources({
            "latitude": latitude,
            "longitude": longitude,
            "city_name": "未知"
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyze/land/{latitude}/{longitude}")
async def analyze_land(latitude: float, longitude: float):
    """分析指定位置的土地利用"""
    try:
        result = await satellite_service.get_satellite_data(latitude, longitude, 1000)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyze/enhanced/{latitude}/{longitude}/{city_name}")
async def analyze_enhanced(latitude: float, longitude: float, city_name: str):
    """增强版综合分析"""
    try:
        result = await enhanced_analysis_service.analyze_comprehensive(
            latitude, longitude, city_name, 1000
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 启动增强版数据中心选址系统...")
    print("📱 访问地址: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    print("🔧 版本: 2.0.0 - 增强版专业分析")
    
    uvicorn.run(
        "main_enhanced:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
