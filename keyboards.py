from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💰 Баланс"), KeyboardButton(
            text="➕ Доход"), KeyboardButton(text="➖ Расход")],
        [KeyboardButton(text="📊 Отчёт"), KeyboardButton(text="📂 Категории")]
    ], resize_keyboard=True
)


async def get_category_keyboard(categories):
    buttons = [[InlineKeyboardButton(
        text=cat, callback_data=f"category_{cat}")] for cat in categories]
    buttons.append([InlineKeyboardButton(
        text="➕ Добавить категорию", callback_data="add_category")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
