import asyncpg
from typing import Optional
from backend.core.config import settings

_pool: Optional[asyncpg.Pool] = None

async def init_db():
    global _pool
    if settings.database_url:
        _pool = await asyncpg.create_pool(dsn=settings.database_url, min_size=1, max_size=10)

async def close_db():
    global _pool
    if _pool:
        await _pool.close()

def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Database pool chưa được khởi tạo hoặc DATABASE_URL chưa cài đặt.")
    return _pool        