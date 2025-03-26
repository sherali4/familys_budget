import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import token

TOKEN = token
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Определение состояний для FSM


class CategoryState(StatesGroup):
    adding = State()
    editing_new = State()
    deleting = State()


# Обычная клавиатура с основными кнопками
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💰 Баланс"), KeyboardButton(text="➕ Доход")],
        [KeyboardButton(text="➖ Расход"), KeyboardButton(text="📦 Заказ")],
        [KeyboardButton(text="📂 Категории товаров")]
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
execute_query('''CREATE TABLE IF NOT EXISTS categories (
                  id INTEGER PRIMARY KEY, name TEXT UNIQUE)''')

# Функции для работы с категориями


def add_category(name):
    execute_query("INSERT INTO categories (name) VALUES (?)", (name,))


def delete_category(name):
    execute_query("DELETE FROM categories WHERE name = ?", (name,))


def get_categories():
    return [row[0] for row in execute_query("SELECT name FROM categories").fetchall() if row[0] is not None]

# Инлайн-клавиатура для категорий товаров


def get_category_keyboard():
    categories = get_categories()
    buttons = [
        [InlineKeyboardButton(text=cat, callback_data=f"category_{cat}")]
        for cat in categories if cat
    ]
    buttons.append([InlineKeyboardButton(
        text="➕ Добавить категорию", callback_data="add_category")])
    buttons.append([InlineKeyboardButton(
        text="🔙 Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@dp.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer("Привет! Это бот для управления семейным бюджетом.\nВыберите действие ниже:", reply_markup=keyboard)


@dp.message(lambda message: message.text == "📂 Категории товаров")
async def show_categories(message: Message):
    await message.answer("Выберите категорию товара или управление категориями:", reply_markup=get_category_keyboard())


@dp.callback_query(lambda callback: callback.data.startswith("category_"))
async def category_selected(callback: types.CallbackQuery):
    category_name = callback.data.split("_")[1]
    await callback.message.answer(f"Вы выбрали категорию: {category_name}")
    await callback.answer()

# 🔹 Добавление категории


@dp.callback_query(lambda callback: callback.data == "add_category")
async def add_category_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название новой категории:")
    await state.set_state(CategoryState.adding)
    await callback.answer()


@dp.message(CategoryState.adding)
async def process_new_category(message: Message, state: FSMContext):
    category_name = message.text.strip()
    if not category_name:
        await message.answer("❌ Название категории не может быть пустым! Введите другое название:")
        return
    if category_name in get_categories():
        await message.answer(f"⚠ Категория '{category_name}' уже существует! Введите другое название:")
        return
    add_category(category_name)
    await message.answer(f"✅ Категория '{category_name}' добавлена!", reply_markup=get_category_keyboard())
    await state.clear()


@dp.callback_query(lambda callback: callback.data == "back_to_main")
async def back_to_main_menu(callback: types.CallbackQuery):
    await callback.message.answer("Возвращаемся в главное меню", reply_markup=keyboard)
    await callback.answer()


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
