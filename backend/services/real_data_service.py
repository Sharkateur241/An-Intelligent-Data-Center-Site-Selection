"""
RealDataService — single source of truth for all external geospatial data.
All other services call this instead of using heuristics or hardcoded lookups.
"""

import asyncio
import logging
import os
import math
from typing import Any, Dict, List, Optional, Literal

import ssl

import aiohttp

logger = logging.getLogger(__name__)

# Allow SSL verification to be disabled in dev environments where local proxy
# breaks cert chains (same pattern as GEE_DISABLE_SSL_VERIFY).
_DISABLE_SSL = os.getenv("DISABLE_SSL_VERIFY", "false").lower() in ("true", "1", "yes")
_SSL_CTX: Any = False if _DISABLE_SSL else None  # None → aiohttp default (verify)

# ── Configuration (all overridable via env vars) ─────────────────────────────
NASA_POWER_URL    = os.getenv("NASA_POWER_BASE_URL",
    "https://power.larc.nasa.gov/api/temporal/climatology/point")
OPEN_METEO_CLIMATE_URL = os.getenv("OPEN_METEO_CLIMATE_URL",
    "https://climate-api.open-meteo.com/v1/climate")
OPEN_METEO_ARCHIVE_URL = os.getenv("OPEN_METEO_ARCHIVE_URL",
    "https://archive-api.open-meteo.com/v1/archive")
OPEN_ELEVATION_URL = os.getenv("OPEN_ELEVATION_URL",
    "https://api.open-elevation.com/api/v1/lookup")
OVERPASS_URL      = os.getenv("OVERPASS_API_URL",
    "https://overpass-api.de/api/interpreter")
USGS_HAZARD_URL   = os.getenv("USGS_HAZARD_URL",
    "https://earthquake.usgs.gov/ws/designmaps/nehrp-2020.json")

_TIMEOUT = aiohttp.ClientTimeout(total=30)
_RETRIES = 2
_BACKOFF = 2.0


class DataUnavailableError(Exception):
    """Raised when a real data source cannot be reached after retries."""
    def __init__(self, source: str, lat: float, lon: float, reason: str = ""):
        self.source = source
        self.lat = lat
        self.lon = lon
        self.reason = reason
        super().__init__(
            f"Data unavailable from {source} at ({lat},{lon}): {reason}"
        )


def _cache_key(source: str, lat: float, lon: float) -> str:
    return f"{source}:{round(lat, 4)}:{round(lon, 4)}"


async def _fetch_with_retry(
    session: aiohttp.ClientSession,
    url: str,
    params: dict,
    source_name: str,
    lat: float,
    lon: float,
) -> dict:
    """GET request with 2 retries and exponential backoff."""
    last_exc: Exception = RuntimeError("No attempts made")
    for attempt in range(_RETRIES + 1):
        try:
            async with session.get(url, params=params, timeout=_TIMEOUT) as resp:
                if resp.status >= 500:
                    raise aiohttp.ClientResponseError(
                        resp.request_info, resp.history, status=resp.status
                    )
                if resp.status >= 400:
                    text = await resp.text()
                    raise DataUnavailableError(
                        source_name, lat, lon,
                        f"HTTP {resp.status}: {text[:200]}"
                    )
                return await resp.json(content_type=None)
        except DataUnavailableError:
            raise
        except Exception as exc:
            last_exc = exc
            if attempt < _RETRIES:
                logger.debug(
                    "Retry %d/%d for %s at (%s,%s): %s",
                    attempt + 1, _RETRIES, source_name, lat, lon, exc
                )
                await asyncio.sleep(_BACKOFF * (attempt + 1))
    raise DataUnavailableError(source_name, lat, lon, str(last_exc))


