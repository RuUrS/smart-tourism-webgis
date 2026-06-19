import os
import requests
from psycopg2.extras import RealDictCursor
from database import get_connection

def search_knowledge(keyword: str, limit: int = 8):
    """
    查询老君山旅游知识库。
    用于 Agent 检索景点介绍、路线攻略、天气提示、安全提醒、服务设施和常见问答。
    """
    try:
        if not keyword:
            keyword = ""

        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        like_keyword = f"%{keyword}%"

        cur.execute(
            """
            SELECT
                id,
                title,
                category,
                related_poi,
                content,
                content_type,
                keywords,
                source,
                source_url,
                verify_status
            FROM tourism_knowledge
            WHERE
                title ILIKE %s
                OR category ILIKE %s
                OR related_poi ILIKE %s
                OR content ILIKE %s
                OR COALESCE(keywords, '') ILIKE %s
            ORDER BY
                CASE
                    WHEN title ILIKE %s THEN 1
                    WHEN related_poi ILIKE %s THEN 2
                    WHEN COALESCE(keywords, '') ILIKE %s THEN 3
                    WHEN category ILIKE %s THEN 4
                    ELSE 5
                END,
                id ASC
            LIMIT %s;
            """,
            (
                like_keyword,
                like_keyword,
                like_keyword,
                like_keyword,
                like_keyword,
                like_keyword,
                like_keyword,
                like_keyword,
                like_keyword,
                limit
            )
        )

        rows = cur.fetchall()
        cur.close()
        conn.close()

        return {
            "keyword": keyword,
            "count": len(rows),
            "items": list(rows)
        }

    except Exception as e:
        return {
            "keyword": keyword,
            "count": 0,
            "items": [],
            "error": str(e)
        }
    
def search_poi(keyword: str = "", poi_type: str = ""):
    """
    查询老君山 POI。
    poi_type 可选：
    attraction 景点
    transport 交通/索道
    service 服务设施
    """
    try:
        keyword = str(keyword or "").strip()
        poi_type = str(poi_type or "").strip()

        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        conditions = ["geom IS NOT NULL"]
        params = []

        if keyword:
            conditions.append(
                "(name ILIKE %s OR subtype ILIKE %s OR address ILIKE %s OR description ILIKE %s)"
            )
            kw = f"%{keyword}%"
            params.extend([kw, kw, kw, kw])

        if poi_type:
            conditions.append("type = %s")
            params.append(poi_type)

        where_sql = " AND ".join(conditions)

        cur.execute(
            f"""
            SELECT
                id,
                name,
                type,
                subtype,
                address,
                description,
                source,
                verify_status,
                ST_X(geom) AS lng,
                ST_Y(geom) AS lat
            FROM laojunshan_poi
            WHERE {where_sql}
            LIMIT 10;
            """,
            params
        )

        rows = cur.fetchall()
        cur.close()
        conn.close()

        return {
            "keyword": keyword,
            "poi_type": poi_type,
            "count": len(rows),
            "items": list(rows)
        }

    except Exception as e:
        return {
            "keyword": keyword,
            "poi_type": poi_type,
            "count": 0,
            "items": [],
            "error": str(e)
        }

