"""
Data Center Intelligent Site Selection and Energy Optimization System - Backend Main
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
import math

# Load environment variables
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

# Create FastAPI application
app = FastAPI(
    title="Data Center Intelligent Site Selection and Energy Optimization System",
    description="Data Center Site Selection Analysis System Based on Satellite Imagery and AI",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Should be set to specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
satellite_service = SatelliteService()
image_service = ImageAnalysisService()
energy_service = EnergyAssessmentService()
decision_service = DecisionAnalysisService()
power_supply_service = PowerSupplyAnalysisService()
energy_storage_service = EnergyStorageAnalysisService()
promethee_mcgp_service = PROMETHEEMCGP()
multimodal_service = MultimodalAnalysisService()

# Initialize AI analysis services
energy_ai_service = EnergyAIAnalysisService()
power_supply_ai_service = PowerSupplyAIAnalysisService()
energy_storage_ai_service = EnergyStorageAIAnalysisService()
decision_ai_service = DecisionAIAnalysisService()

# Initialize other analysis services
regional_analysis_service = RegionalAnalysisService()
heat_utilization_service = HeatUtilizationAnalysisService()


# Remove non-existent service initializations

# Data models
class LocationRequest(BaseModel):
    """Location request model"""
    latitude: float
    longitude: float
    radius: float = 1000  # meters
    city_name: Optional[str] = None

class AnalysisResult(BaseModel):
    """Analysis results model - AI enhanced version"""
    location: Dict[str, float]
    land_analysis: Dict[str, Any]
    energy_assessment: Dict[str, Any]
    decision_recommendation: Dict[str, Any]
    heat_utilization: Dict[str, Any]
    geographic_environment: Dict[str, Any]
    power_supply_analysis: Dict[str, Any]
    energy_storage_analysis: Dict[str, Any]
    promethee_mcgp_analysis: Dict[str, Any]
    
    # AI analysis results
    ai_multimodal_analysis: Optional[Dict[str, Any]] = None
    ai_energy_analysis: Optional[Dict[str, Any]] = None
    ai_power_supply_analysis: Optional[Dict[str, Any]] = None
    ai_energy_storage_analysis: Optional[Dict[str, Any]] = None
    ai_decision_analysis: Optional[Dict[str, Any]] = None

class CityAnalysisRequest(BaseModel):
    """City analysis request model"""
    cities: List[str]


class LocationRecommendationRequest(BaseModel):
    """Request model for nearby location recommendation"""
    latitude: float
    longitude: float
    search_radius_km: float = 100
    samples: int = 16


class LocationRecommendation(BaseModel):
    """Recommended location payload"""
    latitude: float
    longitude: float
    distance_km: float
    suitability_score: float
    solar_zone: Optional[str] = None
    wind_zone: Optional[str] = None
    water: Optional[str] = None
    hazards: Optional[List[str]] = None
    rationale: Optional[str] = None


class LocationRecommendationResponse(BaseModel):
    """API response for nearby recommendation"""
    recommended_location: LocationRecommendation
    candidates: List[LocationRecommendation]


def _haversine_offset(lat: float, lon: float, distance_km: float, bearing_deg: float) -> Dict[str, float]:
    """Return new lat/lon after moving distance_km on given bearing."""
    R = 6371.0
    bearing = math.radians(bearing_deg)
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)
    lat2 = math.asin(math.sin(lat1) * math.cos(distance_km / R) +
                     math.cos(lat1) * math.sin(distance_km / R) * math.cos(bearing))
    lon2 = lon1 + math.atan2(
        math.sin(bearing) * math.sin(distance_km / R) * math.cos(lat1),
        math.cos(distance_km / R) - math.sin(lat1) * math.sin(lat2)
    )
    return {"lat": math.degrees(lat2), "lon": (math.degrees(lon2) + 540) % 360 - 180}


async def _quick_geo_snapshot(lat: float, lon: float) -> Dict[str, Any]:
    """
    Lightweight geographic snapshot mirroring analyze_geographic_environment but
    without heavy satellite fetch, for rapid nearby screening.
    """
    # Elevation heuristic
    if lat > 40:
        base_elevation = 1000 + (lat - 40) * 200
    elif lat > 30:
        base_elevation = 200 + (lat - 30) * 50
    else:
        base_elevation = 50 + (lat - 20) * 20
    if lon > 100:
        base_elevation += 500
    elif lon < 110:
        base_elevation -= 100
    # Deterministic estimate: midpoint of the ±100 m residual uncertainty band
    elevation = int(base_elevation + 20)

    # Water proximity heuristic
    water_sources = []
    if lon > 110:
        water_sources.append({"type": "河流", "distance_km": 5})
    if lat > 35:
        water_sources.append({"type": "地下水", "distance_km": 10})
    water_tag = "丰富" if water_sources else "一般"

    # Hazards
    hazards = []
    if lat > 40:
        hazards.append("低温冻害")
    if 20 <= lat <= 30 and 110 <= lon <= 120:
        hazards.append("台风")
    if 30 <= lat <= 40:
        hazards.append("洪涝")
    if lon > 100:
        hazards.append("干旱")

    return {
        "elevation": elevation,
        "water": water_tag,
        "hazards": hazards
    }


def _score_from_potential(label: str) -> float:
    if label == "高":
        return 30
    if label == "中等":
        return 20
    if label == "低":
        return 8
    return 5


async def _score_candidate(lat: float, lon: float) -> Dict[str, Any]:
    """Compute a lightweight suitability score for a candidate point."""
    solar = await energy_service._get_solar_data(lat, lon)  # type: ignore
    wind = await energy_service._get_wind_data(lat, lon)  # type: ignore
    grid = await energy_service._assess_grid_capacity(lat, lon)  # type: ignore
    geo = await _quick_geo_snapshot(lat, lon)

    score = (
        _score_from_potential(solar.get("solar_potential")) +
        _score_from_potential(wind.get("wind_potential")) +
        min(grid.get("available_capacity", 0), 200) / 4  # cap and scale
    )
    # Penalties
    score -= len(geo["hazards"]) * 6
    if geo["water"] == "丰富":
        score += 5

    return {
        "latitude": lat,
        "longitude": lon,
        "suitability_score": round(score, 2),
        "solar_zone": solar.get("solar_zone"),
        "wind_zone": wind.get("wind_zone"),
        "water": geo.get("water"),
        "hazards": geo.get("hazards"),
        "grid_capacity": grid.get("available_capacity"),
    }

# API routes
@app.get("/")
async def root():
    """Root path"""
    return {
        "message": "Data Center Intelligent Site Selection and Energy Optimization System API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy"}

@app.post("/analyze/location", response_model=AnalysisResult)
async def analyze_location(request: LocationRequest):
    """
    Analyze data center site feasibility for a given location - AI enhanced version
    """
    try:
        # 1. Fetch satellite imagery
        satellite_data = await satellite_service.get_satellite_image(
            request.latitude, 
            request.longitude, 
            radius=request.radius
        )
        
        # 2. Run AI analysis (optimized - serial execution to avoid API rate limiting)
        print("🔄 Starting AI analysis...")
        
        # Serial AI analysis to avoid API rate limiting
        ai_results = []
        ai_services = [
            ("Multimodal analysis", multimodal_service.analyze_with_gee_data, [satellite_data]),
            ("Energy analysis", energy_ai_service.analyze_energy_resources_ai, [satellite_data]),
            ("Power supply analysis", power_supply_ai_service.analyze_power_supply_ai, [satellite_data, 100]),
            ("Energy storage analysis", energy_storage_ai_service.analyze_storage_layout_ai, [satellite_data, 100, 0.7]),
            ("Decision analysis", decision_ai_service.analyze_location_ai, [satellite_data])
        ]
        
        for name, service_func, args in ai_services:
            try:
                print(f"🔄 Starting {name}...")
                result = await asyncio.wait_for(
                    service_func(*args),
                    timeout=60  # 60 second timeout per service
                )
                ai_results.append(result)
                print(f"✅ {name} completed")
            except Exception as e:
                print(f"❌ {name} failed: {e}")
                ai_results.append({"success": False, "error": str(e)})
        
        # Unpack results
        ai_multimodal, ai_energy, ai_power_supply, ai_energy_storage, ai_decision = ai_results
        
        
        # Run simplified decision analysis
        try:
            promethee_mcgp_analysis = await asyncio.wait_for(
                promethee_mcgp_service.analyze_data_center_site_selection_with_ai(
                    request.latitude, request.longitude, request.city_name,
                    ai_multimodal, ai_energy, ai_power_supply, ai_energy_storage, ai_decision
                ),
                timeout=60  # 60 second timeout
            )
            print("✅ Decision analysis completed")
        except Exception as e:
            print(f"❌ Decision analysis failed: {e}")
            promethee_mcgp_analysis = {"success": False, "error": str(e)}
        
        # Set results variable for compatibility
        results = [ai_multimodal, ai_energy, ai_power_supply, ai_energy_storage, ai_decision, promethee_mcgp_analysis]
        
        # Print detailed error info
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ Task {i} failed: {result}")
                import traceback
                traceback.print_exc()
        
        # Process AI analysis results
        def normalize_ai(raw, label: str):
            if isinstance(raw, Exception):
                return {"success": False, "error": str(raw), "analysis": f"{label} failed: {raw}"}
            if not isinstance(raw, dict):
                return {"success": False, "error": "Unknown AI response", "analysis": str(raw)}
            # Ensure there's something to show in UI
            if not raw.get("success", False):
                msg = raw.get("error") or raw.get("message") or "AI service returned no result"
                raw.setdefault("analysis", f"{label} error: {msg}")
            else:
                # If success but no analysis text, stringify key info
                if not raw.get("analysis"):
                    raw["analysis"] = raw.get("summary") or raw.get("recommendation") or str(raw)
            return raw

        ai_multimodal = normalize_ai(results[0], "Multimodal")
        ai_energy = normalize_ai(results[1], "Energy")
        ai_power_supply = normalize_ai(results[2], "Power supply")
        ai_energy_storage = normalize_ai(results[3], "Energy storage")
        ai_decision = normalize_ai(results[4], "Decision")
        
        # PROMETHEE-MCGP analysis result
        promethee_mcgp_analysis = results[5] if not isinstance(results[5], Exception) else {"error": str(results[5])}
        
        # Fetch basic land use analysis (including area calculation)
        image_service = ImageAnalysisService()
        try:
            print("🔄 Starting land use analysis...")
            land_analysis = await image_service.analyze_land_use(satellite_data)
            print(f"✅ Land use analysis successful: {land_analysis.get('success', False)}")
        except Exception as e:
            print(f"❌ Land use analysis failed: {e}")
            import traceback
            print(f"Error details: {traceback.format_exc()}")
            land_analysis = {"success": False, "error": str(e)}
        
        # Use AI analysis results as primary results
        energy_assessment = ai_energy if ai_energy.get("success") else {}
        power_supply_analysis = ai_power_supply if ai_power_supply.get("success") else {}
        energy_storage_analysis = ai_energy_storage if ai_energy_storage.get("success") else {}
        decision_recommendation = ai_decision if ai_decision.get("success") else {}
        
        # Other analyses (based on AI results)
        heat_utilization = await energy_service.analyze_heat_utilization(
            request.latitude, request.longitude, land_analysis
        )
        geographic_environment = await energy_service.analyze_geographic_environment(
            request.latitude, request.longitude, request.radius
        )
        power_supply_analysis = ai_power_supply if ai_power_supply.get("success") else {}
        energy_storage_analysis = ai_energy_storage if ai_energy_storage.get("success") else {}
        
        # Ensure geographic_environment includes satellite image info
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
            # Include AI analysis results
            ai_multimodal_analysis=ai_multimodal,
            ai_energy_analysis=ai_energy,
            ai_power_supply_analysis=ai_power_supply,
            ai_energy_storage_analysis=ai_energy_storage,
            ai_decision_analysis=ai_decision
        )
        
    except Exception as e:
        print(f"❌ Exception during analysis: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/recommend/location", response_model=LocationRecommendationResponse)
async def recommend_location(request: LocationRecommendationRequest):
    """
    Recommend a nearby alternative location within search_radius_km.
    Uses lightweight heuristics (solar, wind, grid, hazards) to avoid long latency.
    """
    try:
        candidates: List[LocationRecommendation] = []
        n = max(4, request.samples)
        for i in range(n):
            # Evenly spaced bearings; distance increases linearly from 30 % to 100 % of
            # search radius so candidates span the full annulus deterministically.
            bearing = (360 / n) * i
            distance = request.search_radius_km * (0.3 + 0.7 * i / max(n - 1, 1))
            pt = _haversine_offset(request.latitude, request.longitude, distance, bearing)
            scored = await _score_candidate(pt["lat"], pt["lon"])
            candidates.append(
                LocationRecommendation(
                    latitude=scored["latitude"],
                    longitude=scored["longitude"],
                    distance_km=round(distance, 2),
                    suitability_score=scored["suitability_score"],
                    solar_zone=scored.get("solar_zone"),
                    wind_zone=scored.get("wind_zone"),
                    water=scored.get("water"),
                    hazards=scored.get("hazards"),
                    rationale=(
                        f"太阳能{scored.get('solar_zone', '')}、风区{scored.get('wind_zone', '')}，"
                        f"电网容量约{scored.get('grid_capacity', '未知')}MW，水资源{scored.get('water', '一般')}"
                    )
                )
            )

        best = max(candidates, key=lambda c: c.suitability_score)
        return LocationRecommendationResponse(
            recommended_location=best,
            candidates=candidates
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")

@app.post("/analyze/cities")
async def analyze_cities(request: CityAnalysisRequest):
    """
    Batch analysis of data center site selection for multiple cities
    """
    try:
        results = {}
        for city in request.cities:
            # Get city coordinates (requires city coordinates database)
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
        raise HTTPException(status_code=500, detail=f"City analysis failed: {str(e)}")

@app.get("/satellite/image/{lat}/{lon}")
async def get_satellite_image(lat: float, lon: float, zoom: int = 15, radius: float = 1000):
    """
    Get satellite image for specified location
    """
    try:
        image_data = await satellite_service.get_satellite_image(lat, lon, zoom, radius)
        return {"image_url": image_data["url"], "metadata": image_data["metadata"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get satellite image: {str(e)}")

@app.get("/energy/resources/{lat}/{lon}")
async def get_energy_resources(lat: float, lon: float, radius: float = 1000):
    """
    Get energy resource information for specified location
    """
    try:
        resources = await energy_service.get_local_energy_resources(lat, lon, radius)
        return resources
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get energy resources: {str(e)}")

@app.post("/analyze/multimodal")
async def analyze_with_multimodal(request: LocationRequest):
    """
    Analyze satellite imagery with multimodal model
    """
    try:
        # 1. Fetch satellite imagery
        satellite_data = await satellite_service.get_satellite_image(
            request.latitude, 
            request.longitude, 
            radius=request.radius
        )
        
        # 2. Analyze with multimodal model
        multimodal_result = await multimodal_service.analyze_with_gee_data(satellite_data)
        
        return {
            "location": {"latitude": request.latitude, "longitude": request.longitude},
            "satellite_data": satellite_data,
            "multimodal_analysis": multimodal_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multimodal analysis failed: {str(e)}")

@app.post("/analyze/multimodal/custom")
async def analyze_with_custom_prompt(request: LocationRequest, custom_prompt: str = None):
    """
    Multimodal analysis with custom prompt
    """
    try:
        # 1. Fetch satellite imagery
        satellite_data = await satellite_service.get_satellite_image(
            request.latitude, 
            request.longitude, 
            radius=request.radius
        )
        
        # 2. Analyze with custom prompt
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
        raise HTTPException(status_code=500, detail=f"Custom multimodal analysis failed: {str(e)}")

@app.get("/multimodal/test")
async def test_multimodal_api():
    """
    Test multimodal API connection
    """
    try:
        test_result = await multimodal_service.test_api_connection()
        return test_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API test failed: {str(e)}")

@app.post("/analyze/temporal")
async def analyze_temporal(request: LocationRequest, time_points: int = 3):
    """
    Time series analysis - dynamic evaluation with multiple images
    """
    try:
        # Get real satellite images at multiple time points
        temporal_data = await satellite_service.get_temporal_satellite_data(
            request.latitude, 
            request.longitude, 
            radius=request.radius,
            time_points=time_points
        )
        
        # Perform time series analysis
        temporal_result = await multimodal_service.temporal_analysis(temporal_data)
        
        return {
            "location": {"latitude": request.latitude, "longitude": request.longitude},
            "temporal_analysis": temporal_result,
            "time_points": time_points,
            "temporal_data": temporal_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Time series analysis failed: {str(e)}")

class CustomMetricsRequest(BaseModel):
    """Custom metrics analysis request model"""
    latitude: float
    longitude: float
    radius: float = 1000
    metrics: List[str]
    weights: Optional[Dict[str, float]] = None

@app.post("/analyze/custom-metrics")
async def analyze_custom_metrics(request: CustomMetricsRequest):
    """
    Custom metrics analysis
    """
    try:
        # Get satellite imagery
        satellite_data = await satellite_service.get_satellite_image(
            request.latitude, 
            request.longitude, 
            radius=request.radius
        )
        
        # Perform custom metrics analysis
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
        raise HTTPException(status_code=500, detail=f"Custom metrics analysis failed: {str(e)}")

class MultiDimensionRequest(BaseModel):
    """Multi-dimensional analysis request model"""
    latitude: float
    longitude: float
    radius: float = 1000
    dimensions: Dict[str, List[str]]

@app.post("/analyze/multi-dimension")
async def analyze_multi_dimension(request: MultiDimensionRequest):
    """
    Multi-dimensional scoring evaluation
    """
    try:
        # Get satellite imagery
        satellite_data = await satellite_service.get_satellite_image(
            request.latitude, 
            request.longitude, 
            radius=request.radius
        )
        
        # Perform multi-dimensional analysis
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
        raise HTTPException(status_code=500, detail=f"Multi-dimensional analysis failed: {str(e)}")

@app.post("/analyze/ai/energy")
async def analyze_energy_ai(request: LocationRequest):
    """
    Analyze energy resources with AI
    """
    try:
        # 1. Fetch satellite imagery
        satellite_data = await satellite_service.get_satellite_image(
            request.latitude, 
            request.longitude, 
            radius=request.radius
        )
        
        # 2. Analyze energy resources with AI
        ai_result = await energy_ai_service.analyze_energy_resources_ai(satellite_data)
        
        return {
            "location": {"latitude": request.latitude, "longitude": request.longitude},
            "satellite_data": satellite_data,
            "ai_energy_analysis": ai_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI energy analysis failed: {str(e)}")

@app.post("/analyze/ai/power-supply")
async def analyze_power_supply_ai(request: LocationRequest, power_demand: float = 100):
    """
    Analyze power supply plan with AI
    """
    try:
        # 1. Fetch satellite imagery
        satellite_data = await satellite_service.get_satellite_image(
            request.latitude, 
            request.longitude, 
            radius=request.radius
        )
        
        # 2. Analyze power supply plan with AI
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
        raise HTTPException(status_code=500, detail=f"AI power supply analysis failed: {str(e)}")

@app.post("/analyze/ai/energy-storage")
async def analyze_energy_storage_ai(request: LocationRequest, 
                                  power_demand: float = 100,
                                  renewable_ratio: float = 0.7):
    """
    Analyze energy storage layout with AI
    """
    try:
        # 1. Fetch satellite imagery
        satellite_data = await satellite_service.get_satellite_image(
            request.latitude, 
            request.longitude, 
            radius=request.radius
        )
        
        # 2. Analyze energy storage layout with AI
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
        raise HTTPException(status_code=500, detail=f"AI energy storage layout analysis failed: {str(e)}")

@app.post("/analyze/ai/decision")
async def analyze_decision_ai(request: LocationRequest):
    """
    Perform decision analysis with AI
    """
    try:
        # 1. Fetch satellite imagery
        satellite_data = await satellite_service.get_satellite_image(
            request.latitude, 
            request.longitude, 
            radius=request.radius
        )
        
        # 2. Get traditional analysis results as reference
        land_analysis = await image_service.analyze_land_use(satellite_data)
        energy_assessment = await energy_service.assess_energy_resources(
            request.latitude, 
            request.longitude,
            land_analysis
        )
        
        # 3. Perform decision analysis with AI
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
        raise HTTPException(status_code=500, detail=f"AI decision analysis failed: {str(e)}")

@app.post("/analyze/ai/comprehensive")
async def analyze_comprehensive_ai(request: LocationRequest, 
                                 power_demand: float = 100,
                                 renewable_ratio: float = 0.7):
    """
    Perform comprehensive analysis with AI
    """
    try:
        # 1. Fetch satellite imagery
        satellite_data = await satellite_service.get_satellite_image(
            request.latitude, 
            request.longitude, 
            radius=request.radius
        )
        
        # 2. Execute all AI analyses in parallel
        tasks = [
            energy_ai_service.analyze_energy_resources_ai(satellite_data),
            power_supply_ai_service.analyze_power_supply_ai(satellite_data, power_demand),
            energy_storage_ai_service.analyze_storage_layout_ai(satellite_data, power_demand, renewable_ratio),
            multimodal_service.analyze_with_gee_data(satellite_data)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 3. Process results
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
        raise HTTPException(status_code=500, detail=f"AI comprehensive analysis failed: {str(e)}")


@app.post("/analyze/regional")
async def analyze_regional(request: LocationRequest):
    """
    Analyze regional characteristics
    """
    try:
        result = await regional_analysis_service.analyze_regional_characteristics(
            request.latitude, request.longitude, request.city_name
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Regional analysis failed: {str(e)}")

@app.post("/analyze/heat-utilization")
async def analyze_heat_utilization(request: LocationRequest):
    """
    Analyze waste heat utilization
    """
    try:
        result = await heat_utilization_service.analyze_heat_utilization(
            request.latitude, request.longitude, 100, request.city_name
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Waste heat utilization analysis failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
