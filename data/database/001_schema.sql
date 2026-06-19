-- PostGIS 数据库建表示例
-- 使用前请先在数据库中执行：CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS poi (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50),
    subtype VARCHAR(50),
    address TEXT,
    description TEXT,
    source VARCHAR(100),
    verify_status VARCHAR(50),
    geom geometry(Point, 4326)
);

CREATE INDEX IF NOT EXISTS idx_poi_geom ON poi USING GIST (geom);

CREATE TABLE IF NOT EXISTS tourism_knowledge (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200),
    content TEXT,
    category VARCHAR(50),
    related_poi_id INTEGER,
    source TEXT,
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS route_template (
    id SERIAL PRIMARY KEY,
    route_name VARCHAR(100),
    difficulty VARCHAR(30),
    node_sequence TEXT,
    estimated_time VARCHAR(50),
    suitable_user TEXT,
    description TEXT,
    source TEXT
);

CREATE TABLE IF NOT EXISTS crowd_status_mock (
    id SERIAL PRIMARY KEY,
    poi_id INTEGER,
    crowd_status VARCHAR(20),
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_type VARCHAR(50) DEFAULT 'mock'
);
