/* app/static/js/biometrics.js */

document.addEventListener("DOMContentLoaded", () => {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const captureBtn = document.getElementById('capture-btn');
    const status = document.getElementById('status');
    const cameraSelect = document.getElementById('camera-select');
    
    // Obtenemos las URLs y Tokens desde los atributos data- del botón o variables globales
    // En este caso, usaremos una variable global definida en el HTML antes de cargar este script
    const CONFIG = window.BIOMETRIC_CONFIG; 

    let currentStream = null;

    async function getCameras() {
        try {
            await navigator.mediaDevices.getUserMedia({ video: true });
            const devices = await navigator.mediaDevices.enumerateDevices();
            const videoDevices = devices.filter(d => d.kind === 'videoinput');
            
            cameraSelect.innerHTML = "";
            let selectedId = null;

            videoDevices.forEach((d, i) => {
                const opt = document.createElement('option');
                opt.value = d.deviceId;
                opt.text = d.label || `Cámara ${i+1}`;
                cameraSelect.appendChild(opt);
                
                const label = opt.text.toLowerCase();
                if (!selectedId && (label.includes("integrated") || label.includes("usb") || label.includes("webcam"))) {
                    selectedId = d.deviceId;
                }
            });

            if (videoDevices.length > 0) {
                cameraSelect.value = selectedId || videoDevices[0].deviceId;
                startCamera(cameraSelect.value);
            } else {
                status.innerText = "No se encontraron cámaras.";
            }
        } catch(e) {
            console.error(e);
            status.innerText = "Error: Acceso a cámara denegado.";
        }
    }

    async function startCamera(id) {
        if(currentStream) currentStream.getTracks().forEach(t => t.stop());
        
        status.innerText = "Conectando cámara...";
        captureBtn.disabled = true;

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: { deviceId: { exact: id }, width: { ideal: 640 }, height: { ideal: 480 } } 
            });
            currentStream = stream;
            video.srcObject = stream;
        } catch(e) {
            status.innerText = "Error al abrir cámara.";
        }
    }

    // VALIDACIÓN ROBUSTA: Esperar a que el video tenga datos reales
    video.addEventListener('canplay', () => {
        if (video.videoWidth > 0 && video.videoHeight > 0) {
            status.innerText = "Cámara lista. ¡Mantén el rostro en el óvalo!";
            status.style.color = "green";
            captureBtn.disabled = false;
        }
    });

    cameraSelect.addEventListener('change', () => startCamera(cameraSelect.value));

    captureBtn.addEventListener('click', () => {
        // 1. Validación Defensiva: ¿La cámara tiene dimensiones reales?
        if (video.videoWidth === 0 || video.videoHeight === 0) {
            alert("La cámara aún no está lista. Espera unos segundos.");
            return;
        }

        // Dibujar el frame actual del video en el canvas
        const context = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        // Obtener la imagen en base64
        const dataURL = canvas.toDataURL('image/jpeg', 0.9);

        // Enviar al backend usando la URL de la configuración
        fetch(CONFIG.enrollUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": CONFIG.csrfToken
            },
            body: JSON.stringify({ image: dataURL })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert("Error: " + data.error);
            } else {
                alert("¡Éxito! " + data.message);
                window.location.href = data.redirect;
            }
        })
        .catch(err => {
            console.error("Error en la petición:", err);
            alert("Ocurrió un error de conexión.");
        });
    });

    // Iniciar
    getCameras();
});