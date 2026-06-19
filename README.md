# 老君山智能旅游 WebGIS 系统

## 一、项目简介

本系统以河南省洛阳市栾川县老君山景区为案例区，构建集 WebGIS 地图展示、旅游 POI 查询、实时天气、路径规划、周边交通态势、模拟客流分析、基础路网展示、ECharts 数据大屏和大模型 Agent 旅游小助手于一体的智能旅游服务系统。

系统以 PostGIS 作为空间数据库，采用 Vue 3 + Leaflet 构建前端地图界面，采用 FastAPI 构建后端服务，接入高德 API 和智谱 AI GLM-4.5-Flash，实现基于大模型与功能 Agent 的旅游信息服务。

## 二、技术栈

- 前端：Vue 3、Vite、Leaflet、ECharts
- 后端：FastAPI、Python
- 数据库：PostgreSQL、PostGIS
- 地图服务：高德地图瓦片、高德 Web 服务 API、高德 JS API
- 大模型：智谱 AI GLM-4.5-Flash
- 数据来源：景区 POI、栾川县边界、OSM 路网、旅游知识库、模拟客流数据

## 三、开发环境

- 操作系统：Windows 11
- Node.js：v24.15.0
- npm：11.12.1
- Python：3.12+
- PostgreSQL：14+
- PostGIS：3+
- Git：2.54.0

## 四、主要功能

1. 栾川县边界与老君山 POI 展示
2. 在线地图搜索与点位详情查询
3. 实时天气卡片与天气跟随点位
4. 高德路径规划与周边交通态势查询
5. 模拟客流点与客流热力图
6. OSM 基础路网展示
7. 多 Agent 智能旅游小助手
8. ECharts 智能旅游数据大屏
9. LangChain Demo 框架验证模块

## 五、启动方式

### 后端启动

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 前端启动

> 前端项目基于 Vite 构建，运行前请先安装 Node.js 和 npm。

```powershell
cd frontend
npm install
npm run dev
```
