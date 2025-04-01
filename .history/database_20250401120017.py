import aiosqlite
from config import DB_NAME


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY,
                            role INTEGER, 
                            telegram_id INTEGER UNIQUE, 
                            name TEXT)''')

        await db.execute('''CREATE TABLE IF NOT EXISTS categories (
                            id INTEGER PRIMARY KEY, 
                            mahsulot_turi_nomi TEXT, 
                            izoh TEXT,
                            user_id INTEGER,
                            emoji INTEGER,                         
                            FOREIGN KEY(user_id) REFERENCES users(telegram_id))''')

        await db.execute('''CREATE TABLE IF NOT EXISTS zakazlar (
                            id INTEGER PRIMARY KEY, 
                            user_id INTEGER, 
                            type TEXT, 
                            amount REAL, 
                            category TEXT,
                            date TEXT,
                            FOREIGN KEY(user_id) REFERENCES users(telegram_id))''')

        await db.execute('''CREATE TABLE IF NOT EXISTS prefixes (
                            id INTEGER PRIMARY KEY, 
                            mahsulot_turi_nomi TEXT UNIQUE, 
                            emoji TEXT)''')  # ✅ Xato tuzatildi

        await db.commit()


async def execute_query(query, params=()):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(query, params)
        await db.commit()
        return await cursor.fetchall()


async def add_user(telegram_id, name):
    await execute_query("INSERT OR IGNORE INTO users (telegram_id, name, role) VALUES (?, ?, ?)", (telegram_id, name, 0))


async def add_transaction(user_id, type, amount, category, date):
    await execute_query("INSERT INTO zakazlar (user_id, type, amount, category, date) VALUES (?, ?, ?, ?, ?)",
                        (user_id, type, amount, category, date))


async def get_user(telegram_id):
    result = await execute_query("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    return result[0] if result else None


async def get_transactions(user_id):
    return await execute_query("SELECT type, amount, category, date FROM zakazlar WHERE user_id = ?", (user_id,))

