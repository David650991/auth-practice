export function finalizeEnrollment({ video, canvas, config, scanLine, instructionText }) {
    instructionText.innerText = 'GUARDANDO BIOMETRÍA...';

    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0);
    const dataURL = canvas.toDataURL('image/jpeg', 0.9);

    fetch(config.enrollUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': config.csrfToken },
        body: JSON.stringify({ image: dataURL })
    })
    .then(r => r.json())
    .then(data => {
        scanLine.style.display = 'none';
        if(data.error) {
            alert('Error final: ' + data.error);
            location.reload();
        } else {
            alert('¡REGISTRO COMPLETADO!');
            window.location.href = data.redirect;
        }
    })
    .catch(err => {
        console.error(err);
        alert('Error final: ' + err.message);
    });
}
