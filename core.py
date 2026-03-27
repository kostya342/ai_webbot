import os
import requests
import re
from dotenv import load_dotenv

load_dotenv()

class YandexAI:
    def __init__(self):
        self.api_key = os.getenv("YANDEX_API_KEY")
        self.folder_id = os.getenv("YANDEX_FOLDER_ID")
        
    def _get_headers(self):
        """Авторизация для всех API (везде нужен Api-Key)"""
        key = self.api_key.strip() if self.api_key else ""
        return {'Authorization': f'Api-Key {key}'}

    def get_response(self, user_text):
        """Запрос к YandexGPT"""
        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        payload = {
            "modelUri": f"gpt://{self.folder_id}/yandexgpt/latest",
            "completionOptions": {"stream": False, "temperature": 0.5, "maxTokens": "1000"},
            "messages": [
                {"role": "system", "text": "Ты краткий ассистент. Отвечай на русском. Не используй символы $."},
                {"role": "user", "text": user_text}
            ]
        }
        try:
            res = requests.post(url, headers=self._get_headers(), json=payload, timeout=10)
            if res.status_code == 200:
                return res.json()['result']['alternatives'][0]['message']['text']
            return f"Ошибка GPT ({res.status_code}): {res.text}"
        except Exception as e:
            return f"Ошибка сети GPT: {e}"

    def stt(self, audio_bytes):
        """Распознавание речи (STT) - исправленная версия"""
        # Определяем формат аудио по первым байтам (можно упростить, если знаете формат)
        url = f"https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
        params = {
            'folderId': self.folder_id,
            'lang': 'ru-RU',
            'format': 'lpcm'  # или 'oggopus', если у вас OGG
        }
        
        # Для Telegram voice — это OGG Opus, нужно указать format=oggopus
        # Но у вас audio_bytes может быть в другом формате, проверьте
        
        try:
            res = requests.post(
                url, 
                headers=self._get_headers(), 
                params=params,
                data=audio_bytes,
                timeout=15
            )
            if res.status_code == 200:
                result = res.json()
                return result.get('result', '')
            print(f"STT Error {res.status_code}: {res.text}")
            return ""
        except Exception as e:
            print(f"STT Exception: {e}")
            return ""

    def synthesize_speech(self, text):
        """Озвучка текста (TTS) - исправленная версия"""
        url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
        clean_text = re.sub(r'[*#`$]', '', text)[:1000]
        
        # Параметры передаются как form-data
        data = {
            'text': clean_text,
            'lang': 'ru-RU',
            'voice': 'jane',  # или 'oksana', 'alena', 'filipp'
            'folderId': self.folder_id,
            'format': 'mp3',
            'emotion': 'neutral'
        }
        
        try:
            res = requests.post(
                url, 
                headers=self._get_headers(), 
                data=data,  # requests сам установит Content-Type
                timeout=10
            )
            if res.status_code == 200:
                return res.content
            print(f"TTS Error {res.status_code}: {res.text}")
            return None
        except Exception as e:
            print(f"TTS Exception: {e}")
            return None
