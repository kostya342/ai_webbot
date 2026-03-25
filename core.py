import os
import requests
import re

class YandexAI:
    def __init__(self):
        self.api_key = os.getenv("YANDEX_API_KEY")
        self.folder_id = os.getenv("YANDEX_FOLDER_ID")
        self.messages = [
            {
                "role": "system",
                "text": "Ты полезный ассистент. Отвечай подробно. Формулы пиши в формате LaTeX внутри $$...$$."
            }
        ]

    def get_auth_header(self):
        if not self.api_key:
            return {}
        if self.api_key.startswith('AQVN') or self.api_key.startswith('AKIA'):
            return {'Authorization': f'Api-Key {self.api_key}'}
        elif self.api_key.startswith('AQV'):
            return {'Authorization': f'Bearer {self.api_key}'}
        return {'Authorization': f'Api-Key {self.api_key}'}

    def prepare_speech(self, text):
        text = re.sub(r'\$\$(.*?)\$\$', r'\1', text)
        text = re.sub(r'\$', '', text)
        text = re.sub(r'\\\((.*?)\\\)', r'\1', text)
        text = re.sub(r'\\\[(.*?)\\\]', r'\1', text)
        text = re.sub(r'-\s*([A-Za-z])\b', r' \1', text)
        text = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'\1 разделить на \2', text)
        text = text.replace('=', ' равно ')
        text = text.replace('+', ' плюс ')
        text = text.replace('-', ' минус ')
        text = re.sub(r'(\d)\s*\*\s*(\d)', r'\1 умножить на \2', text)
        text = text.replace('^', ' в степени ')
        
        greek = {
            '\\alpha': 'альфа', '\\beta': 'бета', '\\gamma': 'гамма',
            '\\delta': 'дельта', '\\pi': 'пи', '\\sigma': 'сигма',
            '\\omega': 'омега', '\\theta': 'тета'
        }
        for latex, word in greek.items():
            text = text.replace(latex, word)
        
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def get_response(self, user_text):
        self.messages.append({"role": "user", "text": user_text})
        
        headers = self.get_auth_header()
        headers['x-folder-id'] = self.folder_id
        headers['Content-Type'] = 'application/json'
        
        try:
            response = requests.post(
                'https://llm.api.cloud.yandex.net/foundationModels/v1/completion',
                headers=headers,
                json={
                    "modelUri": f"gpt://{self.folder_id}/yandexgpt/latest",
                    "completionOptions": {"stream": False, "temperature": 0.7, "maxTokens": 1000},
                    "messages": self.messages
                }
            )
            if response.status_code == 200:
                reply = response.json()['result']['alternatives'][0]['message']['text']
                self.messages.append({"role": "assistant", "text": reply})
                return reply
            else:
                return f"Ошибка API: {response.status_code}"
        except Exception as e:
            return f"Ошибка: {str(e)}"

    def synthesize_speech(self, text):
        if not self.api_key or not self.folder_id:
            return None
        
        text = self.prepare_speech(text)[:1500]
        headers = self.get_auth_header()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        
        try:
            response = requests.post(
                'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize',
                headers=headers,
                data={
                    'text': text,
                    'lang': 'ru-RU',
                    'voice': 'jane',
                    'folderId': self.folder_id,
                    'format': 'mp3',
                    'speed': '0.9'
                }
            )
            if response.status_code == 200:
                return response.content
        except Exception:
            pass
        return None

    def clear_history(self):
        self.messages = [
            {
                "role": "system",
                "text": "Ты полезный ассистент. Отвечай подробно. Формулы пиши в формате LaTeX внутри $$...$$."
            }
        ]
