import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("NEON_DB_URL")

async def get_db_pool():
    return await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)

async def close_db_pool(pool):
    await pool.close()
