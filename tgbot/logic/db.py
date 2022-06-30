from dataclasses import dataclass
from datetime import datetime
import asyncpg


@dataclass
class Users:
    id: int
    username: str
    first_name: str
    last_name: str
    language_code: str
    is_deleted: bool
    date: datetime

class Db():
    def __init__(self):
        self.pool = None

    async def connect(self, url:str):
        self.pool = await asyncpg.create_pool(url)

    async def disconnect(self):
        await self.pool.close()

    async def create_db(self) -> None:
        await self.pool.execute(
            """CREATE TABLE IF NOT EXISTS 
            users 
                (user_id BIGINT PRIMARY KEY, 
                username VARCHAR(255), 
                first_name VARCHAR(255), 
                last_name VARCHAR(255), 
                language VARCHAR(255), 
                is_deleted BOOLEAN,
                created_at timestamp with time zone default now()
                )"""
        )

    async def get_user(self, user_id: int) -> Users:
        result =  await self.pool.fetchrow(
            "SELECT * FROM users WHERE user_id = $1", user_id
        )
        return Users(**result)


    async def write_user(self, user: Users):
        if await self.is_user_exist(user.id):
            pass
        else:
            await self.pool.execute(
                "INSERT INTO users(user_id, username, first_name, last_name, language, is_deleted, created_at) VALUES($1, $2, $3, $4, $5, $6, $7)",
                user.id, user.username, user.first_name, user.last_name, user.language_code, user.is_deleted, user.date
            )

    
    async def count_user(self) -> int:
        result = await self.pool.fetchval("SELECT COUNT(*) FROM users WHERE is_deleted = FALSE")
        return result

    async def is_user_exist(self, user_ud: int) -> bool:
        result = await self.pool.fetchval("SELECT COUNT(*) FROM users WHERE user_id = $1", user_ud)
        return result > 0

    async def count_today_user(self):
        result = await self.pool.fetchval("SELECT COUNT(*) FROM users WHERE created_at >= current_date")
        return result