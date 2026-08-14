"""
Módulo de Text-to-Speech usando gTTS (Google Text-to-Speech).
Gera áudio de pronúncia para os trechos em inglês.
"""
from io import BytesIO

import streamlit as st
from gtts import gTTS


@st.cache_data(show_spinner=False)
def gerar_audio(texto: str, lang: str = "en") -> bytes:
    """Gera o áudio (mp3, em bytes) para o texto informado. Resultado cacheado."""
    buffer = BytesIO()
    tts = gTTS(text=texto, lang=lang)
    tts.write_to_fp(buffer)
    buffer.seek(0)
    return buffer.read()


def render_audio_button(texto: str, key: str, lang: str = "en"):
    """Renderiza um botão que gera e reproduz o áudio de pronúncia sob demanda."""
    if st.button("🔊 Ouvir pronúncia", key=key):
        try:
            with st.spinner("Gerando áudio..."):
                audio_bytes = gerar_audio(texto, lang=lang)
            st.audio(audio_bytes, format="audio/mp3")
        except Exception as e:
            st.error(f"❌ Não foi possível gerar o áudio: {e}")
