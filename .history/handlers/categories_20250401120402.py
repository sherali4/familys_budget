from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import aiosqlite
from keyboards import get_category_keyboard, get_category_selection_keyboard
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from itertools import zip_longest
from functions.emoji import Emojilar

router = Router()



class EditCategoryState(StatesGroup):
    waiting_for_new_category = State()


# FSM yaratamiz
class CategoryState(StatesGroup):
    waiting_for_category_name = State()


@router.message(F.text == "📜 Mahsulot turlari")
async def show_categories(message: Message):
    async with aiosqlite.connect("budget.db") as db:
        async with db.execute("SELECT mahsulot_turi_nomi, emoji FROM categories") as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                mahsulot_turi_nomi1, emoji1 = row
                # print(f"{emoji1}-{mahsulot_turi_nomi1}")
        async with db.execute("SELECT mahsulot_turi_nomi, emoji FROM prefixes") as cursor:
            prefix_data = await cursor.fetchall()

prefix_dict = {row[0].lower(): row[1] for row in prefix_data}

category_buttons = [
    InlineKeyboardButton(
        text=f"{prefix_dict.get(row[0].lower(), '')} {row[0]}",  # `lower()` bilan tekshirish
        callback_data=f"category_{row[0]}"
    ) for row in rows
]


    # 2 tadan tugmalarni joylashtirish
    category_keyboard = [list(filter(None, pair)) for pair in zip_longest(*[iter(category_buttons)]*3, fillvalue=None)]

    # Qo‘shimcha tugmalar (quyida alohida qator)
    category_keyboard.append([
        InlineKeyboardButton(text="➕ Qo‘shish", callback_data="add_category"),
        InlineKeyboardButton(text="✏️ O‘zgartirish", callback_data="edit_category"),
        InlineKeyboardButton(text="🗑 O‘chirish", callback_data="delete_category")
    ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=category_keyboard)

    await message.answer("Kategoriya tanlang:", reply_markup=keyboard)
####################################################################

# "➕ Qo‘shish" tugmasi bosilganda yangi kategoriya nomini so‘rash
@router.callback_query(F.data == "add_category")
async def ask_new_category(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()  # Eski ro‘yxatni o‘chirish
    await callback.message.answer("📝 Yangi kategoriya nomini kiriting:")
    await state.set_state(CategoryState.waiting_for_category_name)


# Foydalanuvchi yangi kategoriya nomini yuborganda, bazaga qo‘shish va ro‘yxatni yangilash
@router.message(CategoryState.waiting_for_category_name)
async def add_new_category(message: Message, state: FSMContext):
    category_name = message.text.strip()

    if not category_name:
        await message.answer("⚠️ Kategoriya nomi bo‘sh bo‘lishi mumkin emas. Qayta kiriting:")
        return

    async with aiosqlite.connect("budget.db") as db:
        # Takrorlanishni tekshirish
#################################TRANSLATOR##########################################################
        from deep_translator import GoogleTranslator
        import emoji
        translated = GoogleTranslator(source="uz", target="en").translate(category_name)
        # print(translated)
        translated = translated.lower()

        if Emojilar(category_name).topish():
            pass

        async with db.execute("SELECT COUNT(*) FROM prefixes WHERE mahsulot_turi_nomi = ?",
                              (category_name,)) as cursor:
            (exists,) = await cursor.fetchone()

        if exists > 0:
            pass
            # await message.answer(f"⚠️ '{category_name}' kategoriyasi allaqachon mavjud!")
        else:
            # Yangi kategoriya qo‘shish
            emoji_text = emoji.emojize(f":{translated}:", language="alias")

            # Emoji to‘g‘ri ishlayotganini tekshirish
            if emoji_text == f":{translated}:":
                emoji_text = "🔹"
            print(translated)
            if Emojilar(category_name).topish():
                print('emoji mavjud')
            else:
                await db.execute("INSERT INTO prefixes (mahsulot_turi_nomi, emoji) VALUES (?, ?)", (category_name, emoji_text))
            await db.commit()

#############################################################################################
        async with db.execute("SELECT COUNT(*) FROM categories WHERE mahsulot_turi_nomi = ?",
                              (category_name,)) as cursor:
            (exists,) = await cursor.fetchone()

        if exists > 0:
            await message.answer(f"⚠️ '{category_name}' kategoriyasi allaqachon mavjud!")
        else:
            # Yangi kategoriya qo‘shish
            if Emojilar(category_name).topish():
                await db.execute("INSERT INTO categories (mahsulot_turi_nomi, emoji) VALUES (?, ?)", (category_name, 1))
            else:
                await db.execute("INSERT INTO categories (mahsulot_turi_nomi, emoji) VALUES (?, ?)", (category_name, 0))
            await db.commit()

            # Eski ro‘yxatni o‘chirish
            await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)

            # Yangi ro‘yxatni chiqarish
            keyboard = await get_category_keyboard()
            await message.answer(f"✅ '{category_name}' kategoriyasi qo‘shildi!", reply_markup=keyboard)

    await state.clear()
######################################################################################


# "✏️ O‘zgartirish" tugmasi bosilganda eski kategoriyalar ro‘yxatini chiqarish
@router.callback_query(F.data == "edit_category")
async def ask_category_to_edit(callback: CallbackQuery):
    keyboard = await get_category_selection_keyboard()
    await callback.message.edit_text("🔄 Qaysi kategoriyani o‘zgartirmoqchisiz?", reply_markup=keyboard)


# Eski kategoriya tugmasi bosilganda yangi nomni so‘rash
@router.callback_query(F.data.startswith("edit_"))
async def ask_new_category_name(callback: CallbackQuery, state: FSMContext):
    old_category = callback.data.split("_", 1)[1]  # "edit_nomi" → "nomi"

    await state.update_data(old_category=old_category)
    await callback.message.edit_text(f"✍️ '{old_category}' o‘rniga yangi nomni kiriting:")
    await state.set_state(EditCategoryState.waiting_for_new_category)


# Foydalanuvchi yangi nomni kiritganda, bazada o‘zgartirish
@router.message(EditCategoryState.waiting_for_new_category)
async def edit_category_name(message: Message, state: FSMContext):
    new_category = message.text.strip()
    data = await state.get_data()
    old_category = data.get("old_category")

    async with aiosqlite.connect("budget.db") as db:
        # Yangi nom allaqachon mavjudligini tekshiramiz
        async with db.execute("SELECT COUNT(*) FROM categories WHERE mahsulot_turi_nomi = ?",
                              (new_category,)) as cursor:
            (exists,) = await cursor.fetchone()

        if exists > 0:
            await message.answer(f"⚠️ '{new_category}' nomli kategoriya allaqachon mavjud! Boshqa nom tanlang.")
            return

        # Nomni yangilaymiz
        await db.execute("UPDATE categories SET mahsulot_turi_nomi = ? WHERE mahsulot_turi_nomi = ?",
                         (new_category, old_category))
        await db.commit()

    # **Eski ro‘yxatni yangilab, tugmalar bilan qaytaramiz**
    keyboard = await get_category_keyboard()

    await message.answer(
        f"✅ '{old_category}' endi '{new_category}' deb o‘zgartirildi!\n\n📜 Yangilangan mahsulot turlari ro‘yxati:",
        reply_markup=keyboard)

    await state.clear()

######################################O'CHIRISH###########################################################


from itertools import zip_longest

@router.callback_query(F.data == "delete_category")
async def ask_category_to_delete(callback: CallbackQuery):
    async with aiosqlite.connect("budget.db") as db:
        async with db.execute("SELECT mahsulot_turi_nomi FROM categories") as cursor:
            rows = await cursor.fetchall()

    if not rows:
        await callback.message.answer("⚠️ Hech qanday kategoriya mavjud emas!")
        return

    # Kategoriya tugmalarini yaratish (faqat nomlar, hech qanday prefix yo‘q)
    category_buttons = [
        InlineKeyboardButton(text=row[0], callback_data=f"confirm_delete_{row[0]}")
        for row in rows
    ]

    # 3 ta ustunli formatga o'tkazish
    category_keyboard = [list(filter(None, group)) for group in zip_longest(*[iter(category_buttons)]*3, fillvalue=None)]

    # Bekor qilish tugmachasini qo‘shish
    category_keyboard.append([InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_delete")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=category_keyboard)

    await callback.message.edit_text("🗑 O‘chirmoqchi bo‘lgan kategoriyani tanlang:", reply_markup=keyboard)


@router.callback_query(F.data.startswith("confirm_delete_"))
async def confirm_delete_category(callback: CallbackQuery):
    category_name = callback.data.split("_", 2)[2]  # Kategoriya nomini ajratib olish

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Ha, o‘chirish", callback_data=f"delete_{category_name}")],
        [InlineKeyboardButton(text="❌ Yo‘q, bekor qilish", callback_data="cancel_delete")]
    ])

    await callback.message.edit_text(f"⚠️ '{category_name}' kategoriyasini o‘chirishni tasdiqlaysizmi?", reply_markup=keyboard)




@router.callback_query(F.data.startswith("delete_"))
async def delete_category(callback: CallbackQuery):
    category_name = callback.data.split("_", 1)[1]  # Kategoriya nomini ajratib olish

    async with aiosqlite.connect("budget.db") as db:
        await db.execute("DELETE FROM categories WHERE mahsulot_turi_nomi = ?", (category_name,))
        await db.commit()

    await callback.message.edit_text(f"✅ '{category_name}' kategoriyasi o‘chirildi.")

    # Yangi ro‘yxatni chiqarish
    keyboard = await get_category_keyboard()
    await callback.message.answer("📜 Yangilangan mahsulot turlari ro‘yxati:", reply_markup=keyboard)



@router.callback_query(F.data == "cancel_delete")
async def cancel_delete(callback: CallbackQuery):
    keyboard = await get_category_keyboard()
    await callback.message.edit_text("📜 Mahsulot turlari ro‘yxati:", reply_markup=keyboard)
