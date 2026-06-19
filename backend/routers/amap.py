import os
import requests
from fastapi import APIRouter, HTTPException, Query
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/api/amap", tags=["amap"])
#辅助函数，根据经纬度获取行政区划 adcode
def get_adcode_by_location(lng: float, lat: float):
    """
    根据经纬度调用高德逆地理编码，获取行政区划 adcode。
    """
    amap_key = os.getenv("AMAP_KEY")

    if not amap_key:
        return None

    url = "https://restapi.amap.com/v3/geocode/regeo"

    params = {
        "key": amap_key,
        "location": f"{lng},{lat}",
        "extensions": "base",
        "output": "json"
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        if data.get("status") != "1":
            return None

        regeocode = data.get("regeocode", {})
        address_component = regeocode.get("addressComponent", {})

        adcode = address_component.get("adcode")

        # 有时候 adcode 可能返回空数组或空字符串，统一处理
        if isinstance(adcode, list):
            return adcode[0] if adcode else None

        return adcode or None

    except Exception:
        return None

@router.get("/search")
def search_amap_poi(
    keywords: str = Query(..., description="搜索关键词"),
    city: str = Query("410324", description="城市/区县 adcode，默认栾川县"),
):
    """
    调用高德 Web 服务 POI 关键字搜索。
    """
    amap_key = os.getenv("AMAP_KEY")

    if not amap_key:
        raise HTTPException(status_code=500, detail="未配置 AMAP_KEY")

    url = "https://restapi.amap.com/v3/place/text"

    params = {
        "key": amap_key,
        "keywords": keywords,
        "city": city,
        "citylimit": "false",
        "output": "json",
        "offset": 10,
        "page": 1,
        "extensions": "base"
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        if data.get("status") != "1":
            raise HTTPException(
                status_code=500,
                detail=f"高德 POI 搜索异常：{data.get('info', '未知错误')}"
            )

        pois = data.get("pois", [])

        results = []

        for poi in pois:
            location = poi.get("location", "")

            if not location or "," not in location:
                continue

            lng, lat = location.split(",")

            lng_value = float(lng)
            lat_value = float(lat)

            # 高德 POI 搜索结果里的 adcode 有时为 null
            # 如果为空，就根据经纬度调用逆地理编码获取 adcode
            adcode = poi.get("adcode")

            if not adcode:
                adcode = get_adcode_by_location(lng_value, lat_value)

            results.append({
                "id": poi.get("id"),
                "name": poi.get("name"),
                "type": poi.get("type"),
                "address": poi.get("address"),
                "pname": poi.get("pname"),
                "cityname": poi.get("cityname"),
                "adname": poi.get("adname"),
                "adcode": adcode,
                "lng": lng_value,
                "lat": lat_value
            })

        return {
            "keywords": keywords,
            "count": len(results),
            "pois": results
        }

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"请求高德 POI 失败：{str(e)}")


@router.get("/tips")
def amap_tips(
    keywords: str = Query(..., description="输入提示关键词"),
    city: str = Query("410324", description="默认栾川县")
):
    """
    调用高德输入提示接口。
    """
    amap_key = os.getenv("AMAP_KEY")

    if not amap_key:
        raise HTTPException(status_code=500, detail="未配置 AMAP_KEY")

    url = "https://restapi.amap.com/v3/assistant/inputtips"

    params = {
        "key": amap_key,
        "keywords": keywords,
        "city": city,
        "datatype": "all",
        "output": "json"
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        if data.get("status") != "1":
            raise HTTPException(
                status_code=500,
                detail=f"高德输入提示异常：{data.get('info', '未知错误')}"
            )

        tips = []

        for item in data.get("tips", []):
            tips.append({
                "id": item.get("id"),
                "name": item.get("name"),
                "district": item.get("district"),
                "address": item.get("address"),
                "location": item.get("location")
            })

        return {
            "keywords": keywords,
            "tips": tips
        }

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"请求高德输入提示失败：{str(e)}")

@router.get("/route")
def amap_route(
    origin: str = Query(..., description="起点，经度,纬度"),
    destination: str = Query(..., description="终点，经度,纬度"),
    mode: str = Query("walking", description="walking 或 driving")
):
    """
    调用高德路径规划。
    walking: 步行
    driving: 驾车
    """
    amap_key = os.getenv("AMAP_KEY")

    if not amap_key:
        raise HTTPException(status_code=500, detail="未配置 AMAP_KEY")

    if mode == "driving":
        url = "https://restapi.amap.com/v3/direction/driving"
    else:
        url = "https://restapi.amap.com/v3/direction/walking"

    params = {
        "key": amap_key,
        "origin": origin,
        "destination": destination,
        "output": "json"
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        if data.get("status") != "1":
            raise HTTPException(
                status_code=500,
                detail=f"高德路径规划异常：{data.get('info', '未知错误')}"
            )

        route = data.get("route", {})
        paths = route.get("paths", [])

        if not paths:
            return {
                "mode": mode,
                "distance": None,
                "duration": None,
                "polyline": [],
                "raw": data
            }

        path = paths[0]

        coordinates = []

        for step in path.get("steps", []):
            polyline = step.get("polyline", "")

            if not polyline:
                continue

            points = polyline.split(";")

            for point in points:
                if "," not in point:
                    continue

                lng, lat = point.split(",")
                coordinates.append([float(lng), float(lat)])

        return {
            "mode": mode,
            "distance": float(path.get("distance", 0)),
            "duration": float(path.get("duration", 0)),
            "polyline": coordinates,
            "raw": {
                "origin": origin,
                "destination": destination
            }
        }

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"请求高德路径规划失败：{str(e)}") 
@router.get("/regeo")
def amap_regeo(
    lng: float = Query(..., description="经度"),
    lat: float = Query(..., description="纬度"),
    radius: int = Query(800, description="查询半径，单位米")
):
    """
    根据经纬度调用高德逆地理编码，获取所在行政区、地址和附近 POI。
    用于点击地图任意位置后查询该位置周边信息。
    """
    amap_key = os.getenv("AMAP_KEY")

    if not amap_key:
        raise HTTPException(status_code=500, detail="未配置 AMAP_KEY")

    url = "https://restapi.amap.com/v3/geocode/regeo"

    params = {
        "key": amap_key,
        "location": f"{lng},{lat}",
        "radius": radius,
        "extensions": "all",
        "output": "json"
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        if data.get("status") != "1":
            raise HTTPException(
                status_code=500,
                detail=f"高德逆地理编码异常：{data.get('info', '未知错误')}"
            )

        regeocode = data.get("regeocode", {})
        address_component = regeocode.get("addressComponent", {})

        adcode = address_component.get("adcode")
        if isinstance(adcode, list):
            adcode = adcode[0] if adcode else None

        pois = []
        for item in regeocode.get("pois", [])[:10]:
            location = item.get("location", "")

            poi_lng = None
            poi_lat = None

            if location and "," in location:
                arr = location.split(",")
                if len(arr) >= 2:
                    try:
                        poi_lng = float(arr[0])
                        poi_lat = float(arr[1])
                    except ValueError:
                        pass

            pois.append({
                "id": item.get("id"),
                "name": item.get("name"),
                "type": item.get("type"),
                "address": item.get("address"),
                "distance": item.get("distance"),
                "direction": item.get("direction"),
                "lng": poi_lng,
                "lat": poi_lat
            })

        return {
            "formatted_address": regeocode.get("formatted_address"),
            "province": address_component.get("province"),
            "city": address_component.get("city"),
            "district": address_component.get("district"),
            "township": address_component.get("township"),
            "adcode": adcode,
            "lng": lng,
            "lat": lat,
            "pois": pois
        }

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"请求高德逆地理编码失败：{str(e)}")
def parse_amap_polyline(polyline: str):
    """
    将高德行政区 polyline 转为 GeoJSON Polygon / MultiPolygon 坐标。
    高德 polyline 常见格式：
    lng,lat;lng,lat|lng,lat;lng,lat
    """
    if not polyline:
        return None

    polygons = []

    parts = polyline.split("|")

    for part in parts:
        ring = []

        points = part.split(";")

        for point in points:
            if "," not in point:
                continue

            lng, lat = point.split(",")

            try:
                ring.append([float(lng), float(lat)])
            except ValueError:
                continue

        if len(ring) >= 3:
            # GeoJSON Polygon 外环需要闭合
            if ring[0] != ring[-1]:
                ring.append(ring[0])

            polygons.append([ring])

    if not polygons:
        return None

    if len(polygons) == 1:
        return {
            "type": "Polygon",
            "coordinates": polygons[0]
        }

    return {
        "type": "MultiPolygon",
        "coordinates": polygons
    }
@router.get("/district")
def amap_district(
    keywords: str = Query(..., description="行政区名称，例如 郑州市、焦作市、二七区"),
    subdistrict: int = Query(0, description="下级行政区级数，默认0")
):
    """
    调用高德行政区域查询，返回行政区边界 GeoJSON。
    """
    amap_key = os.getenv("AMAP_KEY")

    if not amap_key:
        raise HTTPException(status_code=500, detail="未配置 AMAP_KEY")

    url = "https://restapi.amap.com/v3/config/district"

    params = {
        "key": amap_key,
        "keywords": keywords,
        "subdistrict": subdistrict,
        "extensions": "all",
        "output": "json"
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        if data.get("status") != "1":
            raise HTTPException(
                status_code=500,
                detail=f"高德行政区查询异常：{data.get('info', '未知错误')}"
            )

        districts = data.get("districts", [])

        features = []

        for item in districts:
            geometry = parse_amap_polyline(item.get("polyline", ""))

            if not geometry:
                continue

            features.append({
                "type": "Feature",
                "properties": {
                    "name": item.get("name"),
                    "adcode": item.get("adcode"),
                    "citycode": item.get("citycode"),
                    "level": item.get("level"),
                    "center": item.get("center")
                },
                "geometry": geometry
            })

        return {
            "keywords": keywords,
            "count": len(features),
            "geojson": {
                "type": "FeatureCollection",
                "features": features
            }
        }

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"请求高德行政区查询失败：{str(e)}")     