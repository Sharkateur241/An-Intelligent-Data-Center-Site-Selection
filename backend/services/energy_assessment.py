"""
Energy resource assessment service - evaluates solar, wind, and other renewable energy sources
"""

import requests
import json
from typing import Dict, Any, List, Optional
import numpy as np
from datetime import datetime, timedelta
import math

class EnergyAssessmentService:
    """Energy resource assessment service class"""
    
    def __init__(self):
        """Initialize energy assessment service"""
        # Energy resource database
        self.energy_data = {
            "solar_irradiance": {},  # Solar irradiance data
            "wind_speed": {},        # Wind speed data
            "temperature": {},       # Temperature data
            "humidity": {}           # Humidity data
        }
        
        # Energy storage device database
        self.storage_devices = {
            "lithium_battery": {
                "capacity_range": (1, 100),  # MWh
                "efficiency": 0.95,
                "cost_per_mwh": 200000,  # CNY/MWh
                "lifetime": 15  # years
            },
            "pumped_hydro": {
                "capacity_range": (100, 1000),  # MWh
                "efficiency": 0.80,
                "cost_per_mwh": 150000,  # CNY/MWh
                "lifetime": 50  # years
            },
            "compressed_air": {
                "capacity_range": (10, 500),  # MWh
                "efficiency": 0.70,
                "cost_per_mwh": 100000,  # CNY/MWh
                "lifetime": 30  # years
            }
        }
    
    async def assess_energy_resources(self, lat: float, lon: float, land_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess energy resources at a specified location
        
        Args:
            lat: Latitude
            lon: Longitude
            land_analysis: Land use analysis result
            
        Returns:
            Energy resource assessment result
        """
        try:
            # Fetch local energy resource data
            solar_data = await self._get_solar_data(lat, lon)
            wind_data = await self._get_wind_data(lat, lon)
            
            # Assess renewable energy potential
            renewable_potential = await self._assess_renewable_potential(
                lat, lon, solar_data, wind_data, land_analysis
            )
            
            # Assess storage needs
            storage_assessment = await self._assess_storage_needs(
                renewable_potential, land_analysis
            )
            
            # Assess grid connection capacity
            grid_assessment = await self._assess_grid_capacity(lat, lon)
            
            return {
                "solar_data": solar_data,
                "wind_data": wind_data,
                "renewable_potential": renewable_potential,
                "storage_assessment": storage_assessment,
                "grid_assessment": grid_assessment,
                "recommendations": await self._generate_energy_recommendations(
                    lat, lon, renewable_potential, storage_assessment, grid_assessment
                )
            }
            
        except Exception as e:
            print(f"Energy resource assessment failed: {e}")
            raise e
    
    async def _get_solar_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Get solar energy data based on real geographic location
        """
        import random
        
        # Solar energy resource assessment based on real geographic location
        
        # Calculate base solar irradiance from coordinates
        base_irradiance = 1000 + (90 - abs(lat)) * 20  # Latitude effect
        
        # Longitude effect (east/west difference)
        if lon > 100:  # Western region
            base_irradiance += 200
        elif lon < 110:  # Eastern region
            base_irradiance -= 100
        
        # City-specific adjustments
        city_adjustments = {
            (39.9042, 116.4074): 1500,  # Beijing
            (31.2304, 121.4737): 1200,  # Shanghai
            (22.5431, 114.0579): 1300,  # Shenzhen
            (30.2741, 120.1551): 1400,  # Hangzhou
            (37.5149, 105.1967): 2000,  # Zhongwei
            (26.647, 106.6302): 1200,   # Guiyang
            (23.1291, 113.2644): 1300,  # Guangzhou
            (36.0611, 103.8343): 1800   # Lanzhou
        }
        
        # Find the nearest city
        min_distance = float('inf')
        closest_irradiance = base_irradiance
        
        for (city_lat, city_lon), irradiance in city_adjustments.items():
            distance = ((lat - city_lat) ** 2 + (lon - city_lon) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                closest_irradiance = irradiance
        
        # Add some random variation to simulate real data uncertainty
        variation = random.uniform(0.9, 1.1)
        annual_irradiance = int(closest_irradiance * variation)
        
        # Determine solar resource grade
        if annual_irradiance > 1800:
            solar_zone = "Zone 1"
            potential = "high"
        elif annual_irradiance > 1600:
            solar_zone = "Zone 2"
            potential = "high"
        elif annual_irradiance > 1400:
            solar_zone = "Zone 3"
            potential = "moderate"
        else:
            solar_zone = "Zone 4"
            potential = "low"
        
        return {
            "annual_irradiance": annual_irradiance,  # kWh/m²
            "solar_zone": solar_zone,
            "peak_sun_hours": round(annual_irradiance / 1000, 1),  # Peak sun hours
            "solar_potential": potential,
            "latitude": lat,
            "longitude": lon
        }
    
    async def _get_wind_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Get wind energy data based on real geographic location
        """
        import random
        
        # Wind energy resource assessment based on real geographic location
        
        # Calculate base wind speed from coordinates
        base_speed = 4.0 + (90 - abs(lat)) * 0.1  # Latitude effect
        
        # Longitude effect (east/west difference)
        if lon > 100:  # Western region
            base_speed += 1.5
        elif lon < 110:  # Eastern region
            base_speed -= 0.5
        
        # City-specific adjustments
        city_adjustments = {
            (39.9042, 116.4074): 5.5,  # Beijing
            (31.2304, 121.4737): 4.0,  # Shanghai
            (22.5431, 114.0579): 4.5,  # Shenzhen
            (30.2741, 120.1551): 4.2,  # Hangzhou
            (37.5149, 105.1967): 7.0,  # Zhongwei
            (26.647, 106.6302): 3.5,   # Guiyang
            (23.1291, 113.2644): 4.0,  # Guangzhou
            (36.0611, 103.8343): 6.5   # Lanzhou
        }
        
        # Find the nearest city
        min_distance = float('inf')
        closest_speed = base_speed
        
        for (city_lat, city_lon), speed in city_adjustments.items():
            distance = ((lat - city_lat) ** 2 + (lon - city_lon) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                closest_speed = speed
        
        # Add some random variation
        variation = random.uniform(0.9, 1.1)
        average_speed = round(closest_speed * variation, 1)
        
        # Calculate power density
        power_density = int(0.5 * 1.225 * (average_speed ** 3))  # W/m²
        
        # Determine wind resource grade
        if average_speed > 7.0:
            wind_zone = "Wind Zone 1"
            potential = "high"
        elif average_speed > 6.0:
            wind_zone = "Wind Zone 2"
            potential = "high"
        elif average_speed > 5.0:
            wind_zone = "Wind Zone 3"
            potential = "moderate"
        else:
            wind_zone = "Wind Zone 4"
            potential = "low"
        
        wind_zones = {
            "Wind Zone 1": {"avg_speed": 8.5, "power_density": 400},  # W/m²
            "Wind Zone 2": {"avg_speed": 7.0, "power_density": 300},
            "Wind Zone 3": {"avg_speed": 6.0, "power_density": 200},
            "Wind Zone 4": {"avg_speed": 5.0, "power_density": 100}
        }
        
        return {
            "wind_zone": wind_zone,
            "average_speed": average_speed,  # m/s
            "power_density": power_density,  # W/m²
            "wind_potential": potential,
            "latitude": lat,
            "longitude": lon
        }
    
    async def _assess_renewable_potential(self, lat: float, lon: float, 
                                        solar_data: Dict[str, Any], 
                                        wind_data: Dict[str, Any],
                                        land_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess renewable energy potential
        """
        # Calculate available land area
        total_area = land_analysis.get("total_area", 1000000)  # square meters
        suitable_areas = land_analysis.get("suitable_areas", [])
        
        # Calculate solar generation potential
        solar_potential = 0
        if solar_data["solar_potential"] in ["high", "moderate"]:
            # Assume 30% of land is available for solar
            solar_area = total_area * 0.3
            solar_capacity = solar_area * solar_data["annual_irradiance"] * 0.2  # 20% efficiency
            solar_potential = solar_capacity / 1000  # Convert to MWh
        
        # Calculate wind generation potential
        wind_potential = 0
        if wind_data["wind_potential"] in ["high", "moderate"]:
            # Assume 20% of land is available for wind power
            wind_area = total_area * 0.2
            wind_capacity = wind_area * wind_data["power_density"] / 1000  # Convert to MW
            wind_potential = wind_capacity * 8760 * 0.3  # Annual generation, 30% capacity factor
        
        # Calculate total renewable energy potential
        total_renewable = solar_potential + wind_potential
        
        return {
            "solar_potential": {
                "capacity_mw": solar_potential / 8760 * 1000,  # MW
                "annual_generation_mwh": solar_potential,
                "land_requirement": total_area * 0.3
            },
            "wind_potential": {
                "capacity_mw": wind_potential / 8760 * 1000,  # MW
                "annual_generation_mwh": wind_potential,
                "land_requirement": total_area * 0.2
            },
            "total_renewable_potential": {
                "capacity_mw": total_renewable / 8760 * 1000,
                "annual_generation_mwh": total_renewable
            }
        }
    
    async def _assess_storage_needs(self, renewable_potential: Dict[str, Any], 
                                  land_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess storage needs
        """
        # Assumed annual data center power consumption
        data_center_consumption = 100000  # MWh/year
        
        # Renewable energy generation
        renewable_generation = renewable_potential["total_renewable_potential"]["annual_generation_mwh"]
        
        # Calculate storage requirements
        storage_needs = {
            "emergency_backup": data_center_consumption * 0.1,  # 10% emergency backup
            "peak_shaving": data_center_consumption * 0.2,      # 20% peak shaving
            "grid_stabilization": data_center_consumption * 0.05,  # 5% grid stabilization
            "total_required": data_center_consumption * 0.35
        }
        
        # Recommend storage technologies
        recommended_storage = []
        for tech, specs in self.storage_devices.items():
            if specs["capacity_range"][0] <= storage_needs["total_required"] <= specs["capacity_range"][1]:
                recommended_storage.append({
                    "technology": tech,
                    "capacity_mwh": storage_needs["total_required"],
                    "efficiency": specs["efficiency"],
                    "cost": storage_needs["total_required"] * specs["cost_per_mwh"],
                    "lifetime": specs["lifetime"]
                })
        
        # Fix coverage ratio calculation - keep within reasonable range
        coverage_ratio = renewable_generation / data_center_consumption
        renewable_coverage = min(coverage_ratio, 1.0)  # max 100%
        
        return {
            "storage_needs": storage_needs,
            "recommended_technologies": recommended_storage,
            "renewable_coverage": renewable_coverage,
            "renewable_generation_mwh": renewable_generation,
            "data_center_consumption_mwh": data_center_consumption
        }
    
    async def _assess_grid_capacity(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Assess grid connection capacity
        """
        # Assess grid capacity based on geographic location
        grid_capacity = {
            "available_capacity": 100,  # MW
            "voltage_level": "220kV",
            "distance_to_substation": 5,  # km
            "grid_stability": "good"
        }
        
        # Adjust based on specific location
        if 39.0 <= lat <= 40.0:  # Beijing area
            grid_capacity.update({
                "available_capacity": 50,  # High grid load
                "voltage_level": "500kV",
                "distance_to_substation": 2,
                "grid_stability": "tight",
                "constraints": ["High grid load", "Grid capacity expansion required"]
            })
        elif 22.0 <= lat <= 23.0:  # Shenzhen area
            grid_capacity.update({
                "available_capacity": 80,
                "voltage_level": "220kV",
                "distance_to_substation": 3,
                "grid_stability": "good"
            })
        elif 36.0 <= lat <= 37.0:  # Gansu area
            grid_capacity.update({
                "available_capacity": 200,  # Sufficient grid capacity
                "voltage_level": "330kV",
                "distance_to_substation": 10,
                "grid_stability": "sufficient"
            })
        
        return grid_capacity
    
    async def _generate_energy_recommendations(self, lat: float, lon: float,
                                            renewable_potential: Dict[str, Any],
                                            storage_assessment: Dict[str, Any],
                                            grid_assessment: Dict[str, Any]) -> List[str]:
        """
        Generate energy configuration recommendations
        """
        recommendations = []
        
        # Based on renewable energy potential
        if renewable_potential["solar_potential"]["capacity_mw"] > 50:
            recommendations.append("Recommend building a large-scale solar power station")
        
        if renewable_potential["wind_potential"]["capacity_mw"] > 30:
            recommendations.append("Recommend building wind power generation facilities")
        
        # Based on storage needs
        if storage_assessment["renewable_coverage"] > 0.8:
            recommendations.append("Renewable energy can meet most power demand")
        elif storage_assessment["renewable_coverage"] > 0.5:
            recommendations.append("Renewable energy can meet partial demand — traditional energy supplement needed")
        else:
            recommendations.append("Limited renewable energy — primarily reliant on traditional grid supply")
        
        # Based on grid capacity
        if grid_assessment["available_capacity"] < 100:
            recommendations.append("Limited grid capacity — recommend building storage systems for peak shaving")
        
        # Location-specific recommendations
        if 36.0 <= lat <= 37.0:  # Gansu area
            recommendations.extend([
                "Gansu has abundant solar resources — recommend building large-scale PV stations",
                "Consider building an energy storage center to provide peak-regulation services to eastern regions"
            ])
        elif 22.0 <= lat <= 23.0:  # Shenzhen area
            recommendations.extend([
                "Shenzhen has limited land — consider offshore solar or wind power",
                "Recommend building a distributed energy storage system"
            ])
        elif 39.0 <= lat <= 40.0:  # Beijing area
            recommendations.extend([
                "Beijing has high grid load — carefully evaluate grid impact",
                "Recommend building storage systems to reduce grid stress"
            ])
        
        return recommendations
    
    async def analyze_heat_utilization(self, lat: float, lon: float, 
                                     land_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze data center waste heat utilization options based on real location and city characteristics
        """
        import random
        
        # Estimate data center scale based on geographic location
        # Large cities typically have larger data centers
        city_scale_factors = {
            (39.9042, 116.4074): 1.5,  # Beijing - large
            (31.2304, 121.4737): 1.8,  # Shanghai - extra large
            (22.5431, 114.0579): 1.3,  # Shenzhen - large
            (30.2741, 120.1551): 1.2,  # Hangzhou - medium
            (37.5149, 105.1967): 0.8,  # Zhongwei - small
            (26.647, 106.6302): 0.9,   # Guiyang - small
            (23.1291, 113.2644): 1.1,  # Guangzhou - medium
            (36.0611, 103.8343): 0.7   # Lanzhou - small
        }
        
        # Find the nearest city scale factor
        min_distance = float('inf')
        scale_factor = 1.0  # default
        
        for (city_lat, city_lon), factor in city_scale_factors.items():
            distance = ((lat - city_lat) ** 2 + (lon - city_lon) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                scale_factor = factor
        
        # Data center power (MW)
        base_power = 50  # Base power
        data_center_power = int(base_power * scale_factor + random.uniform(-10, 20))
        
        # Heat recovery rate adjusted by climate conditions
        if lat > 40:  # Cold northern region
            heat_recovery_rate = 0.7  # 70% - high heating demand
        elif lat > 30:  # Central region
            heat_recovery_rate = 0.6  # 60% - moderate
        else:  # Southern region
            heat_recovery_rate = 0.5  # 50% - low heating demand
        
        recoverable_heat = round(data_center_power * heat_recovery_rate, 1)
        
        # Analyze waste heat utilization options based on location
        heat_utilization = {
            "recoverable_heat_mw": recoverable_heat,
            "data_center_power_mw": data_center_power,
            "heat_recovery_rate": heat_recovery_rate,
            "utilization_options": [],
            "economic_benefits": {},
            "recommendations": []
        }
        
        # Northern region - district heating
        if lat > 35:
            heating_demand = 0.8 if lat > 40 else 0.6  # Heating demand intensity
            heat_utilization["utilization_options"].append({
                "type": "district_heating",
                "capacity_mw": recoverable_heat * heating_demand,
                "target_users": "residential areas, schools, hospitals",
                "distance_km": 3 if lat > 40 else 5,
                "economic_value": int(recoverable_heat * heating_demand * 1200000),  # CNY/year
                "feasibility": "high",
                "co2_savings": int(recoverable_heat * heating_demand * 500)  # tons/year
            })
        
        # Southern region - industrial heat
        if lat < 35:
            industrial_demand = 0.7 if lon > 110 else 0.5  # Industrial demand intensity
            heat_utilization["utilization_options"].append({
                "type": "industrial_heat",
                "capacity_mw": recoverable_heat * industrial_demand,
                "target_users": "factories, food processing, textile mills",
                "distance_km": 8 if lon > 110 else 12,
                "economic_value": int(recoverable_heat * industrial_demand * 900000),  # CNY/year
                "feasibility": "moderate",
                "co2_savings": int(recoverable_heat * industrial_demand * 400)  # tons/year
            })
        
        # Greenhouse agriculture - applicable to all regions
        greenhouse_capacity = recoverable_heat * 0.3
        heat_utilization["utilization_options"].append({
            "type": "greenhouse_agriculture",
            "capacity_mw": round(greenhouse_capacity, 1),
            "target_users": "agricultural parks, flower cultivation, vegetable greenhouses",
            "distance_km": 10,
            "economic_value": int(greenhouse_capacity * 600000),  # CNY/year
            "feasibility": "high",
            "co2_savings": int(greenhouse_capacity * 300)  # tons/year
        })
        
        # Special regional options
        if 22.0 <= lat <= 24.0 and 113.0 <= lon <= 115.0:  # Pearl River Delta
            heat_utilization["utilization_options"].append({
                "type": "seawater_desalination",
                "capacity_mw": recoverable_heat * 0.2,
                "target_users": "municipal water supply, industrial water",
                "distance_km": 20,
                "economic_value": int(recoverable_heat * 0.2 * 1500000),  # CNY/year
                "feasibility": "moderate",
                "co2_savings": int(recoverable_heat * 0.2 * 200)  # tons/year
            })
        
        # Calculate economic benefits
        total_annual_value = sum(option["economic_value"] for option in heat_utilization["utilization_options"])
        total_co2_savings = sum(option["co2_savings"] for option in heat_utilization["utilization_options"])
        
        # Payback period adjusted by city economic level
        if scale_factor > 1.5:  # Large city
            payback_period = 2.5
        elif scale_factor > 1.0:  # Medium city
            payback_period = 3.0
        else:  # Small city
            payback_period = 4.0
        
        heat_utilization["economic_benefits"] = {
            "annual_revenue": total_annual_value,
            "payback_period": payback_period,  # years
            "co2_reduction": total_co2_savings,  # tons/year
            "investment_cost": int(total_annual_value * payback_period),  # CNY
            "roi_percentage": round((total_annual_value / (total_annual_value * payback_period)) * 100, 1)
        }
        
        # Generate targeted recommendations
        if lat > 40:
            heat_utilization["recommendations"].append(f"Recommend building a district heating system supplying {int(recoverable_heat * 0.8)} MW to surrounding areas to meet winter heating demand")
        elif lat > 35:
            heat_utilization["recommendations"].append(f"Recommend a combined district heating and industrial heat system with total capacity {recoverable_heat} MW")
        else:
            heat_utilization["recommendations"].append(f"Recommend supplying {int(recoverable_heat * 0.7)} MW of industrial heat to nearby factories to improve energy efficiency")
        
        heat_utilization["recommendations"].extend([
            f"Recommend building a {int(greenhouse_capacity)} MW greenhouse agriculture project for synergy between energy and agriculture",
            f"Waste heat utilization estimated annual revenue: {total_annual_value:,} CNY, payback period: {payback_period} years",
            f"Estimated annual CO2 reduction: {total_co2_savings} tons — significant environmental benefit"
        ])
        
        return heat_utilization
    
    async def analyze_geographic_environment(self, lat: float, lon: float, radius: float = 1000) -> Dict[str, Any]:
        """
        Analyze geographic environment - rivers, elevation, forest cover, and other resources
        """
        import random
        
        # Environmental analysis based on geographic location
        env_analysis = {
            "elevation": 0,
            "water_resources": {},
            "forest_coverage": 0,
            "climate_zone": "",
            "natural_hazards": [],
            "satellite_image_url": ""
        }
        
        # Altitude estimation
        if lat > 40:  # Northern high-altitude region
            base_elevation = 1000 + (lat - 40) * 200
        elif lat > 30:  # Central region
            base_elevation = 200 + (lat - 30) * 50
        else:  # Southern region
            base_elevation = 50 + (lat - 20) * 20
            
        # Longitude effect
        if lon > 100:  # Western region
            base_elevation += 500
        elif lon < 110:  # Eastern region
            base_elevation -= 100
            
        env_analysis["elevation"] = int(base_elevation + random.uniform(-100, 200))
        
        # Water resource analysis
        water_sources = []
        if lon > 110:  # Eastern coastal region
            water_sources.append({"type": "river", "distance_km": random.randint(2, 8), "capacity": "abundant"})
        if lat > 35:  # Northern region
            water_sources.append({"type": "groundwater", "depth_m": random.randint(50, 150), "capacity": "moderate"})
        if 22 <= lat <= 25 and 110 <= lon <= 115:  # Pearl River Delta
            water_sources.append({"type": "seawater", "distance_km": random.randint(5, 15), "capacity": "abundant"})
            
        env_analysis["water_resources"] = {
            "sources": water_sources,
            "total_capacity": "abundant" if len(water_sources) > 2 else "moderate" if len(water_sources) > 1 else "limited"
        }
        
        # Forest coverage
        if lat > 45:  # Northeast region
            forest_coverage = random.uniform(40, 60)
        elif 25 <= lat <= 35:  # Central region
            forest_coverage = random.uniform(20, 40)
        else:  # Southern region
            forest_coverage = random.uniform(30, 50)
        env_analysis["forest_coverage"] = round(forest_coverage, 1)
        
        # Climate zone
        if lat > 40:
            climate_zone = "Temperate continental climate"
        elif lat > 30:
            climate_zone = "Subtropical monsoon climate"
        else:
            climate_zone = "Tropical monsoon climate"
        env_analysis["climate_zone"] = climate_zone
        
        # Natural hazard risks
        hazards = []
        if lat > 40:  # Northern region
            hazards.append("frost damage")
        if 20 <= lat <= 30 and 110 <= lon <= 120:  # Southeast coast
            hazards.append("typhoon")
        if 30 <= lat <= 40:  # Central region
            hazards.append("flooding")
        if lon > 100:  # Western region
            hazards.append("drought")
        env_analysis["natural_hazards"] = hazards
        
        # Generate satellite image data using the Google Earth Engine Map API
        satellite_data = await self._get_satellite_image_data(lat, lon, radius)
        env_analysis["satellite_image_url"] = satellite_data["url"]
        env_analysis["satellite_image_metadata"] = satellite_data["metadata"]
        
        return env_analysis

    async def _get_satellite_image_data(self, lat: float, lon: float, radius: float = 1000) -> Dict[str, Any]:
        """
        Get satellite image data using GEE for real satellite imagery
        """
        try:
            # Import satellite service
            from .satellite_service import SatelliteService
            
            # Create satellite service instance
            satellite_service = SatelliteService()
            
            # Fetch satellite image via GEE using the actual radius
            image_data = await satellite_service.get_satellite_image(lat, lon, zoom=10, radius=radius)
            
            return image_data
            
        except Exception as e:
            print(f"GEE satellite image fetch failed: {e}")
            # Return a placeholder image
            return {
                "url": f"https://via.placeholder.com/400x600/4CAF50/FFFFFF?text=GEE+Image:+{lat:.2f},+{lon:.2f}",
                "metadata": {
                    "center": [lat, lon],
                    "radius": radius,
                    "coverage_radius": f"{radius/1000} km",
                    "error": str(e),
                    "gee_available": False
                }
            }

    async def get_local_energy_resources(self, lat: float, lon: float, radius: float = 1000) -> Dict[str, Any]:
        """
        Get local energy resource information
        """
        solar_data = await self._get_solar_data(lat, lon)
        wind_data = await self._get_wind_data(lat, lon)
        env_analysis = await self.analyze_geographic_environment(lat, lon, radius)
        
        return {
            "solar": solar_data,
            "wind": wind_data,
            "environment": env_analysis,
            "location": {"latitude": lat, "longitude": lon},
            "assessment_date": datetime.now().isoformat()
        }
    
    async def analyze_enhanced_heat_utilization(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Enhanced waste heat utilization analysis
        """
        try:
            # Get base waste heat data
            base_analysis = await self.analyze_heat_utilization(lat, lon, {})
            
            # Enhanced analysis
            enhanced_analysis = await self._enhanced_heat_analysis(lat, lon, base_analysis)
            
            return enhanced_analysis
            
        except Exception as e:
            print(f"Enhanced waste heat utilization analysis failed: {e}")
            return {"error": str(e)}
    
    async def _enhanced_heat_analysis(self, lat: float, lon: float, base_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced waste heat analysis"""
        try:
            # Get climate zone and region type
            climate_zone = self._get_climate_zone(lat, lon)
            region_type = self._get_region_type(lat, lon)
            
            # Analyze waste heat utilization potential
            heat_potential = await self._assess_heat_potential(lat, lon, region_type)
            
            # Analyze implementation feasibility
            feasibility_analysis = self._analyze_heat_feasibility(lat, lon, region_type, climate_zone)
            
            # Generate comprehensive recommendations
            comprehensive_recommendations = self._generate_comprehensive_heat_recommendations(
                base_analysis, heat_potential, feasibility_analysis
            )
            
            return {
                "base_analysis": base_analysis,
                "climate_zone": climate_zone,
                "region_type": region_type,
                "heat_potential": heat_potential,
                "feasibility_analysis": feasibility_analysis,
                "comprehensive_recommendations": comprehensive_recommendations,
                "analysis_method": "Enhanced waste heat utilization analysis"
            }
            
        except Exception as e:
            print(f"Enhanced waste heat analysis failed: {e}")
            return {"error": str(e)}
    
    def _get_climate_zone(self, lat: float, lon: float) -> str:
        """Get climate zone"""
        if lat > 50:
            return "Subarctic"
        elif lat > 40:
            return "Temperate"
        elif lat > 30:
            return "Warm temperate"
        elif lat > 20:
            return "Subtropical"
        else:
            return "Tropical"
    
    def _get_region_type(self, lat: float, lon: float) -> str:
        """Get region type"""
        if 20 <= lat <= 35 and 110 <= lon <= 125:
            return "South China"
        elif 25 <= lat <= 40 and 100 <= lon <= 110:
            return "Southwest China"
        elif 30 <= lat <= 45 and 120 <= lon <= 135:
            return "East China"
        elif 35 <= lat <= 50 and 110 <= lon <= 125:
            return "North China"
        elif 40 <= lat <= 55 and 80 <= lon <= 100:
            return "Northwest China"
        else:
            return "Other"
    
    async def _assess_heat_potential(self, lat: float, lon: float, region_type: str) -> Dict[str, Any]:
        """Assess waste heat utilization potential"""
        # Assess waste heat utilization potential based on location and climate
        
        # Calculate annual utilization hours
        if region_type in ["North China", "Northwest China"]:
            annual_hours = 6000  # High heating demand in northern regions
            heat_demand_ratio = 0.8
        elif region_type in ["South China", "East China"]:
            annual_hours = 4000  # Lower heating demand in southern regions
            heat_demand_ratio = 0.6
        else:
            annual_hours = 5000  # Other regions
            heat_demand_ratio = 0.7
        
        # Calculate potential revenue
        potential_revenue = 100 * heat_demand_ratio * annual_hours * 0.1  # 10k CNY/year
        
        return {
            "annual_utilization_hours": annual_hours,
            "heat_demand_ratio": heat_demand_ratio,
            "potential_revenue": round(potential_revenue, 2),
            "utilization_level": "high" if heat_demand_ratio > 0.7 else "moderate" if heat_demand_ratio > 0.5 else "low"
        }
    
    def _analyze_heat_feasibility(self, lat: float, lon: float, region_type: str, climate_zone: str) -> Dict[str, Any]:
        """Analyze waste heat utilization feasibility"""
        feasibility_score = 0
        factors = []
        
        # Climate condition score
        if climate_zone in ["Subarctic", "Temperate"]:
            feasibility_score += 30
            factors.append("Favorable climate conditions with high heating demand")
        elif climate_zone in ["Warm temperate", "Subtropical"]:
            feasibility_score += 20
            factors.append("Moderate climate conditions with utilization potential")
        else:
            feasibility_score += 10
            factors.append("Climate constraints limit utilization potential")
        
        # Regional development level score
        if region_type in ["East China", "South China"]:
            feasibility_score += 25
            factors.append("Economically developed with good technical conditions")
        elif region_type in ["North China", "Southwest China"]:
            feasibility_score += 20
            factors.append("Moderate economic development with some technical capacity")
        else:
            feasibility_score += 15
            factors.append("Below-average economic development — technical support needed")
        
        # Infrastructure score
        if self._has_good_infrastructure(lat, lon):
            feasibility_score += 20
            factors.append("Well-developed infrastructure facilitates implementation")
        else:
            feasibility_score += 10
            factors.append("Average infrastructure — improvements needed")
        
        # Policy support score
        if region_type in ["North China", "Northwest China"]:
            feasibility_score += 15
            factors.append("Strong policy support")
        else:
            feasibility_score += 10
            factors.append("Moderate policy support")
        
        # Determine feasibility level
        if feasibility_score >= 80:
            level = "high"
            recommendation = "Strongly recommended"
        elif feasibility_score >= 60:
            level = "moderate"
            recommendation = "Recommended"
        elif feasibility_score >= 40:
            level = "low"
            recommendation = "Proceed with caution"
        else:
            level = "very low"
            recommendation = "Not recommended"
        
        return {
            "feasibility_score": feasibility_score,
            "level": level,
            "recommendation": recommendation,
            "factors": factors
        }
    
    def _has_good_infrastructure(self, lat: float, lon: float) -> bool:
        """Check whether the location has good infrastructure"""
        # Simplified infrastructure check
        developed_regions = [
            (30, 45, 120, 135),  # East China
            (20, 35, 110, 125),  # South China
            (35, 50, 110, 125),  # North China
        ]
        
        for min_lat, max_lat, min_lon, max_lon in developed_regions:
            if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                return True
        return False
    
    def _generate_comprehensive_heat_recommendations(self, base_analysis: Dict[str, Any], 
                                                   heat_potential: Dict[str, Any],
                                                   feasibility_analysis: Dict[str, Any]) -> List[str]:
        """Generate comprehensive waste heat utilization recommendations"""
        recommendations = []
        
        # Recommendations based on feasibility level
        feasibility_level = feasibility_analysis.get("level", "moderate")
        
        if feasibility_level == "high":
            recommendations.extend([
                "Excellent waste heat utilization conditions — prioritize implementation",
                "A large-scale waste heat utilization system can be built",
                "Recommend partnering with local government for policy support"
            ])
        elif feasibility_level == "moderate":
            recommendations.extend([
                "Good waste heat utilization conditions — implementation recommended",
                "A medium-scale waste heat utilization system can be built",
                "Recommend conducting a detailed technical feasibility study"
            ])
        elif feasibility_level == "low":
            recommendations.extend([
                "Average waste heat utilization conditions — proceed with caution",
                "Recommend starting with a small-scale pilot project",
                "Infrastructure improvements are needed"
            ])
        else:
            recommendations.extend([
                "Poor waste heat utilization conditions — not recommended",
                "Recommend exploring alternative energy utilization methods",
                "Significant investment would be required to improve conditions"
            ])
        
        # Recommendations based on waste heat potential
        utilization_level = heat_potential.get("utilization_level", "moderate")
        if utilization_level == "high":
            recommendations.append("High waste heat utilization potential — recommend increasing investment")
        elif utilization_level == "moderate":
            recommendations.append("Moderate waste heat utilization potential — recommend proportionate investment")
        else:
            recommendations.append("Limited waste heat utilization potential — recommend controlling investment scale")
        
        return recommendations