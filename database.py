import aiosqlite

class Database:
    def __init__(self, db_path="database.db"):
        self.db_path = db_path
        self.conn = None

    async def connect(self):
        """Initialize the database connection"""
        self.conn = await aiosqlite.connect(self.db_path)
        await self.conn.execute("PRAGMA foreign_keys = ON;")
        await self.conn.commit()

    async def fetch(self, query, *args):
        """Fetch multiple rows from the database"""
        async with self.conn.execute(query, args) as cursor:
            return await cursor.fetchall()

    async def fetch_one(self, query, *args):
        """Fetch a single row from the database"""
        async with self.conn.execute(query, args) as cursor:
            return await cursor.fetchone()

    async def execute(self, query, *args):
        """Execute a query that modifies the database (INSERT, UPDATE, DELETE)"""
        await self.conn.execute(query, args)
        await self.conn.commit()

    async def close(self):
        """Close the database connection"""
        await self.conn.close()

db = Database()
