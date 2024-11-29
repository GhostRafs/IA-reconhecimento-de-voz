from flask import Flask, request, jsonify
from transformers import AutoProcessor, AutoModelForAudioClassification
import torch
import torch.nn.functional as F
import librosa

app = Flask(__name__)

# Carregar modelo e processador
processor = AutoProcessor.from_pretrained("./emotion-recognition-model")
model = AutoModelForAudioClassification.from_pretrained("./emotion-recognition-model")

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    audio, _ = librosa.load(file, sr=16000)
    inputs = processor(audio, sampling_rate=16000, return_tensors="pt", padding=True)

    with torch.no_grad():
        logits = model(**inputs).logits
        probs = F.softmax(logits, dim=-1)
        predicted_id = torch.argmax(probs, dim=-1).item()
        confidence = probs[0, predicted_id].item()

    emotion_labels = ["angry", "disgusted", "happy", "fearful", "neutral", "sad", "surprised"]
    predicted_emotion = emotion_labels[predicted_id]

    return jsonify({
        "emotion": predicted_emotion,
        "confidence": confidence
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
