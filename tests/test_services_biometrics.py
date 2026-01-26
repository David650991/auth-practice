import types

from app.services import biometrics


def test_pipelines_module_exposes_functions():
    assert hasattr(biometrics.pipelines, 'enroll_biometric_pipeline')
    assert hasattr(biometrics.pipelines, 'login_biometric_pipeline')
    assert hasattr(biometrics.pipelines, 'validate_pose_challenge')


def test_validate_pose_handles_invalid_image(monkeypatch):
    def fake_decode(image):
        return None, None

    monkeypatch.setattr(biometrics.encoders, 'decode_base64_image', fake_decode)
    ok, msg = biometrics.pipelines.validate_pose_challenge('nope', 'CENTER')
    assert ok is False
    assert msg
