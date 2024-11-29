let mediaRecorder;
let audioChunks = [];

const startRecordingButton = document.getElementById("start-recording");
const stopRecordingButton = document.getElementById("stop-recording");
const audioUploadInput = document.getElementById("audio-upload");
const uploadButton = document.getElementById("upload-button");
const statusText = document.getElementById("status");
const modal = document.getElementById("action-modal");
const container = document.querySelector(".container");

startRecordingButton.addEventListener("click", async () => {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    alert("Seu navegador não suporta gravação de áudio!");
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    audioChunks = [];
    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };

    mediaRecorder.onstart = () => {
      statusText.textContent = "Gravando...";
      toggleButtons(true);
    };

    mediaRecorder.onstop = async () => {
      statusText.textContent = "Gravação finalizada!";
      toggleButtons(false);

      const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
      await processAudio(audioBlob);
    };

    mediaRecorder.start();
  } catch (error) {
    handleMicrophoneError(error);
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
    await processAudio(file);
  } else {
    statusText.textContent = "Por favor, selecione um arquivo de áudio.";
  }
});

async function processAudio(audioBlob) {
  const formData = new FormData();
  formData.append("file", audioBlob, "audio.wav");

  try {
    const response = await fetch("http://127.0.0.1:5000/predict", {
      method: "POST",
      body: formData,
    });

    if (response.ok) {
      const result = await response.json();
      displayResult(result);
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

function displayResult(result) {
  document.getElementById("emotion").textContent = result.emotion;
  document.getElementById("confidence").textContent = `${(result.confidence * 100).toFixed(2)}%`;
  document.getElementById("result").style.display = "block";
}

function toggleButtons(isRecording) {
  startRecordingButton.disabled = isRecording;
  stopRecordingButton.disabled = !isRecording;
}

function handleMicrophoneError(error) {
  console.error("Erro ao acessar o microfone:", error);
  let errorMessage = "Erro ao acessar o microfone!";

  switch (error.name) {
    case "NotAllowedError":
      errorMessage = "Permissão de microfone negada!";
      break;
    case "NotFoundError":
      errorMessage = "Microfone não encontrado!";
      break;
    case "NotReadableError":
      errorMessage = "O microfone está sendo usado por outro programa.";
      break;
  }

  alert(errorMessage);
  statusText.textContent = errorMessage;
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("choose-record").addEventListener("click", () => {
    modal.style.display = "none";
    container.style.display = "block";
    toggleRecordingUI(true);
  });

  document.getElementById("choose-upload").addEventListener("click", () => {
    modal.style.display = "none";
    container.style.display = "block";
    toggleRecordingUI(false);
  });
});

function toggleRecordingUI(isRecording) {
  startRecordingButton.style.display = isRecording ? "inline-block" : "none";
  stopRecordingButton.style.display = isRecording ? "inline-block" : "none";
  audioUploadInput.style.display = isRecording ? "none" : "block";
  uploadButton.style.display = isRecording ? "none" : "inline-block";
}
