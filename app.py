import streamlit as st
from transformers import AutoProcessor, AutoModelForAudioClassification
import torch
import torch.nn.functional as F
import librosa

# Configuração da página
st.set_page_config(page_title="Análise de Emoções em Áudio", layout="centered")

# Título do aplicativo
st.title("Análise de Emoções em Áudio")
st.write("Faça o upload de um arquivo de áudio para detectar a emoção predominante.")


# Carregar modelo e processador
@st.cache_resource
def load_model():
    processor = AutoProcessor.from_pretrained("Tagoreparaizo/IAUnit")
    model = AutoModelForAudioClassification.from_pretrained("Tagoreparaizo/IAUnit")
    return processor, model


processor, model = load_model()

# Input do usuário: upload do arquivo de áudio
uploaded_file = st.file_uploader("Faça upload de um arquivo de áudio (formato .wav):", type=["wav"])

if uploaded_file is not None:
    # Exibir informações sobre o arquivo
    st.audio(uploaded_file, format="audio/wav")

    # Processar o áudio
    file_path = uploaded_file.name
    audio, sample_rate = librosa.load(uploaded_file, sr=16000)

    inputs = processor(audio, sampling_rate=16000, return_tensors="pt", padding=True)

    with torch.no_grad():
        logits = model(**inputs).logits

    probs = F.softmax(logits, dim=-1)

    predicted_id = torch.argmax(probs, dim=-1).item()
    confidence = probs[0, predicted_id].item()

    emotion_labels = ["angry", "disgusted", "happy", "fearful", "neutral", "sad", "surprised"]
    predicted_emotion = emotion_labels[predicted_id]

    # Exibir resultados
    st.subheader("Resultado da Análise")
    st.write(f"**Emoção Predita:** {predicted_emotion}")
    st.write(f"**ID Predito:** {predicted_id}")
    st.write(f"**Confiança:** {confidence:.2f}")
else:
    st.write("Por favor, faça o upload de um arquivo para começar a análise.")
