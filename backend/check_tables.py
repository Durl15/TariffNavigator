import aiosqlite
import asyncio

async def check():
    async with aiosqlite.connect('tariffnav.db') as db:
        cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = await cursor.fetchall()
        print('\nExisting tables:')
        for t in tables:
            print(f'  - {t[0]}')
        print()

asyncio.run(check())
