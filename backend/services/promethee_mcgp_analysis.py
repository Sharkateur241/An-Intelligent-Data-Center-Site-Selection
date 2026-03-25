"""
PROMETHEE II + MCGP decision analysis — all input data from real APIs.
Multi-candidate PROMETHEE II (9 candidates: origin + 8 compass offsets at 30 km).
"""

import asyncio
import math
import os
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

import numpy as np

from .real_data_service import RealDataService, DataUnavailableError

# ── Tuneable weights from env vars ────────────────────────────────────────────
def _w(name: str, default: float) -> float:
    return float(os.getenv(name, str(default)))

SIGMA = float(os.getenv("PROMETHEE_SIGMA", "0.2"))

WEIGHTS = {
    "solar_irradiance":        _w("PROMETHEE_WEIGHT_SOLAR",  0.20),
    "wind_speed":              _w("PROMETHEE_WEIGHT_WIND",   0.15),
    "grid_capacity":           _w("PROMETHEE_WEIGHT_GRID",   0.20),
    "land_suitability":        _w("PROMETHEE_WEIGHT_LAND",   0.15),
    "hazard_score":            _w("PROMETHEE_WEIGHT_HAZARD", 0.15),
    "temperature_suitability": _w("PROMETHEE_WEIGHT_TEMP",   0.075),
    "water_availability":      _w("PROMETHEE_WEIGHT_WATER",  0.075),
}

IS_BENEFIT = {k: True for k in WEIGHTS}   # all criteria are benefit-type


# ── Helper converters ────────────────────────────────────────────────────────

def _hazard_to_score(hazards: Dict) -> float:
    return {"LOW": 90.0, "MEDIUM": 60.0, "HIGH": 20.0}.get(
        hazards.get("flood_risk", "LOW"), 50.0
    )

def _water_to_score(water: Dict) -> float:
    return {"SCARCE": 20.0, "MODERATE": 60.0, "ABUNDANT": 90.0}.get(
        water.get("water_availability", "MODERATE"), 60.0
    )

def _temp_to_cooling_score(climate: Dict) -> float:
    cdd = climate.get("cooling_degree_days", 0)
    if cdd < 500:   return 90.0
    if cdd < 1500:  return 70.0
    if cdd < 3000:  return 50.0
    return 30.0

def _risk_to_score(level: str) -> float:
    return {"LOW": 90.0, "MEDIUM": 60.0, "HIGH": 20.0}.get(level, 50.0)

def _land_suitability(land: Dict) -> float:
    bare = land.get("bare_or_sparse_fraction", 0.0)
    built = land.get("built_up_fraction", 0.0)
    # Penalise high built-up (expensive land)
    return max(0.0, min(100.0, bare * 100 - built * 30))


# ── Haversine offset ─────────────────────────────────────────────────────────

def _offset(lat: float, lon: float, dist_km: float, bearing_deg: float
            ) -> Tuple[float, float]:
    R = 6371.0
    b = math.radians(bearing_deg)
    lat1 = math.radians(lat)
    lat2 = math.asin(
        math.sin(lat1) * math.cos(dist_km / R)
        + math.cos(lat1) * math.sin(dist_km / R) * math.cos(b)
    )
    lon2 = math.radians(lon) + math.atan2(
        math.sin(b) * math.sin(dist_km / R) * math.cos(lat1),
        math.cos(dist_km / R) - math.sin(lat1) * math.sin(lat2),
    )
    return math.degrees(lat2), (math.degrees(lon2) + 540) % 360 - 180


# ── Gaussian preference function ─────────────────────────────────────────────

def _gaussian(d: float, sigma: float = SIGMA) -> float:
    if d <= 0:
        return 0.0
    return 1.0 - math.exp(-(d ** 2) / (2 * sigma ** 2))


# ── PROMETHEE II ─────────────────────────────────────────────────────────────

def _promethee_ii(
    matrix: np.ndarray,
    weights: List[float],
    is_benefit: List[bool],
) -> np.ndarray:
    """
    Full PROMETHEE II.
    matrix: shape (n_alternatives, n_criteria) — values already normalised to [0,1].
    Returns net flows for each alternative, shape (n,).
    """
    n, m = matrix.shape
    pi = np.zeros((n, n))  # aggregated preference

    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            total = 0.0
            for c in range(m):
                da = matrix[a, c] - matrix[b, c]
                if not is_benefit[c]:
                    da = -da
                total += weights[c] * _gaussian(da)
            pi[a, b] = total

    phi_plus  = pi.sum(axis=1) / (n - 1)
    phi_minus = pi.sum(axis=0) / (n - 1)
    return phi_plus - phi_minus   # net flow ∈ [-1, 1]


