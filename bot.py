import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from core import GeminiAI
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("Нет токена бота")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()
ai = GeminiAI()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я AI ассистент с доступом в интернет. Пиши текст или отправляй голосовые!")

@dp.message(Command("clear"))
async def cmd_clear(message: types.Message):
    ai.clear_history()
    await message.answer("История диалога очищена.")

# Обработка голосовых сообщений
@dp.message(F.voice)
async def handle_voice(message: types.Message):
    await bot.send_chat_action(message.chat.id, action="typing")
    try:
        # Скачиваем голосовое сообщение из ТГ
        file_id = message.voice.file_id
        file = await bot.get_file(file_id)
        downloaded_file = await bot.download_file(file.file_path)
        audio_bytes = downloaded_file.read()
        
        # Шлем в Gemini (Телега использует формат OGG)
        response_text = ai.get_response_from_audio(audio_bytes, mime_type="audio/ogg")
        await message.answer(response_text)
    except Exception as e:
        await message.answer(f"Не удалось распознать голос: {e}")

# Обработка текста
@dp.message(F.text)
async def handle_message(message: types.Message):
    await bot.send_chat_action(message.chat.id, action="typing")
    response_text = ai.get_response(message.text)
    await message.answer(response_text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
