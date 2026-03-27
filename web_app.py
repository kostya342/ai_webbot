import streamlit as st
from core import GeminiAI
import base64
from streamlit_mic_recorder import mic_recorder

st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")

if 'client' not in st.session_state:
    st.session_state.client = GeminiAI()
if 'messages' not in st.session_state:
    st.session_state.messages = []

st.title("Умная колонка (Gemini + Yandex TTS)")

col1, col2 = st.columns([3, 1])
with col2:
    auto_speak = st.checkbox("Авто-озвучка", value=True)
    if st.button("Очистить историю"):
        st.session_state.client.clear_history()
        st.session_state.messages = []
        st.rerun()

# Отрисовка истории
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Сайдбар для голосового ввода
with st.sidebar:
    st.markdown("### 🎙️ Голосовой ввод")
    st.caption("Нажми, чтобы сказать голосом")
    # Кнопка записи аудио из браузера
    audio = mic_recorder(start_prompt="🔴 Начать запись", stop_prompt="⏹ Остановить", key='recorder')

# Текстовый ввод
prompt = st.chat_input("Или введите вопрос текстом...")

# Логика обработки
user_input_text = prompt
audio_bytes = None

if audio:
    audio_bytes = audio['bytes']
    user_input_text = "🎙 [Голосовое сообщение]"

if user_input_text or audio_bytes:
    st.session_state.messages.append({"role": "user", "content": user_input_text})
    with st.chat_message("user"):
        st.markdown(user_input_text)
    
    with st.chat_message("assistant"):
        with st.spinner("Думаю и ищу в интернете..."):
            
            # Если есть аудио, шлем байты аудио (mic_recorder пишет в WAV)
            if audio_bytes:
                response_text = st.session_state.client.get_response_from_audio(audio_bytes, mime_type="audio/wav")
            else:
                response_text = st.session_state.client.get_response(user_input_text)
            
            st.markdown(response_text)
            
            # Озвучка Яндексом
            if auto_speak:
                audio_data = st.session_state.client.synthesize_speech(response_text)
                if audio_data:
                    audio_b64 = base64.b64encode(audio_data).decode('utf-8')
                    st.components.v1.html(f"""
                        <script>
                        const audio = new Audio('data:audio/mp3;base64,{audio_b64}');
                        audio.play().catch(e => console.log(e));
                        </script>
                    """, height=0)
            
            st.session_state.messages.append({"role": "assistant", "content": response_text})
