from flask import Flask, render_template, request, jsonify
from transformers import AutoProcessor, AutoModelForAudioClassification
import torch
import torch.nn.functional as F
import librosa

app = Flask(__name__)

# Carregar modelo e processador
processor = AutoProcessor.from_pretrained("models/emotion-recognition-model")
model = AutoModelForAudioClassification.from_pretrained("models/emotion-recognition-model")

# Rota para a página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota para análise de áudio
@app.route('/analyze', methods=['POST'])
def analyze():
    file_name = request.json.get("file_name")
    file_path = f"audio_files/{file_name}"
    
    # Carregar áudio
    audio, sample_rate = librosa.load(file_path, sr=16000)
    inputs = processor(audio, sampling_rate=16000, return_tensors="pt", padding=True)
    
    # Predição
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = F.softmax(logits, dim=-1)
    predicted_id = torch.argmax(probs, dim=-1).item()
    confidence = probs[0, predicted_id].item()
    
    # Emotions
    emotion_labels = ["angry", "disgusted", "happy", "fearful", "neutral", "sad", "surprised"]
    predicted_emotion = emotion_labels[predicted_id]
    
    return jsonify({
        "predicted_emotion": predicted_emotion,
        "confidence": confidence
    })

if __name__ == '__main__':
    app.run(debug=True)
