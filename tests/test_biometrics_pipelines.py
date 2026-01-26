"""
Tests para el módulo de pipelines biométricos.
"""

import pytest


class TestEnrollBiometricPipeline:
    """Tests para enroll_biometric_pipeline."""
    
    def test_enroll_with_invalid_image_returns_error(self):
        from app.services.biometrics.pipelines import enroll_biometric_pipeline
        
        success, message, encoding = enroll_biometric_pipeline("invalid-data")
        
        assert success is False
        assert encoding is None
        assert "corrupta" in message.lower() or "no detectado" in message.lower()
    
    def test_enroll_with_empty_string_returns_error(self):
        from app.services.biometrics.pipelines import enroll_biometric_pipeline
        
        success, message, encoding = enroll_biometric_pipeline("")
        
        assert success is False
        assert encoding is None


class TestLoginBiometricPipeline:
    """Tests para login_biometric_pipeline."""
    
    def test_login_with_invalid_image_returns_error(self):
        from app.services.biometrics.pipelines import login_biometric_pipeline
        
        success, message, user = login_biometric_pipeline("invalid-data")
        
        assert success is False
        assert user is None
    
    def test_login_with_custom_tolerance(self):
        from app.services.biometrics.pipelines import login_biometric_pipeline
        
        success, message, user = login_biometric_pipeline("invalid", tolerance=0.6)
        
        assert success is False


class TestValidatePoseChallenge:
    """Tests para validate_pose_challenge."""
    
    def test_validate_pose_with_invalid_image(self):
        from app.services.biometrics.pipelines import validate_pose_challenge
        
        valid, message = validate_pose_challenge("invalid-image", "CENTER")
        
        assert valid is False
        assert message != ""
    
    def test_validate_pose_with_empty_image(self):
        from app.services.biometrics.pipelines import validate_pose_challenge
        
        valid, message = validate_pose_challenge("", "LEFT")
        
        assert valid is False
