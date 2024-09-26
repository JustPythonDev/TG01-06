import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram. filters import CommandStart, Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import sqlite3
import requests
import logging
import random

from config import TOKEN


bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

button_register = KeyboardButton(text="Регистрация в ТГ-боте")
button_exchange_rates = KeyboardButton(text="Курс валют")
button_tips = KeyboardButton(text="Советы по экономии")
button_finances = KeyboardButton(text="Личные финансы")

keyboard = ReplyKeyboardMarkup(keyboard=[
    [button_register, button_exchange_rates],
    [button_tips, button_finances]
], resize_keyboard=True)


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('user.db')
        self.cur = self.conn.cursor()

        self.cur.execute('''CREATE TABLE IF NOT EXISTS users (
            id integer primary key autoincrement,
            telegram_id integer not null unique,
            name text not null,
            category1 text,
            category2 text,
            category3 text,
            expenses1 real,
            expenses2 real,
            expenses3 real
        )''')

        self.conn.commit()


class FinancesForm(StatesGroup):
    category1 = State()
    category2 = State()
    category3 = State()
    expenses1 = State()
    expenses2 = State()
    expenses3 = State()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет! Я ваш личный финансовый помощник. Выберите одну из опций в меню:",
                         reply_markup=keyboard)


@dp.message(F.text == "Регистрация в ТГ-боте")
async def register(message: Message):
    telegram_id = message.from_user.id
    name = message.from_user.first_name

    db.cur.execute('''SELECT * FROM users WHERE telegram_id = ?''', (telegram_id,))
    user = db.cur.fetchone()
    if user:
        await message.answer("Вы уже зарегистрированы!")
    else:
        db.cur.execute('''INSERT INTO users (telegram_id, name) VALUES (?, ?)''', (telegram_id, name))
        db.conn.commit()
        await message.answer("Вы успешно зарегистрированы!")

@dp.message(F.text == "Курс валют")
async def exchange_rates(message: Message):
    url = "https://v6.exchangerate-api.com/v6/09edf8b2bb246e1f801cbfba/latest/USD"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code != 200:
            await message.answer("Не удалось получить данные о курсе валют!")
            return
        usd_to_rub = data["conversion_rates"]["RUB"]
        eur_to_usd = data["conversion_rates"]["EUR"]

        euro_to_rub = usd_to_rub / eur_to_usd

        await message.answer(f"1 USD - {usd_to_rub:.2f}  RUB\n"
                             f"1 EUR - {euro_to_rub:.2f}  RUB")
    except:
        await message.answer("Произошла ошибка")


@dp.message(F.text == "Советы по экономии")
async def tips(message: Message):
    tips = [
        "Совет 1: Ведите бюджет и следите за своими расходами.",
        "Совет 2: Откладывайте часть доходов на сбережения.",
        "Совет 3: Покупайте товары по скидкам и распродажам."
    ]
    tip = random.choice(tips)
    await message.answer(tip)


@dp.message(F.text == "Личные финансы")
async def finances(message: Message, state: FSMContext):
    await state.set_state(FinancesForm.category1)
    await message.reply("Введите первую категорию расходов")

@dp.message(FinancesForm.category1)
async def finances(message: Message, state: FSMContext):
    await state.update_data(category1=message.text)
    await state.set_state(FinancesForm.expenses1)
    await message.reply("Введите расходы для первой категории")

@dp.message(FinancesForm.expenses1)
async def finances(message: Message, state: FSMContext):
    await state.update_data(expenses1=float(message.text))
    await state.set_state(FinancesForm.category2)
    await message.reply("Введите вторую категорию расходов")

@dp.message(FinancesForm.category2)
async def finances(message: Message, state: FSMContext):
    await state.update_data(category2=message.text)
    await state.set_state(FinancesForm.expenses2)
    await message.reply("Введите расходы для второй категории")

@dp.message(FinancesForm.expenses2)
async def finances(message: Message, state: FSMContext):
    await state.update_data(expenses2=float(message.text))
    await state.set_state(FinancesForm.category3)
    await message.reply("Введите третью категорию расходов")

@dp.message(FinancesForm.category3)
async def finances(message: Message, state: FSMContext):
    await state.update_data(category3=message.text)
    await state.set_state(FinancesForm.expenses3)
    await message.reply("Введите расходы для третьей категории")

@dp.message(FinancesForm.expenses3)
async def finances(message: Message, state: FSMContext):
    data = await state.get_data()
    telegram_id = message.from_user.id
    db.cur.execute('''
    UPDATE users 
    SET category1 = ?, category2 = ?, category3 = ?,
        expenses1 = ?, expenses2 = ?, expenses3 = ?
    WHERE telegram_id = ?''', (
        data['category1'], data['category2'], data['category3'],
        data['expenses1'], data['expenses2'], float(message.text),
        telegram_id,))
    db.conn.commit()
    await state.clear()

    await message.answer('Категории и расходы сохранены')

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    db = Database()
    asyncio.run(main())