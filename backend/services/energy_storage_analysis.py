"""
Energy storage layout analysis service - analyzes storage center layout and configuration
"""

import math
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class StorageOption:
    """Energy storage option"""
    name: str
    capacity: float  # Storage capacity (MWh)
    power: float  # Power (MW)
    efficiency: float  # Efficiency
    cost_per_mwh: float  # Cost per MWh (10k CNY)
    land_requirement: float  # Land requirement (km²)
    lifespan: int  # Lifespan (years)
    suitability_score: float  # Suitability score
    description: str

class EnergyStorageAnalysisService:
    """Energy storage layout analysis service class"""
    
    def __init__(self):
        """Initialize energy storage analysis service"""
        self.storage_technologies = {
            "lithium_battery": {
                "name": "Lithium-ion battery",
                "efficiency": 0.90,
                "cost_per_mwh": 200,  # 10k CNY/MWh
                "land_per_mwh": 0.001,  # km²/MWh
                "lifespan": 15,
                "suitable_for": ["peak_shaving", "frequency_regulation", "emergency_backup"]
            },
            "pumped_hydro": {
                "name": "Pumped hydro storage",
                "efficiency": 0.75,
                "cost_per_mwh": 150,
                "land_per_mwh": 0.01,
                "lifespan": 50,
                "suitable_for": ["large_scale_storage", "peak_shaving", "frequency_regulation"]
            },
            "compressed_air": {
                "name": "Compressed air energy storage",
                "efficiency": 0.70,
                "cost_per_mwh": 180,
                "land_per_mwh": 0.005,
                "lifespan": 30,
                "suitable_for": ["large_scale_storage", "peak_shaving"]
            },
            "flow_battery": {
                "name": "Flow battery",
                "efficiency": 0.80,
                "cost_per_mwh": 300,
                "land_per_mwh": 0.002,
                "lifespan": 20,
                "suitable_for": ["long_duration_storage", "peak_shaving"]
            },
            "hydrogen_storage": {
                "name": "Hydrogen energy storage",
                "efficiency": 0.60,
                "cost_per_mwh": 400,
                "land_per_mwh": 0.003,
                "lifespan": 25,
                "suitable_for": ["long_term_storage", "cross_season_storage"]
            }
        }
    
    async def analyze_storage_layout(self, lat: float, lon: float, 
                                   power_demand: float = 100,
                                   renewable_ratio: float = 0.7) -> Dict[str, Any]:
        """
        Analyze energy storage layout options
        
        Args:
            lat: Latitude
            lon: Longitude
            power_demand: Power demand (MW)
            renewable_ratio: Renewable energy ratio
            
        Returns:
            Energy storage layout analysis result
        """
        try:
            # Calculate storage requirements
            storage_requirements = self._calculate_storage_requirements(
                power_demand, renewable_ratio
            )
            
            # Get terrain conditions
            terrain_type = self._get_terrain_type(lat, lon)
            water_availability = self._assess_water_availability(lat, lon)
            land_availability = self._assess_land_availability(lat, lon)
            
            # Analyze various storage options
            storage_options = []
            
            # Lithium-ion battery analysis
            if land_availability > 0.1:  # Requires some land
                lithium_option = self._analyze_lithium_battery(
                    storage_requirements, terrain_type, land_availability
                )
                storage_options.append(lithium_option)
            
            # Pumped hydro storage analysis
            if water_availability > 0.6 and terrain_type in ["mountainous", "hilly"]:
                pumped_hydro_option = self._analyze_pumped_hydro(
                    storage_requirements, terrain_type, water_availability
                )
                storage_options.append(pumped_hydro_option)
            
            # Compressed air energy storage analysis
            if terrain_type in ["plain", "hilly"] and land_availability > 0.2:
                caes_option = self._analyze_compressed_air(
                    storage_requirements, terrain_type, land_availability
                )
                storage_options.append(caes_option)
            
            # Flow battery analysis
            if land_availability > 0.05:
                flow_battery_option = self._analyze_flow_battery(
                    storage_requirements, terrain_type, land_availability
                )
                storage_options.append(flow_battery_option)
            
            # Hydrogen energy storage analysis
            if land_availability > 0.3:  # Requires larger land area
                hydrogen_option = self._analyze_hydrogen_storage(
                    storage_requirements, terrain_type, land_availability
                )
                storage_options.append(hydrogen_option)
            
            # Sort recommended options
            storage_options.sort(key=lambda x: x.suitability_score, reverse=True)
            
            # Calculate combined storage plan
            recommended_combination = self._recommend_storage_combination(
                storage_options, storage_requirements
            )
            
            return {
                "storage_requirements": storage_requirements,
                "terrain_type": terrain_type,
                "water_availability": water_availability,
                "land_availability": land_availability,
                "available_options": [
                    {
                        "name": option.name,
                        "capacity": option.capacity,
                        "power": option.power,
                        "efficiency": option.efficiency,
                        "cost_per_mwh": option.cost_per_mwh,
                        "land_requirement": option.land_requirement,
                        "lifespan": option.lifespan,
                        "suitability_score": option.suitability_score,
                        "description": option.description
                    }
                    for option in storage_options
                ],
                "recommended_combination": recommended_combination,
                "total_storage_capacity": sum(opt.capacity for opt in storage_options),
                "total_land_requirement": sum(opt.land_requirement for opt in storage_options),
                "total_cost": sum(opt.cost_per_mwh * opt.capacity for opt in storage_options)
            }
            
        except Exception as e:
            print(f"Energy storage layout analysis failed: {e}")
            return {
                "error": str(e),
                "available_options": [],
                "recommended_combination": []
            }
    
    def _calculate_storage_requirements(self, power_demand: float, 
                                      renewable_ratio: float) -> Dict[str, float]:
        """Calculate storage requirements"""
        # Base storage need: 20-30% of renewable energy generation
        base_storage = power_demand * renewable_ratio * 0.25
        
        # Emergency backup: 10% of total demand
        emergency_backup = power_demand * 0.1
        
        # Peak shaving: 15% of total demand
        peak_shaving = power_demand * 0.15
        
        # Frequency regulation: 5% of total demand
        frequency_regulation = power_demand * 0.05
        
        return {
            "base_storage": base_storage,
            "emergency_backup": emergency_backup,
            "peak_shaving": peak_shaving,
            "frequency_regulation": frequency_regulation,
            "total_energy": base_storage + emergency_backup + peak_shaving,
            "total_power": power_demand * 0.3  # Total power requirement
        }
    
    def _get_terrain_type(self, lat: float, lon: float) -> str:
        """Get terrain type"""
        # Simplified terrain classification
        if 25 <= lat <= 35 and 100 <= lon <= 110:  # Southwest mountain area
            return "mountainous"
        elif 30 <= lat <= 40 and 110 <= lon <= 120:  # North China Plain
            return "plain"
        elif 20 <= lat <= 30 and 110 <= lon <= 120:  # South China hills
            return "hilly"
        elif 40 <= lat <= 50 and 80 <= lon <= 100:  # Northwest plateau
            return "plateau"
        else:
            return "plain"
    
    def _assess_water_availability(self, lat: float, lon: float) -> float:
        """Assess water resource availability"""
        # Simple assessment based on geographic location
        if 20 <= lat <= 35 and 110 <= lon <= 125:  # South China
            return 0.9
        elif 25 <= lat <= 40 and 100 <= lon <= 110:  # Southwest China
            return 0.8
        elif 30 <= lat <= 45 and 120 <= lon <= 135:  # East China
            return 0.7
        elif 35 <= lat <= 50 and 110 <= lon <= 125:  # North China
            return 0.4
        elif 40 <= lat <= 55 and 80 <= lon <= 100:  # Northwest China
            return 0.2
        else:
            return 0.5
    
    def _assess_land_availability(self, lat: float, lon: float) -> float:
        """Assess land availability"""
        # Simple assessment based on population density and geographic conditions
        if 40 <= lat <= 55 and 80 <= lon <= 100:  # Northwest China
            return 0.9
        elif 25 <= lat <= 40 and 100 <= lon <= 110:  # Southwest China
            return 0.7
        elif 30 <= lat <= 45 and 120 <= lon <= 135:  # East China
            return 0.4
        elif 35 <= lat <= 50 and 110 <= lon <= 125:  # North China
            return 0.5
        elif 20 <= lat <= 30 and 110 <= lon <= 120:  # South China
            return 0.3
        else:
            return 0.6
    
    def _analyze_lithium_battery(self, requirements: Dict[str, float], 
                               terrain_type: str, land_availability: float) -> StorageOption:
        """Analyze lithium-ion battery option"""
        config = self.storage_technologies["lithium_battery"]
        
        capacity = requirements["total_energy"]
        power = requirements["total_power"]
        
        # Calculate suitability score
        suitability_score = 0.8  # Base score
        
        if terrain_type in ["plain", "hilly"]:
            suitability_score += 0.1
        
        if land_availability > 0.5:
            suitability_score += 0.1
        
        return StorageOption(
            name=config["name"],
            capacity=capacity,
            power=power,
            efficiency=config["efficiency"],
            cost_per_mwh=config["cost_per_mwh"],
            land_requirement=capacity * config["land_per_mwh"],
            lifespan=config["lifespan"],
            suitability_score=suitability_score,
            description="Lithium-ion battery storage system suitable for peak shaving and frequency regulation"
        )
    
    def _analyze_pumped_hydro(self, requirements: Dict[str, float], 
                            terrain_type: str, water_availability: float) -> StorageOption:
        """Analyze pumped hydro storage option"""
        config = self.storage_technologies["pumped_hydro"]
        
        capacity = requirements["total_energy"] * 1.5  # Pumped hydro has larger capacity
        power = requirements["total_power"] * 0.8
        
        suitability_score = 0.6  # Base score
        
        if terrain_type in ["mountainous", "hilly"]:
            suitability_score += 0.3
        
        if water_availability > 0.7:
            suitability_score += 0.2
        
        return StorageOption(
            name=config["name"],
            capacity=capacity,
            power=power,
            efficiency=config["efficiency"],
            cost_per_mwh=config["cost_per_mwh"],
            land_requirement=capacity * config["land_per_mwh"],
            lifespan=config["lifespan"],
            suitability_score=suitability_score,
            description=f"Pumped hydro storage system based on {terrain_type} terrain and water resources"
        )
    
    def _analyze_compressed_air(self, requirements: Dict[str, float], 
                              terrain_type: str, land_availability: float) -> StorageOption:
        """Analyze compressed air energy storage option"""
        config = self.storage_technologies["compressed_air"]
        
        capacity = requirements["total_energy"] * 1.2
        power = requirements["total_power"] * 0.9
        
        suitability_score = 0.7  # Base score
        
        if terrain_type in ["plain", "hilly"]:
            suitability_score += 0.2
        
        if land_availability > 0.6:
            suitability_score += 0.1
        
        return StorageOption(
            name=config["name"],
            capacity=capacity,
            power=power,
            efficiency=config["efficiency"],
            cost_per_mwh=config["cost_per_mwh"],
            land_requirement=capacity * config["land_per_mwh"],
            lifespan=config["lifespan"],
            suitability_score=suitability_score,
            description=f"Large-scale compressed air energy storage system suitable for {terrain_type} terrain"
        )
    
    def _analyze_flow_battery(self, requirements: Dict[str, float], 
                            terrain_type: str, land_availability: float) -> StorageOption:
        """Analyze flow battery option"""
        config = self.storage_technologies["flow_battery"]
        
        capacity = requirements["total_energy"] * 0.8
        power = requirements["total_power"] * 0.6
        
        suitability_score = 0.75  # Base score
        
        if land_availability > 0.3:
            suitability_score += 0.15
        
        return StorageOption(
            name=config["name"],
            capacity=capacity,
            power=power,
            efficiency=config["efficiency"],
            cost_per_mwh=config["cost_per_mwh"],
            land_requirement=capacity * config["land_per_mwh"],
            lifespan=config["lifespan"],
            suitability_score=suitability_score,
            description="Flow battery system suitable for long-duration energy storage"
        )
    
    def _analyze_hydrogen_storage(self, requirements: Dict[str, float], 
                                terrain_type: str, land_availability: float) -> StorageOption:
        """Analyze hydrogen energy storage option"""
        config = self.storage_technologies["hydrogen_storage"]
        
        capacity = requirements["total_energy"] * 2.0  # Hydrogen storage has large capacity
        power = requirements["total_power"] * 0.5
        
        suitability_score = 0.6  # Base score
        
        if land_availability > 0.7:
            suitability_score += 0.3
        
        return StorageOption(
            name=config["name"],
            capacity=capacity,
            power=power,
            efficiency=config["efficiency"],
            cost_per_mwh=config["cost_per_mwh"],
            land_requirement=capacity * config["land_per_mwh"],
            lifespan=config["lifespan"],
            suitability_score=suitability_score,
            description="Hydrogen energy system suitable for long-term and cross-season energy storage"
        )
    
    def _recommend_storage_combination(self, options: List[StorageOption], 
                                     requirements: Dict[str, float]) -> List[Dict[str, Any]]:
        """Recommend combined storage plan"""
        if not options:
            return []
        
        # Select the top 3 most suitable options
        top_options = options[:3]
        
        combination = []
        remaining_energy = requirements["total_energy"]
        remaining_power = requirements["total_power"]
        
        for option in top_options:
            if remaining_energy > 0 and remaining_power > 0:
                # Calculate each option proportion in the combination
                energy_ratio = min(option.capacity / requirements["total_energy"], 1.0)
                power_ratio = min(option.power / requirements["total_power"], 1.0)
                
                combination.append({
                    "name": option.name,
                    "energy_ratio": energy_ratio,
                    "power_ratio": power_ratio,
                    "capacity": option.capacity * energy_ratio,
                    "power": option.power * power_ratio,
                    "suitability_score": option.suitability_score,
                    "description": option.description
                })
                
                remaining_energy -= option.capacity * energy_ratio
                remaining_power -= option.power * power_ratio
        
        return combination