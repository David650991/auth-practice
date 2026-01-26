const HARDWARE_PROFILE = {
    blocked: ['virtual', 'droid', 'phone', 'remote', 'obs', 'manycam', 'iriun', 'enlace', 'mobile'],
    preferred: ['usb', 'uvc', 'integrated', 'webcam', 'hd', 'camera', 'microsoft', 'logitech']
};

let streamReference = null;

export async function startHardwareScan(statusEl, videoEl) {
    if (!statusEl || !videoEl) return null;

    statusEl.innerText = '[HARDWARE] ESCANEANDO SENSORES...';
    statusEl.style.color = '#00f0ff';

    await navigator.mediaDevices.getUserMedia({ video: true });
    const devices = await navigator.mediaDevices.enumerateDevices();
    const videoDevices = devices.filter(d => d.kind === 'videoinput');

    if (videoDevices.length === 0) {
        throw new Error('NO SE DETECTAN CÁMARAS.');
    }

    let bestDeviceId = null;
    const log = [];

    for (const device of videoDevices) {
        const label = device.label.toLowerCase();
        let state = '[?]';

        if (HARDWARE_PROFILE.blocked.some(block => label.includes(block))) {
            state = '[BLOQUEADA - VIRTUAL/MOVIL]';
            log.push(`${device.label} -> ${state}`);
            continue;
        }

        if (HARDWARE_PROFILE.preferred.some(pref => label.includes(pref))) {
            bestDeviceId = device.deviceId;
            state = '[ACEPTADA - PREFERIDA]';
            log.push(`${device.label} -> ${state}`);
            break;
        }

        if (!bestDeviceId) {
            bestDeviceId = device.deviceId;
            state = '[ACEPTADA - GENÉRICA]';
        }
        log.push(`${device.label} -> ${state}`);
    }

    if (!bestDeviceId) {
        statusEl.innerHTML = `<span style="color:red">ACCESO DENEGADO. DISPOSITIVOS RECHAZADOS:</span><br>` +
            log.map(l => `<div style="font-size:0.8em; color:#555;">${l}</div>`).join('');
        return null;
    }

    statusEl.innerText = '[ENLACE] INICIANDO STREAM SEGURO...';
    const stream = await navigator.mediaDevices.getUserMedia({
        video: {
            deviceId: { exact: bestDeviceId },
            width: { ideal: 640 },
            height: { ideal: 480 }
        }
    });

    streamReference = stream;
    videoEl.srcObject = stream;
    statusEl.innerText = 'SISTEMA ACTIVO. ALINEAR ROSTRO.';
    return stream;
}

export function getStream() {
    return streamReference;
}
