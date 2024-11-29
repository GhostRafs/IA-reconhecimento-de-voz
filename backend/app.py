import os
import streamlit as st
import librosa
import soundfile as sf
import numpy as np
from transformers import AutoProcessor, AutoModelForAudioClassification
import torch
import torch.nn.functional as F

# Diretório do modelo treinado
MODEL_DIR = "emotion-recognition-model"

# Verificar se os arquivos necessários existem
if not os.path.exists(MODEL_DIR):
    st.error("O diretório do modelo treinado não foi encontrado. Verifique a estrutura do projeto.")
    st.stop()

# Carregar o modelo e o processador treinados a partir do diretório
try:
    processor = AutoProcessor.from_pretrained(MODEL_DIR)
    model = AutoModelForAudioClassification.from_pretrained(MODEL_DIR)
except Exception as e:
    st.error(f"Erro ao carregar o modelo treinado: {e}")
    st.stop()

# Configuração da página do Streamlit
st.set_page_config(page_title="Análise de Emoções por Áudio", layout="centered")
st.title("🎙️ Análise de Emoções por Áudio")
st.markdown("Grave um áudio diretamente no navegador ou envie um arquivo `.wav` para analisar as emoções.")

# Upload do áudio
audio_file = st.file_uploader("Faça upload de um arquivo de áudio (.wav)", type=["wav"])

# Exibir botão para gravação futura
if st.button("Gravar Áudio"):
    st.warning("Funcionalidade de gravação direto no navegador ainda em desenvolvimento para Streamlit.")

# Processamento do áudio
if audio_file is not None:
    try:
        # Salvar o áudio enviado no diretório apropriado
        UPLOAD_DIR = "uploaded_audio"
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        uploaded_audio_path = os.path.join(UPLOAD_DIR, "uploaded_audio.wav")
        with open(uploaded_audio_path, "wb") as f:
            f.write(audio_file.read())

        # Carregar o áudio e validar a taxa de amostragem
        audio, sample_rate = librosa.load(uploaded_audio_path, sr=None)
        if sample_rate != 16000:
            st.warning("Ajustando a taxa de amostragem para 16kHz...")
            audio = librosa.resample(audio, orig_sr=sample_rate, target_sr=16000)

        # Processar o áudio com o modelo
        with st.spinner("Processando o áudio..."):
            inputs = processor(audio, sampling_rate=16000, return_tensors="pt", padding=True)
            with torch.no_grad():
                logits = model(**inputs).logits

            # Aplicar softmax para calcular as probabilidades
            probs = F.softmax(logits, dim=-1)

            # Identificar a emoção
            predicted_id = torch.argmax(probs, dim=-1).item()
            confidence = probs[0, predicted_id].item()
            emotion_labels = ["angry", "disgusted", "happy", "fearful", "neutral", "sad", "surprised"]
            predicted_emotion = emotion_labels[predicted_id]

        # Exibir os resultados ao usuário
        st.success(f"Emoção Prevista: **{predicted_emotion}**")
        st.info(f"Confiança: **{confidence:.2f}**")

    except Exception as e:
        st.error(f"Ocorreu um erro ao processar o áudio: {e}")

# Instruções adicionais
st.markdown(
    """
    ### Instruções para Gravação de Áudio:
    - Use ferramentas externas para gravar áudio no formato `.wav` (16kHz).
    - Certifique-se de que o áudio esteja claro e sem ruídos excessivos para melhores resultados.
    """
)

# Diretório onde os arquivos serão salvos
MODEL_DIR = "emotion-recognition-model"

# Criar o diretório caso ele não exista
import os
os.makedirs(MODEL_DIR, exist_ok=True)

# Salvar o modelo e o processador no diretório
try:
    processor.save_pretrained(MODEL_DIR)
    model.save_pretrained(MODEL_DIR)
    print(f"Arquivos do modelo salvos em {MODEL_DIR}")
except Exception as e:
    print(f"Erro ao salvar os arquivos: {e}")
