import streamlit as st
from core import YandexAI
import base64

st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")

if 'client' not in st.session_state:
    st.session_state.client = YandexAI()
if 'messages' not in st.session_state:
    st.session_state.messages = []

st.title("AI Assistant")

auto_speak = st.checkbox("Авто-озвучка", value=True)

if st.button("Очистить историю"):
    st.session_state.client.clear_history()
    st.session_state.messages = []
    st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Введите вопрос...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Думаю..."):
            response_text = st.session_state.client.get_response(prompt)
            st.markdown(response_text)
            
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