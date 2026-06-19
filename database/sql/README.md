# SQL 脚本说明

本目录用于保存老君山智能旅游 WebGIS 系统数据库相关 SQL 脚本。

## 文件说明

- 00_enable_postgis.sql：启用 PostGIS 扩展
- 01_create_tables.sql：系统主要数据表建表语句
- 02_insert_tourism_knowledge.sql：旅游知识库数据
- 03_insert_route_template.sql：游览路线模板数据
- 04_insert_crowd_status.sql：模拟客流数据
- 05_create_agent_call_log.sql：Agent 调用日志表
- 06_create_road_network_view.sql：路网展示视图
- 07_create_indexes.sql：空间索引和普通索引
- 08_insert_laojunshan_poi.sql:POI点数据
- 09_insert_luanchuan_boundary.sql：栾川县边界数据

## 使用顺序

建议按文件编号顺序执行。
