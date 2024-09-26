import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import requests
import logging

from config import TOKEN, NASA_API_KEY

bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)


class Form(StatesGroup):
    card = State()


class Deck:
    def __init__(self, selected_card: str):
        self.deck_id = self.shuffle_deck()
        if self.check_ru_card(selected_card):
            self.selected_card = selected_card

        self.right_row = []
        self.left_row = []

    def check_ru_card(self, card):
        value = card[:-1]  # Все символы, кроме последнего
        suit = card[-1]  # Последний символ

        if isinstance(value, int) and value >= 2 and value <= 10:
            return True

        if value.upper() in ('В', 'Д', 'К', 'Т'):
            return True

        if suit.upper() in ('П', 'Т', 'Б', 'Ч'):
            return True

        return False

    def shuffle_deck(self):
       url = "https://deckofcardsapi.com/api/deck/new/shuffle"
       deck_id = requests.get(url).json()['deck_id']
       print(deck_id)
       return deck_id

    def get_pair_from_deck(self):
        url = f"https://deckofcardsapi.com/api/deck/{self.deck_id}/draw/?count=2"
        response = requests.get(url)
        return response.json()

    def translate_card(self, value, suit):
        dict_values = {
                '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', '9': '9', '10': '10',
                'JACK': 'В', 'QUEEN': 'Д', 'KING': 'К', 'ACE': 'Т'
            }

        dict_suites = {
            'SPADES': 'П',  # Spades -> Пики
            'CLUBS': 'Т',  # Clubs -> Трефы
            'DIAMONDS': 'Б',  # Diamonds -> Бубны
            'HEARTS': 'Ч'  # Hearts -> Червы
        }
        ru_value = dict_values.get(value.upper())
        if not ru_value:
            return None

        ru_suit = dict_suites.get(suit.upper())
        if not ru_suit:
            return None

        return ru_value + ru_suit

    def check_pair_from_deck(self):
        image_url = None
        banker_is_winning = None

        pair_of_cards = self.get_pair_from_deck()
        right_card_info = pair_of_cards['cards'][0]
        right_card = self.translate_card(right_card_info['value'], right_card_info['suit'])
        self.right_row.append(right_card)
        if right_card == self.selected_card:
            image_url = right_card_info['image']
            banker_is_winning = True
        else:
            left_card_info = pair_of_cards['cards'][1]
            left_card = self.translate_card(left_card_info['value'], left_card_info['suit'])
            self.left_row.append(left_card)

            if left_card == self.selected_card:
                image_url = left_card_info['image']
                banker_is_winning = False

        return banker_is_winning, image_url


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(text='Этот бот умеет играть в старинную карточную игру "Фараон"\n'
             'Правила простые: Понтёр (игрок) называет карту.\n'
             'Банкомёт начинает промётывать свою колоду направо и налево.\n'
             'Если карта понтёра легла НАЛЕВО от банкомёта, то выиграл Понтёр, если НАПРАВО — то Банкомёт.\n'
             'Для начала игры введите команду /game')


@dp.message(Command("game"))
async def game(message: Message, state: FSMContext):
    print(game)
    await message.answer(text="Введите название карты, на которую делаете ставку,\n"
                             "в формате: номинал(2-10/В-Т)масть(П/Т/Ч/Б)\n"
                             "Примеры: ВЧ, 9П")
    await state.set_state(Form.card)


@dp.message(Form.card)
async def name(message: Message, state: FSMContext):
    card = message.text
    deck = Deck(card)
    if deck.selected_card is None:
        await message.answer(f"Ошибка ввода")
        await state.set_state(Form.card)
        return

    banker_is_winning = None
    while banker_is_winning is None:
        banker_is_winning, image_url = deck.check_pair_from_deck()

    await message.answer_photo(photo=image_url,
            caption=f"На раздаче № {len(deck.right_row)} этом раунде победил {'Банкомёт' if banker_is_winning else 'Понтёр'}")
    await message.answer(f"Карты Банкомёта: {', '.join(deck.right_row)}")
    await message.answer(f"Карты Понтёра: {', '.join(deck.left_row)}")


async def main():
   await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())