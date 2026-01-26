import { initCaptcha } from './captcha.js';
import { captureLogin } from './liveness.js';
import { getConfig } from './config.js';

document.addEventListener('DOMContentLoaded', () => {
    const statusEl = document.getElementById('status');
    const videoEl = document.getElementById('camera-feed');
    const grid = document.getElementById('node-grid');
    const instruction = document.getElementById('instruction-text');
    const layer = document.getElementById('security-layer');
    const loginBtn = document.getElementById('btn-login');
    const scanFx = document.getElementById('scan-fx');

    const CONFIG = getConfig();

    if (statusEl) statusEl.innerText = '[SISTEMA] INICIALIZANDO PROTOCOLO DE DEFENSA...';

    initCaptcha({ grid, instruction, layer, statusEl, videoEl });

    if (loginBtn) {
        loginBtn.addEventListener('click', () => {
            if (scanFx) scanFx.style.display = 'block';
            captureLogin({
                videoEl,
                statusEl,
                csrfToken: CONFIG.csrfToken
            });
        });
    }
});
