# Vue 3 + Vite

This template should help get you started developing with Vue 3 in Vite. The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.

Learn more about IDE Support for Vue in the [Vue Docs Scaling up Guide](https://vuejs.org/guide/scaling-up/tooling.html#ide-support).

# frontend

`frontend/` 目录是本项目的前端工程目录，基于 Vue 3 + Vite 开发，主要负责地图页面展示、用户登录入口、POI 搜索、天气展示、路线规划、智能旅游助手和前端交互界面。

## 项目结构

```text
frontend
├─ public/              # 前端公共静态资源目录
├─ src/                 # 前端核心源码目录
├─ .env.example         # 前端环境变量模板文件
├─ .gitignore           # 前端 Git 忽略规则
├─ .gitkeep             # 空目录占位文件
├─ README.md            # 前端说明文档
├─ index.html           # Vite 前端入口 HTML 文件
├─ leaflet-test.html    # Leaflet 地图测试页面
├─ package-lock.json    # 前端依赖锁定文件
├─ package.json         # 前端依赖、脚本和项目信息配置
└─ vite.config.js       # Vite 配置文件，包含开发服务和后端接口代理配置
```

## 主要目录说明

| 目录 / 文件      | 作用                                                                      |
| ---------------- | ------------------------------------------------------------------------- |
| `public/`        | 存放前端公共静态资源，例如图标、favicon 等。                              |
| `src/`           | 存放前端核心源码，包括组件、路由、工具函数、全局样式等。                  |
| `index.html`     | 前端页面入口文件，Vite 会从这里加载 Vue 应用。                            |
| `package.json`   | 前端项目配置文件，记录依赖包和运行命令。                                  |
| `vite.config.js` | Vite 配置文件，用于配置本地开发服务、端口、局域网访问和 `/api` 接口代理。 |
| `.env.example`   | 前端环境变量模板，真实 `.env` 文件不上传 GitHub。                         |

## 前端运行方式

安装依赖：

```bash
npm install
```

启动前端开发服务：

```bash
npm run dev -- --host 0.0.0.0
```

本机访问：

```text
http://localhost:5173
```

局域网手机访问：

```text
http://电脑IP:5173
```

## 说明

- 前端接口请求建议统一使用 `/api/...`，由 `vite.config.js` 代理转发到后端服务。
- 不建议在代码中写死 `localhost` 或局域网 IP，避免换网络后接口失效。
- `node_modules/`、`.env`、构建产物等内容已通过 `.gitignore` 排除，不上传 GitHub。
