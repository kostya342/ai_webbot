import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiAI:
    def __init__(self):
        # Инициализация Gemini
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_key:
            raise ValueError("Нет ключа GEMINI_API_KEY в .env")
            
        genai.configure(api_key=self.gemini_key)
        
        # Включаем поиск Google и настраиваем промпт от багов с формулами
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            tools=[{"google_search_retrieval": {}}],
            system_instruction=(
                "Ты умный и полезный ИИ-ассистент. "
                "ВАЖНО: Никогда не используй символы $ или $$ для математических формул. "
                "Пиши математику обычным текстом, например: x^2 + y = z. "
                "Твои ответы читают в Telegram, избегай сложной разметки, которая ломает парсер."
            )
        )
        self.chat = self.model.start_chat(history=[])
        
        # Данные Яндекса для озвучки (TTS)
        self.yandex_api_key = os.getenv("YANDEX_API_KEY")
        self.yandex_folder_id = os.getenv("YANDEX_FOLDER_ID")

    def get_response(self, user_text):
        try:
            response = self.chat.send_message(user_text)
            return response.text
        except Exception as e:
            return f"Ошибка Gemini: {str(e)}"

    def get_response_from_audio(self, audio_bytes, mime_type="audio/ogg"):
        # Нейронка слушает аудио напрямую!
        try:
            prompt = "Послушай это аудио и ответь на вопрос или выполни просьбу."
            audio_part = {"mime_type": mime_type, "data": audio_bytes}
            response = self.chat.send_message([prompt, audio_part])
            return response.text
        except Exception as e:
            return f"Ошибка обработки аудио: {str(e)}"

    def clear_history(self):
        self.chat = self.model.start_chat(history=[])

    def synthesize_speech(self, text):
        if not self.yandex_api_key or not self.yandex_folder_id:
            return None
            
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        if self.yandex_api_key.startswith('Api-Key') or self.yandex_api_key.startswith('Bearer'):
             headers['Authorization'] = self.yandex_api_key
        else:
             headers['Authorization'] = f'Api-Key {self.yandex_api_key}'
        
        # Чистим текст от звездочек Markdown, чтобы Яндекс не спотыкался
        clean_text = text.replace('*', '').replace('#', '').strip()[:1500]
        
        try:
            response = requests.post(
                'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize',
                headers=headers,
                data={
                    'text': clean_text,
                    'lang': 'ru-RU',
                    'voice': 'jane',
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
