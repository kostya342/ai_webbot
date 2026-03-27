import os
import requests
import re
from dotenv import load_dotenv

load_dotenv()

class YandexAI:
    def __init__(self):
        # Ключи для разных сервисов
        self.gpt_key = os.getenv("YANDEX_API_KEY")
        self.tts_key = os.getenv("YANDEX_TTS_API_KEY") or self.gpt_key # Если нет отдельного, берем общий
        self.stt_key = os.getenv("YANDEX_STT_API_KEY") # Твой новый ключ для STT
        
        self.folder_id = os.getenv("YANDEX_FOLDER_ID")
        self.system_prompt = "Ты краткий помощник. Отвечай на русском. Не используй символы $."

    def _get_headers(self, key):
        """Вспомогательный метод для формирования заголовков"""
        if not key: return {}
        if key.startswith('AQVN'):
            return {'Authorization': f'Bearer {key}'}
        return {'Authorization': f'Api-Key {key}'}

    def get_response(self, user_text):
        """Запрос к YandexGPT (использует gpt_key)"""
        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        payload = {
            "modelUri": f"gpt://{self.folder_id}/yandexgpt/latest",
            "completionOptions": {"stream": False, "temperature": 0.5, "maxTokens": "2000"},
            "messages": [
                {"role": "system", "text": self.system_prompt},
                {"role": "user", "text": user_text}
            ]
        }
        try:
            res = requests.post(url, headers=self._get_headers(self.gpt_key), json=payload, timeout=10)
            if res.status_code == 200:
                return res.json()['result']['alternatives'][0]['message']['text']
            return f"Ошибка GPT ({res.status_code}): {res.text}"
        except Exception as e:
            return f"Ошибка сети GPT: {e}"

    def stt(self, audio_bytes):
        """Распознавание речи (использует stt_key)"""
        url = f"https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?folderId={self.folder_id}&lang=ru-RU"
        try:
            # Важно: для STT используем отдельный ключ
            res = requests.post(url, headers=self._get_headers(self.stt_key), data=audio_bytes, timeout=15)
            if res.status_code == 200:
                return res.json().get('result', '')
            return f"Ошибка STT ({res.status_code})"
        except Exception as e:
            print(f"STT Exception: {e}")
            return ""

    def synthesize_speech(self, text):
        """Озвучка текста (использует tts_key)"""
        url = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'
        clean_text = re.sub(r'[*#`$]', '', text)[:1000]
        try:
            res = requests.post(url, headers=self._get_headers(self.tts_key), data={
                'text': clean_text, 'lang': 'ru-RU', 'voice': 'jane',
                'folderId': self.folder_id, 'format': 'mp3'
            }, timeout=10)
            return res.content if res.status_code == 200 else None
        except:
            return None
