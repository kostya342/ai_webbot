import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiAI:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_key:
            raise ValueError("GEMINI_API_KEY не найден")
            
        genai.configure(api_key=self.gemini_key)
        
        # Автоматический подбор модели
        self.model_name = self._get_available_model()
        print(f"Использую модель: {self.model_name}")

        # Пробуем инициализировать с поиском, если не выйдет — без него
        try:
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                tools=[{"google_search_retrieval": {}}], # Умный поиск
                system_instruction="Ты краткий ИИ-помощник. Не используй $ в формулах."
            )
            # Проверочный запрос для поиска
            self.chat = self.model.start_chat(history=[])
        except Exception:
            print("Поиск Google недоступен, запускаю без него...")
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction="Ты краткий ИИ-помощник. Не используй $ в формулах."
            )
            self.chat = self.model.start_chat(history=[])

        self.yandex_api_key = os.getenv("YANDEX_API_KEY")
        self.yandex_folder_id = os.getenv("YANDEX_FOLDER_ID")

    def _get_available_model(self):
        """Проверяет, какие модели доступны твоему ключу"""
        try:
            models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            # Приоритет выбора
            for preferred in ['models/gemini-1.5-flash', 'models/gemini-1.5-flash-latest', 'models/gemini-pro']:
                if preferred in models:
                    return preferred
            return models[0] if models else 'gemini-1.5-flash'
        except Exception:
            return 'gemini-1.5-flash' # Фоллбек

    def get_response(self, user_text):
        try:
            response = self.chat.send_message(user_text)
            return response.text
        except Exception as e:
            return f"Ошибка при ответе: {str(e)}"

    def get_response_from_audio(self, audio_bytes, mime_type="audio/ogg"):
        try:
            # Для аудио лучше использовать прямую генерацию
            response = self.model.generate_content([
                "Послушай и ответь кратко на русском.",
                {"mime_type": mime_type, "data": audio_bytes}
            ])
            return response.text
        except Exception as e:
            return f"Ошибка аудио: {str(e)}"

    def synthesize_speech(self, text):
        if not self.yandex_api_key or not self.yandex_folder_id:
            return None
        
        headers = {'Authorization': f'Api-Key {self.yandex_api_key}'} if not self.yandex_api_key.startswith('AQV') else {'Authorization': f'Bearer {self.yandex_api_key}'}
        
        try:
            res = requests.post(
                'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize',
                headers=headers,
                data={'text': text.replace('*', '')[:1000], 'lang': 'ru-RU', 'voice': 'jane', 'folderId': self.yandex_folder_id, 'format': 'mp3'}
            )
            return res.content if res.status_code == 200 else None
        except:
            return None

    def clear_history(self):
        self.chat = self.model.start_chat(history=[])