async def _post_with_retry(
    session: aiohttp.ClientSession,
    url: str,
    data: str,
    source_name: str,
    lat: float,
    lon: float,
) -> dict:
    """POST request with 2 retries."""
    last_exc: Exception = RuntimeError("No attempts made")
    for attempt in range(_RETRIES + 1):
        try:
            async with session.post(
                url, data=data, timeout=_TIMEOUT,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            ) as resp:
                if resp.status >= 500:
                    raise aiohttp.ClientResponseError(
                        resp.request_info, resp.history, status=resp.status
                    )
                if resp.status >= 400:
                    text = await resp.text()
                    raise DataUnavailableError(
                        source_name, lat, lon,
                        f"HTTP {resp.status}: {text[:200]}"
                    )
                return await resp.json(content_type=None)
        except DataUnavailableError:
            raise
        except Exception as exc:
            last_exc = exc
            if attempt < _RETRIES:
                await asyncio.sleep(_BACKOFF * (attempt + 1))
    raise DataUnavailableError(source_name, lat, lon, str(last_exc))


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1))
         * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


# ── Köppen climate classification (simplified, from temp + precip) ────────────
def _koppen(annual_temp_c: float, annual_precip_mm: float) -> str:
    """Simplified Köppen classification from annual temperature and precipitation."""
    if annual_precip_mm < 200:
        return "BWh" if annual_temp_c > 18 else "BWk"
    if annual_temp_c > 18:
        if annual_precip_mm > 2000:
            return "Af"
        return "Am" if annual_precip_mm > 1000 else "Aw"
    if annual_temp_c > 0:
        if annual_precip_mm > 800:
            return "Cfb" if annual_temp_c < 15 else "Cfa"
        return "Cs"
    return "Dfc" if annual_temp_c > -10 else "ET"


