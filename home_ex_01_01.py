import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import requests
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

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
