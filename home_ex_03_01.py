import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import sqlite3
import logging

from config import TOKEN, OPEN_WEATHER_API

bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

class Form(StatesGroup):
    answer = State()
    name = State()
    age = State()
    grade = State()

def init_db():
    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS students (
        id integer primary key autoincrement,
        name text not null,
        age integer not null,
        grade text not null,
        chat_id integer not null
    )''')

    conn.commit()
    conn.close()


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):

    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()

    cur.execute('SELECT name, age, grade FROM students WHERE chat_id = ?', (message.chat.id,))
    result = cur.fetchone()

    if result:
        await message.answer(f"Привет, {result[0]}, тебе {result[1]} лет, ты в {result[2]} классе. Верно? (y/n)")
        await state.set_state(Form.answer)
    else:
        await message.answer("Привет, как тебя зовут?")
        await state.set_state(Form.name)


@dp.message(Form.answer)
async def answer(message: Message, state: FSMContext):
    if message.text not in ('y', 'Y'):
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
    await message.answer("В каком ты классе?")
    await state.set_state(Form.grade)


@dp.message(Form.grade)
async def grade(message: Message, state: FSMContext):
    await state.update_data(grade=message.text)
    user_data = await state.get_data()

    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()

    cur.execute('''
    delete from students where chat_id = ?''', (message.chat.id,))

    cur.execute('''
    insert into students (name, age, grade, chat_id) values (?, ?, ?, ?)''',
                (user_data['name'], user_data['age'], user_data['grade'], message.chat.id))

    conn.commit()
    conn.close()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    init_db()
    asyncio.run(main())
