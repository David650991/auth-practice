import { initCaptcha } from './captcha.js';
import { captureLogin } from './liveness.js';

document.addEventListener('DOMContentLoaded', () => {
    const statusEl = document.getElementById('status');
    const videoEl = document.getElementById('camera-feed');
    const grid = document.getElementById('node-grid');
    const instruction = document.getElementById('instruction-text');
    const layer = document.getElementById('security-layer');
    const loginBtn = document.getElementById('btn-login');

    if (statusEl) statusEl.innerText = '[SISTEMA] INICIALIZANDO PROTOCOLO DE DEFENSA...';

    initCaptcha({ grid, instruction, layer, statusEl, videoEl });

    if (loginBtn) {
        loginBtn.addEventListener('click', () => {
            captureLogin({
                videoEl,
                statusEl,
                csrfToken: window.CONFIG ? window.CONFIG.csrf_token : ''
            });
        });
    }
});
