# services

`services/` 目录用于存放后端业务服务逻辑。该目录主要负责对接口层 `routers/` 提供可复用的业务能力，避免把复杂逻辑全部写在路由文件中。

## 文件说明

| 文件                 | 作用                                                                                                                  |
| -------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `agent_tools.py`     | 智能旅游助手工具函数文件，主要用于封装地图搜索、天气查询、路线推荐、POI 查询、上下文整理等可供 Agent 调用的工具能力。 |
| `langchain_agent.py` | LangChain 智能体示例文件，用于测试或扩展基于 LangChain 的智能体调用流程，为后续复杂 Agent 编排预留接口。              |
| `.gitkeep`           | 空目录占位文件，用于保证该目录在 Git 仓库中被保留。                                                                   |
| `README.md`          | 当前目录说明文档，用于解释 `services/` 目录下各文件的作用。                                                           |

## 与 routers 目录的关系

`routers/` 目录主要负责接收前端请求、定义接口路径和返回响应结果；
`services/` 目录主要负责具体业务处理逻辑。

例如：

- `routers/agent.py` 负责提供智能旅游助手接口；
- `services/agent_tools.py` 负责提供智能助手可调用的工具函数；
- `routers/langchain_demo.py` 可调用 `services/langchain_agent.py` 中的 LangChain 示例逻辑。

## 说明

- 本目录不存放真实 API Key、数据库密码等敏感信息。
- 需要读取配置时，应通过后端 `.env` 文件和环境变量获取。
- `__pycache__/` 是 Python 自动生成的缓存目录，已通过 `.gitignore` 排除，不需要上传到 GitHub。
