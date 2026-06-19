from dotenv import load_dotenv

load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import boundary, poi, route, chat, weather, agent, amap, crowd, traffic,recommend,knowledge  # cspell:ignore amap
from routers import dashboard
from routers import langchain_demo
from routers import road
from routers import auth

app = FastAPI(title="智能旅游 WebGIS 后端服务")

# 允许前端访问后端接口
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(boundary.router)#注册边界接口
app.include_router(poi.router)#注册兴趣点接口
app.include_router(route.router)#注册路线接口
app.include_router(chat.router)#注册聊天接口
app.include_router(weather.router)#注册天气接口
app.include_router(agent.router)#注册智能体接口
app.include_router(amap.router)#注册高德接口
app.include_router(crowd.router)#注册模拟客流接口
app.include_router(traffic.router)#注册交通接口
app.include_router(recommend.router)#注册动态路线推荐接口
app.include_router(knowledge.router)#注册知识库接口
app.include_router(dashboard.router)#注册可视化大屏接口
app.include_router(langchain_demo.router)#注册langchain接口
app.include_router(road.router)#注册道路接口
app.include_router(auth.router)#注册用户登录与个人记录接口

@app.get("/")
def root():
    return {
        "message": "智能旅游 WebGIS 后端服务启动成功"
    }