import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
import requests
import random
from gtts import gTTS
import os
from googletrans import Translator

from config import TOKEN, OPEN_WEATHER_API

bot = Bot(token=TOKEN)
dp = Dispatcher()


def get_weather(city):
   api_key = OPEN_WEATHER_API
   url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&lang=ru&appid={api_key}"
   response = requests.get(url)
   return response.json()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Приветики, я бот!")


@dp.message(Command('help'))
async def help(message: Message):
    await message.answer("Этот бот умеет выполнять команды:\n/start\n/help\n/temperature")


@dp.message(Command('temperature'))
async def temperature(message: Message):
    weather_json = get_weather('Anapa')
    temperature = weather_json['main']['temp']
    weather = weather_json['weather'][0]['description']
    await message.answer(f"Погода в Анапе: {weather}. Температура: {temperature}")


@dp.message(F.photo)
async def react_photo(message: Message):
    answer_list = ['Ого, какая фотка!', 'Крутяк, сохраню!', 'Ты всегда прикольные картинки шлешь!']
    rand_answer = random.choice(answer_list)
    await message.answer(rand_answer)
    await bot.download(message.photo[-1], destination=f'img/{message.photo[-1].file_id}.jpg')


@dp.message(F.text.startswith('Скажи '))
async def send_voice(message: Message):
    file_name = "voice_msg.ogg"
    original_msg = message.text[len("Скажи "):]
    print(original_msg)
    tts = gTTS(text=original_msg, lang='ru')
    tts.save(file_name)
    voice_msg = FSInputFile(file_name)
    await bot.send_voice(chat_id=message.chat.id, voice=voice_msg)
    os.remove(file_name)

@dp.message(F.text.startswith('Переведи '))
async def send_voice(message: Message):
    translator = Translator()
    original_msg = message.text[len("Переведи "):]
    print(original_msg)
    translated_text = translator.translate(original_msg, dest='en')
    print(translated_text)
    await message.answer(translated_text)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
