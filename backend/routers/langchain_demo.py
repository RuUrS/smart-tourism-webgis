from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.langchain_agent import run_langchain_demo

router = APIRouter(prefix="/api/langchain", tags=["langchain"])


class LangChainDemoRequest(BaseModel):
    question: str


@router.post("/demo")
def langchain_demo(req: LangChainDemoRequest):
    question = req.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="问题不能为空")

    try:
        result = run_langchain_demo(question)

        return result

    except Exception as e:
        # 注意：这里不要再 raise HTTPException(500)
        # LangChain Demo 只是框架验证模块，失败也要正常返回给前端
        return {
            "success": False,
            "mode": "langchain_demo",
            "answer": (
                "LangChain Demo 当前调用失败，但不会影响主旅游小助手。"
                "该模块仅用于验证 LangChain 框架封装能力，主系统仍使用原生工具调用 Agent。"
            ),
            "error": str(e)
        }