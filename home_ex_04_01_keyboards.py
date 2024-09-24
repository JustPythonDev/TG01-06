from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

start_menu = ReplyKeyboardMarkup(keyboard=[
   [KeyboardButton(text="Привет"), KeyboardButton(text="Пока")]
], resize_keyboard=True)


links_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="Новости", url='https://lenta.ru/')],
   [InlineKeyboardButton(text="Музыка", url='https://music.yandex.ru/home')],
   [InlineKeyboardButton(text="Видео", url='https://rutube.ru/')]
])

dynamic_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="Показать больше", callback_data='show_more')]
])

show_more_keyboard = InlineKeyboardMarkup(inline_keyboard=[
   [InlineKeyboardButton(text="Опция 1", callback_data='option_1')],
   [InlineKeyboardButton(text="Опция 2", callback_data='option_2')]
])
