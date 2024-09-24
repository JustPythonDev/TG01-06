import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile, CallbackQuery

from config import TOKEN
import lesson_ex_04_01_keyboards as kb

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    # await message.answer(f'Приветики, {message.from_user.first_name}', reply_markup=kb.main)
    await message.answer(f'Приветики, {message.from_user.first_name}', reply_markup=kb.inline_keyboard)
    # await message.answer(f'Приветики, {message.from_user.first_name}', reply_markup=await kb.building_keyboard())


@dp.message(F.text == "кнопка 1") ## kb.building_keyboard()
async def test_button(message: Message):
   await message.answer('Обработка нажатия на reply кнопку 1')


@dp.callback_query(F.data == 'news') ## kb.inline_keyboard
async def news(callback: CallbackQuery):
   await callback.answer("Новости подгружаются", show_alert=True)
   await callback.message.answer('Вот свежие новости!')


@dp.callback_query(F.data == 'person') ## kb.inline_keyboard
async def news(callback: CallbackQuery):
   await callback.message.edit_text('Профиль клиента', reply_markup=await kb.building_inline_keyboard())

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
