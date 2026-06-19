import os
import json

from dotenv import load_dotenv
load_dotenv()

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from openai import OpenAI
from database import get_connection

from services.agent_tools import (
    search_knowledge,
    search_poi,
    get_routes,
    get_nearby_services,
    get_weather,
    get_crowd_status,
    get_traffic_status,
    get_dynamic_recommendation
)

router = APIRouter(prefix="/api/agent", tags=["agent"])
ZHIPUAI_DEFAULT_MODEL = "glm-4.5-flash"
ZHIPUAI_DEFAULT_BASE_URL = "https://open.bigmodel.cn/api/paas/v4/"


def get_zhipu_model():
    return os.getenv("ZHIPUAI_MODEL", ZHIPUAI_DEFAULT_MODEL)

class AgentRequest(BaseModel):
    question: str
    agent_type: str = "auto"

AGENT_CONFIGS = {#Agent 配置
    "scenic": {
        "name": "景点讲解 Agent",
        "system": (
            "你是老君山景点讲解 Agent。"
            "你主要负责景点介绍、文化解释、游览价值说明。"
            "回答要像景区讲解员一样自然，但必须基于工具返回的知识库和 POI 数据。"
        ),
        "allowed_tools": ["search_knowledge", "search_poi", "get_weather"]
    },
    "route": {
        "name": "路线推荐 Agent",
        "system": (
            "你是老君山路线推荐 Agent。"
            "你需要结合路线模板、天气、模拟客流给游客推荐合适路线。"
            "如果路线只是节点连接示意，必须说明不是精确导航路径。"
        ),
        "allowed_tools": ["search_knowledge","get_routes", "get_weather", "get_crowd_status"]
    },
    "traffic": {
        "name": "交通出行 Agent",
        "system": (
            "你是老君山交通出行 Agent。"
            "你负责解释路径规划、景区周边道路交通态势和出行注意事项。"
        ),
        "allowed_tools": ["search_knowledge","search_poi", "get_traffic_status", "get_weather"]
    },
    "crowd": {
        "name": "客流分析 Agent",
        "system": (
            "你是老君山客流分析 Agent。"
            "你负责解释模拟客流、拥挤节点和错峰游览建议。"
            "必须说明客流数据是系统模拟数据，不是真实闸机统计。"
        ),
        "allowed_tools": ["search_knowledge","get_crowd_status", "get_routes"]
    },
    "comprehensive": {
        "name": "综合旅游 Agent",
        "system": (
            "你是老君山综合旅游 Agent。"
            "你需要综合 POI、路线、天气、模拟客流和交通态势，给出游客能执行的建议。"
            "不要编造数据库没有的信息。"
        ),
        "allowed_tools": [
            "search_knowledge",
            "search_poi",
            "get_routes",
            "get_weather",
            "get_crowd_status",
            "get_traffic_status",
            "get_dynamic_recommendation"
        ]
    }
}

def get_client():
    api_key = os.getenv("ZHIPUAI_API_KEY")

    if not api_key:
        raise RuntimeError("未配置 ZHIPUAI_API_KEY，请检查 backend/.env 是否正确加载")

    return OpenAI(
        api_key=api_key,
        base_url=os.getenv("ZHIPUAI_BASE_URL", ZHIPUAI_DEFAULT_BASE_URL),
        timeout=60.0,
        max_retries=1
    )


