from flask import Flask, request, jsonify
from transformers import AutoProcessor, AutoModelForAudioClassification
import torch
import torch.nn.functional as F
import librosa
import os

app = Flask(__name__)

# Carregar modelo e processador
MODEL_DIR = "./emotion-recognition-model"

if not os.path.exists(MODEL_DIR):
    raise FileNotFoundError(f"O diretório do modelo '{MODEL_DIR}' não foi encontrado. Certifique-se de treinar ou baixar o modelo antes de executar o servidor.")

processor = AutoProcessor.from_pretrained(MODEL_DIR)
model = AutoModelForAudioClassification.from_pretrained(MODEL_DIR)

# Rótulos das emoções
emotion_labels = ["angry", "disgusted", "happy", "fearful", "neutral", "sad", "surprised"]

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Verificar se um arquivo foi enviado
        if 'file' not in request.files:
            return jsonify({"error": "Nenhum arquivo enviado. Por favor, envie um arquivo de áudio."}), 400

        # Obter o arquivo enviado
        file = request.files['file']

        # Validar o arquivo
        if file.filename == '':
            return jsonify({"error": "Nenhum arquivo selecionado. Por favor, envie um arquivo válido."}), 400

        # Tentar carregar o áudio usando librosa
        try:
            audio, _ = librosa.load(file, sr=16000)
        except Exception as e:
            return jsonify({"error": f"Erro ao processar o arquivo de áudio: {str(e)}"}), 400

        # Pré-processar o áudio
        inputs = processor(audio, sampling_rate=16000, return_tensors="pt", padding=True)

        # Fazer a previsão
        with torch.no_grad():
            logits = model(**inputs).logits
            probs = F.softmax(logits, dim=-1)
            predicted_id = torch.argmax(probs, dim=-1).item()
            confidence = probs[0, predicted_id].item()

        # Obter a emoção correspondente
        predicted_emotion = emotion_labels[predicted_id]

        # Retornar o resultado em JSON
        return jsonify({
            "emotion": predicted_emotion,
            "confidence": confidence
        })

    except Exception as e:
        # Tratar erros genéricos
        return jsonify({"error": f"Ocorreu um erro inesperado: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
