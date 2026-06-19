from fastapi import APIRouter, HTTPException
from database import get_connection

router = APIRouter(prefix="/api/boundary", tags=["boundary"])


@router.get("/luanchuan")
def get_luanchuan_boundary():
    """
    从 PostGIS 中读取栾川县边界，并返回 GeoJSON
    """
    sql = """
        SELECT json_build_object(
            'type', 'FeatureCollection',
            'features', json_agg(
                json_build_object(
                    'type', 'Feature',
                    'properties', json_build_object(
                        'id', id,
                        'name', name,
                        'adcode', adcode
                    ),
                    'geometry', ST_AsGeoJSON(geom)::json
                )
            )
        ) AS geojson
        FROM luanchuan_boundary;
    """

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(sql)
        result = cur.fetchone()[0]
        cur.close()
        conn.close()

        if not result:
            raise HTTPException(status_code=404, detail="未找到栾川县边界数据")

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))