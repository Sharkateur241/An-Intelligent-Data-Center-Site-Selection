"""
Image Analysis Service — land use from ESA WorldCover via RealDataService.
All heuristic lookups replaced with real satellite data.
"""

import cv2
import numpy as np
from typing import Dict, Any, List
from datetime import datetime

from .real_data_service import RealDataService, DataUnavailableError


# ESA WorldCover class → suitability for data-center construction
_SUITABILITY = {
    "Tree cover":              0.30,
    "Shrubland":               0.50,
    "Grassland":               0.70,
    "Cropland":                0.55,
    "Built-up":                0.60,
    "Bare / sparse vegetation": 0.90,
    "Snow and ice":            0.10,
    "Permanent water bodies":  0.05,
    "Herbaceous wetland":      0.15,
    "Mangroves":               0.10,
    "Moss and lichen":         0.40,
}

_BUILT_UP_LABEL = "Built-up"
_BARE_LABEL = "Bare / sparse vegetation"
_WATER_LABEL = "Permanent water bodies"


class ImageAnalysisService:
    """Land use analysis using ESA WorldCover 2021 (10 m resolution) via GEE."""

    def __init__(self):
        self.real_data_service = RealDataService()
        print("ImageAnalysisService ready (ESA WorldCover via RealDataService)")

    async def analyze_land_use(self, satellite_data: Dict[str, Any]) -> Dict[str, Any]:
        metadata = satellite_data.get("metadata", {})
        center = metadata.get("center", [0.0, 0.0])
        radius = float(metadata.get("radius", 1000))
        lat, lon = center[0], center[1]

        area_m2 = 3.14159 * radius ** 2

        try:
            lc = await self.real_data_service.get_land_cover(lat, lon, radius)
        except DataUnavailableError as exc:
            return {
                "success": False,
                "error": str(exc),
                "data_source": "ESA WorldCover 2021 10m",
                "confidence": "N/A",
            }

        distribution = lc["distribution"]
        bare_frac = lc["bare_or_sparse_fraction"]
        built_frac = lc["built_up_fraction"]
        water_frac = lc["water_fraction"]
        dominant = lc["dominant_class"]

        # Weighted suitability score
        suitability_score = sum(
            frac * _SUITABILITY.get(cls, 0.5)
            for cls, frac in distribution.items()
        )
        suitability_score = round(min(suitability_score, 1.0), 4)

        # Suitable areas list
        suitable_areas = []
        if bare_frac > 0.05:
            suitable_areas.append({
                "type": "Bare / sparse vegetation",
                "area_ratio": bare_frac,
                "suitability_score": _SUITABILITY[_BARE_LABEL],
                "description": "Minimal clearing required — lowest construction cost",
                "priority": "High" if bare_frac > 0.2 else "Medium",
            })
        for cls, frac in distribution.items():
            if cls in ("Grassland", "Shrubland", "Cropland") and frac > 0.1:
                suitable_areas.append({
                    "type": cls,
                    "area_ratio": frac,
                    "suitability_score": _SUITABILITY[cls],
                    "description": f"{cls}: moderate land preparation required",
                    "priority": "Medium",
                })

        suitable_areas.sort(key=lambda x: x["suitability_score"], reverse=True)

        # Recommendations
        recommendations = _generate_recommendations(
            bare_frac, built_frac, water_frac, suitability_score, dominant
        )

        # constraints
        constraints = _identify_constraints(distribution)

        return {
            "success": True,
            "total_area": area_m2,
            "land_use_distribution": distribution,
            "suitable_areas": suitable_areas,
            "constraints": constraints,
            "suitability_score": suitability_score,
            "dominant_class": dominant,
            "recommendations": recommendations,
            "data_source": lc["source"],
            "confidence": lc["confidence"],
            "analysis_date": datetime.now().isoformat(),
        }

    # Keep legacy methods used by other parts of the codebase
    def detect_land_changes(
        self, image1: np.ndarray, image2: np.ndarray
    ) -> Dict[str, Any]:
        try:
            gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
            diff = cv2.absdiff(gray1, gray2)
            _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
            import numpy as _np
            kernel = _np.ones((5, 5), _np.uint8)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            change_pixels = int(_np.sum(thresh > 0))
            total_pixels = thresh.shape[0] * thresh.shape[1]
            return {
                "change_ratio": change_pixels / total_pixels,
                "change_pixels": change_pixels,
                "total_pixels": total_pixels,
            }
        except Exception as exc:
            return {"change_ratio": 0, "change_pixels": 0, "total_pixels": 0,
                    "error": str(exc)}

    def predict_land_use_trend(
        self, historical_data: list
    ) -> Dict[str, Any]:
        if len(historical_data) < 2:
            return {"trend": "Insufficient data", "prediction": "Unable to predict"}
        trends = {}
        for land_type in ("Bare / sparse vegetation", "Built-up",
                          "Tree cover", "Permanent water bodies"):
            values = [
                d.get("land_use_distribution", {}).get(land_type, 0)
                for d in historical_data
            ]
            if len(values) >= 2 and values[0] > 0:
                trend = "Increasing" if values[-1] > values[0] else "Decreasing"
                trends[land_type] = {
                    "trend": trend,
                    "change_rate": (values[-1] - values[0]) / values[0],
                }
        return {"trends": trends, "confidence": 0.6}


def _generate_recommendations(
    bare_frac: float,
    built_frac: float,
    water_frac: float,
    score: float,
    dominant: str,
) -> List[str]:
    recs = []
    if bare_frac > 0.4:
        recs.append(
            "Abundant bare/sparse land — excellent for data center construction "
            "with minimal site preparation"
        )
    elif bare_frac > 0.2:
        recs.append(
            "Moderate bare land availability — site preparation manageable"
        )
    else:
        recs.append(
            "Limited bare land — significant site preparation or clearing required"
        )

    if built_frac > 0.5:
        recs.append(
            "High built-up density — land acquisition costs will be elevated"
        )
    if water_frac > 0.3:
        recs.append(
            "High water body coverage — flood control measures essential"
        )
    if score > 0.75:
        recs.append(
            "Overall land suitability is high — recommended for data center development"
        )
    elif score > 0.55:
        recs.append(
            "Moderate land suitability — feasible with appropriate site engineering"
        )
    else:
        recs.append(
            "Low land suitability — consider alternative locations or extensive preparation"
        )
    return recs


def _identify_constraints(distribution: Dict[str, float]) -> List[str]:
    constraints = []
    if distribution.get(_BUILT_UP_LABEL, 0) > 0.5:
        constraints.append("High built-up density — elevated construction costs")
    if distribution.get(_WATER_LABEL, 0) > 0.3:
        constraints.append("High water coverage — hydrological assessment required")
    if distribution.get("Tree cover", 0) + distribution.get("Shrubland", 0) > 0.6:
        constraints.append("High vegetation coverage — land clearance needed")
    if distribution.get(_BARE_LABEL, 0) < 0.1:
        constraints.append("Limited open land — extensive preparation required")
    return constraints
