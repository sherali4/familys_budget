from aiogram.fsm.state import StatesGroup, State


class TransactionState(StatesGroup):
    amount = State()
    category = State()
    confirm = State()
