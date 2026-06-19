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
-- Data for Name: crowd_status; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.crowd_status (id, poi_id, crowd_value, crowd_level, time_slot, update_time, source, remark) VALUES (2, 6, 61, '适中', '中午', '2026-05-22 22:09:26.669388', '系统模拟', '根据 POI 类型、核心节点重要性和时间段生成的模拟客流数据');
INSERT INTO public.crowd_status (id, poi_id, crowd_value, crowd_level, time_slot, update_time, source, remark) VALUES (3, 7, 60, '适中', '中午', '2026-05-22 22:09:26.669388', '系统模拟', '根据 POI 类型、核心节点重要性和时间段生成的模拟客流数据');
INSERT INTO public.crowd_status (id, poi_id, crowd_value, crowd_level, time_slot, update_time, source, remark) VALUES (4, 8, 74, '适中', '中午', '2026-05-22 22:09:26.669388', '系统模拟', '根据 POI 类型、核心节点重要性和时间段生成的模拟客流数据');
INSERT INTO public.crowd_status (id, poi_id, crowd_value, crowd_level, time_slot, update_time, source, remark) VALUES (5, 9, 58, '适中', '中午', '2026-05-22 22:09:26.669388', '系统模拟', '根据 POI 类型、核心节点重要性和时间段生成的模拟客流数据');
INSERT INTO public.crowd_status (id, poi_id, crowd_value, crowd_level, time_slot, update_time, source, remark) VALUES (6, 10, 81, '拥挤', '中午', '2026-05-22 22:09:26.669388', '系统模拟', '根据 POI 类型、核心节点重要性和时间段生成的模拟客流数据');
INSERT INTO public.crowd_status (id, poi_id, crowd_value, crowd_level, time_slot, update_time, source, remark) VALUES (20, 11, 49, '适中', '中午', '2026-05-22 22:09:26.669388', '系统模拟', '根据 POI 类型、核心节点重要性和时间段生成的模拟客流数据');
INSERT INTO public.crowd_status (id, poi_id, crowd_value, crowd_level, time_slot, update_time, source, remark) VALUES (21, 12, 44, '舒适', '中午', '2026-05-22 22:09:26.669388', '系统模拟', '根据 POI 类型、核心节点重要性和时间段生成的模拟客流数据');
INSERT INTO public.crowd_status (id, poi_id, crowd_value, crowd_level, time_slot, update_time, source, remark) VALUES (22, 13, 44, '舒适', '中午', '2026-05-22 22:09:26.669388', '系统模拟', '根据 POI 类型、核心节点重要性和时间段生成的模拟客流数据');
INSERT INTO public.crowd_status (id, poi_id, crowd_value, crowd_level, time_slot, update_time, source, remark) VALUES (23, 14, 55, '适中', '中午', '2026-05-22 22:09:26.669388', '系统模拟', '根据 POI 类型、核心节点重要性和时间段生成的模拟客流数据');
INSERT INTO public.crowd_status (id, poi_id, crowd_value, crowd_level, time_slot, update_time, source, remark) VALUES (7, 15, 57, '适中', '中午', '2026-05-22 22:09:26.669388', '系统模拟', '根据 POI 类型、核心节点重要性和时间段生成的模拟客流数据');
INSERT INTO public.crowd_status (id, poi_id, crowd_value, crowd_level, time_slot, update_time, source, remark) VALUES (8, 16, 46, '适中', '中午', '2026-05-22 22:09:26.669388', '系统模拟', '根据 POI 类型、核心节点重要性和时间段生成的模拟客流数据');
INSERT INTO public.crowd_status (id, poi_id, crowd_value, crowd_level, time_slot, update_time, source, remark) VALUES (26, 17, 53, '适中', '中午', '2026-05-22 22:09:26.669388', '系统模拟', '根据 POI 类型、核心节点重要性和时间段生成的模拟客流数据');
INSERT INTO public.crowd_status (id, poi_id, crowd_value, crowd_level, time_slot, update_time, source, remark) VALUES (27, 18, 41, '舒适', '中午', '2026-05-22 22:09:26.669388', '系统模拟', '根据 POI 类型、核心节点重要性和时间段生成的模拟客流数据');
INSERT INTO public.crowd_status (id, poi_id, crowd_value, crowd_level, time_slot, update_time, source, remark) VALUES (28, 19, 52, '适中', '中午', '2026-05-22 22:09:26.669388', '系统模拟', '根据 POI 类型、核心节点重要性和时间段生成的模拟客流数据');
INSERT INTO public.crowd_status (id, poi_id, crowd_value, crowd_level, time_slot, update_time, source, remark) VALUES (29, 20, 41, '舒适', '中午', '2026-05-22 22:09:26.669388', '系统模拟', '根据 POI 类型、核心节点重要性和时间段生成的模拟客流数据');
INSERT INTO public.crowd_status (id, poi_id, crowd_value, crowd_level, time_slot, update_time, source, remark) VALUES (10, 1, 41, '舒适', '中午', '2026-05-22 22:09:26.669388', '系统模拟', '根据 POI 类型、核心节点重要性和时间段生成的模拟客流数据');
INSERT INTO public.crowd_status (id, poi_id, crowd_value, crowd_level, time_slot, update_time, source, remark) VALUES (1, 2, 52, '适中', '中午', '2026-05-22 22:09:26.669388', '系统模拟', '根据 POI 类型、核心节点重要性和时间段生成的模拟客流数据');
INSERT INTO public.crowd_status (id, poi_id, crowd_value, crowd_level, time_slot, update_time, source, remark) VALUES (12, 3, 59, '适中', '中午', '2026-05-22 22:09:26.669388', '系统模拟', '根据 POI 类型、核心节点重要性和时间段生成的模拟客流数据');
INSERT INTO public.crowd_status (id, poi_id, crowd_value, crowd_level, time_slot, update_time, source, remark) VALUES (13, 4, 58, '适中', '中午', '2026-05-22 22:09:26.669388', '系统模拟', '根据 POI 类型、核心节点重要性和时间段生成的模拟客流数据');
INSERT INTO public.crowd_status (id, poi_id, crowd_value, crowd_level, time_slot, update_time, source, remark) VALUES (9, 5, 67, '适中', '中午', '2026-05-22 22:09:26.669388', '系统模拟', '根据 POI 类型、核心节点重要性和时间段生成的模拟客流数据');


--
-- Name: crowd_status_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.crowd_status_id_seq', 469, true);


--
-- PostgreSQL database dump complete
--

