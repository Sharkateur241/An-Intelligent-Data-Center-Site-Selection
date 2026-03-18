"""
Power Supply Solution Analysis Service - Analyze power supply solutions based on geographic location and energy resources
"""

import math
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class PowerSupplyOption:
    """Power supply solution option"""
    name: str
    capacity: float       # Installed capacity (MW)
    efficiency: float     # Efficiency
    cost_per_mw: float    # Cost per MW (10k CNY)
    land_requirement: float  # Land requirement (km²)
    suitability_score: float  # Suitability score
    description: str

class PowerSupplyAnalysisService:
    """Power Supply Solution Analysis Service Class"""
    
    def __init__(self):
        """Initialize the power supply solution analysis service"""
        self.power_options = {
            "solar_pv": {
                "name": "Solar Photovoltaic",
                "efficiency": 0.20,
                "cost_per_mw": 600,       # 10k CNY/MW
                "land_per_mw": 0.02,      # km²/MW
                "suitable_regions": ["Northwest", "North China", "Northeast"]
            },
            "wind_onshore": {
                "name": "Onshore Wind Power",
                "efficiency": 0.35,
                "cost_per_mw": 800,
                "land_per_mw": 0.05,
                "suitable_regions": ["Northwest", "North China", "Northeast", "Inner Mongolia"]
            },
            "wind_offshore": {
                "name": "Offshore Wind Power",
                "efficiency": 0.40,
                "cost_per_mw": 1200,
                "land_per_mw": 0.01,      # Offshore area
                "suitable_regions": ["East China", "South China", "Bohai Bay"]
            },
            "hydro": {
                "name": "Hydropower",
                "efficiency": 0.85,
                "cost_per_mw": 1000,
                "land_per_mw": 0.1,
                "suitable_regions": ["Southwest", "Central China", "South China"]
            },
            "nuclear": {
                "name": "Nuclear Power",
                "efficiency": 0.90,
                "cost_per_mw": 1500,
                "land_per_mw": 0.5,
                "suitable_regions": ["Coastal Regions"]
            }
        }
    
    async def analyze_power_supply_options(self, lat: float, lon: float, 
                                         power_demand: float = 100) -> Dict[str, Any]:
        """
        Analyze power supply solution options
        
        Args:
            lat: Latitude
            lon: Longitude
            power_demand: Power demand (MW)
            
        Returns:
            Power supply solution analysis results
        """
        try:
            # Get regional characteristics
            region_type = self._get_region_type(lat, lon)
            solar_potential = self._calculate_solar_potential(lat, lon)
            wind_potential = self._calculate_wind_potential(lat, lon)
            water_resources = self._assess_water_resources(lat, lon)
            
            # Analyze various power supply options
            power_options = []
            
            # Solar photovoltaic analysis
            if solar_potential > 1200:  # kWh/m²/year
                solar_option = self._analyze_solar_option(
                    solar_potential, power_demand, region_type
                )
                power_options.append(solar_option)
            
            # Onshore wind power analysis
            if wind_potential > 4.0:  # m/s
                wind_onshore_option = self._analyze_wind_onshore_option(
                    wind_potential, power_demand, region_type
                )
                power_options.append(wind_onshore_option)
            
            # Offshore wind power analysis
            if self._is_coastal_region(lat, lon) and wind_potential > 5.0:
                wind_offshore_option = self._analyze_wind_offshore_option(
                    wind_potential, power_demand, region_type
                )
                power_options.append(wind_offshore_option)
            
            # Hydropower analysis
            if water_resources > 0.5:  # Water resource abundance
                hydro_option = self._analyze_hydro_option(
                    water_resources, power_demand, region_type
                )
                power_options.append(hydro_option)
            
            # Nuclear power analysis
            if self._is_suitable_for_nuclear(lat, lon):
                nuclear_option = self._analyze_nuclear_option(
                    power_demand, region_type
                )
                power_options.append(nuclear_option)
            
            # Sort and rank recommended options
            power_options.sort(key=lambda x: x.suitability_score, reverse=True)
            
            return {
                "region_type": region_type,
                "solar_potential": solar_potential,
                "wind_potential": wind_potential,
                "water_resources": water_resources,
                "power_demand": power_demand,
                "recommended_options": [
                    {
                        "name": option.name,
                        "capacity": option.capacity,
                        "efficiency": option.efficiency,
                        "cost_per_mw": option.cost_per_mw,
                        "land_requirement": option.land_requirement,
                        "suitability_score": option.suitability_score,
                        "description": option.description
                    }
                    for option in power_options
                ],
                "total_land_requirement": sum(opt.land_requirement for opt in power_options),
                "total_cost": sum(opt.cost_per_mw * opt.capacity for opt in power_options)
            }
            
        except Exception as e:
            print(f"Power supply solution analysis failed: {e}")
            return {
                "error": str(e),
                "recommended_options": []
            }
    
    def _get_region_type(self, lat: float, lon: float) -> str:
        """Get region type"""
        if 35 <= lat <= 50 and 110 <= lon <= 125:
            return "North China"
        elif 20 <= lat <= 35 and 110 <= lon <= 125:
            return "South China"
        elif 25 <= lat <= 40 and 100 <= lon <= 110:
            return "Southwest"
        elif 30 <= lat <= 45 and 120 <= lon <= 135:
            return "East China"
        elif 40 <= lat <= 55 and 80 <= lon <= 100:
            return "Northwest"
        else:
            return "Other"
    
    def _calculate_solar_potential(self, lat: float, lon: float) -> float:
        """Calculate solar energy potential"""
        # Base irradiance based on latitude
        base_irradiance = 1000 + (90 - abs(lat)) * 20
        
        # Longitude adjustment
        if lon > 100:
            base_irradiance += 200
        elif lon < 110:
            base_irradiance -= 100
        
        # City-specific adjustments
        city_adjustments = {
            (39.9042, 116.4074): 1500,  # Beijing
            (31.2304, 121.4737): 1200,  # Shanghai
            (22.5431, 114.0579): 1300,  # Shenzhen
            (30.2741, 120.1551): 1400,  # Hangzhou
            (37.5149, 105.1967): 2000,  # Zhongwei
            (26.647,  106.6302): 1200,  # Guiyang
        }
        
        min_distance = float('inf')
        closest_irradiance = base_irradiance
        for (city_lat, city_lon), irradiance in city_adjustments.items():
            distance = ((lat - city_lat) ** 2 + (lon - city_lon) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                closest_irradiance = irradiance
        
        return closest_irradiance
    
    def _calculate_wind_potential(self, lat: float, lon: float) -> float:
        """Calculate wind energy potential"""
        # Base wind speed based on latitude
        base_wind = 3.0 + (90 - abs(lat)) * 0.1
        
        # Longitude adjustment
        if lon > 100:
            base_wind += 1.0
        elif lon < 110:
            base_wind -= 0.5
        
        # City-specific adjustments
        city_adjustments = {
            (39.9042, 116.4074): 4.0,  # Beijing
            (31.2304, 121.4737): 3.5,  # Shanghai
            (22.5431, 114.0579): 4.5,  # Shenzhen
            (30.2741, 120.1551): 3.8,  # Hangzhou
            (37.5149, 105.1967): 5.5,  # Zhongwei
            (26.647,  106.6302): 3.2,  # Guiyang
        }
        
        min_distance = float('inf')
        closest_wind = base_wind
        for (city_lat, city_lon), wind in city_adjustments.items():
            distance = ((lat - city_lat) ** 2 + (lon - city_lon) ** 2) ** 0.5
            if distance < min_distance:
                min_distance = distance
                closest_wind = wind
        
        return closest_wind
    
    def _assess_water_resources(self, lat: float, lon: float) -> float:
        """Assess water resource abundance"""
        # Simple assessment based on geographic location
        if 20 <= lat <= 35 and 110 <= lon <= 125:   # South China
            return 0.8
        elif 25 <= lat <= 40 and 100 <= lon <= 110:  # Southwest
            return 0.9
        elif 30 <= lat <= 45 and 120 <= lon <= 135:  # East China
            return 0.7
        elif 35 <= lat <= 50 and 110 <= lon <= 125:  # North China
            return 0.3
        elif 40 <= lat <= 55 and 80 <= lon <= 100:   # Northwest
            return 0.2
        else:
            return 0.5
    
    def _is_coastal_region(self, lat: float, lon: float) -> bool:
        """Determine whether the location is a coastal region"""
        # Simplified coastal region determination
        coastal_regions = [
            (20, 35, 110, 125),  # South China coast
            (30, 45, 120, 135),  # East China coast
            (35, 50, 115, 125),  # North China coast
        ]
        
        for min_lat, max_lat, min_lon, max_lon in coastal_regions:
            if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                return True
        return False
    
    def _is_suitable_for_nuclear(self, lat: float, lon: float) -> bool:
        """Determine whether the location is suitable for nuclear power"""
        # Nuclear plant siting requirements: coastal, geologically stable, low population density
        return (self._is_coastal_region(lat, lon) and 
                abs(lat) < 50 and  # Avoid high latitudes
                self._assess_water_resources(lat, lon) > 0.6)
    
    def _analyze_solar_option(self, solar_potential: float, power_demand: float, 
                            region_type: str) -> PowerSupplyOption:
        """Analyze solar photovoltaic option"""
        config = self.power_options["solar_pv"]
        
        # Calculate installed capacity
        capacity = power_demand * 1.2  # Account for efficiency losses
        
        # Calculate suitability score
        suitability_score = min(solar_potential / 2000, 1.0) * 0.8  # Base score
        
        if region_type in ["Northwest", "North China", "Northeast"]:
            suitability_score += 0.2  # Regional advantage
        
        return PowerSupplyOption(
            name=config["name"],
            capacity=capacity,
            efficiency=config["efficiency"],
            cost_per_mw=config["cost_per_mw"],
            land_requirement=capacity * config["land_per_mw"],
            suitability_score=suitability_score,
            description=f"Solar photovoltaic solution based on annual irradiance of {solar_potential:.0f} kWh/m²"
        )
    
    def _analyze_wind_onshore_option(self, wind_potential: float, power_demand: float,
                                   region_type: str) -> PowerSupplyOption:
        """Analyze onshore wind power option"""
        config = self.power_options["wind_onshore"]
        
        capacity = power_demand * 1.1
        suitability_score = min(wind_potential / 6.0, 1.0) * 0.7
        
        if region_type in ["Northwest", "North China", "Northeast", "Inner Mongolia"]:
            suitability_score += 0.3
        
        return PowerSupplyOption(
            name=config["name"],
            capacity=capacity,
            efficiency=config["efficiency"],
            cost_per_mw=config["cost_per_mw"],
            land_requirement=capacity * config["land_per_mw"],
            suitability_score=suitability_score,
            description=f"Onshore wind power solution based on average wind speed of {wind_potential:.1f} m/s"
        )
    
    def _analyze_wind_offshore_option(self, wind_potential: float, power_demand: float,
                                    region_type: str) -> PowerSupplyOption:
        """Analyze offshore wind power option"""
        config = self.power_options["wind_offshore"]
        
        capacity = power_demand * 1.05
        suitability_score = min(wind_potential / 7.0, 1.0) * 0.6
        
        if region_type in ["East China", "South China", "Bohai Bay"]:
            suitability_score += 0.4
        
        return PowerSupplyOption(
            name=config["name"],
            capacity=capacity,
            efficiency=config["efficiency"],
            cost_per_mw=config["cost_per_mw"],
            land_requirement=capacity * config["land_per_mw"],
            suitability_score=suitability_score,
            description=f"Offshore wind power solution based on offshore wind speed of {wind_potential:.1f} m/s"
        )
    
    def _analyze_hydro_option(self, water_resources: float, power_demand: float,
                            region_type: str) -> PowerSupplyOption:
        """Analyze hydropower option"""
        config = self.power_options["hydro"]
        
        capacity = power_demand * 0.8  # Hydropower as base load
        suitability_score = water_resources * 0.8
        
        if region_type in ["Southwest", "Central China", "South China"]:
            suitability_score += 0.2
        
        return PowerSupplyOption(
            name=config["name"],
            capacity=capacity,
            efficiency=config["efficiency"],
            cost_per_mw=config["cost_per_mw"],
            land_requirement=capacity * config["land_per_mw"],
            suitability_score=suitability_score,
            description=f"Hydropower solution based on water resource abundance of {water_resources:.1f}"
        )
    
    def _analyze_nuclear_option(self, power_demand: float, region_type: str) -> PowerSupplyOption:
        """Analyze nuclear power option"""
        config = self.power_options["nuclear"]
        
        capacity = power_demand * 2.0  # Nuclear plants are larger in scale
        suitability_score = 0.6  # Base score
        
        if region_type in ["East China", "South China"]:
            suitability_score += 0.3
        
        return PowerSupplyOption(
            name=config["name"],
            capacity=capacity,
            efficiency=config["efficiency"],
            cost_per_mw=config["cost_per_mw"],
            land_requirement=capacity * config["land_per_mw"],
            suitability_score=suitability_score,
            description="Nuclear power solution leveraging coastal geographic advantages"
        )