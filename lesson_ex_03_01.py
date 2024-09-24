import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import aiohttp
import sqlite3
import logging

from config import TOKEN, OPEN_WEATHER_API

bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

class Form(StatesGroup):
    name = State()
    age = State()
    city = State()

def init_db():
    conn = sqlite3.connect('user_data.db')
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        id integer primary key autoincrement,
        name text not null,
        age integer not null,
        city text not null,
        chat_id integer not null
    )''')

    conn.commit()
    conn.close()


async def get_weather(city):
    async with aiohttp.ClientSession() as session:
        url = (f"https://api.openweathermap.org/data/2.5/weather?q={city}"
               f"&units=metric&lang=ru&appid={OPEN_WEATHER_API}")
        print(url)
        async with session.get(url) as response:
            if response.status == 200:
                weather_json = await response.json()
                temperature = weather_json['main']['temp']
                humidity = weather_json['main']['humidity']
                weather = weather_json['weather'][0]['description']

                weather_report = (f'Город {city}\n'
                                  f'Температура {temperature}\n'
                                  f'Влажность воздуха {humidity}\n'
                                  f'Описание погоды {weather}\n')
                return weather_report
            else:
                return 'Не удалось получить данные о погоде'


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer("Привет, как тебя зовут?")
    await state.set_state(Form.name)


@dp.message(Form.name)
async def name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет?")
    await state.set_state(Form.age)


@dp.message(Form.age)
async def age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Из какого ты города?")
    await state.set_state(Form.city)

@dp.message(Form.city)
async def city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    user_data = await state.get_data()

    chat_id = message.chat.id

    conn = sqlite3.connect('user_data.db')
    cur = conn.cursor()

    cur.execute('SELECT 1 FROM users WHERE chat_id = ?', (chat_id,))
    result = cur.fetchone()

    if not result:
        cur.execute('''
        insert into users (name, age, city, chat_id) values (?, ?, ?, ?)''',
                    (user_data['name'], user_data['age'], user_data['city'], chat_id))

        conn.commit()
    conn.close()

    weather_report = await get_weather(user_data['city'])
    await message.answer(weather_report)
    await state.clear()


@dp.message(Command('temperature'))
async def temperature(message: Message):
    conn = sqlite3.connect('user_data.db')
    cur = conn.cursor()

    cur.execute('SELECT city FROM users WHERE chat_id = ?', (message.chat.id,))
    result = cur.fetchone()
    city = ''
    if result:
        city = result[0]

    # Закрытие соединения
    conn.close()

    weather_report = await get_weather(city)
    await message.answer(weather_report)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    init_db()
    asyncio.run(main())
