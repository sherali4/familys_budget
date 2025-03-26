import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = "YOUR_BOT_TOKEN"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Создание БД
conn = sqlite3.connect("budget.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                  id INTEGER PRIMARY KEY, type TEXT, amount REAL, category TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                  id INTEGER PRIMARY KEY, name TEXT, amount REAL, category TEXT)''')
conn.commit()

# Функция для добавления транзакции
def add_transaction(trans_type, amount, category):
    cursor.execute("INSERT INTO transactions (type, amount, category) VALUES (?, ?, ?)",
                   (trans_type, amount, category))
    conn.commit()

# Функция для добавления заказа
def add_order(name, amount, category):
    cursor.execute("INSERT INTO orders (name, amount, category) VALUES (?, ?, ?)",
                   (name, amount, category))
    conn.commit()
    add_transaction("expense", amount, category)  # Заказ уменьшает баланс

# Получение текущего баланса
def get_balance():
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='income'")
    income = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='expense'")
    expense = cursor.fetchone()[0] or 0
    return income - expense

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Привет! Это бот для управления семейным бюджетом.\nИспользуй /income, /expense и /order для управления финансами.")

@dp.message(Command("income"))
async def add_income(message: types.Message):
    try:
        parts = message.text.split()
        amount = float(parts[1])
        category = parts[2] if len(parts) > 2 else "Без категории"
        add_transaction("income", amount, category)
        await message.answer(f"✅ Доход {amount} сум добавлен в категорию {category}.")
    except:
        await message.answer("❌ Используйте формат: /income 100000 Зарплата")

@dp.message(Command("expense"))
async def add_expense(message: types.Message):
    try:
        parts = message.text.split()
        amount = float(parts[1])
        category = parts[2] if len(parts) > 2 else "Без категории"
        add_transaction("expense", amount, category)
        await message.answer(f"❌ Расход {amount} сум добавлен в категорию {category}.")
    except:
        await message.answer("❌ Используйте формат: /expense 50000 Еда")

@dp.message(Command("order"))
async def add_order_handler(message: types.Message):
    try:
        parts = message.text.split()
        name = parts[1]
        amount = float(parts[2])
        category = parts[3] if len(parts) > 3 else "Без категории"
        add_order(name, amount, category)
        await message.answer(f"📦 Заказ '{name}' на сумму {amount} сум добавлен в категорию {category}.")
    except:
        await message.answer("❌ Используйте формат: /order Товар 150000 Электроника")

@dp.message(Command("balance"))
async def show_balance(message: types.Message):
    balance = get_balance()
    await message.answer(f"💰 Текущий баланс: {balance} сум")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
