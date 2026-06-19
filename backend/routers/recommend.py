#动态路线推荐
import os
import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

from database import get_connection

load_dotenv()

router = APIRouter(prefix="/api/recommend", tags=["recommend"])


class DynamicRecommendRequest(BaseModel):
    user_type: str = "first_time"  # first_time / normal / strong
    time_slot: str = "上午"
    traffic_lng: float = 111.65632
    traffic_lat: float = 33.774569
    traffic_radius: int = 3000


def get_weather_info():
    amap_key = os.getenv("AMAP_KEY")

    if not amap_key:
        return None

    url = "https://restapi.amap.com/v3/weather/weatherInfo"

    params = {
        "key": amap_key,
        "city": "410324",
        "extensions": "base",
        "output": "json"
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        if data.get("status") != "1" or not data.get("lives"):
            return None

        item = data["lives"][0]

        return {
            "weather": item.get("weather"),
            "temperature": item.get("temperature"),
            "windpower": item.get("windpower"),
            "reporttime": item.get("reporttime")
        }

    except Exception:
        return None


def get_traffic_info(lng, lat, radius):
    amap_key = os.getenv("AMAP_KEY")

    if not amap_key:
        return None

    url = "https://restapi.amap.com/v3/traffic/status/circle"

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
            return {
                "description": "当前区域暂无可用交通态势数据",
                "evaluation_description": "暂无交通态势数据",
                "status": None,
                "expedite": "暂无",
                "congested": "暂无",
                "blocked": "暂无",
                "amap_info": data.get("info"),
                "amap_infocode": data.get("infocode")
            }
        trafficinfo = data.get("trafficinfo", {})
        evaluation = trafficinfo.get("evaluation", {})

        return {
            "description": trafficinfo.get("description"),
            "evaluation_description": evaluation.get("description"),
            "status": evaluation.get("status"),
            "expedite": evaluation.get("expedite"),
            "congested": evaluation.get("congested"),
            "blocked": evaluation.get("blocked")
        }

    except Exception:
        return None


def get_routes():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        """
        SELECT
            id,
            route_name,
            difficulty,
            node_sequence,
            estimated_time,
            suitable_user,
            description,
            source,
            source_url
        FROM route_template
        ORDER BY id;
        """
    )

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return list(rows)


def get_crowd_dict():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        """
        SELECT
            p.name AS poi_name,
            c.crowd_value,
            c.crowd_level
        FROM crowd_status c
        JOIN laojunshan_poi p
        ON c.poi_id = p.id;
        """
    )

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return {
        row["poi_name"]: {
            "value": row["crowd_value"],
            "level": row["crowd_level"]
        }
        for row in rows
    }


def score_route(route, weather, traffic, crowd_dict, user_type):
    score = 100
    reasons = []
    warnings = []

    difficulty = route.get("difficulty")
    node_sequence = route.get("node_sequence") or ""
    nodes = [item.strip() for item in node_sequence.split(";") if item.strip()]

    # 1. 用户类型评分
    if user_type == "first_time":
        if difficulty == "easy":
            score += 15
            reasons.append("初次游玩游客更适合初阶路线，步行强度较低。")
        elif difficulty == "hard":
            score -= 25
            warnings.append("高阶路线对初次游玩游客强度偏高。")

    if user_type == "normal":
        if difficulty == "easy":
            score += 10
            reasons.append("体力一般游客适合选择初阶路线。")
        elif difficulty == "hard":
            score -= 20
            warnings.append("高阶路线对体力一般游客不够稳妥。")

    if user_type == "strong":
        if difficulty == "hard":
            score += 10
            reasons.append("体力较好游客可考虑高阶路线。")

    # 2. 天气影响
    weather_text = weather.get("weather") if weather else ""

    if weather_text:
        if "雨" in weather_text:
            if difficulty == "hard":
                score -= 30
                warnings.append("当前有雨，高阶徒步路线风险较高。")
            elif difficulty == "medium":
                score -= 15
                warnings.append("当前有雨，中阶路线需注意道路湿滑。")
            else:
                score -= 5
                reasons.append("雨天选择初阶路线相对稳妥。")

        if "雪" in weather_text:
            score -= 35
            warnings.append("雪天山地游览风险较高，应关注景区公告和索道运行情况。")

        if "晴" in weather_text or "多云" in weather_text:
            score += 5
            reasons.append("当前天气较适合观景游览。")

    # 3. 交通影响
    traffic_desc = traffic.get("evaluation_description") if traffic else ""

    if traffic_desc:
        if "严重" in traffic_desc or "拥堵" in traffic_desc:
            score -= 15
            warnings.append(f"景区周边道路状态为{traffic_desc}，到达景区可能耗时增加。")
        elif "缓慢" in traffic_desc or "轻度" in traffic_desc:
            score -= 8
            warnings.append(f"景区周边道路状态为{traffic_desc}，建议预留出行时间。")
        elif "畅通" in traffic_desc:
            score += 5
            reasons.append("景区周边道路较畅通。")

    # 4. 客流影响
    crowded_nodes = []

    for node in nodes:
        crowd = crowd_dict.get(node)
        if not crowd:
            continue

        if crowd["level"] == "拥挤":
            score -= 8
            crowded_nodes.append(node)
        elif crowd["level"] == "适中":
            score -= 3

    if crowded_nodes:
        warnings.append(
            "路线包含模拟客流较高节点：" + "、".join(crowded_nodes)
        )
    else:
        reasons.append("路线未明显集中在高客流节点。")

    score = max(0, min(100, score))

    return {
        "route": route,
        "score": score,
        "reasons": reasons,
        "warnings": warnings,
        "crowded_nodes": crowded_nodes
    }


@router.post("/dynamic-route")
def dynamic_route_recommend(req: DynamicRecommendRequest):
    """
    基于天气、交通态势、模拟客流和用户类型进行动态路线推荐。
    """
    try:
        weather = get_weather_info()
        traffic = get_traffic_info(
            req.traffic_lng,
            req.traffic_lat,
            req.traffic_radius
        )
        routes = get_routes()
        crowd_dict = get_crowd_dict()

        results = []

        for route in routes:
            item = score_route(
                route,
                weather,
                traffic,
                crowd_dict,
                req.user_type
            )
            results.append(item)

        results.sort(key=lambda x: x["score"], reverse=True)

        return {
            "weather": weather,
            "traffic": traffic,
            "user_type": req.user_type,
            "time_slot": req.time_slot,
            "recommendations": results,
            "best": results[0] if results else None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))