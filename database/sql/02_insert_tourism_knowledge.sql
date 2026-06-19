--
-- PostgreSQL database dump
--

-- Dumped from database version 16.4
-- Dumped by pg_dump version 16.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: tourism_knowledge; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.tourism_knowledge (id, title, category, related_poi, content, source, source_url, update_time, content_type, keywords, verify_status, created_at) VALUES (11, '十里画屏游览提示', 'scenic_intro', '十里画屏', '十里画屏是老君山核心自然景观游览区，沿线山体形态丰富，适合观赏峰林、云海和山地景观。雨天或道路湿滑时应注意防滑。', '人工整理', '', NULL, 'article', '十里画屏游览提示,scenic_intro', '已核验', '2026-05-22 18:52:43.849531');
INSERT INTO public.tourism_knowledge (id, title, category, related_poi, content, source, source_url, update_time, content_type, keywords, verify_status, created_at) VALUES (12, '马鬃岭观景提示', 'scenic_intro', '马鬃岭', '马鬃岭是老君山重要观景节点之一，适合远眺山体景观。游览时应结合天气和体力情况合理安排停留时间。', '人工整理', '', NULL, 'article', '马鬃岭观景提示,scenic_intro', '已核验', '2026-05-22 18:52:43.849531');
INSERT INTO public.tourism_knowledge (id, title, category, related_poi, content, source, source_url, update_time, content_type, keywords, verify_status, created_at) VALUES (13, '初阶路线建议', 'route_guide', '老君山景区', '初阶路线适合初次到访老君山或体力一般游客，通常以票务中心、索道、中天门、十里画屏、金顶道观群等核心节点为主，步行强度相对较低。', '人工整理', '', NULL, 'guide', '初阶路线建议,route_guide', '已核验', '2026-05-22 18:52:43.849531');
INSERT INTO public.tourism_knowledge (id, title, category, related_poi, content, source, source_url, update_time, content_type, keywords, verify_status, created_at) VALUES (14, '中阶路线建议', 'route_guide', '老君山景区', '中阶路线适合有一定体力基础的游客，可在核心景点基础上增加部分观景节点，游览时间和步行强度高于初阶路线。', '人工整理', '', NULL, 'guide', '中阶路线建议,route_guide', '已核验', '2026-05-22 18:52:43.849531');
INSERT INTO public.tourism_knowledge (id, title, category, related_poi, content, source, source_url, update_time, content_type, keywords, verify_status, created_at) VALUES (15, '高阶路线风险提示', 'route_guide', '老君山景区', '高阶路线适合体力较好、时间充足的游客。雨雪、大风、低温或道路湿滑情况下，不建议选择高强度徒步路线。', '人工整理', '', NULL, 'guide', '高阶路线风险提示,route_guide', '已核验', '2026-05-22 18:52:43.849531');
INSERT INTO public.tourism_knowledge (id, title, category, related_poi, content, source, source_url, update_time, content_type, keywords, verify_status, created_at) VALUES (16, '雨天游览安全提示', 'weather_tip', '老君山景区', '雨天老君山山地道路可能湿滑，建议游客穿防滑鞋、携带雨具，减少高强度徒步，优先选择索道和核心景观节点游览。', '人工整理', '', NULL, 'guide', '雨天游览安全提示,weather_tip', '已核验', '2026-05-22 18:52:43.849531');
INSERT INTO public.tourism_knowledge (id, title, category, related_poi, content, source, source_url, update_time, content_type, keywords, verify_status, created_at) VALUES (17, '低温天气游览提示', 'weather_tip', '老君山景区', '老君山海拔较高，低温天气体感温度可能明显低于城区。游客应注意保暖，合理控制游览时间。', '人工整理', '', NULL, 'guide', '低温天气游览提示,weather_tip', '已核验', '2026-05-22 18:52:43.849531');
INSERT INTO public.tourism_knowledge (id, title, category, related_poi, content, source, source_url, update_time, content_type, keywords, verify_status, created_at) VALUES (18, '客流错峰建议', 'crowd_tip', '老君山景区', '当金顶道观群、十里画屏等核心节点模拟客流较高时，建议游客适当错峰游览，优先选择客流较低的观景节点或服务节点停留。', '人工整理', '', NULL, 'guide', '客流错峰建议,crowd_tip', '已核验', '2026-05-22 18:52:43.849531');
INSERT INTO public.tourism_knowledge (id, title, category, related_poi, content, source, source_url, update_time, content_type, keywords, verify_status, created_at) VALUES (19, '索道游览提示', 'service', '索道', '老君山游览路线中索道节点承担重要交通换乘功能，游客应结合天气、排队情况和体力状况选择是否乘坐索道。', '人工整理', '', NULL, 'guide', '索道游览提示,service', '已核验', '2026-05-22 18:52:43.849531');
INSERT INTO public.tourism_knowledge (id, title, category, related_poi, content, source, source_url, update_time, content_type, keywords, verify_status, created_at) VALUES (20, '停车与入园提示', 'service', '票务中心', '自驾游客应优先关注景区停车场、票务中心和游客中心位置，节假日或客流高峰期应预留到达和换乘时间。', '人工整理', '', NULL, 'guide', '停车与入园提示,service', '已核验', '2026-05-22 18:52:43.849531');
INSERT INTO public.tourism_knowledge (id, title, category, related_poi, content, source, source_url, update_time, content_type, keywords, verify_status, created_at) VALUES (1, '老君山景区概况', '景区概况', '老君山景区', '老君山位于河南省洛阳市栾川县，是以山地观光、道教文化和地质景观为主要特色的旅游景区。系统将其作为智能旅游 WebGIS 的案例区，用于展示景点查询、路线推荐、附近服务查询和智能问答等功能。', '老君山官网', 'https://www.laojunshan.cn/', '2026-05-17', 'article', '老君山景区概况,景区概况,老君山景区', '已核验', '2026-05-22 18:50:31.332822');
INSERT INTO public.tourism_knowledge (id, title, category, related_poi, content, source, source_url, update_time, content_type, keywords, verify_status, created_at) VALUES (2, '初阶路线说明', '游览线路', '老君山景区', '初阶路线以索道和核心景观节点游览为主，适合初次游玩或体力一般的游客。主要节点包括票务中心、中灵索道、中天门、峰林索道、云景天路、十里画屏、马鬃岭和金顶道观群。', '老君山官网', 'https://www.laojunshan.cn/nd.jsp?id=1938', '2026-05-17', 'article', '初阶路线说明,游览线路,老君山景区', '已核验', '2026-05-22 18:50:31.332822');
INSERT INTO public.tourism_knowledge (id, title, category, related_poi, content, source, source_url, update_time, content_type, keywords, verify_status, created_at) VALUES (3, '中阶路线说明', '游览线路', '老君山景区', '中阶路线适合有一定体力、希望较完整体验老君山核心景观的游客。路线兼顾索道交通与山顶核心景观游览，游览时间和体力消耗高于初阶路线。', '老君山官网', 'https://www.laojunshan.cn/nd.jsp?id=1938', '2026-05-17', 'article', '中阶路线说明,游览线路,老君山景区', '已核验', '2026-05-22 18:50:31.332822');
INSERT INTO public.tourism_knowledge (id, title, category, related_poi, content, source, source_url, update_time, content_type, keywords, verify_status, created_at) VALUES (5, '金顶道观群介绍', '景点介绍', '金顶道观群', '金顶道观群是老君山核心文化景观之一，具有较强的道教文化特色，也是游客游览老君山山顶区域的重要节点。', '老君山官网', 'https://www.laojunshan.cn/', '2026-05-17', 'article', '金顶道观群介绍,景点介绍,金顶道观群', '已核验', '2026-05-22 18:50:31.332822');
INSERT INTO public.tourism_knowledge (id, title, category, related_poi, content, source, source_url, update_time, content_type, keywords, verify_status, created_at) VALUES (4, '高阶路线说明', '游览线路', '老君山景区', '高阶路线适合体力较好、有一定徒步经验的游客。该路线游览强度较高，实际选择时应结合天气、体力状况和景区管理要求，不建议盲目选择高强度路线。', '老君山官网', 'https://www.laojunshan.cn/nd.jsp?id=1938', '2026-05-17', 'article', '高阶路线说明,游览线路,老君山景区', '已核验', '2026-05-22 18:50:31.332822');
INSERT INTO public.tourism_knowledge (id, title, category, related_poi, content, source, source_url, update_time, content_type, keywords, verify_status, created_at) VALUES (6, '十里画屏介绍', '景点介绍', '十里画屏', '十里画屏是老君山核心自然景观游览区，适合观赏山地景观、拍照和体验老君山的自然风光。', '老君山官网', 'https://www.laojunshan.cn/', '2026-05-17', 'article', '十里画屏介绍,景点介绍,十里画屏', '已核验', '2026-05-22 18:50:31.332822');
INSERT INTO public.tourism_knowledge (id, title, category, related_poi, content, source, source_url, update_time, content_type, keywords, verify_status, created_at) VALUES (7, '马鬃岭介绍', '景点介绍', '马鬃岭', '马鬃岭是老君山重要观景节点，适合远眺山地景观，也是核心游览线路中的重要节点。', '老君山官网', 'https://www.laojunshan.cn/', '2026-05-17', 'article', '马鬃岭介绍,景点介绍,马鬃岭', '已核验', '2026-05-22 18:50:31.332822');
INSERT INTO public.tourism_knowledge (id, title, category, related_poi, content, source, source_url, update_time, content_type, keywords, verify_status, created_at) VALUES (8, '索道游览建议', '游览建议', '中灵索道', '对于初次游玩或体力一般的游客，建议优先选择索道辅助游览，以减少爬升消耗，将主要体力保留给山顶核心景观游览。', '老君山官网', 'https://www.laojunshan.cn/nd.jsp?id=1938', '2026-05-17', 'article', '索道游览建议,游览建议,中灵索道', '已核验', '2026-05-22 18:50:31.332822');
INSERT INTO public.tourism_knowledge (id, title, category, related_poi, content, source, source_url, update_time, content_type, keywords, verify_status, created_at) VALUES (9, '体力一般游客建议', '游览建议', '老君山景区', '体力一般或第一次到访老君山的游客，建议选择初阶路线，主要依托索道和核心景点游览，避免选择强度较高的徒步路线。', '老君山官网', 'https://www.laojunshan.cn/nd.jsp?id=1938', '2026-05-17', 'article', '体力一般游客建议,游览建议,老君山景区', '已核验', '2026-05-22 18:50:31.332822');
INSERT INTO public.tourism_knowledge (id, title, category, related_poi, content, source, source_url, update_time, content_type, keywords, verify_status, created_at) VALUES (10, '雨天游览提醒', '游览注意事项', '老君山景区', '老君山为山地型景区，雨天或低温天气下道路湿滑，游客应注意防滑和保暖，必要时减少高强度徒步路线，优先选择较稳妥的游览方式。', '老君山官网', 'https://www.laojunshan.cn/', '2026-05-17', 'article', '雨天游览提醒,游览注意事项,老君山景区', '已核验', '2026-05-22 18:50:31.332822');


--
-- Name: tourism_knowledge_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tourism_knowledge_id_seq', 20, true);


--
-- PostgreSQL database dump complete
--

