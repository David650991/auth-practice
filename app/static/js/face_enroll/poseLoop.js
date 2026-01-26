const SEQUENCE = ['CENTER', 'LEFT', 'RIGHT', 'UP', 'CENTER'];
const MESSAGES = {
    'CENTER': 'MIRA AL FRENTE',
    'LEFT': 'GIRA LENTAMENTE A LA IZQUIERDA ⬅️',
    'RIGHT': 'GIRA LENTAMENTE A LA DERECHA ➡️',
    'UP': 'MIRA HACIA EL TECHO ⬆️'
};

export function runPoseChallenge({
    challengeStepRef,
    advanceStep,
    canvas,
    video,
    instructionText,
    config,
    onComplete,
}) {
    const step = challengeStepRef();
    if (step >= SEQUENCE.length) {
        onComplete();
        return;
    }

    const currentPose = SEQUENCE[step];
    instructionText.innerText = MESSAGES[currentPose] || 'MANTÉN LA POSICIÓN';
    instructionText.style.color = '#004085';

    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0);
    const dataURL = canvas.toDataURL('image/jpeg', 0.8);

    fetch('/check-pose', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': config.csrfToken },
        body: JSON.stringify({ image: dataURL, pose: currentPose })
    })
        .then(r => r.json())
        .then(data => {
            if (data.valid) {
                instructionText.innerText = '✅ CORRECTO';
                instructionText.style.color = 'green';
                advanceStep();
                setTimeout(() => runPoseChallenge({ challengeStepRef, advanceStep, canvas, video, instructionText, config, onComplete }), 1000);
            } else {
                instructionText.innerText = `⚠️ ${data.message}`;
                instructionText.style.color = '#d32f2f';
                setTimeout(() => runPoseChallenge({ challengeStepRef, advanceStep, canvas, video, instructionText, config, onComplete }), 500);
            }
        })
        .catch(err => {
            console.error(err);
            setTimeout(() => runPoseChallenge({ challengeStepRef, advanceStep, canvas, video, instructionText, config, onComplete }), 1000);
        });
}
