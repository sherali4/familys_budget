from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message
from bot import dp
# Agar `add_user` funksiyangiz alohida modulyatsiyalangan bo‘lsa
from database import add_user
from keyboards import main_menu  # `main_menu` tugmalar ro‘yxati

router = Router()  # Router obyektini yaratamiz


@router.message(Command("start"))
async def start_cmd(message: Message):
    await add_user(message.from_user.id, message.from_user.full_name)

    await message.answer_sticker(sticker="CAACAgQAAxkBAAEOKcpn5FJmmvvk7VqX-aBGBCTisy0TYgACKQEAAnsJYQABPNnybwy1VbQ2BA")

    await message.answer(
        "Assalomu alaykum! Oila_budjeti botiga xush kelibsiz!",
        reply_markup=main_menu
    )
