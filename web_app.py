import streamlit as st
from core import YandexAI
import base64
from streamlit_mic_recorder import mic_recorder

st.set_page_config(page_title="Умный Ассистент", page_icon="🎙️")

if 'client' not in st.session_state:
    st.session_state.client = YandexAI()
if 'chat' not in st.session_state:
    st.session_state.chat = []

st.title("🎙️ Голосовой помощник")

# Кнопка записи в сайдбаре
with st.sidebar:
    st.header("Управление")
    audio = mic_recorder(start_prompt="Записать вопрос", stop_prompt="Отправить", key='rec')
    auto_speak = st.checkbox("Озвучивать ответы", value=True)
    if st.button("Очистить чат"):
        st.session_state.chat = []
        st.rerun()

# Отображение сообщений
for m in st.session_state.chat:
    with st.chat_message(m['role']):
        st.write(m['text'])

# Логика ввода
user_query = st.chat_input("Спросите что-нибудь...")

if audio:
    with st.spinner("Распознаю голос..."):
        user_query = st.session_state.client.stt(audio['bytes'])

if user_query:
    st.session_state.chat.append({"role": "user", "text": user_query})
    with st.chat_message("user"):
        st.write(user_query)

    with st.chat_message("assistant"):
        with st.spinner("Думаю..."):
            ans = st.session_state.client.get_response(user_query)
            st.write(ans)
            st.session_state.chat.append({"role": "assistant", "text": ans})
            
            if auto_speak:
                audio_data = st.session_state.client.synthesize_speech(ans)
                if audio_data:
                    b64 = base64.b64encode(audio_data).decode()
                    st.markdown(f'<audio src="data:audio/mp3;base64,{b64}" autoplay>', unsafe_allow_html=True)
