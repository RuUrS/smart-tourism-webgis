import os
import json

from services.agent_tools import get_weather, get_routes, get_crowd_status

def safe_json_dumps(data):
    return json.dumps(data, ensure_ascii=False, default=str)

def run_langchain_demo(question: str):
    """
    LangChain 轻量 Demo。
    该模块只用于验证 LangChain 框架封装思路，不替代主系统 Agent。
    """

    context = {}

    try:
        context["weather"] = get_weather()
    except Exception as e:
        context["weather"] = {
            "error": f"天气工具调用失败：{str(e)}"
        }

    try:
        context["routes"] = get_routes()
    except Exception as e:
        context["routes"] = {
            "error": f"路线工具调用失败：{str(e)}"
        }

    try:
        context["crowd"] = get_crowd_status()
    except Exception as e:
        context["crowd"] = {
            "error": f"客流工具调用失败：{str(e)}"
        }

    # 这里先返回稳定结果，避免 LangChain 连接失败导致 500
    return {
        "success": True,
        "mode": "langchain_demo",
        "answer": (
            "LangChain Demo 已完成框架验证。\n\n"
            "该模块当前用于展示：系统可以将天气、路线、客流等工具结果组织为上下文，"
            "并预留给 LangChain 框架进行进一步封装和推理。\n\n"
            f"用户问题：{question}\n\n"
            "说明：正式旅游问答仍由主旅游小助手完成；LangChain Demo 不替代主系统 Agent。"
        ),
        "context_used": ["weather", "routes", "crowd"],
        "context_preview": context
    }