def test_login_page_renders(client):
    resp = client.get('/login')
    assert resp.status_code == 200
    assert b"Acceso Seguro" in resp.data


def test_register_page_renders(client):
    resp = client.get('/register')
    assert resp.status_code == 200
    assert b"Registro Blindado" in resp.data
