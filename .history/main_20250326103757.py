import asyncio
import aiosqlite
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from config import token

# Инициализация бота и диспетчера
TOKEN = token
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Состояния FSM


class CategoryState(StatesGroup):
    adding = State()


# Клавиатура главного меню
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💰 Баланс"), KeyboardButton(text="➕ Доход")],
        [KeyboardButton(text="➖ Расход"), KeyboardButton(text="📦 Заказ")],
        [KeyboardButton(text="📂 Категории товаров")]
    ],
    resize_keyboard=True
)

# Асинхронная работа с БД


async def execute_query(query, params=()):
    async with aiosqlite.connect("budget.db") as db:
        cursor = await db.execute(query, params)
        await db.commit()
        return await cursor.fetchall()

# Создание таблиц


async def init_db():
    await execute_query('''CREATE TABLE IF NOT EXISTS transactions (
                            id INTEGER PRIMARY KEY, type TEXT, amount REAL, category TEXT)''')
    await execute_query('''CREATE TABLE IF NOT EXISTS orders (
                            id INTEGER PRIMARY KEY, name TEXT, amount REAL, category TEXT)''')
    await execute_query('''CREATE TABLE IF NOT EXISTS categories (
                            id INTEGER PRIMARY KEY, name TEXT UNIQUE)''')

# Функции для работы с категориями


async def add_category(name):
    try:
        await execute_query("INSERT INTO categories (name) VALUES (?)", (name,))
        return True
    except Exception:
        return False


async def get_categories():
    rows = await execute_query("SELECT name FROM categories")
    return [row[0] for row in rows if row[0] is not None]

# Инлайн-клавиатура категорий


async def get_category_keyboard():
    categories = await get_categories()
    buttons = [
        [InlineKeyboardButton(text=cat, callback_data=f"category_{cat}")]
        for cat in categories if cat
    ]
    buttons.append([InlineKeyboardButton(
        text="➕ Добавить категорию", callback_data="add_category")])
    buttons.append([InlineKeyboardButton(
        text="🔙 Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Команда /start


@dp.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer("Привет! Это бот для управления семейным бюджетом.\nВыберите действие:", reply_markup=keyboard)

# Кнопка "Категории товаров"


@dp.message(F.text == "📂 Категории товаров")
async def show_categories(message: Message):
    keyboard = await get_category_keyboard()
    await message.answer("Выберите категорию товара:", reply_markup=keyboard)

# Выбор категории


@dp.callback_query(F.data.startswith("category_"))
async def category_selected(callback: types.CallbackQuery):
    category_name = callback.data.split("_", 1)[1]
    await callback.message.answer(f"Вы выбрали категорию: {category_name}")
    await callback.answer()

# Добавление категории


@dp.callback_query(F.data == "add_category")
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

    categories = await get_categories()
    if category_name in categories:
        await message.answer(f"⚠ Категория '{category_name}' уже существует! Введите другое название:")
        return

    if await add_category(category_name):
        keyboard = await get_category_keyboard()
        await message.answer(f"✅ Категория '{category_name}' добавлена!", reply_markup=keyboard)
    else:
        await message.answer("❌ Ошибка при добавлении категории!")

    await state.clear()

# Возврат в главное меню


@dp.callback_query(F.data == "back_to_main")
async def back_to_main_menu(callback: types.CallbackQuery):
    await callback.message.answer("Возвращаемся в главное меню", reply_markup=keyboard)
    await callback.answer()

# Запуск бота


async def main():
    await init_db()  # Инициализация БД перед запуском
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
