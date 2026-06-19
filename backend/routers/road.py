from fastapi import APIRouter, HTTPException, Query
from psycopg2.extras import RealDictCursor
from database import get_connection

router = APIRouter(prefix="/api/roads", tags=["roads"])


@router.get("")
def get_roads(
    road_type: str = Query("", description="道路类型：main_road、scenic_road、trail")
):
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute(
            """
            SELECT
                id,
                display_name,
                raw_name,
                osm_id,
                code,
                fclass,
                ref,
                oneway,
                maxspeed,
                bridge,
                tunnel,
                road_type,
                walkable,
                source,
                verify_status,
                remark,
                length_m,
                display_level,
                ST_AsGeoJSON(geom)::json AS geometry
            FROM road_network_display
            WHERE geom IS NOT NULL
            AND (%s = '' OR road_type = %s)
            ORDER BY display_level ASC, length_m DESC;
            """,
            (road_type, road_type)
        )

        rows = cur.fetchall()
        cur.close()
        conn.close()

        features = []

        for row in rows:
            features.append({
                "type": "Feature",
                "properties": {
                    "id": row["id"],
                    "display_name": row["display_name"],
                    "raw_name": row["raw_name"],
                    "osm_id": row["osm_id"],
                    "code": row["code"],
                    "fclass": row["fclass"],
                    "ref": row["ref"],
                    "oneway": row["oneway"],
                    "maxspeed": row["maxspeed"],
                    "bridge": row["bridge"],
                    "tunnel": row["tunnel"],
                    "road_type": row["road_type"],
                    "walkable": row["walkable"],
                    "source": row["source"],
                    "verify_status": row["verify_status"],
                    "remark": row["remark"],
                    "length_m": row["length_m"],
                    "display_level": row["display_level"]
                },
                "geometry": row["geometry"]
            })

        return {
            "type": "FeatureCollection",
            "features": features
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))