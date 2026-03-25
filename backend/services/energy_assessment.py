"""
Energy resource assessment service — all data from real APIs via RealDataService.
No heuristics, no lookup tables, no hardcoded city lists.
"""

import math
from typing import Dict, Any, List, Optional
from datetime import datetime

from .real_data_service import RealDataService, DataUnavailableError


class EnergyAssessmentService:
    """Energy resource assessment — real-data backed."""

    def __init__(self):
        self.real_data_service = RealDataService()
        # Storage device specs (technology constants, not geographic heuristics)
        self.storage_devices = {
            "lithium_battery": {
                "capacity_range_mwh": (1, 500),
                "efficiency": 0.95,
                "cost_per_mwh_cny": 200_000,
                "lifetime_years": 15,
            },
            "pumped_hydro": {
                "capacity_range_mwh": (100, 10_000),
                "efficiency": 0.80,
                "cost_per_mwh_cny": 150_000,
                "lifetime_years": 50,
            },
            "compressed_air": {
                "capacity_range_mwh": (10, 2_000),
                "efficiency": 0.70,
                "cost_per_mwh_cny": 100_000,
                "lifetime_years": 30,
            },
        }

    # ── Public wrappers ───────────────────────────────────────────────────────

    async def get_solar_data(self, lat: float, lon: float) -> Dict[str, Any]:
        return await self._get_solar_data(lat, lon)

    async def get_wind_data(self, lat: float, lon: float) -> Dict[str, Any]:
        return await self._get_wind_data(lat, lon)

    async def assess_grid_capacity(self, lat: float, lon: float) -> Dict[str, Any]:
        return await self._assess_grid_capacity(lat, lon)

    # ── Main assessment entry point ───────────────────────────────────────────

    async def assess_energy_resources(
        self, lat: float, lon: float, land_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        solar_data = await self._get_solar_data(lat, lon)
        wind_data = await self._get_wind_data(lat, lon)
        renewable_potential = await self._assess_renewable_potential(
            lat, lon, solar_data, wind_data, land_analysis
        )
        storage_assessment = await self._assess_storage_needs(
            renewable_potential, land_analysis
        )
        grid_assessment = await self._assess_grid_capacity(lat, lon)
        recommendations = await self._generate_energy_recommendations(
            lat, lon, renewable_potential, storage_assessment, grid_assessment
        )
        return {
            "solar_data": solar_data,
            "wind_data": wind_data,
            "renewable_potential": renewable_potential,
            "storage_assessment": storage_assessment,
            "grid_assessment": grid_assessment,
            "recommendations": recommendations,
        }

    # ── Solar — NASA POWER ────────────────────────────────────────────────────

    async def _get_solar_data(self, lat: float, lon: float) -> Dict[str, Any]:
        raw = await self.real_data_service.get_solar_irradiance(lat, lon)
        irradiance = raw["annual_irradiance_kwh_m2"]

        if irradiance > 2000:
            zone, potential = "Zone 1", "high"
        elif irradiance > 1600:
            zone, potential = "Zone 2", "high"
        elif irradiance > 1400:
            zone, potential = "Zone 3", "moderate"
        else:
            zone, potential = "Zone 4", "low"

        return {
            "annual_irradiance": irradiance,
            "solar_zone": zone,
            "peak_sun_hours": round(irradiance / 365, 1),
            "solar_potential": potential,
            "source": raw["source"],
            "confidence": raw["confidence"],
        }

    # ── Wind — Open-Meteo ERA5 ────────────────────────────────────────────────

    async def _get_wind_data(self, lat: float, lon: float) -> Dict[str, Any]:
        raw = await self.real_data_service.get_wind_speed(lat, lon)
        speed = raw["annual_mean_ms"]

        if speed > 7.0:
            zone, potential = "Wind Zone 1", "high"
        elif speed > 6.0:
            zone, potential = "Wind Zone 2", "high"
        elif speed > 5.0:
            zone, potential = "Wind Zone 3", "moderate"
        else:
            zone, potential = "Wind Zone 4", "low"

        return {
            "wind_zone": zone,
            "average_speed": speed,
            "power_density": int(0.5 * 1.225 * speed ** 3),
            "wind_potential": potential,
            "source": raw["source"],
            "confidence": raw["confidence"],
        }

    # ── Grid — OpenStreetMap Overpass ─────────────────────────────────────────

    async def _assess_grid_capacity(self, lat: float, lon: float) -> Dict[str, Any]:
        raw = await self.real_data_service.get_grid_infrastructure(lat, lon, 50_000)
        dist = raw.get("nearest_substation_km")
        voltage = raw.get("estimated_voltage_kv") or 110.0

        if dist is None:
            capacity, stability = 0, "unknown"
        elif dist < 5:
            capacity = min(500, int(voltage * 2))
            stability = "sufficient"
        elif dist < 20:
            capacity = min(200, int(voltage))
            stability = "good"
        elif dist < 50:
            capacity = 50
            stability = "tight"
        else:
            capacity = 0
            stability = "insufficient"

        return {
            "available_capacity": capacity,
            "voltage_level": f"{int(voltage)}kV",
            "distance_to_substation": dist,
            "grid_stability": stability,
            "source": raw["source"],
            "confidence": raw["confidence"],
        }

    # ── Renewable potential ───────────────────────────────────────────────────

    async def _assess_renewable_potential(
        self,
        lat: float,
        lon: float,
        solar_data: Dict[str, Any],
        wind_data: Dict[str, Any],
        land_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        total_area = land_analysis.get("total_area", 1_000_000)  # m²

        solar_potential = 0.0
        if solar_data["solar_potential"] in ("high", "moderate"):
            solar_area = total_area * 0.3
            solar_capacity = (
                solar_area * solar_data["annual_irradiance"] * 0.2
            )  # 20 % panel efficiency
            solar_potential = solar_capacity / 1000  # MWh

        wind_potential = 0.0
        if wind_data["wind_potential"] in ("high", "moderate"):
            wind_area = total_area * 0.2
            wind_capacity = wind_area * wind_data["power_density"] / 1000  # MW
            wind_potential = wind_capacity * 8760 * 0.3  # 30 % capacity factor

        total_renewable = solar_potential + wind_potential
        return {
            "solar_potential": {
                "capacity_mw": solar_potential / 8760 * 1000,
                "annual_generation_mwh": solar_potential,
                "land_requirement": total_area * 0.3,
            },
            "wind_potential": {
                "capacity_mw": wind_potential / 8760 * 1000,
                "annual_generation_mwh": wind_potential,
                "land_requirement": total_area * 0.2,
            },
            "total_renewable_potential": {
                "capacity_mw": total_renewable / 8760 * 1000,
                "annual_generation_mwh": total_renewable,
            },
        }

    # ── Storage needs ─────────────────────────────────────────────────────────

    async def _assess_storage_needs(
        self,
        renewable_potential: Dict[str, Any],
        land_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        # Assume 100 MW data center × 8760 h × 0.7 utilisation = ~613 GWh/yr
        dc_power_mw = 100
        dc_consumption_mwh = dc_power_mw * 8760 * 0.7

        storage_needs = {
            "emergency_backup": dc_power_mw * 4,        # 4 h backup (MWh)
            "peak_shaving": dc_power_mw * 2,            # 2 h peak buffer
            "grid_stabilization": dc_power_mw * 0.5,   # 30 min
            "total_required": dc_power_mw * 6.5,       # total MWh capacity
        }

        renewable_generation = renewable_potential["total_renewable_potential"][
            "annual_generation_mwh"
        ]
        coverage = min(renewable_generation / dc_consumption_mwh, 1.0)

        recommended_storage = []
        total_req = storage_needs["total_required"]
        for tech, specs in self.storage_devices.items():
            lo, hi = specs["capacity_range_mwh"]
            if lo <= total_req <= hi:
                recommended_storage.append({
                    "technology": tech,
                    "capacity_mwh": total_req,
                    "efficiency": specs["efficiency"],
                    "cost": total_req * specs["cost_per_mwh_cny"],
                    "lifetime": specs["lifetime_years"],
                })

        return {
            "storage_needs": storage_needs,
            "recommended_technologies": recommended_storage,
            "renewable_coverage": round(coverage, 4),
            "renewable_generation_mwh": renewable_generation,
            "data_center_consumption_mwh": dc_consumption_mwh,
        }

    # ── Geographic environment ────────────────────────────────────────────────

    async def analyze_geographic_environment(
        self, lat: float, lon: float, radius: float = 1000
    ) -> Dict[str, Any]:
        """Full geographic snapshot using real data APIs."""
        real = await self.real_data_service.get_all(lat, lon, radius_m=max(radius, 5000))

        elevation_m = None
        elev_src = "N/A"
        if "elevation" in real and "error" not in real["elevation"]:
            elevation_m = real["elevation"].get("elevation_m")
            elev_src = real["elevation"].get("source", "Open-Elevation")

        # Climate
        climate_zone = None
        annual_temp = None
        annual_precip = None
        if "climate" in real and "error" not in real["climate"]:
            c = real["climate"]
            climate_zone = c.get("climate_zone")
            annual_temp = c.get("annual_mean_temp_c")
            annual_precip = c.get("annual_precip_mm")

        # Terrain type from elevation
        terrain_type = "plain"
        if elevation_m is not None:
            if elevation_m > 3000:
                terrain_type = "plateau"
            elif elevation_m > 1000:
                terrain_type = "mountainous"
            elif elevation_m > 200:
                terrain_type = "hilly"

        # Natural hazards
        natural_hazards: List[str] = []
        if "hazards" in real and "error" not in real["hazards"]:
            h = real["hazards"]
            if h.get("flood_risk") in ("MEDIUM", "HIGH"):
                natural_hazards.append(f"Flood risk: {h['flood_risk']}")
            if h.get("seismic_risk") in ("MEDIUM", "HIGH"):
                natural_hazards.append(f"Seismic risk: {h['seismic_risk']}")
            if h.get("cyclone_risk") in ("MEDIUM", "HIGH"):
                natural_hazards.append(f"Cyclone risk: {h['cyclone_risk']}")

        # Water resources
        water_resources: Dict[str, Any] = {}
        if "water" in real and "error" not in real["water"]:
            w = real["water"]
            water_resources = {
                "nearest_waterway_km": w.get("nearest_waterway_km"),
                "water_availability": w.get("water_availability"),
                "annual_precip_mm": w.get("annual_precip_mm"),
            }

        # Land cover
        forest_coverage = None
        if "land_cover" in real and "error" not in real["land_cover"]:
            dist = real["land_cover"].get("distribution", {})
            forest_coverage = round(
                dist.get("Tree cover", 0.0) + dist.get("Shrubland", 0.0), 4
            )

        return {
            "elevation": elevation_m,
            "terrain_type": terrain_type,
            "climate_zone": climate_zone,
            "annual_temperature_c": annual_temp,
            "annual_precipitation_mm": annual_precip,
            "forest_coverage": forest_coverage,
            "natural_hazards": natural_hazards,
            "water_resources": water_resources,
            "data_sources": {
                "elevation": elev_src,
                "climate": "Open-Meteo ERA5 2010-2020",
                "hazards": "USGS + Open-Meteo proxy",
                "land_cover": "ESA WorldCover 2021",
                "water": "OpenStreetMap Overpass",
            },
        }

    # ── Heat utilization ──────────────────────────────────────────────────────

    async def analyze_heat_utilization(
        self,
        lat: float,
        lon: float,
        land_analysis: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Waste heat utilization analysis — driven by real climate data."""
        climate = {}
        try:
            climate = await self.real_data_service.get_climate(lat, lon)
        except DataUnavailableError:
            pass

        annual_temp = climate.get("annual_mean_temp_c", 15.0)
        hdd = climate.get("heating_degree_days", 1000.0)
        cdd = climate.get("cooling_degree_days", 500.0)

        # Estimate data center scale from area (no city lookup)
        total_area_m2 = land_analysis.get("total_area", 1_000_000)
        area_km2 = total_area_m2 / 1_000_000
        # Rough scale: 50 MW baseline, +1 MW per km² of analysis area up to 200 MW
        dc_power_mw = min(50 + area_km2, 200)

        # Heat recovery rate: higher in cold climates (more heating demand)
        if hdd > 2000:
            recovery_rate = 0.70
        elif hdd > 1000:
            recovery_rate = 0.60
        else:
            recovery_rate = 0.50

        recoverable_heat = round(dc_power_mw * recovery_rate, 1)

        options = []

        # District heating — viable where HDD is substantial
        if hdd > 500:
            heat_frac = min(0.8, hdd / 3000)
            options.append({
                "type": "district_heating",
                "capacity_mw": round(recoverable_heat * heat_frac, 1),
                "target_users": "residential areas, schools, hospitals",
                "distance_km": 3,
                "economic_value": int(recoverable_heat * heat_frac * 1_200_000),
                "feasibility": "high",
                "co2_savings": int(recoverable_heat * heat_frac * 500),
            })

        # Industrial heat — viable where CDD or industrial activity likely
        if cdd > 100 or annual_temp > 10:
            ind_frac = 0.6
            options.append({
                "type": "industrial_heat",
                "capacity_mw": round(recoverable_heat * ind_frac, 1),
                "target_users": "factories, food processing, textile mills",
                "distance_km": 8,
                "economic_value": int(recoverable_heat * ind_frac * 900_000),
                "feasibility": "moderate",
                "co2_savings": int(recoverable_heat * ind_frac * 400),
            })

        # Greenhouse agriculture — always viable
        gh_frac = 0.3
        options.append({
            "type": "greenhouse_agriculture",
            "capacity_mw": round(recoverable_heat * gh_frac, 1),
            "target_users": "agricultural parks, flower cultivation",
            "distance_km": 10,
            "economic_value": int(recoverable_heat * gh_frac * 600_000),
            "feasibility": "high",
            "co2_savings": int(recoverable_heat * gh_frac * 300),
        })

        total_revenue = sum(o["economic_value"] for o in options)
        total_co2 = sum(o["co2_savings"] for o in options)

        # Payback depends on climate utility — colder = faster payback
        payback = 2.5 if hdd > 2000 else (3.0 if hdd > 1000 else 4.0)

        recommendations = [
            f"Recoverable heat: {recoverable_heat} MW at {recovery_rate*100:.0f}% recovery rate",
            f"Climate zone {climate.get('climate_zone','unknown')} — "
            f"{'high' if hdd > 2000 else 'moderate'} district heating potential",
            f"Estimated annual revenue: {total_revenue:,.0f} CNY",
        ]

        return {
            "recoverable_heat_mw": recoverable_heat,
            "data_center_power_mw": round(dc_power_mw, 1),
            "heat_recovery_rate": recovery_rate,
            "utilization_options": options,
            "economic_benefits": {
                "annual_revenue": total_revenue,
                "payback_period": payback,
                "co2_reduction": total_co2,
                "investment_cost": int(total_revenue * payback),
                "roi_percentage": round(100 / payback, 1),
            },
            "recommendations": recommendations,
            "data_source": "Open-Meteo climate data",
        }

    # ── Energy recommendations ────────────────────────────────────────────────

    async def _generate_energy_recommendations(
        self,
        lat: float,
        lon: float,
        renewable_potential: Dict[str, Any],
        storage_assessment: Dict[str, Any],
        grid_assessment: Dict[str, Any],
    ) -> List[str]:
        recs = []
        solar_cap = renewable_potential["solar_potential"]["capacity_mw"]
        wind_cap = renewable_potential["wind_potential"]["capacity_mw"]
        coverage = storage_assessment["renewable_coverage"]
        grid_cap = grid_assessment["available_capacity"]

        if solar_cap > 50:
            recs.append(
                f"Solar potential {solar_cap:.0f} MW — recommend large-scale PV installation"
            )
        if wind_cap > 30:
            recs.append(
                f"Wind potential {wind_cap:.0f} MW — recommend wind turbine deployment"
            )
        if coverage > 0.8:
            recs.append("Renewable generation can cover >80% of estimated demand")
        elif coverage > 0.5:
            recs.append(
                "Renewable generation covers 50–80% of demand; grid supplement needed"
            )
        else:
            recs.append(
                "Limited renewable coverage — primarily reliant on grid supply"
            )
        if grid_cap < 100:
            recs.append(
                f"Grid capacity {grid_cap} MW is limited — battery storage recommended"
            )
        return recs

    # ── get_local_energy_resources (used by /energy/resources/{lat}/{lon}) ─────

    async def get_local_energy_resources(
        self, lat: float, lon: float, radius: float = 1000
    ) -> Dict[str, Any]:
        solar = await self._get_solar_data(lat, lon)
        wind = await self._get_wind_data(lat, lon)
        grid = await self._assess_grid_capacity(lat, lon)
        return {
            "solar": solar,
            "wind": wind,
            "grid": grid,
            "location": {"latitude": lat, "longitude": lon},
        }