tools = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "查询老君山旅游知识库。适合回答景区概况、景点介绍、游览建议、注意事项、雨天提醒等问题。",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "检索关键词，例如：金顶道观群、初阶路线、十里画屏、雨天游览、索道"
                    }
                },
                "required": ["keyword"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_poi",
            "description": "查询老君山 POI，包括景点、索道、停车场、厕所、游客中心、餐饮住宿等。",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "POI 名称或关键词，例如：金顶、索道、厕所、停车场"
                    },
                    "poi_type": {
                        "type": "string",
                        "description": "POI 类型，可选 attraction、transport、service。没有明确类型时留空。"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_routes",
            "description": "查询老君山推荐游览路线。适合回答第一次游玩、体力一般、中等强度、高强度徒步等路线推荐问题。",
            "parameters": {
                "type": "object",
                "properties": {
                    "difficulty": {
                        "type": "string",
                        "description": "路线难度，可选 easy、medium、hard。体力一般或第一次游玩用 easy。"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_nearby_services",
            "description": "根据经纬度查询附近服务设施，例如厕所、停车场、餐饮、游客中心等。",
            "parameters": {
                "type": "object",
                "properties": {
                    "lng": {
                        "type": "number",
                        "description": "经度"
                    },
                    "lat": {
                        "type": "number",
                        "description": "纬度"
                    },
                    "radius": {
                        "type": "integer",
                        "description": "查询半径，单位米，默认 1000"
                    }
                },
                "required": ["lng", "lat"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询栾川县实时天气，用于判断是否适合高阶路线、山顶观景和徒步。",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_crowd_status",
            "description": "查询老君山模拟客流状态，包括拥挤、适中、舒适等等级。",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_traffic_status",
            "description": "查询老君山景区周边道路交通态势。",
            "parameters": {
                "type": "object",
                "properties": {
                    "lng": {
                        "type": "number",
                        "description": "中心点经度，默认票务中心"
                    },
                    "lat": {
                        "type": "number",
                        "description": "中心点纬度，默认票务中心"
                    },
                    "radius": {
                        "type": "integer",
                        "description": "查询半径，单位米，默认3000"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_dynamic_recommendation",
            "description": "查询动态路线推荐候选结果。",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_type": {
                        "type": "string",
                        "description": "游客类型，可选 first_time、normal、strong"
                    }
                },
                "required": []
            }
        }
    }
]


tool_map = {
    "search_knowledge": search_knowledge,
    "search_poi": search_poi,
    "get_routes": get_routes,
    "get_nearby_services": get_nearby_services,
    "get_weather": get_weather,
    "get_crowd_status": get_crowd_status,
    "get_traffic_status": get_traffic_status,
    "get_dynamic_recommendation": get_dynamic_recommendation
}


def safe_json_dumps(data):
    return json.dumps(data, ensure_ascii=False, default=str)

@router.post("/plan-agent-type")
def plan_agent_type_api(
    question: str = Query(..., description="用户问题")
):
    """
    Planner 测试接口。
    只用于测试问题会被分配给哪个 Agent，不负责生成回答。
    """
    agent_type = plan_agent_type(question)

    return {
        "question": question,
        "agent_type": agent_type
    }

def build_map_action(question: str, agent_type: str):
    """
    给前端返回地图动作建议。
    前端可以根据 map_action 自动打开图层或面板。
    """
    if "热力图" in question or "客流热力" in question:
        return {
            "type": "show_crowd_heatmap"
        }

    if "客流" in question or "拥挤" in question or "人多" in question:
        return {
            "type": "show_crowd_layer"
        }

    if "路线" in question or "推荐" in question or "怎么走" in question:
        return {
            "type": "open_dynamic_route_panel"
        }

    if "交通" in question or "路况" in question or "拥堵" in question:
        return {
            "type": "open_traffic_panel"
        }

    if "天气" in question:
        return {
            "type": "show_weather_card"
        }

    return {
        "type": "none"
    }

def plan_agent_type(question: str):
    """
    简单规则版 Planner。
    用关键词判断应该交给哪个 Agent。
    后续可以替换为大模型 Planner。
    """
    q = question.lower()

    scenic_words = ["介绍", "特色", "景点", "文化", "历史", "金顶", "十里画屏", "马鬃岭"]
    route_words = ["路线", "怎么走", "游玩", "推荐", "体力", "初阶", "中阶", "高阶"]
    traffic_words = ["交通", "堵", "拥堵", "路况", "开车", "自驾", "到达"]
    crowd_words = ["人多", "拥挤", "客流", "热力", "错峰", "排队"]
    weather_words = ["天气", "下雨", "小雨", "温度", "风", "冷", "热"]

    if any(word in question for word in crowd_words):
        return "crowd"

    if any(word in question for word in traffic_words):
        return "traffic"

    if any(word in question for word in route_words):
        return "route"

    if any(word in question for word in scenic_words):
        return "scenic"

    if any(word in question for word in weather_words):
        return "comprehensive"

    return "comprehensive"

@router.post("/travel")
def travel_agent(req: AgentRequest):
    question = req.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="问题不能为空")
    # 1. 根据 agent_type 选择 Agent 配置
    requested_agent_type = req.agent_type or "auto"
    if requested_agent_type == "auto":
        agent_type = plan_agent_type(question)
    else:
        agent_type = requested_agent_type
    agent_config = AGENT_CONFIGS.get(agent_type, AGENT_CONFIGS["comprehensive"])

    allowed_tool_names = agent_config["allowed_tools"]

    # 2. 根据当前 Agent 过滤工具
    selected_tools = [
        tool for tool in tools
        if tool["function"]["name"] in allowed_tool_names
    ]

    client = get_client()
    model = get_zhipu_model()
    # 3. 根据 Agent 类型切换 system prompt
    messages = [
        {
            "role": "system",
            "content": agent_config["system"]
        },
        {
            "role": "user",
            "content": question
        }
    ]

    try:
        # 允许最多 4 轮工具调用，避免无限循环
        used_tools = []

        for _ in range(4):
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=selected_tools,
                tool_choice="auto"
            )

            message = completion.choices[0].message
            tool_calls = getattr(message, "tool_calls", None)

            # 如果模型不再请求工具，直接返回最终回答
            if not tool_calls:
                map_action = build_map_action(question, agent_type)

                save_agent_call_log(
                    question=question,
                    agent_type=agent_type,
                    agent_name=agent_config["name"],
                    tool_used=len(used_tools) > 0,
                    used_tools=used_tools,
                    map_action=map_action
                )
                return {
                    "answer": message.content,
                    "mode": "zhipu_glm_4_5_air_multi_agent",
                    "agent_type": agent_type,
                    "agent_name": agent_config["name"],
                    "planned_agent_type": agent_type,
                    "map_action": map_action,
                    "tool_used": len(used_tools) > 0,
                    "used_tools": used_tools
                }

            messages.append({
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": tool_call.type,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    }
                    for tool_call in tool_calls
                ]
            })
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                raw_args = tool_call.function.arguments or "{}"

                try:
                    args = json.loads(raw_args)
                except json.JSONDecodeError:
                    args = {}
                
                if tool_name not in allowed_tool_names:
                    result = {
                        "error": f"当前 Agent 不允许调用工具：{tool_name}"
                    }
                elif tool_name not in tool_map:
                    result = {
                        "error": f"未知工具：{tool_name}"
                    }
                else:
                    result = tool_map[tool_name](**args)

                used_tools.append({
                    "name": tool_name,
                    "args": args
                })

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": safe_json_dumps(result)
                })

        # 如果 4 轮后仍有工具调用，强制让模型整合已有工具结果
        final_completion = client.chat.completions.create(
            model=model,
            messages=messages
        )

        final_answer = final_completion.choices[0].message.content
        
        map_action = build_map_action(question, agent_type)

        save_agent_call_log(
            question=question,
            agent_type=agent_type,
            agent_name=agent_config["name"],
            tool_used=len(used_tools) > 0,
            used_tools=used_tools,
            map_action=map_action
        )
        return {
            "answer": final_answer,
            "mode": "zhipu_glm_4_5_air_multi_agent",
            "agent_type": agent_type,
            "agent_name": agent_config["name"],
            "planned_agent_type": agent_type,
            "map_action": map_action,
            "tool_used": len(used_tools) > 0,
            "used_tools": used_tools
        }

    except Exception as e:
        error_text = str(e)

        map_action = build_map_action(question, agent_type) if "agent_type" in locals() else {"type": "none"}

        fallback_answer = (
            "当前智谱 AI 大模型连接失败，系统已切换为规则兜底模式。\n\n"
            "根据老君山游览经验，如果是第一次游玩或体力一般，建议优先选择初阶或中阶路线，"
            "以票务中心、索道、中天门、十里画屏、金顶道观群等核心节点为主。"
            "如果遇到雨天、大风、低温或道路湿滑情况，不建议选择高强度高阶徒步路线，"
            "应优先选择索道和相对安全的核心景观点游览。\n\n"
            f"本次大模型连接错误信息：{error_text}"
        )

        try:
            save_agent_call_log(
                question=question,
                agent_type=agent_type if "agent_type" in locals() else "comprehensive",
                agent_name=agent_config["name"] if "agent_config" in locals() else "综合旅游 Agent",
                tool_used=len(used_tools) > 0 if "used_tools" in locals() else False,
                used_tools=used_tools if "used_tools" in locals() else [],
                map_action=map_action
            )
        except Exception as log_error:
            print("兜底模式日志保存失败：", log_error)

        return {
            "answer": fallback_answer,
            "mode": "agent_fallback",
            "agent_type": agent_type if "agent_type" in locals() else "comprehensive",
            "agent_name": agent_config["name"] if "agent_config" in locals() else "综合旅游 Agent",
            "planned_agent_type": agent_type if "agent_type" in locals() else "comprehensive",
            "map_action": map_action,
            "tool_used": len(used_tools) > 0 if "used_tools" in locals() else False,
            "used_tools": used_tools if "used_tools" in locals() else [],
            "error": error_text
        }
    
