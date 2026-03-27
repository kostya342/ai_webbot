import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class GeminiAI:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        # Используем стабильную версию v1beta или v1
        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        
        self.yandex_api_key = os.getenv("YANDEX_API_KEY")
        self.yandex_folder_id = os.getenv("YANDEX_FOLDER_ID")
        
        # История сообщений для контекста
        self.history = []

    def get_response(self, user_text):
        # Добавляем сообщение пользователя в историю
        self.history.append({"role": "user", "parts": [{"text": user_text}]})
        
        # Ограничиваем историю (последние 10 сообщений), чтобы не перегружать
        payload = {
            "contents": self.history[-10:],
            "system_instruction": {
                "parts": [{"text": "Ты краткий помощник. Не используй символы $ в формулах."}]
            }
        }
        
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(self.url, headers=headers, data=json.dumps(payload))
            result = response.json()
            
            if response.status_code == 200:
                # Достаем текст ответа
                bot_text = result['candidates'][0]['content']['parts'][0]['text']
                # Сохраняем ответ бота в историю
                self.history.append({"role": "model", "parts": [{"text": bot_text}]})
                return bot_text
            else:
                error_msg = result.get('error', {}).get('message', 'Unknown error')
                return f"Ошибка API ({response.status_code}): {error_msg}"
        except Exception as e:
            return f"Ошибка запроса: {str(e)}"

    def get_response_from_audio(self, audio_bytes, mime_type="audio/ogg"):
        # Для простоты: на сайте и в боте проще сначала получить текст, 
        # но Gemini поддерживает аудио через base64 в REST API.
        # Пока сделаем заглушку, чтобы проверить, работает ли хотя бы текст.
        return "Голосовой ввод временно недоступен, попробуй текст."

    def synthesize_speech(self, text):
        if not self.yandex_api_key or not self.yandex_folder_id:
            return None
        
        headers = {'Authorization': f'Api-Key {self.yandex_api_key}'} if not self.yandex_api_key.startswith('AQV') else {'Authorization': f'Bearer {self.yandex_api_key}'}
        
        try:
            res = requests.post(
                'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize',
                headers=headers,
                data={
                    'text': text.replace('*', '')[:1000],
                    'lang': 'ru-RU',
                    'voice': 'jane',
                    'folderId': self.yandex_folder_id,
                    'format': 'mp3'
                }
            )
            return res.content if res.status_code == 200 else None
        except:
            return None

    def clear_history(self):
        self.history = []
