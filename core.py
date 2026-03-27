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
        """Единый метод авторизации для всех сервисов"""
        key = self.api_key.strip() if self.api_key else ""
        if key.startswith('AQVN'):
            return {'Authorization': f'Bearer {key}'}
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
        """Распознавание речи (STT)"""
        url = f"https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?folderId={self.folder_id}&lang=ru-RU"
        try:
            res = requests.post(url, headers=self._get_headers(), data=audio_bytes, timeout=15)
            if res.status_code == 200:
                return res.json().get('result', '')
            print(f"STT Error {res.status_code}: {res.text}")
            return ""
        except Exception as e:
            print(f"STT Exception: {e}")
            return ""

    def synthesize_speech(self, text):
        """Озвучка текста (TTS)"""
        url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
        clean_text = re.sub(r'[*#`$]', '', text)[:1000]
        data = {
            'text': clean_text,
            'lang': 'ru-RU',
            'voice': 'jane',
            'folderId': self.folder_id,
            'format': 'mp3'
        }
        try:
            res = requests.post(url, headers=self._get_headers(), data=data, timeout=10)
            if res.status_code == 200:
                return res.content
            return None
        except:
            return None
