-- 用户注册登录与个人使用记录表
-- 可手动执行；后端 auth.py 里也有自动建表逻辑。
CREATE TABLE IF NOT EXISTS app_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    nickname VARCHAR(120),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP
);
CREATE TABLE IF NOT EXISTS user_activity_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES app_users(id) ON DELETE CASCADE,
    record_type VARCHAR(50) NOT NULL,
    title TEXT,
    content JSONB DEFAULT '{}'::jsonb,
    ip_address VARCHAR(80),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_user_activity_records_user_time ON user_activity_records(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_activity_records_type ON user_activity_records(record_type);