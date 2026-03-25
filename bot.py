import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from core import YandexAI
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("Нет токена бота")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()
ai = YandexAI()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я AI ассистент. Задавай вопросы.")

@dp.message(Command("clear"))
async def cmd_clear(message: types.Message):
    ai.clear_history()
    await message.answer("История очищена.")

@dp.message()
async def handle_message(message: types.Message):
    if not message.text:
        return
    
    await bot.send_chat_action(message.chat.id, action="typing")
    response_text = ai.get_response(message.text)
    await message.answer(response_text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())