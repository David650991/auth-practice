import { getStream } from './hardware.js';
import { sendLogin } from './apiClient.js';

export async function captureLogin({ videoEl, statusEl, csrfToken }) {
    const streamReference = getStream();
    if (!videoEl || !statusEl) return;

    if (!streamReference || !streamReference.active) {
        statusEl.innerText = 'ERROR: VIDEO PERDIDO.';
        return;
    }

    const canvas = document.createElement('canvas');
    canvas.width = videoEl.videoWidth;
    canvas.height = videoEl.videoHeight;
    canvas.getContext('2d').drawImage(videoEl, 0, 0);

    const imageData = canvas.toDataURL('image/jpeg');
    statusEl.innerText = 'ANALIZANDO BIOMETRÍA...';

    try {
        const data = await sendLogin(imageData, csrfToken);
        if (data.status === 'success') {
            statusEl.innerText = 'IDENTIDAD CONFIRMADA.';
            statusEl.style.color = '#00ff00';
            setTimeout(() => window.location.href = data.url || '/dashboard', 900);
            return;
        }

        if (data.status === 'redirect' && data.url) {
            statusEl.innerText = 'SESIÓN ACTIVA. REDIRIGIENDO...';
            statusEl.style.color = '#00ff00';
            setTimeout(() => window.location.href = data.url, 600);
            return;
        }

        const reason = data.message || data.error || 'Error de autenticación';
        statusEl.innerText = `DENEGADO: ${reason}`;
        statusEl.style.color = 'red';
    } catch (err) {
        console.error(err);
        statusEl.innerText = 'ERROR DE CONEXIÓN.';
        statusEl.style.color = 'red';
    }
}
