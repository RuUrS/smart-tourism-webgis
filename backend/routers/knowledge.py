#知识库接口
from fastapi import APIRouter, HTTPException, Query
from psycopg2.extras import RealDictCursor
from database import get_connection

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.get("/search")
def search_knowledge_api(
    keyword: str = Query("", description="检索关键词")
):
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        if keyword:
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
                    OR keywords ILIKE %s
                ORDER BY id ASC
                LIMIT 10;
                """,
                (
                    like_keyword,
                    like_keyword,
                    like_keyword,
                    like_keyword,
                    like_keyword
                )
            )
        else:
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
                ORDER BY id ASC
                LIMIT 50;
                """
            )

        rows = cur.fetchall()

        cur.close()
        conn.close()

        return {
            "count": len(rows),
            "items": rows
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))