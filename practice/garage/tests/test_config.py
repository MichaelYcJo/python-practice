"""
Configuration management tests
설정 관리 테스트
"""

import json
import tempfile
from pathlib import Path
import pytest

from garage.config import (
    Config, ConfigManager, OCRSettings, ImageSettings, 
    ProcessingSettings, OutputSettings, CacheSettings, 
    LoggingSettings, SecuritySettings, APISettings
)


class TestConfigClasses:
    """설정 클래스 테스트"""
    
    def test_ocr_settings_defaults(self):
        """OCR 설정 기본값 테스트"""
        settings = OCRSettings()
        assert settings.default_language == "auto"
        assert settings.confidence_threshold == 50
        assert "eng" in settings.supported_languages
        assert "auto" in settings.supported_languages
    
    def test_image_settings_defaults(self):
        """이미지 설정 기본값 테스트"""
        settings = ImageSettings()
        assert settings.default_dpi == 300
        assert not settings.auto_dpi_enabled
        assert 200 in settings.dpi_candidates
        assert 300 in settings.dpi_candidates
    
    def test_processing_settings_defaults(self):
        """처리 설정 기본값 테스트"""
        settings = ProcessingSettings()
        assert settings.max_workers > 0
        assert settings.batch_size == 10
        assert settings.timeout_per_page == 300
        assert settings.resume_enabled
    
    def test_security_settings_file_validation(self):
        """보안 설정 파일 검증 테스트"""
        settings = SecuritySettings()
        
        # 허용된 파일 확장자
        assert settings.is_allowed_file(Path("test.pdf"))
        assert settings.is_allowed_file(Path("test.jpg"))
        assert settings.is_allowed_file(Path("test.PNG"))
        
        # 허용되지 않은 파일 확장자
        assert not settings.is_allowed_file(Path("test.exe"))
        assert not settings.is_allowed_file(Path("test.txt"))


class TestConfigManager:
    """설정 관리자 테스트"""
    
    def test_config_creation(self):
        """설정 생성 테스트"""
        config = Config()
        assert isinstance(config.ocr, OCRSettings)
        assert isinstance(config.image, ImageSettings)
        assert isinstance(config.processing, ProcessingSettings)
        assert isinstance(config.output, OutputSettings)
        assert isinstance(config.cache, CacheSettings)
        assert isinstance(config.logging, LoggingSettings)
        assert isinstance(config.security, SecuritySettings)
        assert isinstance(config.api, APISettings)
    
    def test_config_save_load(self):
        """설정 저장/로드 테스트"""
        manager = ConfigManager()
        original_config = Config()
        
        # 설정 값 변경
        original_config.ocr.default_language = "kor"
        original_config.image.default_dpi = 400
        original_config.processing.max_workers = 8
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            # 저장
            manager.save_config(original_config, temp_path)
            assert temp_path.exists()
            
            # 로드
            loaded_config = manager.load_config(temp_path)
            
            # 검증
            assert loaded_config.ocr.default_language == "kor"
            assert loaded_config.image.default_dpi == 400
            assert loaded_config.processing.max_workers == 8
            
        finally:
            if temp_path.exists():
                temp_path.unlink()
    
    def test_config_validation(self):
        """설정 검증 테스트"""
        manager = ConfigManager()
        config = Config()
        
        # 유효한 설정
        errors = manager.validate_config(config)
        assert len(errors) == 0
        
        # 잘못된 설정
        config.ocr.confidence_threshold = 150  # 100 초과
        config.image.default_dpi = 10  # 50 미만
        config.processing.max_workers = 0  # 1 미만
        
        errors = manager.validate_config(config)
        assert len(errors) > 0
        assert any("confidence" in error for error in errors)
        assert any("DPI" in error for error in errors)
        assert any("workers" in error for error in errors)
    
    def test_sample_config_creation(self):
        """샘플 설정 생성 테스트"""
        manager = ConfigManager()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            manager.create_sample_config(temp_path)
            assert temp_path.exists()
            
            # JSON 파싱 가능한지 확인
            with open(temp_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            assert 'ocr' in data
            assert 'image' in data
            assert 'processing' in data
            
        finally:
            if temp_path.exists():
                temp_path.unlink()


class TestEnvironmentOverrides:
    """환경 변수 오버라이드 테스트"""
    
    def test_env_override(self, monkeypatch):
        """환경 변수 오버라이드 테스트"""
        # 환경 변수 설정
        monkeypatch.setenv("OCR_LANGUAGE", "kor")
        monkeypatch.setenv("IMAGE_DPI", "400")
        monkeypatch.setenv("MAX_WORKERS", "8")
        monkeypatch.setenv("CACHE_ENABLED", "false")
        
        manager = ConfigManager()
        config = manager._load_from_env()
        
        assert config.ocr.default_language == "kor"
        assert config.image.default_dpi == 400
        assert config.processing.max_workers == 8
        assert not config.cache.enabled


if __name__ == "__main__":
    pytest.main([__file__, "-v"])