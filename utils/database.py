import aiosqlite

from constants import DATABASE_FILE_NAME

async def init_database():
    async with aiosqlite.connect(DATABASE_FILE_NAME) as db:
        # warn table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS warnings (
                warn_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                issuer_id INTEGER NOT NULL,
                reason TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )""")
        # guild whitelist table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS whitelisted_guilds (
                guild_whitelist_id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                adder_id INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )""")
        await db.commit()
        print("Successfully initialized database!")

async def execute(query: str, parameters: tuple = ()):
    async with aiosqlite.connect(DATABASE_FILE_NAME) as db:
        async with db.execute(query, parameters) as cursor:
            await db.commit()
            return cursor.lastrowid

async def fetch_all(query: str, parameters: tuple = ()):
    async with aiosqlite.connect(DATABASE_FILE_NAME) as db:
        async with db.execute(query, parameters) as cursor:
            return await cursor.fetchall()

async def fetch_one(query: str, parameters: tuple = ()):
    async with aiosqlite.connect(DATABASE_FILE_NAME) as db:
        async with db.execute(query, parameters) as cursor:
            return await cursor.fetchone()