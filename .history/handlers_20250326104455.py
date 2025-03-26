from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from database import add_user, get_user, add_transaction, get_transactions
from keyboards import main_menu, get_category_keyboard
from states import TransactionState
import datetime

router = Router()


@router.message(Command("start"))
async def start_cmd(message: Message):
    await add_user(message.from_user.id, message.from_user.full_name)
    await message.answer("Привет! Я бот для управления финансами. Выберите действие:", reply_markup=main_menu)


@router.message(F.text == "➕ Доход")
async def income_step_1(message: Message, state: FSMContext):
    await message.answer("Введите сумму дохода:")
    await state.set_state(TransactionState.amount)


@router.message(TransactionState.amount)
async def income_step_2(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        await state.update_data(amount=amount)
        await message.answer("Выберите категорию дохода:")
        await state.set_state(TransactionState.category)
    except ValueError:
        await message.answer("❌ Введите корректное число!")


@router.callback_query(F.data.startswith("category_"))
async def income_step_3(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split("_")[1]
    data = await state.get_data()
    amount = data["amount"]
    user = await get_user(callback.from_user.id)
    date = datetime.datetime.now().strftime("%Y-%m-%d")

    if user:
        await add_transaction(user[0], "income", amount, category, date)
        await callback.message.answer(f"✅ Доход {amount} {category} добавлен!", reply_markup=main_menu)
    await state.clear()
    await callback.answer()
