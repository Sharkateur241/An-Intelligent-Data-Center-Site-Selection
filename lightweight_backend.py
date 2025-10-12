#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轻量级后端 - 跳过GEE，直接返回模拟数据
"""

import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn

# 设置代理
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7897'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7897'

app = FastAPI(title="轻量级数据中心选址系统")

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LocationRequest(BaseModel):
    latitude: float
    longitude: float
    city_name: str
    radius: float = 1000

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "lightweight"}

@app.post("/analyze/location")
async def analyze_location(request: LocationRequest):
    """轻量级位置分析 - 返回模拟数据"""
    
    print(f"🔍 分析位置: {request.city_name} ({request.latitude}, {request.longitude})")
    
    # 模拟分析结果
    result = {
        "location": {
            "latitude": request.latitude,
            "longitude": request.longitude,
            "city_name": request.city_name,
            "radius": request.radius
        },
        "land_analysis": {
            "land_use_distribution": {
                "水体": 9.1,
                "林地": 25.7,
                "草地": 19.7,
                "农田": 18.6,
                "建设用地": 17.7,
                "裸地": 9.2
            },
            "suitable_areas": [
                {"type": "裸地", "area": 0.092, "suitability": 8.5},
                {"type": "建设用地", "area": 0.177, "suitability": 7.2}
            ]
        },
        "energy_assessment": {
            "solar_potential": 7.5,
            "wind_potential": 6.2,
            "renewable_energy_ratio": 0.65
        },
        "ai_multimodal_analysis": {
            "success": True,
            "analysis": f"基于{request.city_name}的地理位置分析，该区域适合建设数据中心。",
            "model": "lightweight-simulator",
            "timestamp": "2024-01-01T00:00:00Z"
        },
        "ai_energy_analysis": {
            "success": True,
            "analysis": "该区域可再生能源潜力良好，建议优先考虑太阳能和风能。",
            "model": "lightweight-simulator"
        },
        "decision_recommendation": {
            "overall_score": 8.2,
            "recommendation": "推荐",
            "key_factors": ["地理位置优越", "能源资源丰富", "土地条件良好"]
        }
    }
    
    print("✅ 分析完成 - 返回模拟数据")
    return result

if __name__ == "__main__":
    print("🚀 启动轻量级后端服务...")
    print("📱 访问地址: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    print("⚠️  注意: 这是轻量级版本，使用模拟数据")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )
