"""用户注册登录与个人使用记录接口。

功能：
1. 注册账号:POST /api/auth/register
2. 登录账号:POST /api/auth/login
3. 获取当前用户:GET /api/auth/me
4. 保存用户记录:POST /api/auth/records
5. 查询我的记录:GET /api/auth/records

说明：
- 不额外依赖 PyJWT / passlib,直接使用 Python 标准库完成密码哈希和 Token 签名。
- 密码不会明文保存，使用 PBKDF2-HMAC-SHA256 加盐哈希。
- Token 是 HMAC 签名的短期登录凭证，默认 7 天有效。
"""
import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import time
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from psycopg2 import errors
from psycopg2.extras import Json, RealDictCursor

from database import get_connection

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Token 默认 7 天有效。正式部署时可按需要调整。
TOKEN_EXPIRE_SECONDS = 60 * 60 * 24 * 7

# 正式部署必须在 backend/.env 中配置 AUTH_SECRET_KEY。
# 示例：AUTH_SECRET_KEY=用 python -c "import secrets; print(secrets.token_urlsafe(32))" 生成
AUTH_SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "dev-change-me-smart-tourism")

USERNAME_PATTERN = re.compile(r"^[\w\u4e00-\u9fa5.@-]{3,80}$", re.UNICODE)

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=80)
    password: str = Field(..., min_length=6, max_length=128)
    nickname: Optional[str] = Field(default=None, max_length=120)

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=80)
    password: str = Field(..., min_length=6, max_length=128)

class UserRecordRequest(BaseModel):
    record_type: str = Field(..., min_length=1, max_length=50)
    title: Optional[str] = Field(default="", max_length=300)
    content: Dict[str, Any] = Field(default_factory=dict)

def ensure_auth_tables() -> None:
    """自动创建账号表和用户记录表。"""
    sql = """
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

    CREATE INDEX IF NOT EXISTS idx_user_activity_records_user_time
    ON user_activity_records(user_id, created_at DESC);

    CREATE INDEX IF NOT EXISTS idx_user_activity_records_type
    ON user_activity_records(record_type);
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
    finally:
        conn.close()

def normalize_username(username: str) -> str:
    username = (username or "").strip()
    if not USERNAME_PATTERN.match(username):
        raise HTTPException(
            status_code=400,
            detail="账号格式不正确：长度 3-80 位，可使用中文、字母、数字、下划线、点、@ 或横线"
        )
    return username

def normalize_nickname(nickname: Optional[str], username: str) -> str:
    value = (nickname or "").strip()
    if not value:
        value = username
    return value[:120]

def hash_password(password: str) -> str:
    """生成带盐密码哈希。保存格式：pbkdf2_sha256$迭代次数$salt$hash"""
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="密码至少需要 6 位")

    iterations = 200_000
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    ).hex()
    return f"pbkdf2_sha256${iterations}${salt}${digest}"

def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, iterations_text, salt, old_digest = password_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        iterations = int(iterations_text)
        new_digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations,
        ).hex()
        return hmac.compare_digest(new_digest, old_digest)
    except Exception:
        return False

def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

def base64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("ascii"))

def sign_token(payload_text: str) -> str:
    return hmac.new(
        AUTH_SECRET_KEY.encode("utf-8"),
        payload_text.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

def create_token(user: Dict[str, Any]) -> str:
    payload = {
        "user_id": user["id"],
        "username": user["username"],
        "exp": int(time.time()) + TOKEN_EXPIRE_SECONDS,
    }
    payload_text = base64url_encode(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    )
    signature = sign_token(payload_text)
    return f"{payload_text}.{signature}"

def parse_token(token: str) -> Dict[str, Any]:
    if not token or "." not in token:
        raise HTTPException(status_code=401, detail="请先登录")

    payload_text, signature = token.split(".", 1)
    expected_signature = sign_token(payload_text)

    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=401, detail="登录凭证无效，请重新登录")

    try:
        payload = json.loads(base64url_decode(payload_text).decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=401, detail="登录凭证解析失败，请重新登录")

    if int(payload.get("exp", 0)) < int(time.time()):
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")

    return payload

def get_bearer_token(request: Request) -> str:
    auth_header = request.headers.get("Authorization") or request.headers.get("authorization") or ""
    if not auth_header.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="请先登录")
    return auth_header.split(" ", 1)[1].strip()


def format_user(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "username": row["username"],
        "nickname": row.get("nickname") or row["username"],
        "created_at": row.get("created_at"),
        "last_login_at": row.get("last_login_at"),
    }

def get_current_user(request: Request) -> Dict[str, Any]:
    ensure_auth_tables()
    token = get_bearer_token(request)
    payload = parse_token(token)

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, username, nickname, created_at, last_login_at
                FROM app_users
                WHERE id = %s
                """,
                (payload.get("user_id"),),
            )
            user = cur.fetchone()

        if not user:
            raise HTTPException(status_code=401, detail="账号不存在，请重新登录")
        return format_user(dict(user))
    finally:
        conn.close()

