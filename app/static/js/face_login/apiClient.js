export async function sendLogin(imageData, csrfToken) {
    const res = await fetch('/face-login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ image: imageData })
    });
    const payload = await res.json();
    payload.httpStatus = res.status;
    return payload;
}
