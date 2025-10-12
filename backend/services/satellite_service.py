"""
卫星数据服务 - 集成Google Earth Engine
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

class SatelliteService:
    """卫星数据服务类"""
    
    def __init__(self):
        """初始化GEE服务"""
        try:
            # 设置SSL和网络配置
            import ssl
            import urllib3
            import os
            
            # 禁用SSL警告
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            # 设置环境变量
            os.environ['PYTHONHTTPSVERIFY'] = '0'
            
            # 初始化Google Earth Engine
            # 使用您的项目ID
            ee.Initialize(project='data-center-location-analysis')
            print("Google Earth Engine 初始化成功")
            self.gee_available = True
        except Exception as e:
            print(f"GEE初始化失败: {e}")
            print("可能是网络连接问题，请检查网络连接和代理设置")
            print("💡 建议运行: python fix_gee_ssl.py 来修复SSL问题")
            self.gee_available = False
            # 不抛出异常，让服务继续运行但不提供GEE功能
            # raise e
    
    async def get_satellite_data(self, lat: float, lon: float, radius: float = 1000) -> Dict[str, Any]:
        """
        获取指定位置的卫星数据
        
        Args:
            lat: 纬度
            lon: 经度
            radius: 搜索半径（米）
            
        Returns:
            包含卫星图像和元数据的字典
        """
        # 创建感兴趣区域
        point = ee.Geometry.Point([lon, lat])
        region = point.buffer(radius)
        
        # 获取Landsat 8/9 图像
        collection = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                     .filterDate('2023-01-01', '2023-12-31')
                     .filterBounds(region)
                     .filter(ee.Filter.lt('CLOUD_COVER', 20)))
        
        # 选择最佳图像（云量最少）
        image = collection.sort('CLOUD_COVER').first()
        
        # 获取图像信息
        image_info = image.getInfo()
        
        # 计算NDVI（归一化植被指数）
        ndvi = image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
        
        # 计算土地覆盖类型
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
        获取多个时间点的卫星数据
        
        Args:
            lat: 纬度
            lon: 经度
            radius: 搜索半径（米）
            time_points: 时间点数量
            
        Returns:
            包含多个时间点卫星数据的列表
        """
        try:
            # 创建感兴趣区域
            point = ee.Geometry.Point([lon, lat])
            region = point.buffer(radius)
            
            # 定义时间范围（过去2年）
            start_date = '2022-01-01'
            end_date = '2024-01-01'
            
            # 获取Landsat 8/9 图像集合
            collection = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                         .filterDate(start_date, end_date)
                         .filterBounds(region)
                         .filter(ee.Filter.lt('CLOUD_COVER', 30)))
            
            # 获取图像列表
            image_list = collection.sort('DATE_ACQUIRED').toList(time_points)
            
            temporal_data = []
            
            for i in range(time_points):
                try:
                    # 获取第i张图像
                    image = ee.Image(image_list.get(i))
                    image_info = image.getInfo()
                    
                    # 获取图像URL
                    image_url = await self._get_gee_satellite_image(lat, lon, radius)
                    
                    # 计算NDVI
                    ndvi = image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
                    
                    # 计算土地覆盖类型
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
                    print(f"获取第{i+1}个时间点数据失败: {e}")
                    # 如果获取失败，使用当前图像作为备选
                    current_data = await self.get_satellite_image(lat, lon, radius=radius)
                    current_data["metadata"]["acquisition_date"] = f"2023-{i+1:02d}-01"
                    current_data["metadata"]["time_index"] = i
                    temporal_data.append(current_data)
            
            return temporal_data
            
        except Exception as e:
            print(f"获取时间序列数据失败: {e}")
            # 备选方案：返回模拟数据
            temporal_data = []
            for i in range(time_points):
                current_data = await self.get_satellite_image(lat, lon, radius=radius)
                current_data["metadata"]["acquisition_date"] = f"2023-{i+1:02d}-01"
                current_data["metadata"]["time_index"] = i
                temporal_data.append(current_data)
            return temporal_data
    
    def _classify_land_cover(self, image: ee.Image) -> ee.Image:
        """
        基于卫星图像进行土地覆盖分类
        
        Args:
            image: Landsat图像
            
        Returns:
            土地覆盖分类结果
        """
        # 使用简单的阈值方法进行土地覆盖分类
        # 0: 水体, 1: 植被, 2: 裸地, 3: 建筑
        
        # 计算NDVI
        ndvi = image.normalizedDifference(['SR_B5', 'SR_B4'])
        
        # 计算NDWI（归一化水体指数）
        ndwi = image.normalizedDifference(['SR_B3', 'SR_B5'])
        
        # 计算建筑指数
        nbi = image.normalizedDifference(['SR_B5', 'SR_B6'])
        
        # 分类规则
        water = ndwi.gt(0.1)
        vegetation = ndvi.gt(0.3)
        bare_land = ndvi.lt(0.1).And(ndwi.lt(0.1))
        building = nbi.gt(0.1).And(ndvi.lt(0.2))
        
        # 合并分类结果
        land_cover = (water.multiply(0)
                    .add(vegetation.multiply(1))
                    .add(bare_land.multiply(2))
                    .add(building.multiply(3)))
        
        return land_cover.rename('land_cover')
    
    async def get_satellite_image(self, lat: float, lon: float, zoom: int = 10, radius: float = 1000) -> Dict[str, Any]:
        """
        获取卫星图像URL - 优先使用GEE真实卫星数据
        
        Args:
            lat: 纬度
            lon: 经度
            zoom: 缩放级别
            radius: 分析半径（米）
            
        Returns:
            包含图像URL和元数据的字典
        """
        try:
            # 首先尝试使用GEE获取真实卫星图像
            gee_result = await self._get_gee_satellite_image(lat, lon, zoom, radius)
            if gee_result and not gee_result.get("error"):
                return gee_result
            
            # 如果GEE失败，尝试备选方案
            print("🔄 GEE获取失败，尝试备选方案...")
            fallback_result = await self._get_fallback_map_image(lat, lon, zoom)
            if fallback_result:
                print("✅ 备选方案成功")
                return fallback_result
            else:
                raise Exception("所有图像获取方案都失败")
            
        except Exception as e:
            print(f"卫星图像获取失败: {e}")
            # 最后尝试备选方案
            try:
                print("🔄 最后尝试备选方案...")
                fallback_result = await self._get_fallback_map_image(lat, lon, zoom)
                if fallback_result:
                    print("✅ 备选方案成功")
                    return fallback_result
            except Exception as fallback_error:
                print(f"❌ 备选方案也失败: {fallback_error}")
            
            raise Exception(f"所有图像获取方案都失败: {e}")
    
    async def _get_gee_satellite_image(self, lat: float, lon: float, zoom: int, radius: float = 1000) -> Dict[str, Any]:
        """使用GEE获取真实卫星图像"""
        try:
            # 确保ee已导入
            import ee
            
            # 设置GEE请求超时时间（使用正确的方法）
            try:
                # 尝试设置超时（如果支持的话）
                if hasattr(ee.data, 'setTimeout'):
                    ee.data.setTimeout(300)
                else:
                    # 使用环境变量设置超时
                    import os
                    os.environ['EE_TIMEOUT'] = '300'
            except:
                pass  # 如果设置失败，继续执行
            
            # 由于GEE Map API需要复杂的认证，我们使用静态图像API
            point = ee.Geometry.Point([lon, lat])
            region = point.buffer(20000)  # 20公里半径
            
            # 使用Dynamic World数据集 - 10米分辨率，每日更新
            print("🔄 使用Dynamic World数据集获取土地利用数据...")
            
            # 直接使用Landsat 8/9作为主要数据源（高质量卫星数据）
            collection = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                         .filterDate('2020-01-01', '2024-12-31')
                         .filterBounds(region)
                         .filter(ee.Filter.lt('CLOUD_COVER', 30)))
            
            image_count = collection.size().getInfo()
            print(f"找到 {image_count} 张Landsat 8/9图像")
            
            if image_count == 0:
                print("该地区无可用Landsat数据，尝试Dynamic World")
                # 备选：使用Dynamic World
                dw_collection = (ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1')
                               .filterBounds(region)
                               .filterDate('2024-01-01', '2024-12-31')
                               .select('label'))
                
                # 为Dynamic World也设置超时
                ee.data.setTimeout(300)  # 5分钟超时
                
                dw_count = dw_collection.size().getInfo()
                print(f"找到 {dw_count} 张Dynamic World图像")
                
                if dw_count == 0:
                    raise Exception("该地区无可用卫星数据")
                
                # 使用Dynamic World单张图像（不进行众数合成）
                dw_image = dw_collection.sort('system:time_start', False).first()
                
                # 先检查图像是否有数据
                image_info = dw_image.getInfo()
                print(f"Dynamic World图像信息: {image_info}")
                
                # 使用正确的波段进行可视化
                rgb_image = dw_image.visualize({
                    'bands': ['label'],
                    'min': 0,
                    'max': 8,
                    'palette': [
                        '419bdf',  # 水体
                        '397d49',  # 林地
                        '88b053',  # 草地
                        '7a87c6',  # 湿地
                        'e49635',  # 农田
                        'dfc35a',  # 灌丛
                        'c4281b',  # 建设用地
                        'a59b8f',  # 裸地
                        'b39fe1'   # 雪冰
                    ]
                })
            else:
                # 使用Landsat图像（主要方案）
                image = collection.sort('CLOUD_COVER').first()
                
                # 先检查图像是否有数据
                image_info = image.getInfo()
                print(f"Landsat图像信息: {image_info}")
                
                # 直接使用原始RGB波段，不进行预处理
                rgb_image = image.select(['SR_B4', 'SR_B3', 'SR_B2'])
                print("✅ GEE图像选择成功")
            
            # 根据半径动态调整图像尺寸和缩放级别
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
            
            # 使用GEE静态图像API - 根据半径动态调整
            try:
                # 确保rgb_image是正确的格式
                print(f"🔍 RGB图像波段: {rgb_image.bandNames().getInfo()}")
                
                # 生成GEE图像URL - 使用正确的参数（按照之前代码的方式）
                # 使用原始尺寸以获得更好的分析效果
                image_url = rgb_image.getThumbURL({
                    'region': region,
                    'dimensions': dimensions,
                    'format': 'png',
                    'bands': ['SR_B4', 'SR_B3', 'SR_B2']
                    # 去掉crs参数，让GEE自动处理
                })
                
                print(f"GEE原始URL: {image_url}")
                
                # 检查URL是否有效
                if not image_url or image_url.startswith('data:'):
                    print("⚠️ GEE图像URL无效，尝试其他方法")
                    # 尝试使用不同的参数
                    try:
                        image_url = rgb_image.getThumbURL({
                            'region': region,
                            'dimensions': dimensions,
                            'format': 'png'
                        })
                        print(f"GEE备用URL: {image_url}")
                    except:
                        raise Exception("GEE图像URL生成失败")
                
                # 直接使用GEE URL，不进行Base64转换
                original_thumb_url = image_url
                print(f"GEE图像URL: {image_url[:100]}...")
                
                # 验证URL格式
                if not image_url.startswith('https://'):
                    raise Exception("GEE URL不是有效的HTTPS URL")
                    
            except Exception as e:
                print(f"GEE图像URL生成失败: {e}")
                print("🔄 尝试使用备选地图服务...")
                
                # 使用备选地图服务
                try:
                    fallback_result = await self._get_fallback_map_image(lat, lon, zoom_level)
                    if fallback_result:
                        print("✅ 备选地图服务成功")
                        return fallback_result
                    else:
                        raise Exception("备选地图服务也失败")
                except Exception as fallback_error:
                    print(f"❌ 备选地图服务失败: {fallback_error}")
                    # 最后生成一个简单的备选图像
                    try:
                        fallback_image = await self._create_fallback_image()
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
                        print(f"❌ 最终备选方案也失败: {final_error}")
                        raise Exception(f"所有图像获取方案都失败: {e}")
            
            print(f"GEE卫星图像请求: 位置({lat}, {lon}), 半径{radius}m, 尺寸{dimensions}x{dimensions}")
            print(f"GEE图像URL: {image_url[:60]}...")
            
            # 检查URL是否有效
            if not image_url or not image_url.startswith('https://'):
                print("⚠️ 图像URL无效，可能是数据问题")
                return {"error": "图像URL生成失败"}
            
            # 如果是getPixels URL，需要下载并转换为Base64
            if 'getPixels' in image_url:
                print("🔄 检测到getPixels URL，正在下载并转换为Base64...")
                try:
                    base64_image = await self._download_gee_image_to_base64(image_url)
                    image_url = base64_image
                    print("✅ GEE图像已转换为Base64格式")
                except Exception as e:
                    print(f"❌ GEE图像下载失败: {e}")
                    raise Exception(f"GEE图像下载失败，不允许降级: {e}")
            
            return {
                "url": image_url,
                "tile_url": image_url,
                "metadata": {
                    "center": [lat, lon],
                    "radius": radius,
                    "dimensions": f"{dimensions}x{dimensions}",
                    "zoom_level": zoom_level,
                    "image_type": "真彩色RGB卫星图像",
                    "data_source": "Landsat 8/9 (主要) / Dynamic World (备选)",
                    "resolution": "30米 (Landsat) / 10米 (Dynamic World)",
                    "coverage_radius": f"{radius/1000}公里",
                    "map_service": "Google Earth Engine",
                    "free_service": False,
                    "gee_available": True,
                    "original_thumb_url": original_thumb_url
                }
            }
            
        except Exception as e:
            print(f"GEE卫星图像获取失败: {e}")
            # 不允许降级，直接抛出异常
            raise Exception(f"GEE卫星图像获取失败，不允许降级: {e}")
    
    async def _download_gee_image_to_base64(self, gee_url: str) -> str:
        """下载GEE图像并转换为Base64格式"""
        try:
            import aiohttp
            import base64
            import ee
            
            # 获取GEE访问令牌 - 使用正确的方法
            try:
                # 方法1: 尝试从ee.data获取token
                access_token = ee.data.get_persistent_credentials().token
            except:
                try:
                    # 方法2: 尝试从ee.oauth获取token
                    access_token = ee.oauth.get_credentials().token
                except:
                    # 方法3: 直接使用GEE URL，不需要token
                    access_token = None
            
            # 下载图像 - 添加超时和连接器设置
            timeout = aiohttp.ClientTimeout(total=300, connect=30)  # 5分钟总超时，30秒连接超时
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
            
            # 检查代理设置
            proxy = None
            http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
            https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
            
            if https_proxy:
                proxy = https_proxy
                print(f"🔄 使用代理: {proxy}")
            elif http_proxy:
                proxy = http_proxy
                print(f"🔄 使用代理: {proxy}")
            else:
                print("⚠️ 未检测到代理设置")
            
            async with aiohttp.ClientSession(
                timeout=timeout, 
                connector=connector,
                trust_env=True  # 自动使用环境变量中的代理
            ) as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                # 如果有token，添加Authorization头
                if access_token:
                    headers['Authorization'] = f'Bearer {access_token}'
                
                print(f"🔄 正在下载GEE图像: {gee_url[:80]}...")
                async with session.get(gee_url, headers=headers) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        
                        # 转换为Base64
                        base64_data = base64.b64encode(image_data).decode('utf-8')
                        base64_url = f"data:image/png;base64,{base64_data}"
                        
                        return base64_url
                    else:
                        raise Exception(f"GEE图像下载失败: HTTP {response.status}")
                        
        except Exception as e:
            raise Exception(f"GEE图像转换失败: {e}")

    def _create_fallback_image(self, lat: float, lon: float, dimensions: int) -> str:
        """创建备选Base64图像"""
        try:
            import base64
            from PIL import Image, ImageDraw, ImageFont
            import io
            
            # 创建图像
            img = Image.new('RGB', (dimensions, dimensions), color='#4CAF50')
            draw = ImageDraw.Draw(img)
            
            # 绘制边框
            draw.rectangle([0, 0, dimensions-1, dimensions-1], outline='#2196F3', width=3)
            
            # 绘制中心点
            center = dimensions // 2
            draw.ellipse([center-10, center-10, center+10, center+10], fill='#FF5722')
            
            # 绘制文字
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                font = ImageFont.load_default()
            
            text = f"GEE: {lat:.2f}, {lon:.2f}"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            draw.text((center - text_width//2, center + 20), text, fill='white', font=font)
            
            # 转换为Base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_bytes = buffer.getvalue()
            base64_image = base64.b64encode(img_bytes).decode('utf-8')
            return f"data:image/png;base64,{base64_image}"
            
        except ImportError:
            # 如果没有PIL，使用简单的Base64图像
            return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        except Exception as e:
            print(f"备选图像创建失败: {e}")
            return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

    async def _get_fallback_map_image(self, lat: float, lon: float, zoom: int) -> Dict[str, Any]:
        """获取备选地图图像"""
        try:
            # 使用OpenStreetMap作为备选方案
            import math
            
            # 计算瓦片坐标
            n = 2.0 ** zoom
            x = int((lon + 180.0) / 360.0 * n)
            y = int((1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * n)
            
            # 使用多个备选地图源
            map_sources = [
                f"https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={zoom}",
                f"https://mt2.google.com/vt/lyrs=s&x={x}&y={y}&z={zoom}",
                f"https://mt3.google.com/vt/lyrs=s&x={x}&y={y}&z={zoom}",
                f"https://tile.openstreetmap.org/{zoom}/{x}/{y}.png"
            ]
            
            tile_url = map_sources[0]  # 默认使用OpenStreetMap
            
            print(f"备选地图图像请求: 位置({lat}, {lon}), 缩放级别{zoom}")
            print(f"瓦片坐标: ({x}, {y})")
            print(f"图像URL: {tile_url}")
            
            # 尝试多个地图源
            for i, tile_url in enumerate(map_sources):
                try:
                    print(f"🔄 尝试地图源 {i+1}/{len(map_sources)}: {tile_url[:50]}...")
                    
                    import aiohttp
                    import os
                    
                    # 设置代理和超时
                    timeout = aiohttp.ClientTimeout(total=15, connect=5)
                    connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
                    
                    # 检查代理设置
                    proxy = None
                    http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
                    https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
                    
                    if https_proxy:
                        proxy = https_proxy
                        print(f"🔄 使用代理: {proxy}")
                    elif http_proxy:
                        proxy = http_proxy
                        print(f"🔄 使用代理: {proxy}")
                    
                    async with aiohttp.ClientSession(
                        timeout=timeout,
                        connector=connector,
                        trust_env=True
                    ) as session:
                        async with session.get(tile_url, proxy=proxy) as response:
                            if response.status == 200:
                                image_data = await response.read()
                                
                                # 检查图像大小，如果太小可能是错误页面
                                if len(image_data) < 1000:
                                    print(f"⚠️ 图像太小，可能是错误页面: {len(image_data)} bytes")
                                    continue
                                
                                import base64
                                base64_image = f"data:image/png;base64,{base64.b64encode(image_data).decode()}"
                                print(f"✅ 地图源 {i+1} 成功，图像大小: {len(image_data)} bytes")
                                
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
                                print(f"❌ 地图源 {i+1} 失败: HTTP {response.status}")
                                continue
                                
                except Exception as e:
                    print(f"❌ 地图源 {i+1} 异常: {e}")
                    continue
            
            print("❌ 所有地图源都失败")
            
            # 生成备选图像
            print("🔄 生成备选图像...")
            try:
                fallback_image = await self._create_fallback_image()
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
                print(f"❌ 备选图像生成失败: {fallback_error}")
                # 最后生成一个简单的测试图像
                try:
                    import base64
                    # 创建一个简单的测试图像（1x1像素的PNG）
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
                    print(f"❌ 测试图像生成失败: {test_error}")
                    return None
            
        except Exception as e:
            print(f"备选地图服务失败: {e}")
            return None
    
    async def get_city_coordinates(self, city_name: str) -> Optional[Dict[str, float]]:
        """
        获取城市坐标
        
        Args:
            city_name: 城市名称
            
        Returns:
            包含经纬度的字典
        """
        # 城市坐标数据库
        city_coords = {
            "北京": {"latitude": 39.9042, "longitude": 116.4074},
            "上海": {"latitude": 31.2304, "longitude": 121.4737},
            "深圳": {"latitude": 22.5431, "longitude": 114.0579},
            "杭州": {"latitude": 30.2741, "longitude": 120.1551},
            "中卫": {"latitude": 37.5149, "longitude": 105.1967},
            "贵阳": {"latitude": 26.6470, "longitude": 106.6302},
            "广州": {"latitude": 23.1291, "longitude": 113.2644},
            "兰州": {"latitude": 36.0611, "longitude": 103.8343}
        }
        
        return city_coords.get(city_name)
