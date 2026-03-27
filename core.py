import os
import requests
import re
import json
from dotenv import load_dotenv

load_dotenv()

class YandexAI:
    def __init__(self):
        self.api_key = os.getenv("YANDEX_API_KEY")
        self.folder_id = os.getenv("YANDEX_FOLDER_ID")
        self.messages = []
        # Умный поиск включается через промпт или спец. поле API (зависит от версии)
        self.system_text = "Ты умный помощник. Отвечай кратко. Не используй $ для формул. Если нужно, ищи информацию в интернете."

    def get_auth_header(self):
        if self.api_key.startswith('AQVN'): # IAM-токен
            return {'Authorization': f'Bearer {self.api_key}'}
        return {'Authorization': f'Api-Key {self.api_key}'} # API-ключ

    def get_response(self, user_text):
        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        payload = {
            "modelUri": f"gpt://{self.folder_id}/yandexgpt/latest",
            "completionOptions": {"stream": False, "temperature": 0.3, "maxTokens": "2000"},
            "messages": [
                {"role": "system", "text": self.system_text},
                {"role": "user", "text": user_text}
            ]
        }
        try:
            res = requests.post(url, headers=self.get_auth_header(), json=payload)
            if res.status_code == 200:
                return res.json()['result']['alternatives'][0]['message']['text']
            return f"Ошибка YandexGPT: {res.status_code}"
        except Exception as e:
            return f"Ошибка связи: {e}"

    def stt(self, audio_bytes):
        """Распознавание речи (вместо Vosk)"""
        url = f"https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?folderId={self.folder_id}&lang=ru-RU"
        try:
            res = requests.post(url, headers=self.get_auth_header(), data=audio_bytes)
            if res.status_code == 200:
                return res.json().get('result', '')
        except:
            pass
        return ""

    def synthesize_speech(self, text):
        """Озвучка текста"""
        clean_text = re.sub(r'[*#`]', '', text).replace('$', '')[:1000]
        url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
        try:
            res = requests.post(url, headers=self.get_auth_header(), data={
                'text': clean_text, 'lang': 'ru-RU', 'voice': 'jane',
                'folderId': self.folder_id, 'format': 'mp3'
            })
            return res.content if res.status_code == 200 else None
        except:
            return None

    def clear_history(self):
        self.messages = []
