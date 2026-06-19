#周边交通态势
import os
import requests
from fastapi import APIRouter, HTTPException, Query
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/api/traffic", tags=["traffic"])


def parse_traffic_result(data, lng, lat, radius, query_mode, matched_road=None, used_radius=None):
    trafficinfo = data.get("trafficinfo", {})
    evaluation = trafficinfo.get("evaluation", {})

    return {
        "success": True,
        "lng": lng,
        "lat": lat,
        "radius": radius,
        "used_radius": used_radius or radius,
        "query_mode": query_mode,
        "matched_road": matched_road,
        "description": trafficinfo.get("description", "暂无交通描述"),
        "evaluation_status": evaluation.get("status"),
        "evaluation_description": evaluation.get("description", "暂无评价"),
        "expedite": evaluation.get("expedite", "暂无"),
        "congested": evaluation.get("congested", "暂无"),
        "blocked": evaluation.get("blocked", "暂无"),
        "unknown": evaluation.get("unknown", "暂无"),
        "amap_info": data.get("info"),
        "amap_infocode": data.get("infocode")
    }


def request_circle_traffic(amap_key, lng, lat, radius):
    url = "https://restapi.amap.com/v3/traffic/status/circle"

    params = {
        "key": amap_key,
        "location": f"{lng},{lat}",
        "radius": radius,
        "output": "json"
    }

    res = requests.get(url, params=params, timeout=10)
    return res.json()


def request_regeo_for_roads(amap_key, lng, lat):
    """
    根据点击位置反查附近道路和 adcode。
    """
    url = "https://restapi.amap.com/v3/geocode/regeo"

    params = {
        "key": amap_key,
        "location": f"{lng},{lat}",
        "radius": 1000,
        "extensions": "all",
        "roadlevel": 1,
        "output": "json"
    }

    res = requests.get(url, params=params, timeout=10)
    data = res.json()

    if data.get("status") != "1":
        return {
            "adcode": None,
            "roads": []
        }

    regeocode = data.get("regeocode", {})
    address_component = regeocode.get("addressComponent", {})

    adcode = address_component.get("adcode")
    if isinstance(adcode, list):
        adcode = adcode[0] if adcode else None

    road_names = []

    # 1. nearby roads
    for item in regeocode.get("roads", []) or []:
        name = item.get("name")
        if name and name not in road_names:
            road_names.append(name)

    # 2. road intersections
    for item in regeocode.get("roadinters", []) or []:
        first_name = item.get("first_name")
        second_name = item.get("second_name")

        if first_name and first_name not in road_names:
            road_names.append(first_name)

        if second_name and second_name not in road_names:
            road_names.append(second_name)

    return {
        "adcode": adcode,
        "roads": road_names
    }


def request_road_traffic(amap_key, road_name, adcode):
    """
    指定道路交通态势。
    """
    url = "https://restapi.amap.com/v3/traffic/status/road"

    params = {
        "key": amap_key,
        "name": road_name,
        "adcode": adcode,
        "output": "json"
    }

    res = requests.get(url, params=params, timeout=10)
    return res.json()


@router.get("/circle")
def get_circle_traffic(
    lng: float = Query(..., description="中心点经度"),
    lat: float = Query(..., description="中心点纬度"),
    radius: int = Query(1000, description="查询半径，单位米")
):
    """
    周边交通态势查询：
    1. 优先查询圆形区域交通态势；
    2. 如果圆形区域无数据，则通过逆地理编码获取附近道路；
    3. 使用指定道路交通态势接口作为备用。
    """
    amap_key = os.getenv("AMAP_KEY")

    if not amap_key:
        raise HTTPException(status_code=500, detail="未配置 AMAP_KEY")

    try:
        errors = []

        # 第一步：多半径尝试圆形区域交通态势
        candidate_radii = []

        for r in [radius, 1500, 3000, 5000]:
            if r not in candidate_radii:
                candidate_radii.append(r)

        for r in candidate_radii:
            data = request_circle_traffic(amap_key, lng, lat, r)

            if data.get("status") == "1":
                return parse_traffic_result(
                    data=data,
                    lng=lng,
                    lat=lat,
                    radius=radius,
                    used_radius=r,
                    query_mode="circle",
                    matched_road=None
                )

            errors.append({
                "type": "circle",
                "radius": r,
                "info": data.get("info"),
                "infocode": data.get("infocode")
            })

        # 第二步：圆形接口失败后，查附近道路
        regeo = request_regeo_for_roads(amap_key, lng, lat)
        adcode = regeo.get("adcode")
        road_names = regeo.get("roads", [])

        if adcode and road_names:
            for road_name in road_names[:5]:
                road_data = request_road_traffic(amap_key, road_name, adcode)

                if road_data.get("status") == "1":
                    return parse_traffic_result(
                        data=road_data,
                        lng=lng,
                        lat=lat,
                        radius=radius,
                        used_radius=radius,
                        query_mode="road_fallback",
                        matched_road=road_name
                    )

                errors.append({
                    "type": "road",
                    "road_name": road_name,
                    "adcode": adcode,
                    "info": road_data.get("info"),
                    "infocode": road_data.get("infocode")
                })

        # 第三步：两种接口都失败，返回容错结果
        return {
            "success": False,
            "lng": lng,
            "lat": lat,
            "radius": radius,
            "used_radius": None,
            "query_mode": "none",
            "matched_road": None,
            "description": "当前区域暂无可用交通态势数据",
            "evaluation_status": None,
            "evaluation_description": "暂无交通态势数据",
            "expedite": "暂无",
            "congested": "暂无",
            "blocked": "暂无",
            "unknown": "暂无",
            "amap_info": errors[-1]["info"] if errors else "UNKNOWN_ERROR",
            "amap_infocode": errors[-1]["infocode"] if errors else "20003",
            "retry_errors": errors,
            "message": "已尝试圆形区域交通态势和附近道路交通态势，但高德未返回有效路况。"
        }
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"请求高德道路交通态势失败：{str(e)}")