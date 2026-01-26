import { runPoseChallenge } from './poseLoop.js';
import { finalizeEnrollment } from './enrollRequest.js';

document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const captureBtn = document.getElementById('capture-btn');
    const instructionText = document.getElementById('instruction-text');
    const scanLine = document.getElementById('scan-line');

    const captchaOverlay = document.getElementById('captcha-overlay');
    const captchaGrid = document.getElementById('captcha-grid');
    const mainContent = document.getElementById('main-content');

    const CONFIG = window.BIOMETRIC_CONFIG;
    let challengeStep = 0;

    const securityIcons = [
        { id: 'shield', char: '🛡️', valid: true },
        { id: 'bomb', char: '💣', valid: false },
        { id: 'bug', char: '🦠', valid: false },
        { id: 'skull', char: '💀', valid: false },
        { id: 'fire', char: '🔥', valid: false },
        { id: 'robot', char: '🤖', valid: false }
    ];

    function initCaptcha() {
        captchaGrid.innerHTML = '';
        const shuffled = [...securityIcons].sort(() => Math.random() - 0.5);

        shuffled.forEach(item => {
            const div = document.createElement('div');
            div.className = 'captcha-item';
            div.innerText = item.char;
            div.onclick = () => {
                if(item.valid) {
                    captchaOverlay.style.display = 'none';
                    mainContent.classList.remove('blur-content');
                    startCamera();
                } else {
                    alert('Acceso Denegado: Objeto inseguro detectado.');
                    initCaptcha();
                }
            };
            captchaGrid.appendChild(div);
        });
    }

    async function startCamera() {
        instructionText.innerText = 'Iniciando sensores...';
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: { width: { ideal: 1280 } } });
            video.srcObject = stream;
        } catch(e) {
            instructionText.innerText = 'Error: Cámara no disponible.';
        }
    }

    video.addEventListener('canplay', () => {
        if(video.videoWidth > 0) {
            instructionText.innerText = '✅ SISTEMA EN LÍNEA. PREPARADO.';
            instructionText.style.color = 'green';
            captureBtn.disabled = false;
            captureBtn.innerText = 'INICIAR PRUEBA DE VIDA';
        }
    });

    captureBtn.addEventListener('click', () => {
        if(challengeStep === 0) {
            captureBtn.disabled = true;
            scanLine.style.display = 'block';
            runPoseChallenge({
                challengeStepRef: () => challengeStep,
                advanceStep: () => { challengeStep += 1; },
                canvas,
                video,
                instructionText,
                config: CONFIG,
                onComplete: () => finalizeEnrollment({ video, canvas, config: CONFIG, scanLine, instructionText })
            });
        }
    });

    // Arrancar con Captcha
    initCaptcha();
});
