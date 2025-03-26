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
    """ buttons.append([InlineKeyboardButton(text="➕ Добавить", callback_data="add_category")])
    buttons.append([InlineKeyboardButton(text="✏ Изменить", callback_data="edit_category")])
    buttons.append([InlineKeyboardButton(text="❌ Удалить", callback_data="delete_category")]) """
    buttons.append([InlineKeyboardButton(
        text="🔙 Назад", callback_data="back_to_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@dp.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer("Привет! Выберите действие:", reply_markup=keyboard)


@dp.message(lambda message: message.text == "📂 Категории товаров")
async def show_categories(message: Message):
    await message.answer("Выберите категорию или действие:", reply_markup=get_category_keyboard())


@dp.callback_query(lambda callback: callback.data.startswith("category_"))
async def category_selected(callback: types.CallbackQuery):
    category_name = callback.data.split("_")[1]
    await callback.message.answer(f"Вы выбрали категорию: {category_name}", reply_markup=keyboard)
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

# ✏ Изменение категории


@dp.callback_query(lambda callback: callback.data == "edit_category")
async def edit_category_handler(callback: types.CallbackQuery):
    categories = get_categories()
    if not categories:
        await callback.message.answer("❌ Нет доступных категорий для изменения.")
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=cat, callback_data=f"edit_{cat}")] for cat in categories
        ]
    )

    await callback.message.answer("Выберите категорию для изменения:", reply_markup=keyboard)
    await callback.answer()


@dp.callback_query(lambda callback: callback.data.startswith("edit_"))
async def select_category_to_edit(callback: types.CallbackQuery, state: FSMContext):
    category_name = callback.data.split("edit_")[1]
    await state.update_data(old_category=category_name)
    await callback.message.answer(f"Введите новое название для категории '{category_name}':")
    await state.set_state(CategoryState.editing_new)
    await callback.answer()


@dp.message(CategoryState.editing_new)
async def process_new_category_name(message: Message, state: FSMContext):
    data = await state.get_data()
    old_category = data.get("old_category")

    new_category = message.text.strip()
    if not new_category:
        await message.answer("❌ Название категории не может быть пустым! Введите другое название:")
        return

    if new_category in get_categories():
        await message.answer(f"⚠ Категория '{new_category}' уже существует! Введите другое название:")
        return

    execute_query("UPDATE categories SET name = ? WHERE name = ?",
                  (new_category, old_category))
    await message.answer(f"✅ Категория '{old_category}' изменена на '{new_category}'!", reply_markup=get_category_keyboard())
    await state.clear()

# ❌ Удаление категории


@dp.callback_query(lambda callback: callback.data == "delete_category")
async def delete_category_handler(callback: types.CallbackQuery):
    categories = get_categories()
    if not categories:
        await callback.message.answer("❌ Нет категорий для удаления.")
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=cat, callback_data=f"del_{cat}")] for cat in categories
        ]
    )

    await callback.message.answer("Выберите категорию для удаления:", reply_markup=keyboard)
    await callback.answer()


@dp.callback_query(lambda callback: callback.data.startswith("del_"))
async def delete_selected_category(callback: types.CallbackQuery):
    category_name = callback.data.split("del_")[1]
    delete_category(category_name)
    await callback.message.answer(f"✅ Категория '{category_name}' удалена!", reply_markup=get_category_keyboard())
    await callback.answer()


@dp.callback_query(lambda callback: callback.data == "back_to_main")
async def back_to_main_menu(callback: types.CallbackQuery):
    await callback.message.answer("Возвращаемся в главное меню", reply_markup=keyboard)
    await callback.answer()


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
