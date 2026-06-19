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
-- Data for Name: route_template; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.route_template (id, route_name, difficulty, node_sequence, estimated_time, suitable_user, description, source, source_url) VALUES (1, '初阶路线', 'easy', '票务中心;中灵索道;中天门;峰林索道;云景天路;十里画屏;马鬃岭;金顶道观群', '4-6小时', '初次游玩或体力一般游客', '该路线以索道和核心景观节点游览为主，步行强度相对较低，适合初次到访老君山或体力一般的游客。', '老君山官网', 'https://www.laojunshan.cn/nd.jsp?id=1938');
INSERT INTO public.route_template (id, route_name, difficulty, node_sequence, estimated_time, suitable_user, description, source, source_url) VALUES (2, '中阶路线', 'medium', '票务中心;中灵索道;中天门;云景天路;十里画屏;马鬃岭;金顶道观群;南天门', '5-7小时', '有一定体力、希望完整体验核心景观的游客', '该路线兼顾索道交通与核心景观游览，适合有一定体力并希望体验老君山山顶景观的游客。', '老君山官网', 'https://www.laojunshan.cn/nd.jsp?id=1938');
INSERT INTO public.route_template (id, route_name, difficulty, node_sequence, estimated_time, suitable_user, description, source, source_url) VALUES (3, '高阶路线', 'hard', '票务中心;中天门;云景天路;十里画屏;马鬃岭;金顶道观群;南天门', '7小时以上', '体力较好、有徒步经验的游客', '该路线游览强度较高，适合体力较好并具有一定山地徒步经验的游客，实际选择时应结合天气和景区管理要求。', '老君山官网', 'https://www.laojunshan.cn/nd.jsp?id=1938');


--
-- Name: route_template_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.route_template_id_seq', 3, true);


--
-- PostgreSQL database dump complete
--

