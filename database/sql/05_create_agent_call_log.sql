CREATE TABLE IF NOT EXISTS agent_call_log (
    id SERIAL PRIMARY KEY,
    question TEXT,
    agent_type VARCHAR(50),
    agent_name VARCHAR(100),
    tool_used BOOLEAN,
    used_tools TEXT,
    map_action VARCHAR(100),
    create_time TIMESTAMP DEFAULT NOW()
);