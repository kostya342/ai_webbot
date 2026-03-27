import asyncio
import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from core import YandexAI
from dotenv import load_dotenv

load_dotenv()
bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher()
ai = YandexAI()

@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer("Привет! Я понимаю текст и голосовые сообщения.")

@dp.message(F.voice)
async def voice_handler(m: types.Message):
    # Скачиваем голосовое
    file = await bot.get_file(m.voice.file_id)
    content = await bot.download_file(file.file_path)
    
    # Распознаем через Яндекс
    text = ai.stt(content.read())
    if not text:
        await m.answer("Не удалось разобрать голос.")
        return
        
    res = ai.get_response(text)
    await m.answer(f"*(Вы сказали: {text})*\n\n{res}", parse_mode="Markdown")

@dp.message(F.text)
async def text_handler(m: types.Message):
    res = ai.get_response(m.text)
    await m.answer(res)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
