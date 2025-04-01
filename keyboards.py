from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import aiosqlite

# 📌 Asosiy Reply Keyboard (foydalanuvchi uchun)
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='💰 Balans')],
        [KeyboardButton(text='🛍️ Buyurtma'), KeyboardButton(text='⏳ Xarajat')],
        [KeyboardButton(text='📜 Mahsulot turlari')]
    ], resize_keyboard=True
)


main_menu2 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='💰 Balans', callback_data='balance')],
        [InlineKeyboardButton(text='🛍️ Buyurtma', callback_data='order'),
         InlineKeyboardButton(text='⏳ Xarajat', callback_data='expenses')],
        [InlineKeyboardButton(text='📜 Mahsulot turlari',
                              callback_data='product_types')]
    ]
)

main_menu1 = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💰 Баланс")],
        [KeyboardButton(text="➕ Доход"), KeyboardButton(text="➖ Расход")],
        [KeyboardButton(text="📊 Отчёт"), KeyboardButton(text="🛒📂 Категории")]
    ], resize_keyboard=True
)


# 📌 Mahsulot kategoriyalari tugmalari
async def get_category_keyboard():
    buttons = []
    async with aiosqlite.connect("budget.db") as db:
        async with db.execute("SELECT mahsulot_turi_nomi FROM categories") as cursor:
            buttons = [InlineKeyboardButton(text=row[0], callback_data=f"category_{row[0]}") async for row in cursor]

    # Tugmalarni 2 tadan chiqarish
    inline_buttons = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]

    # Qo‘shimcha tugmalarni pastga joylashtirish
    inline_buttons.append([
        InlineKeyboardButton(text="➕ Qo‘shish", callback_data="add_category"),
        InlineKeyboardButton(text="✏️ O‘zgartirish",
                             callback_data="edit_category"),
        InlineKeyboardButton(text="🗑 O‘chirish",
                             callback_data="delete_category")
    ])

    return InlineKeyboardMarkup(inline_keyboard=inline_buttons)


# 📌 Tahrirlash uchun kategoriya tanlash klaviaturasi
# 📌 Tahrirlash uchun kategoriya tanlash klaviaturasi
async def get_category_selection_keyboard():
    buttons = []
    async with aiosqlite.connect("budget.db") as db:
        async with db.execute("SELECT mahsulot_turi_nomi FROM categories") as cursor:
            buttons = [InlineKeyboardButton(text=row[0], callback_data=f"edit_{row[0]}") async for row in cursor]

    inline_buttons = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]

    return InlineKeyboardMarkup(inline_keyboard=inline_buttons)
