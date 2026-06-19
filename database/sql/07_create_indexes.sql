CREATE INDEX IF NOT EXISTS idx_laojunshan_poi_geom ON laojunshan_poi USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_luanchuan_boundary_geom ON luanchuan_boundary USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_road_network_geom ON road_network USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_tourism_knowledge_title ON tourism_knowledge (title);
CREATE INDEX IF NOT EXISTS idx_tourism_knowledge_category ON tourism_knowledge (category);
CREATE INDEX IF NOT EXISTS idx_agent_call_log_create_time ON agent_call_log (create_time);