def get_routes(difficulty: str = ""):
    """
    查询路线模板。
    difficulty 可选：easy / medium / hard
    兼容中文：初阶 / 中阶 / 高阶
    """
    try:
        difficulty_map = {
            "初阶": "easy",
            "简单": "easy",
            "easy": "easy",
            "中阶": "medium",
            "中等": "medium",
            "medium": "medium",
            "高阶": "hard",
            "困难": "hard",
            "hard": "hard"
        }

        difficulty = difficulty_map.get(str(difficulty).strip(), str(difficulty).strip())

        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        if difficulty:
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
                WHERE difficulty = %s
                ORDER BY id;
                """,
                (difficulty,)
            )
        else:
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

        return {
            "difficulty": difficulty,
            "count": len(rows),
            "items": list(rows)
        }

    except Exception as e:
        return {
            "difficulty": difficulty,
            "count": 0,
            "items": [],
            "error": str(e)
        }


def get_nearby_services(lng: float, lat: float, radius: int = 1000):
    """
    查询某坐标附近服务设施。
    """
    try:
        lng = float(lng)
        lat = float(lat)
        radius = int(radius or 1000)

        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute(
            """
            SELECT
                id,
                name,
                type,
                subtype,
                address,
                description,
                ROUND(
                    ST_Distance(
                        geom::geography,
                        ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
                    )::numeric,
                    2
                ) AS distance_m
            FROM laojunshan_poi
            WHERE type = 'service'
              AND ST_DWithin(
                  geom::geography,
                  ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                  %s
              )
            ORDER BY distance_m ASC
            LIMIT 10;
            """,
            (lng, lat, lng, lat, radius)
        )

        rows = cur.fetchall()
        cur.close()
        conn.close()

        return {
            "lng": lng,
            "lat": lat,
            "radius": radius,
            "count": len(rows),
            "items": list(rows)
        }

    except Exception as e:
        return {
            "lng": lng,
            "lat": lat,
            "radius": radius,
            "count": 0,
            "items": [],
            "error": str(e)
        }


def get_weather():
    """
    查询栾川县实时天气，供 Agent 调用。
    """
    amap_key = os.getenv("AMAP_KEY")

    if not amap_key:
        return {
            "error": "未配置 AMAP_KEY"
        }

    url = "https://restapi.amap.com/v3/weather/weatherInfo"

    params = {
        "key": amap_key,
        "city": "410324",
        "extensions": "base",
        "output": "json"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data.get("status") != "1" or not data.get("lives"):
            return {
                "error": data.get("info", "天气数据获取失败")
            }

        item = data["lives"][0]

        return {
            "city": item.get("city"),
            "adcode": item.get("adcode"),
            "weather": item.get("weather"),
            "temperature": item.get("temperature"),
            "winddirection": item.get("winddirection"),
            "windpower": item.get("windpower"),
            "humidity": item.get("humidity"),
            "reporttime": item.get("reporttime")
        }

    except Exception as e:
        return {
            "error": f"天气接口调用失败：{str(e)}"
        }

def get_crowd_status():
    """
    查询老君山模拟客流状态。
    注意：这是系统模拟数据，不是真实闸机客流。
    """
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute(
            """
            SELECT
                p.name AS poi_name,
                c.crowd_value,
                c.crowd_level,
                c.time_slot,
                c.update_time
            FROM crowd_status c
            JOIN laojunshan_poi p
            ON c.poi_id = p.id
            ORDER BY c.crowd_value DESC
            LIMIT 10;
            """
        )

        rows = cur.fetchall()
        cur.close()
        conn.close()

        return {
            "data_type": "simulated_crowd",
            "description": "该客流数据为系统模拟数据，不是真实闸机统计。",
            "count": len(rows),
            "items": list(rows)
        }

    except Exception as e:
        return {
            "data_type": "simulated_crowd",
            "count": 0,
            "items": [],
            "error": str(e)
        }


def get_traffic_status(lng: float = 111.65632, lat: float = 33.774569, radius: int = 3000):
    amap_key = os.getenv("AMAP_KEY")

    if not amap_key:
        return {
            "error": "未配置 AMAP_KEY"
        }

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
                "error": data.get("info", "交通态势接口异常")
            }

        trafficinfo = data.get("trafficinfo", {})
        evaluation = trafficinfo.get("evaluation", {})

        return {
            "description": trafficinfo.get("description"),
            "evaluation_description": evaluation.get("description"),
            "expedite": evaluation.get("expedite"),
            "congested": evaluation.get("congested"),
            "blocked": evaluation.get("blocked")
        }

    except Exception as e:
        return {
            "error": str(e)
        }


def get_dynamic_recommendation(user_type: str = "first_time"):
    """
    给 Agent 使用的简化动态推荐工具。
    user_type 可选：first_time / normal / strong
    """
    try:
        user_type = str(user_type or "first_time").strip()

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
                description
            FROM route_template
            ORDER BY
                CASE
                    WHEN difficulty = 'easy' THEN 1
                    WHEN difficulty = 'medium' THEN 2
                    WHEN difficulty = 'hard' THEN 3
                    ELSE 4
                END;
            """
        )

        routes = cur.fetchall()
        cur.close()
        conn.close()

        return {
            "user_type": user_type,
            "count": len(routes),
            "items": list(routes),
            "note": "该动态路线推荐基于路线模板、游客类型和系统规则生成。"
        }

    except Exception as e:
        return {
            "user_type": user_type,
            "count": 0,
            "items": [],
            "error": str(e)
        }