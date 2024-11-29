let mediaRecorder;
let audioChunks = [];

const startRecordingButton = document.getElementById("start-recording");
const stopRecordingButton = document.getElementById("stop-recording");
const audioUploadInput = document.getElementById("audio-upload");
const uploadButton = document.getElementById("upload-button");
const statusText = document.getElementById("status");

startRecordingButton.addEventListener("click", async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

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

      const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
      audioChunks = [];
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

uploadButton.addEventListener("click", async () => {
  const file = audioUploadInput.files[0];
  if (file) {
    statusText.textContent = "Enviando áudio carregado...";
    await uploadAudio(file);
  } else {
    statusText.textContent = "Por favor, selecione um arquivo de áudio.";
  }
});

async function uploadAudio(audioBlob) {
  const formData = new FormData();
  formData.append("file", audioBlob, "audio.wav");

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
      statusText.textContent = "Processamento concluído!";
    } else {
      console.error("Erro ao processar o áudio:", await response.text());
      statusText.textContent = "Erro ao processar o áudio.";
    }
  } catch (error) {
    console.error("Erro na conexão com o servidor:", error);
    statusText.textContent = "Erro na conexão com o servidor.";
  }
}