def save_agent_call_log(#保存日志函数
    question: str,
    agent_type: str,
    agent_name: str,
    tool_used: bool,
    used_tools: list,
    map_action: dict
):
    try:
        conn = get_connection()
        cur = conn.cursor()

        tool_names = ",".join([
            item.get("name", "")
            for item in used_tools
        ])

        map_action_type = "none"
        if map_action and isinstance(map_action, dict):
            map_action_type = map_action.get("type", "none")

        cur.execute(
            """
            INSERT INTO agent_call_log
            (
                question,
                agent_type,
                agent_name,
                tool_used,
                used_tools,
                map_action,
                create_time
            )
            VALUES
            (%s, %s, %s, %s, %s, %s, NOW());
            """,
            (
                question,
                agent_type,
                agent_name,
                tool_used,
                tool_names,
                map_action_type
            )
        )

        conn.commit()
        cur.close()
        conn.close()

    except Exception as e:
        print("Agent 调用日志保存失败：", e)
@router.get("/debug/env")
def debug_agent_env():
    api_key = os.getenv("ZHIPUAI_API_KEY")
    model = get_zhipu_model()

    return {
        "has_api_key": bool(api_key),
        "api_key_prefix": api_key[:6] + "..." if api_key else None,
        "model": model,
        "base_url": "https://open.bigmodel.cn/api/paas/v4/"
    }
