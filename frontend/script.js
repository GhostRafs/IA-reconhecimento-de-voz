let mediaRecorder;
let audioChunks = [];

// Botões
const startRecordingButton = document.getElementById("start-recording");
const stopRecordingButton = document.getElementById("stop-recording");

// Status
const statusText = document.getElementById("status");

startRecordingButton.addEventListener("click", async () => {
  try {
    // Solicitar permissão para o microfone
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    // Iniciar o MediaRecorder
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };

    mediaRecorder.onstart = () => {
      statusText.textContent = "Gravando...";
      stopRecordingButton.disabled = false;
      startRecordingButton.disabled = true;
    };

    mediaRecorder.onstop = async () => {
      statusText.textContent = "Gravação finalizada!";
      stopRecordingButton.disabled = true;
      startRecordingButton.disabled = false;

      // Criar o blob do áudio gravado
      const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
      audioChunks = [];

      // Enviar o áudio para o backend
      await uploadAudio(audioBlob);
    };

    mediaRecorder.start();
  } catch (error) {
    console.error("Erro ao acessar o microfone:", error);
    statusText.textContent = "Erro ao acessar o microfone!";
  }
});

stopRecordingButton.addEventListener("click", () => {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
  }
});

// Função para enviar o áudio para o backend
async function uploadAudio(audioBlob) {
  const formData = new FormData();
  formData.append("file", audioBlob, "audio.wav");

  statusText.textContent = "Enviando áudio...";

  try {
    const response = await fetch("http://127.0.0.1:5000/predict", {
      method: "POST",
      body: formData,
    });

    if (response.ok) {
      const result = await response.json();
      document.getElementById("emotion").textContent = result.emotion;
      document.getElementById("confidence").textContent = (result.confidence * 100).toFixed(2);
      document.getElementById("result").style.display = "block";
    } else {
      console.error("Erro ao processar o áudio:", await response.text());
      statusText.textContent = "Erro ao processar o áudio.";
    }
  } catch (error) {
    console.error("Erro na requisição ao backend:", error);
    statusText.textContent = "Erro na conexão com o servidor.";
  }
}
