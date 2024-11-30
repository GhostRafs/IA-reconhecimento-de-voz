import streamlit as st
import sounddevice as sd
import numpy as np
import tempfile
import requests
import wave
import os

# Função para gravar áudio
def record_audio(duration=5, samplerate=44100):
    st.write("Gravando áudio...")
    recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype="int16")
    sd.wait()
    return recording

# Salvar áudio como .wav
def save_audio(audio_data, samplerate=44100, filename="audio.wav"):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 16 bits
        wf.setframerate(samplerate)
        wf.writeframes(audio_data.tobytes())

# Enviar áudio para o backend
def process_audio(file_path):
    try:
        with open(file_path, "rb") as f:
            files = {"file": (file_path, f, "audio/wav")}
            response = requests.post("http://127.0.0.1:5000/predict", files=files)
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            st.error(f"Erro ao processar o áudio: {response.text}")
    except Exception as e:
        st.error(f"Erro: {e}")
    return None

# Interface do Streamlit
st.title("Reconhecimento de Emoções")

# Modalidade: Gravar ou Enviar
choice = st.radio("Escolha uma ação:", ["Gravar Áudio", "Enviar Áudio"])

if choice == "Gravar Áudio":
    duration = st.slider("Duração da gravação (segundos):", min_value=1, max_value=10, value=5)
    if st.button("Gravar"):
        audio_data = record_audio(duration)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        save_audio(audio_data, filename=temp_file.name)
        st.success("Áudio gravado com sucesso!")
        result = process_audio(temp_file.name)
        if result:
            st.subheader("Resultados:")
            st.write(f"**Emoção Detectada:** {result['emotion']}")
            st.write(f"**Confiança:** {result['confidence'] * 100:.2f}%")
        os.remove(temp_file.name)

elif choice == "Enviar Áudio":
    uploaded_file = st.file_uploader("Faça o upload de um arquivo de áudio (.wav)", type=["wav"])
    if uploaded_file:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_file.write(uploaded_file.read())
        temp_file.close()
        result = process_audio(temp_file.name)
        if result:
            st.subheader("Resultados:")
            st.write(f"**Emoção Detectada:** {result['emotion']}")
            st.write(f"**Confiança:** {result['confidence'] * 100:.2f}%")
        os.remove(temp_file.name)