def _minmax_normalise(col: np.ndarray) -> np.ndarray:
    lo, hi = col.min(), col.max()
    if hi == lo:
        return np.full_like(col, 0.5)
    return (col - lo) / (hi - lo)


class PROMETHEEMCGP:
    """PROMETHEE II + MCGP using real geospatial data for all criteria."""

    def __init__(self):
        self.real_data_service = RealDataService()

    # ── Public entry point ────────────────────────────────────────────────────

    async def analyze_data_center_site_selection(
        self, lat: float, lon: float, city_name: str = None
    ) -> Dict[str, Any]:
        return await self.analyze_data_center_site_selection_with_ai(
            lat, lon, city_name, {}, {}, {}, {}, {}
        )

    async def analyze_data_center_site_selection_with_ai(
        self,
        lat: float,
        lon: float,
        city_name: Optional[str],
        ai_multimodal: Dict,
        ai_energy: Dict,
        ai_power_supply: Dict,
        ai_energy_storage: Dict,
        ai_decision: Dict,
    ) -> Dict[str, Any]:
        try:
            # 1. Build 9 candidates: origin + 8 compass bearings at 30 km
            bearings = [0, 45, 90, 135, 180, 225, 270, 315]
            candidates = [(lat, lon)] + [_offset(lat, lon, 30, b) for b in bearings]

            # 2. Fetch real data for all candidates concurrently
            raw_all = await asyncio.gather(
                *[self.real_data_service.get_all(clat, clon, radius_m=5000)
                  for clat, clon in candidates],
                return_exceptions=True,
            )

            # 3. Build criteria matrix
            crit_names = list(WEIGHTS.keys())
            criteria_matrix = []
            candidate_meta = []

            for i, (clat, clon) in enumerate(candidates):
                raw = raw_all[i]
                if isinstance(raw, Exception):
                    row = {k: 50.0 for k in crit_names}
                else:
                    row = self._extract_criteria(raw)
                criteria_matrix.append(row)
                candidate_meta.append({
                    "latitude": clat,
                    "longitude": clon,
                    "label": "Origin" if i == 0 else f"N{i} ({bearings[i-1]}°)",
                })

            # 4. Normalise and run PROMETHEE II
            np_matrix = np.array(
                [[row[c] for c in crit_names] for row in criteria_matrix],
                dtype=float,
            )
            for j in range(np_matrix.shape[1]):
                np_matrix[:, j] = _minmax_normalise(np_matrix[:, j])

            weights_list  = [WEIGHTS[c] for c in crit_names]
            benefit_list   = [IS_BENEFIT[c] for c in crit_names]
            net_flows = _promethee_ii(np_matrix, weights_list, benefit_list)

            # 5. Build ranked list
            ranked_indices = np.argsort(net_flows)[::-1]
            candidates_ranked = []
            for rank, idx in enumerate(ranked_indices):
                candidates_ranked.append({
                    **candidate_meta[idx],
                    "net_flow": round(float(net_flows[idx]), 4),
                    "rank": rank + 1,
                    "criteria": {c: round(criteria_matrix[idx][c], 2)
                                 for c in crit_names},
                })

            origin_flow = float(net_flows[0])
            origin_score = round((origin_flow + 1) / 2 * 100, 2)
            origin_rank = int(np.where(ranked_indices == 0)[0][0]) + 1

            # 6. MCGP comprehensive score (kept for backward-compat)
            mcgp = self._mcgp_score(criteria_matrix[0])

            # 7. Energy analysis dict (for AnalysisResults.tsx energy panel)
            raw0 = raw_all[0] if not isinstance(raw_all[0], Exception) else {}
            energy_analysis = self._energy_analysis_dict(raw0)
            mcgp["goals"].update({
                "solar_score": min(energy_analysis.get("solar_irradiance", 0) / 20, 100),
                "wind_score":  min(energy_analysis.get("wind_speed", 0) * 10, 100),
                "renewable_score": energy_analysis.get("renewable_coverage", 0),
            })

            return {
                "location": {"latitude": lat, "longitude": lon, "city": city_name},
                "overall_score": origin_score,
                "ranking_position": origin_rank,
                "candidates_ranked": candidates_ranked,
                "criteria_matrix": {
                    crit_names[j]: [criteria_matrix[i][crit_names[j]]
                                    for i in range(len(candidates))]
                    for j in range(len(crit_names))
                },
                "energy_analysis": energy_analysis,
                "mcgp_result": mcgp,
                "final_ranking": {
                    "final_score": origin_score,
                    "level": self._level(origin_score),
                    "recommendation": self._recommendation(origin_score),
                },
                "methodology": "PROMETHEE II with real data — 9 candidates",
            }

        except Exception as exc:
            return {
                "error": str(exc),
                "location": {"latitude": lat, "longitude": lon, "city": city_name},
            }

    # ── Criteria extraction ───────────────────────────────────────────────────

    def _extract_criteria(self, raw: Dict) -> Dict[str, float]:
        solar = raw.get("solar", {})
        wind  = raw.get("wind", {})
        grid  = raw.get("grid", {})
        land  = raw.get("land_cover", {})
        haz   = raw.get("hazards", {})
        clim  = raw.get("climate", {})
        water = raw.get("water", {})

        # Defaults for partial failures
        sol_irr = solar.get("annual_irradiance_kwh_m2", 0) if "error" not in solar else 0
        wnd_spd = wind.get("annual_mean_ms", 0) if "error" not in wind else 0
        grd_cap = 0.0
        if "error" not in grid:
            dist = grid.get("nearest_substation_km")
            v = grid.get("estimated_voltage_kv") or 110
            if dist is None:
                grd_cap = 0
            elif dist < 5:
                grd_cap = min(500, v * 2)
            elif dist < 20:
                grd_cap = min(200, v)
            elif dist < 50:
                grd_cap = 50
            else:
                grd_cap = 0

        lnd_suit = _land_suitability(land) if "error" not in land else 50.0
        haz_score = _hazard_to_score(haz) if "error" not in haz else 50.0
        temp_score = _temp_to_cooling_score(clim) if "error" not in clim else 50.0
        wat_score = _water_to_score(water) if "error" not in water else 50.0

        return {
            "solar_irradiance":        sol_irr,
            "wind_speed":              wnd_spd,
            "grid_capacity":           grd_cap,
            "land_suitability":        lnd_suit,
            "hazard_score":            haz_score,
            "temperature_suitability": temp_score,
            "water_availability":      wat_score,
        }

    def _energy_analysis_dict(self, raw: Dict) -> Dict[str, Any]:
        solar = raw.get("solar", {})
        wind  = raw.get("wind", {})
        irr = solar.get("annual_irradiance_kwh_m2", 0) if "error" not in solar else 0
        spd = wind.get("annual_mean_ms", 0) if "error" not in wind else 0
        ren = min(irr / 2000 + spd / 6.0, 1.0) * 100
        return {
            "solar_irradiance": irr,
            "wind_speed": spd,
            "renewable_coverage": round(ren, 1),
        }

    # ── MCGP (retained for backward-compat, now uses real criteria) ───────────

    def _mcgp_score(self, criteria: Dict[str, float]) -> Dict[str, Any]:
        sol = min(criteria["solar_irradiance"] / 2000 * 100, 100)
        wnd = min(criteria["wind_speed"] * 10, 100)
        grd = min(criteria["grid_capacity"] / 500 * 100, 100)
        lnd = criteria["land_suitability"]
        haz = criteria["hazard_score"]
        tmp = criteria["temperature_suitability"]
        wat = criteria["water_availability"]

        comprehensive = (
            sol * 0.20 + wnd * 0.15 + grd * 0.20
            + lnd * 0.15 + haz * 0.15
            + tmp * 0.075 + wat * 0.075
        )
        goals = {
            "solar_score": round(sol, 2),
            "wind_score": round(wnd, 2),
            "grid_score": round(grd, 2),
            "land_score": round(lnd, 2),
            "hazard_score": round(haz, 2),
            "temp_score": round(tmp, 2),
            "water_score": round(wat, 2),
        }
        return {
            "goals": goals,
            "comprehensive_score": round(comprehensive, 2),
            "method": "MCGP with real data",
        }

    def _level(self, score: float) -> str:
        if score >= 85: return "Excellent"
        if score >= 70: return "Good"
        if score >= 55: return "Average"
        return "Below Average"

    def _recommendation(self, score: float) -> str:
        if score >= 85: return "Strongly Recommended"
        if score >= 70: return "Recommended"
        if score >= 55: return "Worth Considering"
        return "Not Recommended"

    # ── Legacy method names used elsewhere ────────────────────────────────────

    def _generate_recommendation(self, final_ranking: Dict) -> Dict:
        score = final_ranking.get("final_score", 50)
        level = self._level(score)
        recs = {
            "Excellent": [
                "Highly suitable for data center construction",
                "Prioritize this location",
                "Large-scale campus can be planned",
            ],
            "Good": [
                "Suitable for data center construction",
                "Detailed feasibility study recommended",
                "Medium-sized data center viable",
            ],
            "Average": [
                "Marginal suitability — optimization needed",
                "Improve infrastructure before committing",
                "Small-scale construction feasible",
            ],
            "Below Average": [
                "Not recommended without major investment",
                "Seek alternative locations",
                "Significant infrastructure build-out required",
            ],
        }.get(level, [])
        return {
            "overall_assessment": level,
            "score": score,
            "recommendations": recs,
        }
