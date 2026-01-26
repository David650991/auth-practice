"""
Tests para el módulo de encoders biométricos.
"""

import pytest
import numpy as np
import base64


class TestDecodeBase64Image:
    """Tests para decode_base64_image."""
    
    def test_decode_invalid_data_returns_none(self):
        from app.services.biometrics.encoders import decode_base64_image
        
        result_bgr, result_gray = decode_base64_image("not-valid-base64!")
        
        assert result_bgr is None
        assert result_gray is None
    
    def test_decode_empty_string_returns_none(self):
        from app.services.biometrics.encoders import decode_base64_image
        
        result_bgr, result_gray = decode_base64_image("")
        
        assert result_bgr is None
        assert result_gray is None
    
    def test_decode_with_data_uri_prefix(self):
        from app.services.biometrics.encoders import decode_base64_image
        
        # Imagen 1x1 pixel PNG válida en base64
        valid_png = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        
        result_bgr, result_gray = decode_base64_image(valid_png)
        
        assert result_bgr is not None
        assert result_gray is not None
        assert isinstance(result_bgr, np.ndarray)
        assert isinstance(result_gray, np.ndarray)


class TestDetectFaces:
    """Tests para detect_faces."""
    
    def test_detect_faces_empty_image_returns_empty(self):
        from app.services.biometrics.encoders import detect_faces
        
        # Imagen negra sin rostros
        empty_image = np.zeros((100, 100), dtype=np.uint8)
        
        boxes = detect_faces(empty_image)
        
        assert boxes == []
    
    def test_detect_faces_returns_list(self):
        from app.services.biometrics.encoders import detect_faces
        
        gray_image = np.zeros((100, 100), dtype=np.uint8)
        
        result = detect_faces(gray_image)
        
        assert isinstance(result, list)


class TestExtractFaceEncodings:
    """Tests para extract_face_encodings."""
    
    def test_extract_with_no_boxes_returns_empty(self):
        from app.services.biometrics.encoders import extract_face_encodings
        
        dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        encodings = extract_face_encodings(dummy_image, [])
        
        assert encodings == []