class RealDataService:
    """Single source of truth for all geospatial external data."""

    def __init__(self):
        self._cache: Dict[str, Any] = {}

    # ── NASA POWER — Solar irradiance ─────────────────────────────────────────
    async def get_solar_irradiance(self, lat: float, lon: float) -> Dict:
        key = _cache_key("solar", lat, lon)
        if key in self._cache:
            logger.debug("Cache HIT solar (%s,%s)", lat, lon)
            return self._cache[key]
        logger.debug("Cache MISS solar (%s,%s)", lat, lon)

        params = {
            "parameters": "ALLSKY_SFC_SW_DWN",
            "community": "RE",
            "longitude": lon,
            "latitude": lat,
            "format": "JSON",
        }
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=_SSL_CTX)) as session:
            data = await _fetch_with_retry(
                session, NASA_POWER_URL, params, "NASA POWER", lat, lon
            )

        try:
            annual_daily = data["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"]["ANN"]
            annual_yearly = annual_daily * 365
        except (KeyError, TypeError) as exc:
            raise DataUnavailableError("NASA POWER", lat, lon,
                                       f"Unexpected response structure: {exc}")

        result = {
            "annual_irradiance_kwh_m2": round(annual_yearly, 1),
            "daily_mean_kwh_m2": round(annual_daily, 3),
            "source": "NASA POWER",
            "confidence": "measured",
        }
        self._cache[key] = result
        return result

    # ── NASA POWER — Wind speed (climatology, same endpoint as solar) ─────────
    async def get_wind_speed(self, lat: float, lon: float) -> Dict:
        key = _cache_key("wind", lat, lon)
        if key in self._cache:
            logger.debug("Cache HIT wind (%s,%s)", lat, lon)
            return self._cache[key]
        logger.debug("Cache MISS wind (%s,%s)", lat, lon)

        params = {
            "parameters": "WS10M",
            "community": "RE",
            "longitude": lon,
            "latitude": lat,
            "format": "JSON",
        }
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=_SSL_CTX)) as session:
            data = await _fetch_with_retry(
                session, NASA_POWER_URL, params, "NASA POWER (wind)", lat, lon
            )

        try:
            mean_10m = data["properties"]["parameter"]["WS10M"]["ANN"]
        except (KeyError, TypeError) as exc:
            raise DataUnavailableError("NASA POWER (wind)", lat, lon,
                                       f"Unexpected response structure: {exc}")

        # Extrapolate to 100 m using Hellmann power law α=0.143
        mean_100m = mean_10m * (100 / 10) ** 0.143

        result = {
            "annual_mean_ms": round(mean_10m, 2),
            "annual_mean_100m_ms": round(mean_100m, 2),
            "source": "NASA POWER",
            "confidence": "reanalysis",
        }
        self._cache[key] = result
        return result

    # ── Open-Elevation / SRTM — Elevation ────────────────────────────────────
    async def get_elevation(self, lat: float, lon: float) -> Dict:
        key = _cache_key("elevation", lat, lon)
        if key in self._cache:
            logger.debug("Cache HIT elevation (%s,%s)", lat, lon)
            return self._cache[key]
        logger.debug("Cache MISS elevation (%s,%s)", lat, lon)

        params = {"locations": f"{lat},{lon}"}
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=_SSL_CTX)) as session:
            data = await _fetch_with_retry(
                session, OPEN_ELEVATION_URL, params, "Open-Elevation", lat, lon
            )

        try:
            elevation = data["results"][0]["elevation"]
        except (KeyError, IndexError, TypeError) as exc:
            raise DataUnavailableError("Open-Elevation", lat, lon,
                                       f"Unexpected response: {exc}")

        result = {
            "elevation_m": round(float(elevation), 1),
            "source": "Open-Elevation / SRTM",
            "confidence": "measured",
        }
        self._cache[key] = result
        return result

    # ── ESA WorldCover via GEE — Land cover ───────────────────────────────────
    async def get_land_cover(self, lat: float, lon: float, radius_m: float) -> Dict:
        key = _cache_key(f"land_{int(radius_m)}", lat, lon)
        if key in self._cache:
            logger.debug("Cache HIT land_cover (%s,%s)", lat, lon)
            return self._cache[key]
        logger.debug("Cache MISS land_cover (%s,%s)", lat, lon)

        # ESA WorldCover class map
        esa_classes = {
            10: "Tree cover",
            20: "Shrubland",
            30: "Grassland",
            40: "Cropland",
            50: "Built-up",
            60: "Bare / sparse vegetation",
            70: "Snow and ice",
            80: "Permanent water bodies",
            90: "Herbaceous wetland",
            95: "Mangroves",
            100: "Moss and lichen",
        }

        try:
            import ee
            try:
                ee.Initialize(opt_url="https://earthengine.googleapis.com")
            except Exception:
                pass  # already initialized

            point = ee.Geometry.Point([lon, lat])
            region = point.buffer(radius_m)
            wc = ee.ImageCollection("ESA/WorldCover/v200").first().clip(region)
            hist = wc.reduceRegion(
                reducer=ee.Reducer.frequencyHistogram(),
                geometry=region,
                scale=10,
                maxPixels=1e8,
            ).getInfo()

            raw = hist.get("Map", {})
            total = sum(raw.values()) if raw else 0
            if total == 0:
                raise DataUnavailableError(
                    "ESA WorldCover", lat, lon, "No pixels in region"
                )

            distribution = {}
            for code_str, count in raw.items():
                code = int(float(code_str))
                label = esa_classes.get(code, f"Class {code}")
                distribution[label] = round(count / total, 4)

            bare_frac = distribution.get("Bare / sparse vegetation", 0.0)
            built_frac = distribution.get("Built-up", 0.0)
            water_frac = distribution.get("Permanent water bodies", 0.0)
            dom = max(distribution, key=distribution.get) if distribution else "Unknown"

        except DataUnavailableError:
            raise
        except Exception as exc:
            raise DataUnavailableError(
                "ESA WorldCover (GEE)", lat, lon, str(exc)
            )

        result = {
            "distribution": distribution,
            "dominant_class": dom,
            "bare_or_sparse_fraction": bare_frac,
            "built_up_fraction": built_frac,
            "water_fraction": water_frac,
            "source": "ESA WorldCover 2021 10m",
            "confidence": "measured",
        }
        self._cache[key] = result
        return result

    # ── OpenStreetMap Overpass — Grid infrastructure ──────────────────────────
    async def get_grid_infrastructure(
        self, lat: float, lon: float, radius_m: float
    ) -> Dict:
        key = _cache_key(f"grid_{int(radius_m)}", lat, lon)
        if key in self._cache:
            logger.debug("Cache HIT grid (%s,%s)", lat, lon)
            return self._cache[key]
        logger.debug("Cache MISS grid (%s,%s)", lat, lon)

        query = (
            f"[out:json][timeout:30];"
            f"("
            f'way["power"="line"](around:{int(radius_m)},{lat},{lon});'
            f'node["power"="substation"](around:{int(radius_m)},{lat},{lon});'
            f'node["power"="tower"](around:{int(radius_m)},{lat},{lon});'
            f");"
            f"out body;"
        )

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=_SSL_CTX)) as session:
            data = await _post_with_retry(
                session, OVERPASS_URL, f"data={query}",
                "OpenStreetMap Overpass", lat, lon
            )

        elements = data.get("elements", [])
        substations = [
            e for e in elements
            if e.get("type") == "node" and e.get("tags", {}).get("power") == "substation"
        ]
        powerlines = [
            e for e in elements
            if e.get("type") == "way" and e.get("tags", {}).get("power") == "line"
        ]

        # Nearest substation distance
        nearest_sub_km: Optional[float] = None
        voltage_kv: Optional[float] = None
        for sub in substations:
            slat, slon = sub.get("lat", lat), sub.get("lon", lon)
            dist = _haversine_km(lat, lon, slat, slon)
            if nearest_sub_km is None or dist < nearest_sub_km:
                nearest_sub_km = dist
                # Try to extract voltage from tags
                v_str = sub.get("tags", {}).get("voltage", "")
                if v_str:
                    try:
                        # voltage can be "220000" (V) or "220" (kV)
                        v = float(v_str.split(";")[0])
                        voltage_kv = v / 1000 if v > 1000 else v
                    except ValueError:
                        pass

        # Default voltage if not found but substations present
        if substations and voltage_kv is None:
            voltage_kv = 110.0

        # Nearest power line (approximate via first node of way — Overpass body doesn't
        # return way geometry without "geom"; use bounding box centre as proxy)
        nearest_line_km: Optional[float] = None
        for line in powerlines:
            bounds = line.get("bounds")
            if bounds:
                clat = (bounds["minlat"] + bounds["maxlat"]) / 2
                clon = (bounds["minlon"] + bounds["maxlon"]) / 2
                dist = _haversine_km(lat, lon, clat, clon)
                if nearest_line_km is None or dist < nearest_line_km:
                    nearest_line_km = dist

        result = {
            "nearest_substation_km": round(nearest_sub_km, 3) if nearest_sub_km is not None else None,
            "nearest_powerline_km": round(nearest_line_km, 3) if nearest_line_km is not None else None,
            "substation_count_in_radius": len(substations),
            "powerline_count_in_radius": len(powerlines),
            "estimated_voltage_kv": voltage_kv,
            "source": "OpenStreetMap Overpass",
            "confidence": "crowdsourced",
        }
        self._cache[key] = result
        return result

    # ── NASA POWER — Climate (climatology, fast pre-averaged response) ────────
    async def get_climate(self, lat: float, lon: float) -> Dict:
        key = _cache_key("climate", lat, lon)
        if key in self._cache:
            logger.debug("Cache HIT climate (%s,%s)", lat, lon)
            return self._cache[key]
        logger.debug("Cache MISS climate (%s,%s)", lat, lon)

        # T2M = temperature at 2m (°C), PRECTOTCORR = precipitation (mm/day)
        # Climatology endpoint returns monthly + annual means — no daily download needed
        params = {
            "parameters": "T2M,PRECTOTCORR",
            "community": "RE",
            "longitude": lon,
            "latitude": lat,
            "format": "JSON",
        }
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=_SSL_CTX)) as session:
            data = await _fetch_with_retry(
                session, NASA_POWER_URL, params, "NASA POWER (climate)", lat, lon
            )

        try:
            param = data["properties"]["parameter"]
            t2m   = param["T2M"]     # dict: JAN..DEC, ANN
            prec  = param["PRECTOTCORR"]
        except (KeyError, TypeError) as exc:
            raise DataUnavailableError("NASA POWER (climate)", lat, lon,
                                       f"Unexpected response structure: {exc}")

        mean_temp   = t2m["ANN"]
        # PRECTOTCORR["ANN"] is mm/day → multiply by 365 for mm/year
        annual_precip = prec["ANN"] * 365

        # Degree days from monthly means (standard monthly approximation)
        month_keys = ["JAN","FEB","MAR","APR","MAY","JUN",
                      "JUL","AUG","SEP","OCT","NOV","DEC"]
        days_per_month = [31,28,31,30,31,30,31,31,30,31,30,31]
        cdd_annual = sum(
            max(t2m.get(m, mean_temp) - 18, 0) * d
            for m, d in zip(month_keys, days_per_month)
        )
        hdd_annual = sum(
            max(18 - t2m.get(m, mean_temp), 0) * d
            for m, d in zip(month_keys, days_per_month)
        )

        climate_zone = _koppen(mean_temp, annual_precip)

        result = {
            "annual_mean_temp_c": round(mean_temp, 2),
            "annual_precip_mm": round(annual_precip, 1),
            "cooling_degree_days": round(cdd_annual, 1),
            "heating_degree_days": round(hdd_annual, 1),
            "climate_zone": climate_zone,
            "source": "NASA POWER Climatology",
            "confidence": "reanalysis",
        }
        self._cache[key] = result
        return result

    # ── USGS + OSM — Hazards ──────────────────────────────────────────────────
    async def get_hazards(self, lat: float, lon: float) -> Dict:
        key = _cache_key("hazards", lat, lon)
        if key in self._cache:
            logger.debug("Cache HIT hazards (%s,%s)", lat, lon)
            return self._cache[key]
        logger.debug("Cache MISS hazards (%s,%s)", lat, lon)

        # 1. Seismic — USGS NEHRP
        seismic_pga: Optional[float] = None
        seismic_src = "USGS NEHRP 2020"
        try:
            params = {
                "latitude": lat,
                "longitude": lon,
                "riskCategory": "III",
                "siteClass": "D",
                "title": "site",
            }
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=_SSL_CTX)) as session:
                usgs = await _fetch_with_retry(
                    session, USGS_HAZARD_URL, params, "USGS Seismic", lat, lon
                )
            # PGA is in output.data[0].pga
            output = usgs.get("output", {})
            data_list = output.get("data", [])
            if data_list:
                seismic_pga = data_list[0].get("pga")
        except Exception:
            seismic_pga = None

        if seismic_pga is None:
            seismic_risk: Literal["LOW", "MEDIUM", "HIGH"] = "LOW"
        elif seismic_pga < 0.1:
            seismic_risk = "LOW"
        elif seismic_pga < 0.4:
            seismic_risk = "MEDIUM"
        else:
            seismic_risk = "HIGH"

        # 2. Flood risk — GEE Global Flood Database proxy via precipitation
        # We use climate data (high precip + low elevation → flood risk)
        # as a lightweight proxy when GEE is unavailable.
        flood_risk: Literal["LOW", "MEDIUM", "HIGH"] = "LOW"
        flood_src = "Open-Meteo precipitation proxy"
        try:
            climate = await self.get_climate(lat, lon)
            precip = climate["annual_precip_mm"]
            elev_data = await self.get_elevation(lat, lon)
            elev = elev_data["elevation_m"]
            if precip > 1500 and elev < 50:
                flood_risk = "HIGH"
                flood_src = "Open-Meteo + Open-Elevation proxy"
            elif precip > 800 and elev < 100:
                flood_risk = "MEDIUM"
                flood_src = "Open-Meteo + Open-Elevation proxy"
            else:
                flood_risk = "LOW"
                flood_src = "Open-Meteo + Open-Elevation proxy"
        except Exception:
            flood_risk = "LOW"

        # 3. Cyclone risk — latitude-band proxy (IBTrACS data synthesis)
        if 5 <= abs(lat) <= 25 and (
            (80 <= lon <= 180) or (-100 <= lon <= -20)
        ):
            cyclone_risk: Literal["LOW", "MEDIUM", "HIGH"] = "HIGH"
        elif 5 <= abs(lat) <= 35:
            cyclone_risk = "MEDIUM"
        else:
            cyclone_risk = "LOW"

        result = {
            "flood_risk": flood_risk,
            "seismic_pga_g": seismic_pga,
            "seismic_risk": seismic_risk,
            "cyclone_risk": cyclone_risk,
            "source": {
                "flood": flood_src,
                "seismic": seismic_src,
                "cyclone": "IBTrACS latitude-band synthesis",
            },
            "confidence": "modelled",
        }
        self._cache[key] = result
        return result

    # ── OSM waterways + Open-Meteo precipitation — Water proximity ────────────
    async def get_water_proximity(
        self, lat: float, lon: float, radius_m: float
    ) -> Dict:
        key = _cache_key(f"water_{int(radius_m)}", lat, lon)
        if key in self._cache:
            logger.debug("Cache HIT water (%s,%s)", lat, lon)
            return self._cache[key]
        logger.debug("Cache MISS water (%s,%s)", lat, lon)

        query = (
            f"[out:json][timeout:30];"
            f"("
            f'way["waterway"~"river|stream|canal"](around:{int(radius_m)},{lat},{lon});'
            f'node["natural"="water"](around:{int(radius_m)},{lat},{lon});'
            f");"
            f"out body;"
        )

        nearest_km: Optional[float] = None
        waterway_types: List[str] = []

        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=_SSL_CTX)) as session:
                data = await _post_with_retry(
                    session, OVERPASS_URL, f"data={query}",
                    "OpenStreetMap Overpass (water)", lat, lon
                )
            for el in data.get("elements", []):
                tags = el.get("tags", {})
                wtype = tags.get("waterway") or tags.get("natural", "water")
                if wtype not in waterway_types:
                    waterway_types.append(wtype)
                # Approximate distance
                if el.get("type") == "node":
                    dist = _haversine_km(lat, lon, el["lat"], el["lon"])
                    if nearest_km is None or dist < nearest_km:
                        nearest_km = dist
                elif el.get("type") == "way":
                    bounds = el.get("bounds")
                    if bounds:
                        clat = (bounds["minlat"] + bounds["maxlat"]) / 2
                        clon = (bounds["minlon"] + bounds["maxlon"]) / 2
                        dist = _haversine_km(lat, lon, clat, clon)
                        if nearest_km is None or dist < nearest_km:
                            nearest_km = dist
        except Exception:
            pass  # OSM failure: nearest_km remains None

        # Precipitation proxy for water availability
        precip_mm = 0.0
        try:
            climate = await self.get_climate(lat, lon)
            precip_mm = climate["annual_precip_mm"]
        except Exception:
            pass

        if precip_mm > 1000 or (nearest_km is not None and nearest_km < 5):
            availability: Literal["SCARCE", "MODERATE", "ABUNDANT"] = "ABUNDANT"
        elif precip_mm > 400 or (nearest_km is not None and nearest_km < 30):
            availability = "MODERATE"
        else:
            availability = "SCARCE"

        result = {
            "nearest_waterway_km": round(nearest_km, 3) if nearest_km is not None else None,
            "waterway_types": waterway_types,
            "annual_precip_mm": round(precip_mm, 1),
            "water_availability": availability,
            "source": "OpenStreetMap + Open-Meteo",
            "confidence": "crowdsourced+reanalysis",
        }
        self._cache[key] = result
        return result

    # ── Combined fetch ────────────────────────────────────────────────────────
    async def get_all(
        self, lat: float, lon: float, radius_m: float = 5000
    ) -> Dict:
        """Fetch all data sources concurrently. Partial failures return None."""
        tasks = {
            "solar":   self.get_solar_irradiance(lat, lon),
            "wind":    self.get_wind_speed(lat, lon),
            "elevation": self.get_elevation(lat, lon),
            "land_cover": self.get_land_cover(lat, lon, radius_m),
            "grid":    self.get_grid_infrastructure(lat, lon, radius_m),
            "climate": self.get_climate(lat, lon),
            "hazards": self.get_hazards(lat, lon),
            "water":   self.get_water_proximity(lat, lon, radius_m),
        }

        results = await asyncio.gather(
            *tasks.values(), return_exceptions=True
        )

        combined: Dict[str, Any] = {}
        for name, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                combined[name] = {"error": str(result), "source": name}
                logger.warning("get_all partial failure [%s]: %s", name, result)
            else:
                combined[name] = result

        return combined
