import os
import requests
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiAI:
    def __init__(self):
        # 1. Настройка Gemini
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_key:
            raise ValueError("Ошибка: GEMINI_API_KEY не найден в .env")
        
        genai.configure(api_key=self.gemini_key)
        
        # Системная инструкция, чтобы бот не ломал Телеграм формулами и был "умной колонкой"
        self.instruction = (
            "Ты — умный помощник. Отвечай кратко, как умная колонка. "
            "ВАЖНО: Никогда не используй символы $ или $$ для формул. "
            "Пиши математику простым текстом (например, x^2 + y = 10). "
            "Для списков используй обычные дефисы."
        )

        # Инициализация модели с поддержкой поиска Google
        # Используем 'gemini-1.5-flash-latest' для обхода ошибки 404
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-latest",
            tools=[{"google_search_retrieval": {}}], # Включаем умный поиск
            system_instruction=self.instruction
        )
        
        # Создаем чат-сессию
        self.chat = self.model.start_chat(history=[])

        # 2. Настройка Yandex TTS (оставляем твою логику)
        self.yandex_api_key = os.getenv("YANDEX_API_KEY")
        self.yandex_folder_id = os.getenv("YANDEX_FOLDER_ID")

    def get_response(self, user_text):
        """Получает текстовый ответ от Gemini"""
        try:
            # Отправляем сообщение в чат
            response = self.chat.send_message(user_text)
            return response.text
        except Exception as e:
            # Если всё же вылетает 404, пробуем метод без истории (как запасной)
            try:
                fallback_res = self.model.generate_content(user_text)
                return fallback_res.text
            except Exception as e2:
                return f"Ошибка Gemini: {str(e2)}"

    def get_response_from_audio(self, audio_bytes, mime_type="audio/ogg"):
        """Обработка аудио напрямую нейронкой (без Vosk)"""
        try:
            # Gemini сама умеет слушать байты аудио
            audio_part = {
                "mime_type": mime_type,
                "data": audio_bytes
            }
            prompt = "Послушай и ответь на русском языке."
            response = self.model.generate_content([prompt, audio_part])
            
            # Добавляем ответ в историю чата вручную, чтобы контекст сохранялся
            return response.text
        except Exception as e:
            return f"Ошибка распознавания аудио: {str(e)}"

    def synthesize_speech(self, text):
        """Озвучка текста через Yandex SpeechKit"""
        if not self.yandex_api_key or not self.yandex_folder_id:
            return None
        
        # Очистка текста от символов разметки, чтобы голос не "читал" звездочки
        clean_text = text.replace('*', '').replace('#', '').replace('`', '')
        clean_text = clean_text[:1500] # Ограничение Yandex TTS
        
        headers = {}
        if self.yandex_api_key.startswith('AQVN'): # Если это IAM-токен
            headers['Authorization'] = f'Bearer {self.yandex_api_key}'
        else: # Если это API-ключ
            headers['Authorization'] = f'Api-Key {self.yandex_api_key}'
        
        try:
            response = requests.post(
                'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize',
                headers=headers,
                data={
                    'text': clean_text,
                    'lang': 'ru-RU',
                    'voice': 'jane', # Можно сменить на 'filipp'
                    'folderId': self.yandex_folder_id,
                    'format': 'mp3',
                    'speed': '1.0'
                }
            )
            if response.status_code == 200:
                return response.content
        except Exception:
            pass
        return None

    def clear_history(self):
        """Очистка памяти диалога"""
        self.chat = self.model.start_chat(history=[])
