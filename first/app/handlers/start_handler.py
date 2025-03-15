from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from ..core import settings
from ..utils import get_thread
from aiogram.fsm.state import StatesGroup, State

start_router = Router()

class UserState(StatesGroup):
    thread_id = State()

@start_router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    thread_id = await get_thread(state)

    await state.update_data(thread_id=thread_id)
    await state.set_state(UserState.thread_id) 

    await message.answer(f"Ваш thread_id сохранен")

