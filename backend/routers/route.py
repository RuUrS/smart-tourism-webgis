#路线接口
from fastapi import APIRouter, HTTPException
from psycopg2.extras import RealDictCursor
from database import get_connection

router = APIRouter(prefix="/api/routes", tags=["routes"])


@router.get("")
def get_routes():
    """
    获取所有路线模板
    """
    sql = """
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

    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql)
        routes = cur.fetchall()
        cur.close()
        conn.close()

        return {
            "routes": routes
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{route_id}/geojson")
def get_route_geojson(route_id: int):
    """
    根据路线模板，把路线节点转为 GeoJSON。
    返回路线节点点图层和路线连线。
    """
    try:
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
            WHERE id = %s;
            """,
            (route_id,)
        )

        route = cur.fetchone()

        if not route:
            cur.close()
            conn.close()
            raise HTTPException(status_code=404, detail="未找到该路线")

        node_names = [
            item.strip()
            for item in route["node_sequence"].split(";")
            if item.strip()
        ]

        pois = []
        missing_nodes = []

        for index, node_name in enumerate(node_names):
            cur.execute(
                """
                SELECT
                    id,
                    name,
                    type,
                    subtype,
                    address,
                    description,
                    ST_X(geom) AS lng,
                    ST_Y(geom) AS lat
                FROM laojunshan_poi
                WHERE name = %s
                  AND geom IS NOT NULL
                LIMIT 1;
                """,
                (node_name,)
            )

            poi = cur.fetchone()

            if poi:
                pois.append({
                    "order": index + 1,
                    "id": poi["id"],
                    "name": poi["name"],
                    "type": poi["type"],
                    "subtype": poi["subtype"],
                    "address": poi["address"],
                    "description": poi["description"],
                    "lng": float(poi["lng"]),
                    "lat": float(poi["lat"])
                })
            else:
                missing_nodes.append(node_name)

        cur.close()
        conn.close()

        features = []

        # 路线连线
        if len(pois) >= 2:
            line_coordinates = [
                [poi["lng"], poi["lat"]]
                for poi in pois
            ]

            features.append({
                "type": "Feature",
                "properties": {
                    "feature_type": "route_line",
                    "route_id": route["id"],
                    "route_name": route["route_name"],
                    "difficulty": route["difficulty"]
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": line_coordinates
                }
            })

        # 路线节点
        for poi in pois:
            features.append({
                "type": "Feature",
                "properties": {
                    "feature_type": "route_node",
                    "order": poi["order"],
                    "id": poi["id"],
                    "name": poi["name"],
                    "type": poi["type"],
                    "subtype": poi["subtype"],
                    "address": poi["address"],
                    "description": poi["description"]
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [poi["lng"], poi["lat"]]
                }
            })

        return {
            "route": route,
            "missing_nodes": missing_nodes,
            "geojson": {
                "type": "FeatureCollection",
                "features": features
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))