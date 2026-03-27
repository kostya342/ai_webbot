import os
import requests
import google.generativeai as genai
from google.generativeai.types import content_types
from dotenv import load_dotenv

load_dotenv()

class GeminiAI:
    def __init__(self):
        # 1. Настройка Gemini
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_key:
            raise ValueError("GEMINI_API_KEY не найден")
            
        genai.configure(api_key=self.gemini_key)
        
        # Инструкция для "умной колонки" и исправления формул
        self.instruction = (
            "Ты — умный голосовой помощник. Отвечай кратко и понятно. "
            "НИКОГДА не используй символы $ или $$ для формул. "
            "Пиши математику обычными буквами (например: x в квадрате плюс y равно 10)."
        )

        # Пытаемся подключить поиск с НОВЫМ названием инструмента
        try:
            # В новых версиях API инструмент называется 'google_search'
            tools = [ {'google_search': {}} ] 
            
            self.model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                tools=tools,
                system_instruction=self.instruction
            )
            # Проверка: создаем чат
            self.chat = self.model.start_chat(history=[])
        except Exception as e:
            print(f"Поиск не удалось подключить ({e}), запускаю чистую модель...")
            self.model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=self.instruction
            )
            self.chat = self.model.start_chat(history=[])

        # 2. Настройка Yandex TTS
        self.yandex_api_key = os.getenv("YANDEX_API_KEY")
        self.yandex_folder_id = os.getenv("YANDEX_FOLDER_ID")

    def get_response(self, user_text):
        """Получение текста с обработкой ошибок"""
        try:
            response = self.chat.send_message(user_text)
            return response.text
        except Exception as e:
            # Если чат сломался, пробуем одиночный запрос
            try:
                fallback = self.model.generate_content(user_text)
                return fallback.text
            except Exception as e2:
                return f"Ошибка Gemini: {str(e2)}. Проверь, включен ли VPN на сервере."

    def get_response_from_audio(self, audio_bytes, mime_type="audio/ogg"):
        """Понимание аудио (голоса) напрямую"""
        try:
            # Создаем структуру для передачи аудио
            audio_data = {
                "mime_type": mime_type,
                "data": audio_bytes
            }
            # Шлем аудио в модель
            response = self.model.generate_content([
                "Послушай и ответь на русском языке кратко.",
                audio_data
            ])
            return response.text
        except Exception as e:
            return f"Ошибка обработки аудио: {str(e)}"

    def synthesize_speech(self, text):
        """Озвучка текста через Яндекс (TTS)"""
        if not self.yandex_api_key or not self.yandex_folder_id:
            return None
        
        # Убираем всё, что мешает озвучке (Markdown знаки)
        clean_text = text.replace('*', '').replace('#', '').replace('`', '').strip()
        
        headers = {}
        if self.yandex_api_key.startswith('AQVN'):
            headers['Authorization'] = f'Bearer {self.yandex_api_key}'
        else:
            headers['Authorization'] = f'Api-Key {self.yandex_api_key}'
        
        try:
            response = requests.post(
                'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize',
                headers=headers,
                data={
                    'text': clean_text[:1500],
                    'lang': 'ru-RU',
                    'voice': 'jane',
                    'folderId': self.yandex_folder_id,
                    'format': 'mp3',
                    'speed': '1.0'
                }
            )
            if response.status_code == 200:
                return response.content
        except:
            pass
        return None

    def clear_history(self):
        self.chat = self.model.start_chat(history=[])
