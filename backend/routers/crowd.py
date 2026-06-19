#模拟客流
from datetime import datetime
import random

from fastapi import APIRouter, HTTPException, Query
from psycopg2.extras import RealDictCursor

from database import get_connection

router = APIRouter(prefix="/api/crowd", tags=["crowd"])


def get_crowd_level(value: int):
    """
    根据客流指数返回等级。
    """
    if value >= 75:
        return "拥挤"
    if value >= 45:
        return "适中"
    return "舒适"


def build_crowd_value(name: str, poi_type: str, subtype: str, time_slot: str):
    """
    生成模拟客流指数。
    这里不是实际客流预测，而是用于系统演示的规则模拟。
    """
    base = 35

    # 核心景点基础客流更高
    if name in ["金顶道观群", "十里画屏", "中天门"]:
        base = 75
    elif name in ["马鬃岭", "云景天路", "峰林索道"]:
        base = 60
    elif name in ["票务中心", "老君山游客中心", "老君山停车场"]:
        base = 55
    elif poi_type == "transport":
        base = 58
    elif poi_type == "service":
        base = 45
    elif poi_type == "attraction":
        base = 50

    # 时间段影响
    if time_slot == "上午":
        base += 10
    elif time_slot == "中午":
        base += 0
    elif time_slot == "下午":
        base += 6
    elif time_slot == "傍晚":
        base -= 5

    # 增加一点随机波动，让每次模拟有变化
    value = base + random.randint(-10, 10)

    # 限制在 0-100
    value = max(0, min(100, value))

    return value


@router.get("/status")
def get_crowd_status():
    """
    获取当前模拟客流状态。
    """
    sql = """
        SELECT
            c.id,
            c.poi_id,
            p.name AS poi_name,
            p.type,
            p.subtype,
            p.address,
            p.description,
            c.crowd_value,
            c.crowd_level,
            c.time_slot,
            c.update_time,
            c.source,
            c.remark,
            ST_X(p.geom) AS lng,
            ST_Y(p.geom) AS lat
        FROM crowd_status c
        JOIN laojunshan_poi p
        ON c.poi_id = p.id
        WHERE p.geom IS NOT NULL
        ORDER BY c.crowd_value DESC;
    """

    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        return {
            "count": len(rows),
            "items": rows
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulate")
def simulate_crowd(
    time_slot: str = Query("上午", description="时间段：上午、中午、下午、傍晚")
):
    """
    根据 POI 类型和时间段重新生成模拟客流。
    """
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # 取出老君山 POI
        cur.execute(
            """
            SELECT
                id,
                name,
                type,
                subtype
            FROM laojunshan_poi
            WHERE geom IS NOT NULL
            ORDER BY id;
            """
        )

        pois = cur.fetchall()

        if not pois:
            raise HTTPException(status_code=404, detail="未找到 POI 数据")

        for poi in pois:
            value = build_crowd_value(
                poi["name"],
                poi["type"],
                poi["subtype"],
                time_slot
            )

            level = get_crowd_level(value)

            cur.execute(
                """
                INSERT INTO crowd_status
                (poi_id, crowd_value, crowd_level, time_slot, update_time, source, remark)
                VALUES
                (%s, %s, %s, %s, NOW(), %s, %s)
                ON CONFLICT (poi_id)
                DO UPDATE SET
                    crowd_value = EXCLUDED.crowd_value,
                    crowd_level = EXCLUDED.crowd_level,
                    time_slot = EXCLUDED.time_slot,
                    update_time = NOW(),
                    source = EXCLUDED.source,
                    remark = EXCLUDED.remark;
                """,
                (
                    poi["id"],
                    value,
                    level,
                    time_slot,
                    "系统模拟",
                    "根据 POI 类型、核心节点重要性和时间段生成的模拟客流数据"
                )
            )

        conn.commit()
        cur.close()
        conn.close()

        return {
            "message": "模拟客流生成成功",
            "time_slot": time_slot,
            "count": len(pois)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/heatmap")
def get_crowd_heatmap():
    """
    获取客流热力图数据。
    前端可根据 lng、lat、crowd_value 绘制热力扩散圆。
    """
    sql = """
        SELECT
            c.poi_id,
            p.name AS poi_name,
            c.crowd_value,
            c.crowd_level,
            ST_X(p.geom) AS lng,
            ST_Y(p.geom) AS lat
        FROM crowd_status c
        JOIN laojunshan_poi p
        ON c.poi_id = p.id
        WHERE p.geom IS NOT NULL
        ORDER BY c.crowd_value DESC;
    """

    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        return {
            "count": len(rows),
            "items": rows
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))