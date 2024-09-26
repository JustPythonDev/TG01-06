import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
import requests

from config import TOKEN, THE_DOG_API_KEY

bot = Bot(token=TOKEN)
dp = Dispatcher()

def get_dog_breeds():
   url = 'https://api.thedogapi.com/v1/breeds'
   headers = {'x-api-key': THE_DOG_API_KEY}
   response = requests.get(url, headers=headers)
   return response.json()


def get_dog_image_by_breed(breed_id):
   url = f'https://api.thedogapi.com/v1/images/search?breed_ids={breed_id}'
   headers = {'x-api-key': THE_DOG_API_KEY}
   response = requests.get(url, headers=headers)
   data = response.json()
   return data[0]['url']


def get_breed_info(breed_name):
   breeds = get_dog_breeds()
   for breed in breeds:
      if breed['name'].lower() == breed_name.lower():
         return breed


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer('Привет, напиши мне название породы собаки - и я пришлю ее фото и информацию о ней')


@dp.message()
async def send_dog_info(message: Message):
   breed_name = message.text
   breed_info = get_breed_info(breed_name)
   if breed_info:
      dog_image_url = get_dog_image_by_breed(breed_info['id'])
      info = (
         f"Порода: {breed_info['name']}\n"
         f"Выведено для: {breed_info['bred_for']}\n"
         f"Продолжительность жизни: {breed_info['life_span']} лет"
      )
      await message.answer_photo(photo=dog_image_url, caption=info)
   else:
      await message.answer("Порода не найдена. Попробуйте еще раз.")


async def main():
   await dp.start_polling(bot)

if __name__ == '__main__':
   asyncio.run(main())