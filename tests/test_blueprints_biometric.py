def test_face_login_page_accessible(client):
    resp = client.get('/face-login-page')
    assert resp.status_code == 200
    assert b"Acceso Biom" in resp.data  # "Acceso Biométrico" en UTF-8


def test_face_enroll_requires_login(client):
    resp = client.get('/face-enroll-page')
    # Flask-Login redirects to login when unauthenticated
    assert resp.status_code in (301, 302)
