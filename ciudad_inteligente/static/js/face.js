const video = document.getElementById('inputVideo');
const canvas = document.getElementById('overlay');
const statusDiv = document.getElementById('status');
const captureUploadBtn = document.getElementById('captureUploadBtn');

async function startCamera() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: 'user' },
            audio: false
        });
        video.srcObject = stream;
    } catch (err) {
        alert("No se pudo iniciar la cámara: " + err.message);
    }
}

function syncCanvasToVideo() {
    const rect = video.getBoundingClientRect();
    canvas.style.width = rect.width + "px";
    canvas.style.height = rect.height + "px";
    canvas.width = rect.width;
    canvas.height = rect.height;
    return { width: rect.width, height: rect.height };
}

async function onPlay() {
    const MODEL_URL = '/static/models';

    await faceapi.loadSsdMobilenetv1Model(MODEL_URL);
    await faceapi.loadFaceLandmarkModel(MODEL_URL);
    await faceapi.loadFaceRecognitionModel(MODEL_URL);
    await faceapi.loadFaceExpressionModel(MODEL_URL);

    async function runDetection() {
        if (video.paused || video.ended) return setTimeout(runDetection, 200);

        const displaySize = syncCanvasToVideo();

        const fullFaceDescriptions = await faceapi.detectAllFaces(video)
            .withFaceLandmarks()
            .withFaceDescriptors()
            .withFaceExpressions();

        const resizedResults = faceapi.resizeResults(fullFaceDescriptions, displaySize);

        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // ❌ Eliminado: faceapi.draw.drawDetections(canvas, resizedResults);
        // ❌ Eliminado: faceapi.draw.drawFaceExpressions(canvas, resizedResults, 0.05);

        // ✅ Solo dibujamos los landmarks (puntos faciales)
        faceapi.draw.drawFaceLandmarks(canvas, resizedResults);

        setTimeout(runDetection, 100);
    }

    runDetection();
}

video.addEventListener('playing', onPlay);

function takeSnapshot() {
    const canvasTmp = document.createElement('canvas');
    const vw = video.videoWidth, vh = video.videoHeight;
    const ratio = vw && vh ? (vw / vh) : (640 / 480);
    canvasTmp.width = 640;
    canvasTmp.height = Math.round(640 / ratio);
    const ctx = canvasTmp.getContext('2d');
    ctx.drawImage(video, 0, 0, canvasTmp.width, canvasTmp.height);
    return canvasTmp.toDataURL('image/jpeg', 0.92);
}

async function captureAndUpload() {
    statusDiv.textContent = "Cargando...";
    statusDiv.className = "loading";

    const dataUrl = takeSnapshot();
    const res = await fetch(dataUrl);
    const blob = await res.blob();
    const formData = new FormData();
    formData.append('photo', blob, 'captura.jpg');

    const response = await fetch('/upload-photo/', { method: 'POST', body: formData });
    const result = await response.json();

    if (result.autorizado) {
        window.location.href = result.redirect_url; // redirige desde el cliente
    } else {
        statusDiv.textContent = "❌ No autorizado";
    }


}

captureUploadBtn.addEventListener('click', captureAndUpload);
window.addEventListener('load', startCamera);