@router.get("/debug/zhipu-ping")
def debug_zhipu_ping():
    """
    测试后端是否能真正连通智谱大模型接口。
    """
    try:
        client = get_client()
        model = get_zhipu_model()

        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": "请只回复 ok"
                }
            ],
            temperature=0.1
        )

        return {
            "success": True,
            "model": model,
            "answer": completion.choices[0].message.content
        }

    except Exception as e:
        return {
            "success": False,
            "error_type": e.__class__.__name__,
            "error": str(e),
            "repr": repr(e),
            "cause": repr(e.__cause__) if getattr(e, "__cause__", None) else None
        }
@router.get("/debug/zhipu-tools")
def debug_zhipu_tools():
    """
    测试智谱模型是否能正常接收 tools 参数。
    """
    try:
        client = get_client()
        model = get_zhipu_model()

        test_tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge",
                    "description": "查询老君山旅游知识库。",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "keyword": {
                                "type": "string",
                                "description": "检索关键词"
                            }
                        },
                        "required": ["keyword"]
                    }
                }
            }
        ]

        completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": "雨天老君山适合走高阶路线吗？"
                }
            ],
            tools=test_tools,
            tool_choice="auto"
        )

        message = completion.choices[0].message

        return {
            "success": True,
            "model": model,
            "content": message.content,
            "tool_calls": [
                tool_call.model_dump()
                for tool_call in getattr(message, "tool_calls", []) or []
            ]
        }

    except Exception as e:
        return {
            "success": False,
            "error_type": e.__class__.__name__,
            "error": str(e),
            "repr": repr(e),
            "cause": repr(e.__cause__) if getattr(e, "__cause__", None) else None
        }
@router.get("/debug/local-tools")
def debug_local_tools():
    """
    测试 Agent 本地工具函数是否正常。
    """
    results = {}

    try:
        results["search_knowledge"] = search_knowledge(keyword="雨天", limit=3)
    except Exception as e:
        results["search_knowledge"] = {
            "error": str(e)
        }

    try:
        results["get_routes"] = get_routes()
    except Exception as e:
        results["get_routes"] = {
            "error": str(e)
        }

    try:
        results["get_weather"] = get_weather()
    except Exception as e:
        results["get_weather"] = {
            "error": str(e)
        }

    try:
        results["get_crowd_status"] = get_crowd_status()
    except Exception as e:
        results["get_crowd_status"] = {
            "error": str(e)
        }

    return results
@router.get("/debug/tool-roundtrip")
def debug_tool_roundtrip():
    """
    测试：模型发起工具调用 → 后端执行工具 → 再把工具结果交给模型总结。
    """
    try:
        client = get_client()
        model = get_zhipu_model()

        messages = [
            {
                "role": "user",
                "content": "雨天老君山适合走高阶路线吗？"
            }
        ]

        selected_tools = [
            tool for tool in tools
            if tool["function"]["name"] == "search_knowledge"
        ]

        first = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=selected_tools,
            tool_choice="auto"
        )

        first_message = first.choices[0].message
        tool_calls = getattr(first_message, "tool_calls", None)

        if not tool_calls:
            return {
                "success": True,
                "stage": "no_tool_call",
                "answer": first_message.content
            }

        messages.append({
            "role": "assistant",
            "content": first_message.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in tool_calls
            ]
        })

        for tc in tool_calls:
            args = json.loads(tc.function.arguments or "{}")
            result = search_knowledge(**args)

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "name": tc.function.name,
                "content": safe_json_dumps(result)
            })

        second = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=selected_tools
        )

        return {
            "success": True,
            "stage": "tool_roundtrip_success",
            "answer": second.choices[0].message.content
        }

    except Exception as e:
        return {
            "success": False,
            "error_type": e.__class__.__name__,
            "error": str(e),
            "repr": repr(e),
            "cause": repr(e.__cause__) if getattr(e, "__cause__", None) else None
        }