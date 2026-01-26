import { startHardwareScan } from './hardware.js';

const SYMBOLS = ['❖', '✜', '🛡️', '⚡', '⌬', '⏣', '⌖', '⎔', '◈'];
let targetSymbol = null;

export function initCaptcha({ grid, instruction, layer, statusEl, videoEl }) {
    if (!grid || !instruction || !layer) return;

    grid.innerHTML = '';
    targetSymbol = SYMBOLS[Math.floor(Math.random() * SYMBOLS.length)];
    instruction.innerHTML = `IDENTIFICAR NODO ACTIVO: <span class="target-symbol" style="color: #00f0ff; font-size:1.5em;">${targetSymbol}</span>`;

    const nodes = [];
    nodes.push({ symbol: targetSymbol, valid: true });
    for (let i = 0; i < 8; i++) {
        const decoy = SYMBOLS[Math.floor(Math.random() * SYMBOLS.length)];
        nodes.push({ symbol: decoy, valid: false });
    }

    shuffle(nodes).forEach(node => {
        const btn = document.createElement('div');
        btn.className = 'node-btn';
        btn.innerText = node.symbol;
        btn.onclick = () => validateNode(node.valid, layer, statusEl, videoEl);
        grid.appendChild(btn);
    });
}

function shuffle(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
}

function validateNode(isValid, layer, statusEl, videoEl) {
    const errorMsg = document.getElementById('captcha-error');
    if (isValid) {
        layer.style.opacity = '0';
        setTimeout(() => {
            layer.style.display = 'none';
            startHardwareScan(statusEl, videoEl)
                .then(() => {
                    const btn = document.getElementById('btn-login');
                    if (btn) btn.disabled = false;
                })
                .catch(err => {
                    console.error(err);
                    if (statusEl) {
                        statusEl.innerText = `ERROR DE HARDWARE: ${err.message}`;
                        statusEl.style.color = 'red';
                    }
                });
        }, 500);
    } else {
        if (errorMsg) errorMsg.innerText = 'ACCESO DENEGADO: PATRÓN INCORRECTO';
        setTimeout(() => initCaptcha({ grid: document.getElementById('node-grid'), instruction: document.getElementById('instruction-text'), layer, statusEl, videoEl }), 800);
    }
}
