#知识库问答接口
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from psycopg2.extras import RealDictCursor
from database import get_connection

router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    question: str


def build_keywords(question: str):
    """
    简单关键词抽取。
    不接大模型时，先用规则提高检索命中率。
    """
    q = question.strip()

    candidate_keywords = [
        "老君山",
        "初阶路线",
        "中阶路线",
        "高阶路线",
        "路线",
        "怎么玩",
        "第一次",
        "体力",
        "索道",
        "中灵索道",
        "云景索道",
        "峰林索道",
        "票务中心",
        "中天门",
        "云景天路",
        "十里画屏",
        "马鬃岭",
        "金顶道观群",
        "南天门",
        "寨沟",
        "追梦谷",
        "景点",
        "厕所",
        "停车",
        "餐饮",
        "住宿",
        "雨天",
        "天气",
        "注意事项"
    ]

    keywords = []

    for kw in candidate_keywords:
        if kw in q:
            keywords.append(kw)

    # 常见意图补充
    if "第一次" in q or "新手" in q or "体力一般" in q or "轻松" in q:
        keywords.append("初阶路线")
        keywords.append("体力一般游客建议")

    if "怎么游" in q or "怎么玩" in q or "推荐" in q or "行程" in q:
        keywords.append("路线")

    if "雨" in q or "下雨" in q:
        keywords.append("雨天游览提醒")

    if not keywords:
        keywords.append(q)

    # 去重
    return list(dict.fromkeys(keywords))


@router.post("")
def chat(req: ChatRequest):
    """
    知识库问答接口。
    当前版本：基于数据库检索和规则组织回答。
    后续可升级为大模型 Agent。
    """
    question = req.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="问题不能为空")

    keywords = build_keywords(question)

    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        knowledge_results = []
        route_results = []
        poi_results = []

        # 1. 检索知识库
        for kw in keywords:
            cur.execute(
                """
                SELECT
                    id,
                    title,
                    category,
                    related_poi,
                    content,
                    source,
                    source_url
                FROM tourism_knowledge
                WHERE
                    title ILIKE %s
                    OR category ILIKE %s
                    OR related_poi ILIKE %s
                    OR content ILIKE %s
                LIMIT 5;
                """,
                (f"%{kw}%", f"%{kw}%", f"%{kw}%", f"%{kw}%")
            )
            knowledge_results.extend(cur.fetchall())

        # 2. 检索路线模板
        for kw in keywords:
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
                WHERE
                    route_name ILIKE %s
                    OR difficulty ILIKE %s
                    OR node_sequence ILIKE %s
                    OR suitable_user ILIKE %s
                    OR description ILIKE %s
                LIMIT 5;
                """,
                (f"%{kw}%", f"%{kw}%", f"%{kw}%", f"%{kw}%", f"%{kw}%")
            )
            route_results.extend(cur.fetchall())

        # 3. 检索 POI
        for kw in keywords:
            cur.execute(
                """
                SELECT
                    id,
                    name,
                    type,
                    subtype,
                    address,
                    description,
                    source,
                    verify_status
                FROM laojunshan_poi
                WHERE
                    name ILIKE %s
                    OR type ILIKE %s
                    OR subtype ILIKE %s
                    OR address ILIKE %s
                    OR description ILIKE %s
                LIMIT 5;
                """,
                (f"%{kw}%", f"%{kw}%", f"%{kw}%", f"%{kw}%", f"%{kw}%")
            )
            poi_results.extend(cur.fetchall())

        cur.close()
        conn.close()

        # 去重
        knowledge_unique = {item["id"]: item for item in knowledge_results}.values()
        route_unique = {item["id"]: item for item in route_results}.values()
        poi_unique = {item["id"]: item for item in poi_results}.values()

        answer_parts = []

        # 4. 优先组织路线相关回答
        if route_unique:
            answer_parts.append("根据系统中的路线模板，可以参考以下游览方案：")
            for r in list(route_unique)[:3]:
                answer_parts.append(
                    f"【{r['route_name']}】\n"
                    f"难度：{r['difficulty']}\n"
                    f"预计时间：{r['estimated_time']}\n"
                    f"适合人群：{r['suitable_user']}\n"
                    f"路线节点：{r['node_sequence']}\n"
                    f"说明：{r['description']}"
                )

        # 5. 组织知识库回答
        if knowledge_unique:
            if not answer_parts:
                answer_parts.append("根据老君山知识库，检索到以下相关内容：")

            for k in list(knowledge_unique)[:5]:
                answer_parts.append(
                    f"【{k['title']}】\n{k['content']}"
                )

        # 6. 组织 POI 回答
        if poi_unique:
            answer_parts.append("相关景点或服务点包括：")
            for p in list(poi_unique)[:5]:
                answer_parts.append(
                    f"【{p['name']}】\n"
                    f"类型：{p['type']} / {p['subtype']}\n"
                    f"地址：{p['address'] or '暂无地址信息'}\n"
                    f"简介：{p['description'] or '暂无简介'}"
                )

        if not answer_parts:
            return {
                "answer": (
                    "暂未在知识库中检索到相关内容。你可以尝试询问：\n"
                    "1. 第一次去老君山怎么玩？\n"
                    "2. 初阶路线适合哪些人？\n"
                    "3. 金顶道观群有什么特点？\n"
                    "4. 老君山有哪些索道？"
                ),
                "keywords": keywords,
                "references": []
            }

        return {
            "answer": "\n\n".join(answer_parts),
            "keywords": keywords,
            "references": {
                "knowledge": list(knowledge_unique)[:5],
                "routes": list(route_unique)[:3],
                "pois": list(poi_unique)[:5]
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))