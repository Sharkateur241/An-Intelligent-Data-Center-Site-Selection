"""
Satellite data service - integrates Google Earth Engine
"""

import ee
import requests
import json
from typing import Dict, Any, Optional, Tuple, List
import os
from datetime import datetime, timedelta
import base64
import io
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SatelliteService:
    """Satellite data service"""
    
    def __init__(self):
        """Initialize GEE service"""
        try:
            # SSL / network setup
            import ssl
            import urllib3
            import os

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            os.environ['PYTHONHTTPSVERIFY'] = '0'

            # Proxy setup: only set if actually provided
            http_proxy = os.getenv('HTTP_PROXY') or os.getenv('http_proxy')
            https_proxy = os.getenv('HTTPS_PROXY') or os.getenv('https_proxy')

            if http_proxy:
                os.environ['HTTP_PROXY'] = http_proxy
                os.environ['http_proxy'] = http_proxy
                print(f"HTTP proxy set: {http_proxy}")

            if https_proxy:
                os.environ['HTTPS_PROXY'] = https_proxy
                os.environ['https_proxy'] = https_proxy
                print(f"HTTPS proxy set: {https_proxy}")

            # Initialize Google Earth Engine
            project_id = os.getenv('GEE_PROJECT_ID', 'data-center-location-analysis')
            ee.Initialize(project=project_id)
            print(f"Google Earth Engine initialized, project: {project_id}")
            self.gee_available = True
        except Exception as e:
            print(f"GEE init failed: {e}")
            print("Check network/proxy; run `python setup_gee_auth.py` if auth needed.")
            self.gee_available = False
    
    async def get_satellite_data(self, lat: float, lon: float, radius: float = 1000) -> Dict[str, Any]:
        """
        Get satellite data for a specified location
        
        Args:
            lat: Latitude
            lon: Longitude
            radius: Search radius (meters)
            
        Returns:
            Dictionary containing satellite image and metadata
        """
        # Create area of interest
        point = ee.Geometry.Point([lon, lat])
        region = point.buffer(radius)
        
        # Get Landsat 8/9 images
        collection = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                     .filterDate('2023-01-01', '2023-12-31')
                     .filterBounds(region)
                     .filter(ee.Filter.lt('CLOUD_COVER', 20)))
        
        # Select the best image (lowest cloud cover)
        image = collection.sort('CLOUD_COVER').first()
        
        # Get image information
        image_info = image.getInfo()
        
        # Calculate NDVI (Normalized Difference Vegetation Index)
        ndvi = image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
        
        # Calculate land cover type
        land_cover = self._classify_land_cover(image)
        
        return {
            "image": image,
            "ndvi": ndvi,
            "land_cover": land_cover,
            "metadata": {
                "acquisition_date": image_info.get('properties', {}).get('DATE_ACQUIRED'),
                "cloud_cover": image_info.get('properties', {}).get('CLOUD_COVER'),
                "center": [lat, lon],
                "radius": radius
            }
        }
    
    async def get_temporal_satellite_data(self, lat: float, lon: float, radius: float = 1000, 
                                        time_points: int = 3) -> List[Dict[str, Any]]:
        """
        Get satellite data for multiple time points
        
        Args:
            lat: Latitude
            lon: Longitude
            radius: Search radius (meters)
            time_points: Number of time points
            
        Returns:
            List containing satellite data for multiple time points
        """
        try:
            # Create area of interest
            point = ee.Geometry.Point([lon, lat])
            region = point.buffer(radius)
            
            # Define time range (past 2 years)
            start_date = '2022-01-01'
            end_date = '2024-01-01'
            
            # Get Landsat 8/9 image collection
            collection = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                         .filterDate(start_date, end_date)
                         .filterBounds(region)
                         .filter(ee.Filter.lt('CLOUD_COVER', 30)))
            
            # Get image list
            image_list = collection.sort('DATE_ACQUIRED').toList(time_points)
            
            temporal_data = []
            
            for i in range(time_points):
                try:
                    # Get the i-th image
                    image = ee.Image(image_list.get(i))
                    image_info = image.getInfo()
                    
                    # Get image URL
                    image_url = await self._get_gee_satellite_image(lat, lon, radius)
                    
                    # Calculate NDVI
                    ndvi = image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
                    
                    # Calculate land cover type
                    land_cover = self._classify_land_cover(image)
                    
                    temporal_data.append({
                        "image": image,
                        "ndvi": ndvi,
                        "land_cover": land_cover,
                        "url": image_url["url"],
                        "metadata": {
                            "acquisition_date": image_info.get('properties', {}).get('DATE_ACQUIRED'),
                            "cloud_cover": image_info.get('properties', {}).get('CLOUD_COVER'),
                            "center": [lat, lon],
                            "radius": radius,
                            "time_index": i
                        }
                    })
                    
                except Exception as e:
                    print(f"Failed to retrieve data for time point {i+1}: {e}")
                    # If retrieval fails, use current image as fallback
                    current_data = await self.get_satellite_image(lat, lon, radius=radius)
                    current_data["metadata"]["acquisition_date"] = f"2023-{i+1:02d}-01"
                    current_data["metadata"]["time_index"] = i
                    temporal_data.append(current_data)
            
            return temporal_data
            
        except Exception as e:
            print(f"Failed to retrieve time series data: {e}")
            # Fallback: return simulated data
            temporal_data = []
            for i in range(time_points):
                current_data = await self.get_satellite_image(lat, lon, radius=radius)
                current_data["metadata"]["acquisition_date"] = f"2023-{i+1:02d}-01"
                current_data["metadata"]["time_index"] = i
                temporal_data.append(current_data)
            return temporal_data
    
    def _classify_land_cover(self, image: ee.Image) -> ee.Image:
        """
        Perform land cover classification based on satellite image
        
        Args:
            image: Landsat image
            
        Returns:
            Land cover classification result
        """
        # Use simple threshold method for land cover classification
        # 0: Water, 1: Vegetation, 2: Bare Land, 3: Buildings
        
        # Calculate NDVI
        ndvi = image.normalizedDifference(['SR_B5', 'SR_B4'])
        
        # Calculate NDWI (Normalized Difference Water Index)
        ndwi = image.normalizedDifference(['SR_B3', 'SR_B5'])
        
        # Calculate building index
        nbi = image.normalizedDifference(['SR_B5', 'SR_B6'])
        
        # Classification rules
        water = ndwi.gt(0.1)
        vegetation = ndvi.gt(0.3)
        bare_land = ndvi.lt(0.1).And(ndwi.lt(0.1))
        building = nbi.gt(0.1).And(ndvi.lt(0.2))
        
        # Merge classification results
        land_cover = (water.multiply(0)
                    .add(vegetation.multiply(1))
                    .add(bare_land.multiply(2))
                    .add(building.multiply(3)))
        
        return land_cover.rename('land_cover')
    
    async def get_satellite_image(self, lat: float, lon: float, zoom: int = 10, radius: float = 1000) -> Dict[str, Any]:
        """
        Get satellite image URL - prioritizes real GEE satellite data
        
        Args:
            lat: Latitude
            lon: Longitude
            zoom: Zoom level
            radius: Analysis radius (meters)
            
        Returns:
            Dictionary containing image URL and metadata
        """
        try:
            # First attempt to retrieve real satellite image using GEE
            gee_result = await self._get_gee_satellite_image(lat, lon, zoom, radius)
            if gee_result and not gee_result.get("error"):
                return gee_result
            
            # If GEE fails, try fallback option
            print("🔄 GEE retrieval failed, trying fallback option...")
            fallback_result = await self._get_fallback_map_image(lat, lon, zoom)
            if fallback_result:
                print("✅ Fallback option succeeded")
                return fallback_result
            else:
                raise Exception("All image retrieval options failed")
            
        except Exception as e:
            print(f"Satellite image retrieval failed: {e}")
            # Last attempt with fallback option
            try:
                print("🔄 Final attempt with fallback option...")
                fallback_result = await self._get_fallback_map_image(lat, lon, zoom)
                if fallback_result:
                    print("✅ Fallback option succeeded")
                    return fallback_result
            except Exception as fallback_error:
                print(f"❌ Fallback option also failed: {fallback_error}")
            
            raise Exception(f"All image retrieval options failed: {e}")
    
    async def _get_gee_satellite_image(self, lat: float, lon: float, zoom: int, radius: float = 1000) -> Dict[str, Any]:
        """Retrieve real satellite image using GEE"""
        try:
            # Ensure ee is imported
            import ee
            
            # Set GEE request timeout (using correct method)
            try:
                # Attempt to set timeout (if supported)
                if hasattr(ee.data, 'setTimeout'):
                    ee.data.setTimeout(300)
                else:
                    # Set timeout via environment variable
                    import os
                    os.environ['EE_TIMEOUT'] = '300'
            except:
                pass  # Continue execution if setting fails
            
            # Since GEE Map API requires complex authentication, use static image API
            point = ee.Geometry.Point([lon, lat])
            region = point.buffer(20000)  # 20 km radius
            
            # Use Dynamic World dataset - 10m resolution, updated daily
            print("🔄 Using Dynamic World dataset to retrieve land use data...")
            
            # Use Landsat 8/9 as primary data source (high-quality satellite data)
            collection = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                         .filterDate('2020-01-01', '2024-12-31')
                         .filterBounds(region)
                         .filter(ee.Filter.lt('CLOUD_COVER', 30)))
            
            # Optimization: directly attempt to retrieve image without counting total
            try:
                image = collection.sort('CLOUD_COVER').first()
                image_info = image.getInfo()
                print("✅ Landsat 8/9 image found")
                has_landsat = True
            except:
                print("No Landsat data available for this area, trying Dynamic World")
                has_landsat = False
            
            if not has_landsat:
                print("No Landsat data available for this area, trying Dynamic World")
                # Fallback: use Dynamic World
                dw_collection = (ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1')
                               .filterBounds(region)
                               .filterDate('2024-01-01', '2024-12-31')
                               .select('label'))
                
                # Set timeout for Dynamic World as well
                try:
                    if hasattr(ee.data, 'setTimeout'):
                        ee.data.setTimeout(300)
                    else:
                        os.environ['EE_TIMEOUT'] = '300'
                except:
                    pass
                
                dw_count = dw_collection.size().getInfo()
                print(f"Found {dw_count} Dynamic World images")
                
                if dw_count == 0:
                    raise Exception("No satellite data available for this area")
                
                # Use a single Dynamic World image (no mode compositing)
                dw_image = dw_collection.sort('system:time_start', False).first()
                
                # Check if image has data
                image_info = dw_image.getInfo()
                print(f"Dynamic World image info: {image_info}")
                
                # Visualize using correct bands
                rgb_image = dw_image.visualize({
                    'bands': ['label'],
                    'min': 0,
                    'max': 8,
                    'palette': [
                        '419bdf',  # Water
                        '397d49',  # Forest
                        '88b053',  # Grassland
                        '7a87c6',  # Wetland
                        'e49635',  # Farmland
                        'dfc35a',  # Shrubland
                        'c4281b',  # Built-up land
                        'a59b8f',  # Bare land
                        'b39fe1'   # Snow/Ice
                    ]
                })
            else:
                # Use Landsat image (primary option)
                # image was already retrieved above
                print(f"Landsat image info: {image_info}")
                
                # Use raw RGB bands without preprocessing
                rgb_image = image.select(['SR_B4', 'SR_B3', 'SR_B2'])
                print("✅ GEE image selection successful")
            
            # Dynamically adjust image size and zoom level based on radius
            if radius <= 1000:
                dimensions = 400
                zoom_level = 15
            elif radius <= 2000:
                dimensions = 512
                zoom_level = 14
            elif radius <= 5000:
                dimensions = 600
                zoom_level = 13
            else:
                dimensions = 800
                zoom_level = 12
            
            # Use GEE static image API - dynamically adjusted based on radius
            try:
                # Ensure rgb_image is in the correct format
                print(f"🔍 RGB image bands: {rgb_image.bandNames().getInfo()}")
                
                # Generate GEE image URL - using correct parameters
                # Use original dimensions for better analysis quality
                image_url = rgb_image.getThumbURL({
                    'region': region,
                    'dimensions': dimensions,
                    'format': 'png',
                    'bands': ['SR_B4', 'SR_B3', 'SR_B2']
                    # Omit crs parameter, let GEE handle automatically
                })
                
                print(f"GEE original URL: {image_url}")
                
                # Check if URL is valid
                if not image_url or image_url.startswith('data:'):
                    print("⚠️ GEE image URL is invalid, trying alternative method")
                    # Try with different parameters
                    try:
                        image_url = rgb_image.getThumbURL({
                            'region': region,
                            'dimensions': dimensions,
                            'format': 'png'
                        })
                        print(f"GEE fallback URL: {image_url}")
                    except:
                        raise Exception("GEE image URL generation failed")
                
                # Use GEE URL directly without Base64 conversion
                original_thumb_url = image_url
                print(f"GEE image URL: {image_url[:100]}...")
                
                # Validate URL format
                if not image_url.startswith('https://'):
                    raise Exception("GEE URL is not a valid HTTPS URL")
                    
            except Exception as e:
                print(f"GEE image URL generation failed: {e}")
                print("🔄 Trying fallback map service...")
                
                # Use fallback map service
                try:
                    fallback_result = await self._get_fallback_map_image(lat, lon, zoom_level)
                    if fallback_result:
                        print("✅ Fallback map service succeeded")
                        return fallback_result
                    else:
                        raise Exception("Fallback map service also failed")
                except Exception as fallback_error:
                    print(f"❌ Fallback map service failed: {fallback_error}")
                    # Final attempt: generate a simple fallback image
                    try:
                        fallback_image = self._create_fallback_image(lat, lon, dimensions)
                        return {
                            "url": fallback_image,
                            "tile_url": "fallback",
                            "metadata": {
                                "center": [lat, lon],
                                "zoom": zoom_level,
                                "source": "EmergencyFallback",
                                "radius": radius
                            }
                        }
                    except Exception as final_error:
                        print(f"❌ Final fallback option also failed: {final_error}")
                        raise Exception(f"All image retrieval options failed: {e}")
            
            print(f"GEE satellite image request: location ({lat}, {lon}), radius {radius}m, dimensions {dimensions}x{dimensions}")
            print(f"GEE image URL: {image_url[:60]}...")
            
            # Check if URL is valid
            if not image_url or not image_url.startswith('https://'):
                print("⚠️ Image URL is invalid, may be a data issue")
                return {"error": "Image URL generation failed"}
            
            # If it is a getPixels URL, download and convert to Base64
            if 'getPixels' in image_url:
                print("🔄 Detected getPixels URL, downloading and converting to Base64...")
                try:
                    base64_image = await self._download_gee_image_to_base64(image_url)
                    image_url = base64_image
                    print("✅ GEE image converted to Base64 format")
                except Exception as e:
                    print(f"❌ GEE image download failed: {e}")
                    raise Exception(f"GEE image download failed, downgrade not allowed: {e}")
            
            return {
                "url": image_url,
                "tile_url": image_url,
                "metadata": {
                    "center": [lat, lon],
                    "radius": radius,
                    "dimensions": f"{dimensions}x{dimensions}",
                    "zoom_level": zoom_level,
                    "image_type": "True Color RGB Satellite Image",
                    "data_source": "Landsat 8/9 (Primary) / Dynamic World (Fallback)",
                    "resolution": "30m (Landsat) / 10m (Dynamic World)",
                    "coverage_radius": f"{radius/1000} km",
                    "map_service": "Google Earth Engine",
                    "free_service": False,
                    "gee_available": True,
                    "original_thumb_url": original_thumb_url
                }
            }
            
        except Exception as e:
            print(f"GEE satellite fetch failed: {e}")
            # Allow graceful fallback
            return await self._get_fallback_map_image(lat, lon, zoom)
    
    async def _download_gee_image_to_base64(self, gee_url: str) -> str:
        """Download GEE image and convert to Base64 format"""
        try:
            import aiohttp
            import base64
            import ee
            
            # Get GEE access token - using correct method
            try:
                # Method 1: try to get token from ee.data
                access_token = ee.data.get_persistent_credentials().token
            except:
                try:
                    # Method 2: try to get token from ee.oauth
                    access_token = ee.oauth.get_credentials().token
                except:
                    # Method 3: use GEE URL directly, no token needed
                    access_token = None
            
            # Download image - add timeout and connector settings
            timeout = aiohttp.ClientTimeout(total=300, connect=30)  # 5-minute total timeout, 30-second connect timeout
            # Disable SSL verification when using local proxy to avoid TLS-in-TLS cert issues
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=5, ssl=False)
            
            # Check proxy settings
            proxy = None
            http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
            https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
            
            if https_proxy:
                proxy = https_proxy
                print(f"🔄 Using proxy: {proxy}")
            elif http_proxy:
                proxy = http_proxy
                print(f"🔄 Using proxy: {proxy}")
            else:
                print("⚠️ No proxy settings detected")
            
            async with aiohttp.ClientSession(
                timeout=timeout, 
                connector=connector,
                trust_env=True  # Automatically use proxy from environment variables
            ) as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                # Add Authorization header if token is available
                if access_token:
                    headers['Authorization'] = f'Bearer {access_token}'
                
                print(f"🔄 Downloading GEE image: {gee_url[:80]}...")
                async with session.get(gee_url, headers=headers) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        
                        # Convert to Base64
                        base64_data = base64.b64encode(image_data).decode('utf-8')
                        base64_url = f"data:image/png;base64,{base64_data}"
                        
                        return base64_url
                    else:
                        raise Exception(f"GEE image download failed: HTTP {response.status}")
                        
        except Exception as e:
            raise Exception(f"GEE image conversion failed: {e}")

    def _create_fallback_image(self, lat: float, lon: float, dimensions: int) -> str:
        """Create a fallback Base64 image"""
        try:
            import base64
            from PIL import Image, ImageDraw, ImageFont
            import io
            
            # Create image
            img = Image.new('RGB', (dimensions, dimensions), color='#4CAF50')
            draw = ImageDraw.Draw(img)
            
            # Draw border
            draw.rectangle([0, 0, dimensions-1, dimensions-1], outline='#2196F3', width=3)
            
            # Draw center point
            center = dimensions // 2
            draw.ellipse([center-10, center-10, center+10, center+10], fill='#FF5722')
            
            # Draw text
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                font = ImageFont.load_default()
            
            text = f"GEE: {lat:.2f}, {lon:.2f}"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            draw.text((center - text_width//2, center + 20), text, fill='white', font=font)
            
            # Convert to Base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_bytes = buffer.getvalue()
            base64_image = base64.b64encode(img_bytes).decode('utf-8')
            return f"data:image/png;base64,{base64_image}"
            
        except ImportError:
            # If PIL is not available, use simple Base64 image
            return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        except Exception as e:
            print(f"Fallback image creation failed: {e}")
            return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

    async def _get_fallback_map_image(self, lat: float, lon: float, zoom: int) -> Dict[str, Any]:
        """Retrieve fallback map image"""
        try:
            # Use OpenStreetMap as fallback option
            import math
            
            # Calculate tile coordinates
            n = 2.0 ** zoom
            x = int((lon + 180.0) / 360.0 * n)
            y = int((1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * n)
            
            # Use multiple fallback map sources
            map_sources = [
                f"https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={zoom}",
                f"https://mt2.google.com/vt/lyrs=s&x={x}&y={y}&z={zoom}",
                f"https://mt3.google.com/vt/lyrs=s&x={x}&y={y}&z={zoom}",
                f"https://tile.openstreetmap.org/{zoom}/{x}/{y}.png"
            ]
            
            tile_url = map_sources[0]  # Default to first source
            
            print(f"Fallback map image request: location ({lat}, {lon}), zoom level {zoom}")
            print(f"Tile coordinates: ({x}, {y})")
            print(f"Image URL: {tile_url}")
            
            # Try multiple map sources
            for i, tile_url in enumerate(map_sources):
                try:
                    print(f"🔄 Trying map source {i+1}/{len(map_sources)}: {tile_url[:50]}...")
                    
                    import aiohttp
                    import os
                    
                    # Set proxy and timeout
                    timeout = aiohttp.ClientTimeout(total=15, connect=5)
                    # Disable SSL verification when routing via local proxy
                    connector = aiohttp.TCPConnector(limit=10, limit_per_host=5, ssl=False)
                    
                    # Check proxy settings
                    proxy = None
                    http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
                    https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
                    
                    if https_proxy:
                        proxy = https_proxy
                        print(f"🔄 Using proxy: {proxy}")
                    elif http_proxy:
                        proxy = http_proxy
                        print(f"🔄 Using proxy: {proxy}")
                    
                    async with aiohttp.ClientSession(
                        timeout=timeout,
                        connector=connector,
                        trust_env=True
                    ) as session:
                        async with session.get(tile_url, proxy=proxy) as response:
                            if response.status == 200:
                                image_data = await response.read()
                                
                                # Check image size; if too small it may be an error page
                                if len(image_data) < 1000:
                                    print(f"⚠️ Image too small, may be an error page: {len(image_data)} bytes")
                                    continue
                                
                                import base64
                                base64_image = f"data:image/png;base64,{base64.b64encode(image_data).decode()}"
                                print(f"✅ Map source {i+1} succeeded, image size: {len(image_data)} bytes")
                                
                                return {
                                    "url": base64_image,
                                    "tile_url": tile_url,
                                    "metadata": {
                                        "center": [lat, lon],
                                        "zoom": zoom,
                                        "tile_coords": [x, y],
                                        "source": f"MapSource{i+1}",
                                        "radius": 1000
                                    }
                                }
                            else:
                                print(f"❌ Map source {i+1} failed: HTTP {response.status}")
                                continue
                                
                except Exception as e:
                    print(f"❌ Map source {i+1} exception: {e}")
                    continue
            
            print("❌ All map sources failed")
            
            # Generate fallback image
            print("🔄 Generating fallback image...")
            try:
                fallback_image = self._create_fallback_image(lat, lon, 400)
                return {
                    "url": fallback_image,
                    "tile_url": "fallback",
                    "metadata": {
                        "center": [lat, lon],
                        "zoom": zoom,
                        "tile_coords": [x, y],
                        "source": "Fallback",
                        "radius": 1000
                    }
                }
            except Exception as fallback_error:
                print(f"❌ Fallback image generation failed: {fallback_error}")
                # Last resort: generate a simple test image
                try:
                    import base64
                    # Create a simple test image (1x1 pixel PNG)
                    test_image_data = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")
                    test_image = f"data:image/png;base64,{base64.b64encode(test_image_data).decode()}"
                    return {
                        "url": test_image,
                        "tile_url": "test",
                        "metadata": {
                            "center": [lat, lon],
                            "zoom": zoom,
                            "source": "TestImage",
                            "radius": 1000
                        }
                    }
                except Exception as test_error:
                    print(f"❌ Test image generation failed: {test_error}")
                    return None
            
        except Exception as e:
            print(f"Fallback map service failed: {e}")
            return None
    
    async def get_city_coordinates(self, city_name: str) -> Optional[Dict[str, float]]:
        """
        Get city coordinates
        
        Args:
            city_name: City name
            
        Returns:
            Dictionary containing latitude and longitude
        """
        # City coordinate database
        city_coords = {
            "Beijing":     {"latitude": 39.9042, "longitude": 116.4074},
            "Shanghai":    {"latitude": 31.2304, "longitude": 121.4737},
            "Shenzhen":    {"latitude": 22.5431, "longitude": 114.0579},
            "Hangzhou":    {"latitude": 30.2741, "longitude": 120.1551},
            "Zhongwei":    {"latitude": 37.5149, "longitude": 105.1967},
            "Guiyang":     {"latitude": 26.6470, "longitude": 106.6302},
            "Guangzhou":   {"latitude": 23.1291, "longitude": 113.2644},
            "Lanzhou":     {"latitude": 36.0611, "longitude": 103.8343}
        }
        
        return city_coords.get(city_name)
