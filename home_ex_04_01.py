import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile, CallbackQuery
import logging

from config import TOKEN
import home_ex_04_01_keyboards as kb

bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# При отправке команды /start бот будет показывать меню с кнопками "Привет" и "Пока".
# При нажатии на кнопку "Привет" бот должен отвечать "Привет, {имя пользователя}!",
# а при нажатии на кнопку "Пока" бот должен отвечать "До свидания, {имя пользователя}!".
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer('Выберите пункт меню', reply_markup=kb.start_menu)

@dp.message(F.text == "Привет")
async def hi(message: Message):
    await message.answer(f'Привет, {message.from_user.first_name}')

@dp.message(F.text == "Пока")
async def bye(message: Message):
    await message.answer(f'До свидания, {message.from_user.first_name}')


# При отправке команды /links бот будет показывать инлайн-кнопки с URL-ссылками.
# Создайте три кнопки с ссылками на новости/музыку/видео
@dp.message(Command('links'))
async def links(message: Message):
    await message.answer('выберите ссылку', reply_markup=kb.links_keyboard)


# При отправке команды /dynamic бот будет показывать инлайн-кнопку "Показать больше".
# При нажатии на эту кнопку бот должен заменять её на две новые кнопки "Опция 1" и "Опция 2".
# При нажатии на любую из этих кнопок бот должен отправлять сообщение с текстом выбранной опции.
@dp.message(Command('dynamic'))
async def dynamic(message: Message):
    await message.answer('dynamic', reply_markup=kb.dynamic_keyboard)

@dp.callback_query(F.data == 'show_more')
async def show_more(callback: CallbackQuery):
    await callback.message.edit_text('Выберите опцию', reply_markup=kb.show_more_keyboard)


@dp.callback_query(F.data == 'option_1')
async def option_1(callback: CallbackQuery):
    await callback.message.edit_text('Опция 1', reply_markup=kb.show_more_keyboard)


@dp.callback_query(F.data == 'option_2')
async def option_2(callback: CallbackQuery):
    await callback.message.edit_text('Опция 2', reply_markup=kb.show_more_keyboard)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
