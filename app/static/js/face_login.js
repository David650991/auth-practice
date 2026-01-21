/* app/static/js/face_login.js */

document.addEventListener("DOMContentLoaded", () => {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const btn = document.getElementById('login-btn');
    const status = document.getElementById('status');
    const cameraSelect = document.getElementById('camera-select');
    
    // Configuración inyectada desde HTML
    const CONFIG = window.LOGIN_CONFIG;

    let currentStream = null;

    async function getCameras() {
        try {
            await navigator.mediaDevices.getUserMedia({ video: true });
            const devices = await navigator.mediaDevices.enumerateDevices();
            const videoDevices = devices.filter(d => d.kind === 'videoinput');
            
            cameraSelect.innerHTML = "";
            videoDevices.forEach((d, i) => {
                const opt = document.createElement('option');
                opt.value = d.deviceId;
                opt.text = d.label || `Cámara ${i+1}`;
                cameraSelect.appendChild(opt);
            });
            
            if(videoDevices.length > 0) {
                startCamera(videoDevices[0].deviceId);
            } else {
                status.innerText = "No se detectaron cámaras.";
            }
        } catch(e) { 
            console.error(e);
            status.innerText = "Error: Acceso a cámara denegado."; 
        }
    }

    async function startCamera(id) {
        if(currentStream) currentStream.getTracks().forEach(t => t.stop());
        
        status.innerText = "Conectando cámara...";
        btn.disabled = true;

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

    // Habilitar botón solo cuando haya video real
    video.addEventListener('canplay', () => {
        status.innerText = "Esperando...";
        btn.disabled = false;
    });

    cameraSelect.addEventListener('change', () => startCamera(cameraSelect.value));

    btn.addEventListener('click', () => {
        // Validación defensiva
        if (video.videoWidth === 0) return;

        status.innerText = "Analizando rostro...";
        
        // Captura
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0);
        
        const dataURL = canvas.toDataURL('image/jpeg', 0.9);

        // Envío al backend
        fetch(CONFIG.loginUrl, {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "X-CSRFToken": CONFIG.csrfToken 
            },
            body: JSON.stringify({ image: dataURL })
        })
        .then(r => r.json())
        .then(data => {
            if(data.status === 'success' || data.status === 'redirect'){
                status.innerText = "✔ Identidad Confirmada. Redirigiendo...";
                status.style.color = "#0f0";
                setTimeout(() => {
                    window.location.href = data.url;
                }, 1000); // Pequeña pausa para que el usuario vea el éxito
            } else {
                status.innerText = "⛔ " + (data.message || "No reconocido");
                status.style.color = "red";
            }
        })
        .catch(e => { 
            console.error(e);
            status.innerText = "Error de conexión con el servidor."; 
            status.style.color = "red";
        });
    });

    // Iniciar
    getCameras();
});