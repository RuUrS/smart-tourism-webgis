from fastapi import APIRouter, HTTPException, Query
from database import get_connection

router = APIRouter(prefix="/api/pois", tags=["pois"])


@router.get("")
def get_pois(
    type: str | None = Query(default=None),
    keyword: str | None = Query(default=None)
):
    """
    获取老君山 POI 点位。
    支持按 type 分类筛选，也支持 keyword 名称搜索。
    """
    conditions = ["p.geom IS NOT NULL"]
    params = []

    if type:
        conditions.append("p.type = %s")
        params.append(type)

    if keyword:
        conditions.append("""
            (
                p.name ILIKE %s
                OR p.subtype ILIKE %s
                OR p.description ILIKE %s
                OR p.address ILIKE %s
            )
        """)
        kw = f"%{keyword}%"
        params.extend([kw, kw, kw, kw])

    where_sql = " AND ".join(conditions)

    sql = f"""
        SELECT json_build_object(
            'type', 'FeatureCollection',
            'features', COALESCE(json_agg(
                json_build_object(
                    'type', 'Feature',
                    'properties', json_build_object(
                        'id', p.id,
                        'name', p.name,
                        'type', p.type,
                        'subtype', p.subtype,
                        'address', p.address,
                        'description', p.description,
                        'source', p.source,
                        'verify_status', p.verify_status
                    ),
                    'geometry', ST_AsGeoJSON(p.geom)::json
                )
            ), '[]'::json)
        ) AS geojson
        FROM laojunshan_poi p
        WHERE {where_sql};
    """

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, params)
        result = cur.fetchone()[0]
        cur.close()
        conn.close()
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/nearby")
def get_nearby_pois(
    lng: float,
    lat: float,
    radius: int = 1000,
    type: str | None = None,
    exclude_id: int | None = None
):
    """
    查询指定经纬度附近一定半径内的 POI。
    radius 单位：米
    type 可选，例如 service / attraction / transport
    exclude_id 用于排除当前选中的 POI
    """
    conditions = [
        "p.geom IS NOT NULL",
        """
        ST_DWithin(
            p.geom::geography,
            ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
            %s
        )
        """
    ]

    params = [lng, lat, radius]

    if type:
        conditions.append("p.type = %s")
        params.append(type)

    if exclude_id:
        conditions.append("p.id <> %s")
        params.append(exclude_id)

    where_sql = " AND ".join(conditions)

    sql = f"""
        WITH nearby AS (
            SELECT
                p.id,
                p.name,
                p.type,
                p.subtype,
                p.address,
                p.description,
                p.source,
                p.verify_status,
                p.geom,
                ROUND(
                    ST_Distance(
                        p.geom::geography,
                        ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography
                    )::numeric,
                    2
                ) AS distance_m
            FROM laojunshan_poi p
            WHERE {where_sql}
            ORDER BY distance_m ASC
        )
        SELECT json_build_object(
            'type', 'FeatureCollection',
            'features', COALESCE(json_agg(
                json_build_object(
                    'type', 'Feature',
                    'properties', json_build_object(
                        'id', id,
                        'name', name,
                        'type', type,
                        'subtype', subtype,
                        'address', address,
                        'description', description,
                        'source', source,
                        'verify_status', verify_status,
                        'distance_m', distance_m
                    ),
                    'geometry', ST_AsGeoJSON(geom)::json
                )
            ), '[]'::json)
        ) AS geojson
        FROM nearby;
    """

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql, [lng, lat] + params)
        result = cur.fetchone()[0]
        cur.close()
        conn.close()
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))