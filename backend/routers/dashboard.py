#echarts大屏接口
from fastapi import APIRouter, HTTPException
from psycopg2.extras import RealDictCursor

from database import get_connection

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
def get_dashboard_summary():
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # POI 总数
        cur.execute("SELECT COUNT(*) AS total FROM laojunshan_poi;")
        poi_total = cur.fetchone()["total"]

        # POI 类型统计
        cur.execute(
            """
            SELECT type, COUNT(*) AS count
            FROM laojunshan_poi
            GROUP BY type
            ORDER BY count DESC;
            """
        )
        poi_by_type = cur.fetchall()

        # 客流等级统计
        cur.execute(
            """
            SELECT crowd_level AS level, COUNT(*) AS count
            FROM crowd_status
            GROUP BY crowd_level
            ORDER BY count DESC;
            """
        )
        crowd_by_level = cur.fetchall()

        # 热门客流 TOP5
        cur.execute(
            """
            SELECT
                p.name,
                c.crowd_value,
                c.crowd_level
            FROM crowd_status c
            JOIN laojunshan_poi p
            ON c.poi_id = p.id
            ORDER BY c.crowd_value DESC
            LIMIT 5;
            """
        )
        top_crowd_pois = cur.fetchall()

        # 路线难度统计
        cur.execute(
            """
            SELECT difficulty, COUNT(*) AS count
            FROM route_template
            GROUP BY difficulty
            ORDER BY difficulty;
            """
        )
        route_by_difficulty = cur.fetchall()

        # 知识库数量
        cur.execute("SELECT COUNT(*) AS total FROM tourism_knowledge;")
        knowledge_total = cur.fetchone()["total"]
 
        # 路网总数与总长度
        cur.execute(
            """
            SELECT
                COUNT(*) AS road_total,
                ROUND(COALESCE(SUM(length_m), 0) / 1000.0, 2) AS road_length_km
            FROM road_network_display;
            """
        )
        road_base = cur.fetchone()

        # 道路类型数量统计
        cur.execute(
            """
            SELECT
                road_type,
                COUNT(*) AS count
            FROM road_network_display
            GROUP BY road_type
            ORDER BY count DESC;
            """
        )
        road_by_type = cur.fetchall()

        # 道路类型长度统计
        cur.execute(
            """
            SELECT
                road_type,
                ROUND(COALESCE(SUM(length_m), 0) / 1000.0, 2) AS length_km
            FROM road_network_display
            GROUP BY road_type
            ORDER BY length_km DESC;
            """
        )
        road_length_by_type = cur.fetchall()

        # 可步行道路统计
        cur.execute(
            """
            SELECT
                CASE WHEN walkable THEN '可步行' ELSE '不可步行' END AS walkable_status,
                COUNT(*) AS count
            FROM road_network_display
            GROUP BY walkable_status;
            """
        )
        road_walkable = cur.fetchall()

        # 路网核验状态统计
        cur.execute(
            """
            SELECT
                verify_status,
                COUNT(*) AS count
            FROM road_network_display
            GROUP BY verify_status
            ORDER BY count DESC;
            """
        )
        road_verify_status = cur.fetchall()

        # OSM 原始道路类型 TOP8
        cur.execute(
            """
            SELECT
                fclass,
                COUNT(*) AS count
            FROM road_network_display
            WHERE fclass IS NOT NULL
            GROUP BY fclass
            ORDER BY count DESC
            LIMIT 8;
            """
        )
        road_fclass_top = cur.fetchall()
        
        # Agent 调用总数
        cur.execute(
            """
            SELECT COUNT(*) AS total
            FROM agent_call_log;
            """
        )
        agent_total = cur.fetchone()["total"]

        # 各类 Agent 调用统计
        cur.execute(
            """
            SELECT
                agent_name,
                COUNT(*) AS count
            FROM agent_call_log
            GROUP BY agent_name
            ORDER BY count DESC;
            """
        )
        agent_by_type = cur.fetchall()

        # 工具调用统计
        cur.execute(
            """
            SELECT
                used_tools
            FROM agent_call_log
            WHERE used_tools IS NOT NULL
            AND used_tools <> '';
            """
        )
        tool_rows = cur.fetchall()

        tool_count_map = {}

        for row in tool_rows:
            tools_text = row["used_tools"]
            if not tools_text:
                continue

            for tool_name in tools_text.split(","):
                tool_name = tool_name.strip()
                if not tool_name:
                    continue
                tool_count_map[tool_name] = tool_count_map.get(tool_name, 0) + 1

        tool_usage_top = [
            {
                "tool_name": key,
                "count": value
            }
            for key, value in sorted(
                tool_count_map.items(),
                key=lambda item: item[1],
                reverse=True
            )[:5]
        ]

        cur.close()
        conn.close()

        return {
            "poi_total": poi_total,
            "poi_by_type": poi_by_type,
            "crowd_by_level": crowd_by_level,
            "top_crowd_pois": top_crowd_pois,
            "route_by_difficulty": route_by_difficulty,
            "knowledge_total": knowledge_total,
            
            "road_total": road_base["road_total"],
            "road_length_km": road_base["road_length_km"],
            "road_by_type": road_by_type,
            "road_length_by_type": road_length_by_type,
            "road_walkable": road_walkable,
            "road_verify_status": road_verify_status,
            "road_fclass_top": road_fclass_top,
            "agent_total": agent_total,
            "agent_by_type": agent_by_type,
            "tool_usage_top": tool_usage_top
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))