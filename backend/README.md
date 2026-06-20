# backend

`backend/` 目录是本项目的后端服务目录，基于 FastAPI 开发，主要负责向前端提供地图数据、POI 查询、天气查询、路线规划、智能旅游助手、用户注册登录、用户使用记录等接口服务。

## 目录结构

```text
backend
├─ routers/              # 后端接口路由目录，不同功能接口按模块拆分
├─ schemas/              # 数据结构目录，预留用于请求体、响应体、数据模型定义
├─ services/             # 后端业务服务目录，存放 Agent 工具、LangChain 示例等业务逻辑
├─ .env.example          # 环境变量模板，实际运行时需复制为 .env 并填写数据库、API Key 等配置
├─ .gitkeep              # 空目录占位文件，用于保留 Git 默认不跟踪的空目录
├─ database.py           # 数据库连接与查询工具，负责连接 PostgreSQL / PostGIS
├─ main.py               # 后端应用入口，负责创建 FastAPI 应用、配置跨域、注册各个路由模块
└─ requirements.txt      # Python 后端依赖包列表
```

## 文件夹说明

| 文件夹      | 作用                                                                                          |
| ----------- | --------------------------------------------------------------------------------------------- |
| `routers/`  | 存放后端接口路由文件，例如用户登录、POI 查询、天气、路线规划、智能助手、高德地图接口等。      |
| `schemas/`  | 预留的数据结构目录，可用于存放 Pydantic 请求体、响应体、数据校验模型等。                      |
| `services/` | 存放后端业务服务逻辑，例如 Agent 工具函数、LangChain 示例逻辑等，供 `routers/` 中的接口调用。 |

## 主要文件说明

| 文件               | 作用                                                                                             |
| ------------------ | ------------------------------------------------------------------------------------------------ |
| `main.py`          | 后端启动入口，创建 FastAPI 应用，配置 CORS 跨域，统一注册 `routers/` 目录下的接口模块。          |
| `database.py`      | 数据库连接文件，负责读取数据库配置并连接 PostgreSQL / PostGIS，用于空间数据和业务数据查询。      |
| `requirements.txt` | 后端 Python 依赖列表，部署或本地运行前需要通过该文件安装依赖。                                   |
| `.env.example`     | 环境变量模板文件，用于说明后端运行所需配置，例如数据库连接、智谱 API Key、高德 Key、登录密钥等。 |
| `.gitkeep`         | 占位文件，用于让空目录也能被 Git 保留。                                                          |

## 环境变量说明

真实运行时需要在 `backend/` 目录下创建 `.env` 文件。
`.env` 文件不上传 GitHub，只上传 `.env.example` 作为配置模板。

常见配置包括：

```env
DATABASE_URL=postgresql://用户名:密码@127.0.0.1:5432/数据库名
ZHIPUAI_API_KEY=请填写智谱API_KEY
ZHIPUAI_MODEL=glm-4.5-flash
ZHIPUAI_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
AUTH_SECRET_KEY=请自行生成随机密钥
AMAP_KEY=请填写高德地图Key
```

## 后端启动方式

进入后端目录：

```bash
cd backend
```

安装依赖：

```bash
pip install -r requirements.txt
```

启动后端服务：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

启动成功后，本地接口文档地址为：

```text
http://127.0.0.1:8000/docs
```

局域网访问时，可将 `127.0.0.1` 替换为后端所在电脑的局域网 IP。

## 说明

- `backend/.env` 中包含数据库密码、API Key、登录密钥等敏感信息，已通过 `.gitignore` 排除，不应上传到 GitHub。
- 后端接口统一在 `main.py` 中注册。
- 接口层代码主要放在 `routers/`，复杂业务逻辑可放在 `services/`，数据结构定义可放在 `schemas/`。