def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return ""

@router.post("/register")
def register(payload: RegisterRequest):
    """注册账号。注册成功后直接返回 token，前端可自动进入地图。"""
    ensure_auth_tables()
    username = normalize_username(payload.username)
    nickname = normalize_nickname(payload.nickname, username)
    password_hash = hash_password(payload.password)

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            try:
                cur.execute(
                    """
                    INSERT INTO app_users (username, password_hash, nickname, last_login_at)
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                    RETURNING id, username, nickname, created_at, last_login_at
                    """,
                    (username, password_hash, nickname),
                )
                user = dict(cur.fetchone())
                conn.commit()
            except errors.UniqueViolation:
                conn.rollback()
                raise HTTPException(status_code=409, detail="该账号已存在，请换一个账号或直接登录")

        user_data = format_user(user)
        return {
            "message": "注册成功",
            "token": create_token(user_data),
            "user": user_data,
        }
    finally:
        conn.close()

@router.post("/login")
def login(payload: LoginRequest):
    """登录账号。"""
    ensure_auth_tables()
    username = normalize_username(payload.username)

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT id, username, password_hash, nickname, created_at, last_login_at
                FROM app_users
                WHERE username = %s
                """,
                (username,),
            )
            row = cur.fetchone()

            if not row or not verify_password(payload.password, row["password_hash"]):
                raise HTTPException(status_code=401, detail="账号或密码错误")

            cur.execute(
                """
                UPDATE app_users
                SET last_login_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id, username, nickname, created_at, last_login_at
                """,
                (row["id"],),
            )
            user = dict(cur.fetchone())
            conn.commit()

        user_data = format_user(user)
        return {
            "message": "登录成功",
            "token": create_token(user_data),
            "user": user_data,
        }
    finally:
        conn.close()

@router.get("/me")
def me(current_user: Dict[str, Any] = Depends(get_current_user)):
    """获取当前登录用户。"""
    return {"user": current_user}

@router.post("/records")
def create_record(
    payload: UserRecordRequest,
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """保存当前登录用户的一条使用记录。游客没有 token，不会调用到这里。"""
    ensure_auth_tables()
    record_type = payload.record_type.strip()[:50]
    title = (payload.title or record_type).strip()[:300]
    content = payload.content or {}

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                INSERT INTO user_activity_records
                    (user_id, record_type, title, content, ip_address, user_agent)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, user_id, record_type, title, content, created_at
                """,
                (
                    current_user["id"],
                    record_type,
                    title,
                    Json(content),
                    get_client_ip(request),
                    request.headers.get("user-agent", ""),
                ),
            )
            record = dict(cur.fetchone())
            conn.commit()

        return {"message": "记录保存成功", "record": record}
    finally:
        conn.close()

@router.get("/records")
def list_records(
    current_user: Dict[str, Any] = Depends(get_current_user),
    record_type: Optional[str] = Query(default=None, max_length=50),
    limit: int = Query(default=30, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """查询当前账号自己的使用记录。"""
    ensure_auth_tables()

    params = [current_user["id"]]
    where_sql = "WHERE user_id = %s"

    if record_type:
        where_sql += " AND record_type = %s"
        params.append(record_type.strip()[:50])

    params.extend([limit, offset])

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                f"""
                SELECT id, record_type, title, content, created_at
                FROM user_activity_records
                {where_sql}
                ORDER BY created_at DESC, id DESC
                LIMIT %s OFFSET %s
                """,
                tuple(params),
            )
            records = [dict(row) for row in cur.fetchall()]

        return {"records": records}
    finally:
        conn.close()

@router.post("/logout")
def logout():
    """前端清除本地 token 即可；这个接口仅用于保持接口完整。"""
    return {"message": "已退出登录"}