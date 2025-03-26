import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from config import token

TOKEN = token
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Клавиатура с кнопками
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💰 Баланс"), KeyboardButton(text="➕ Доход")],
        [KeyboardButton(text="➖ Расход"), KeyboardButton(text="📦 Заказ")]
    ],
    resize_keyboard=True
)

# Функция для работы с БД


def execute_query(query, params=()):
    with sqlite3.connect("budget.db") as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor


# Создание таблиц
execute_query('''CREATE TABLE IF NOT EXISTS transactions (
                  id INTEGER PRIMARY KEY, type TEXT, amount REAL, category TEXT)''')
execute_query('''CREATE TABLE IF NOT EXISTS orders (
                  id INTEGER PRIMARY KEY, name TEXT, amount REAL, category TEXT)''')

# Функция для добавления транзакции


def add_transaction(trans_type, amount, category):
    execute_query("INSERT INTO transactions (type, amount, category) VALUES (?, ?, ?)",
                  (trans_type, amount, category))

# Функция для добавления заказа


def add_order(name, amount, category):
    execute_query("INSERT INTO orders (name, amount, category) VALUES (?, ?, ?)",
                  (name, amount, category))
    add_transaction("expense", amount, category)

# Получение текущего баланса


def get_balance():
    income = execute_query(
        "SELECT SUM(amount) FROM transactions WHERE type='income'").fetchone()[0] or 0
    expense = execute_query(
        "SELECT SUM(amount) FROM transactions WHERE type='expense'").fetchone()[0] or 0
    return income - expense


@dp.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer("Привет! Это бот для управления семейным бюджетом.\nВыберите действие ниже:", reply_markup=keyboard)


@dp.message(lambda message: message.text == "💰 Баланс")
async def show_balance(message: Message):
    balance = get_balance()
    await message.answer(f"💰 Текущий баланс: {balance} сум")


@dp.message(lambda message: message.text == "➕ Доход")
async def request_income(message: Message):
    await message.answer("Введите доход в формате: \n/income 100000 Зарплата")


@dp.message(lambda message: message.text == "➖ Расход")
async def request_expense(message: Message):
    await message.answer("Введите расход в формате: \n/expense 50000 Еда")


@dp.message(lambda message: message.text == "📦 Заказ")
async def request_order(message: Message):
    await message.answer("Введите заказ в формате: \n/order Товар 150000 Электроника")


@dp.message(Command("income"))
async def add_income(message: Message):
    parts = message.text.split(maxsplit=2)
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("❌ Используйте формат: /income 100000 Зарплата")
        return
    amount = float(parts[1])
    category = parts[2] if len(parts) > 2 else "Без категории"
    add_transaction("income", amount, category)
    await message.answer(f"✅ Доход {amount} сум добавлен в категорию {category}.")


@dp.message(Command("expense"))
async def add_expense(message: Message):
    parts = message.text.split(maxsplit=2)
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("❌ Используйте формат: /expense 50000 Еда")
        return
    amount = float(parts[1])
    category = parts[2] if len(parts) > 2 else "Без категории"
    add_transaction("expense", amount, category)
    await message.answer(f"❌ Расход {amount} сум добавлен в категорию {category}.")


@dp.message(Command("order"))
async def add_order_handler(message: Message):
    parts = message.text.split(maxsplit=3)
    if len(parts) < 3 or not parts[2].isdigit():
        await message.answer("❌ Используйте формат: /order Товар 150000 Электроника")
        return
    name = parts[1]
    amount = float(parts[2])
    category = parts[3] if len(parts) > 3 else "Без категории"
    add_order(name, amount, category)
    await message.answer(f"📦 Заказ '{name}' на сумму {amount} сум добавлен в категорию {category}.")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
