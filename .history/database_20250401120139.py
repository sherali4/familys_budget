import aiosqlite
from config import DB_NAME


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        # FOREIGN KEY qo‘llab-quvvatlashni yoqish
        await db.execute("PRAGMA foreign_keys = ON;")

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
                            FOREIGN KEY(user_id) REFERENCES users(telegram_id) ON DELETE CASCADE)''')

        await db.execute('''CREATE TABLE IF NOT EXISTS zakazlar (
                            id INTEGER PRIMARY KEY, 
                            user_id INTEGER, 
                            transaction_type TEXT,  -- type o‘rniga
                            amount REAL, 
                            category TEXT,
                            date TEXT,
                            FOREIGN KEY(user_id) REFERENCES users(telegram_id) ON DELETE CASCADE)''')

        await db.execute('''CREATE TABLE IF NOT EXISTS prefixes (
                            id INTEGER PRIMARY KEY, 
                            mahsulot_turi_nomi TEXT UNIQUE, 
                            emoji TEXT)''')

        await db.commit()


async def execute_query(query, params=()):
    async with aiosqlite.connect(DB_NAME) as db:
        # FOREIGN KEY cheklovlarini yoqish
        await db.execute("PRAGMA foreign_keys = ON;")
        cursor = await db.execute(query, params)
        await db.commit()
        return await cursor.fetchall()


async def add_user(telegram_id, name):
    await execute_query("INSERT OR IGNORE INTO users (telegram_id, name, role) VALUES (?, ?, ?)", (telegram_id, name, 0))


async def add_transaction(user_id, transaction_type, amount, category, date):
    await execute_query("INSERT INTO zakazlar (user_id, transaction_type, amount, category, date) VALUES (?, ?, ?, ?, ?)",
                        (user_id, transaction_type, amount, category, date))


async def get_user(telegram_id):
    result = await execute_query("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    return result[0] if result else None


async def get_transactions(user_id):
    return await execute_query("SELECT transaction_type, amount, category, date FROM zakazlar WHERE user_id = ?", (user_id,))
