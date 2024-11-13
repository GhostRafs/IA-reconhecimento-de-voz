function analyzeAudio() {
    const audioSelect = document.getElementById("audioSelect");
    const fileName = audioSelect.value;

    fetch('/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ file_name: fileName })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("result").innerHTML = 
            `Emoção: ${data.predicted_emotion} <br> Confiança: ${data.confidence.toFixed(2)}`;
    })
    .catch(error => console.error('Erro:', error));
}
