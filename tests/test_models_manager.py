"""
Tests para el gestor de modelos ML.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestModelsDirectory:
    """Tests para gestión de directorio de modelos."""
    
    def test_ensure_models_directory_creates_dir(self, tmp_path):
        from app import models_manager
        
        original_dir = models_manager.MODELS_DIR
        models_manager.MODELS_DIR = tmp_path / 'test_models'
        
        models_manager.ensure_models_directory()
        
        assert models_manager.MODELS_DIR.exists()
        models_manager.MODELS_DIR = original_dir


class TestModelPresence:
    """Tests para verificación de presencia de modelos."""
    
    def test_is_model_present_returns_false_when_missing(self, tmp_path):
        from app import models_manager
        
        original_dir = models_manager.MODELS_DIR
        models_manager.MODELS_DIR = tmp_path
        
        result = models_manager.is_model_present('nonexistent.dat')
        
        assert result is False
        models_manager.MODELS_DIR = original_dir
    
    def test_is_model_present_returns_true_when_exists(self, tmp_path):
        from app import models_manager
        
        original_dir = models_manager.MODELS_DIR
        models_manager.MODELS_DIR = tmp_path
        
        # Crear archivo dummy
        (tmp_path / 'test_model.dat').touch()
        
        result = models_manager.is_model_present('test_model.dat')
        
        assert result is True
        models_manager.MODELS_DIR = original_dir


class TestDlibModelDownload:
    """Tests para descarga del modelo Dlib."""
    
    def test_download_skips_if_model_exists(self, tmp_path):
        from app import models_manager
        
        original_dir = models_manager.MODELS_DIR
        models_manager.MODELS_DIR = tmp_path
        
        # Crear modelo dummy
        (tmp_path / models_manager.DLIB_MODEL['filename']).write_bytes(b'dummy')
        
        result = models_manager.download_dlib_model()
        
        assert result is True
        models_manager.MODELS_DIR = original_dir
    
    @patch('urllib.request.urlretrieve')
    def test_download_handles_network_error(self, mock_urlretrieve, tmp_path):
        from app import models_manager
        
        original_dir = models_manager.MODELS_DIR
        models_manager.MODELS_DIR = tmp_path
        
        mock_urlretrieve.side_effect = Exception("Network error")
        
        result = models_manager.download_dlib_model()
        
        assert result is False
        models_manager.MODELS_DIR = original_dir
