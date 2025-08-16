"""
PDF Processor tests
PDF 처리기 테스트
"""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import pytest
from PIL import Image

from garage.pdf_processor import (
    PDFProcessor, OCRProcessor, ProcessorFactory, 
    ProcessingConfig, ProcessingStatus, WordData, 
    PageResult, DocumentResult, ImagePreprocessor,
    LanguageDetector, DPIOptimizer, CheckpointManager,
    MemoryCache
)


class TestProcessingConfig:
    """처리 설정 테스트"""
    
    def test_default_config(self):
        """기본 설정 테스트"""
        config = ProcessingConfig()
        assert config.dpi == 300
        assert config.language == "auto"
        assert config.confidence_threshold == 50
        assert config.workers == 4
        assert not config.auto_dpi
        assert not config.save_json
        assert config.resume
        assert not config.keep_checkpoints
    
    def test_custom_config(self):
        """커스텀 설정 테스트"""
        config = ProcessingConfig(
            dpi=400,
            language="kor",
            confidence_threshold=70,
            workers=8,
            auto_dpi=True,
            save_json=True
        )
        assert config.dpi == 400
        assert config.language == "kor"
        assert config.confidence_threshold == 70
        assert config.workers == 8
        assert config.auto_dpi
        assert config.save_json


class TestWordData:
    """단어 데이터 테스트"""
    
    def test_word_data_creation(self):
        """단어 데이터 생성 테스트"""
        word = WordData(
            text="Hello",
            confidence=85,
            bbox={"x": 10, "y": 20, "w": 50, "h": 15},
            page_number=1
        )
        assert word.text == "Hello"
        assert word.confidence == 85
        assert word.bbox["x"] == 10
        assert word.page_number == 1


class TestPageResult:
    """페이지 결과 테스트"""
    
    def test_successful_page_result(self):
        """성공한 페이지 결과 테스트"""
        words = [
            WordData("Hello", 85, {"x": 10, "y": 20, "w": 50, "h": 15}, 1),
            WordData("World", 90, {"x": 70, "y": 20, "w": 60, "h": 15}, 1)
        ]
        
        result = PageResult(
            page_number=1,
            status=ProcessingStatus.COMPLETED,
            words=words,
            language="eng",
            processing_time=2.5
        )
        
        assert result.page_number == 1
        assert result.status == ProcessingStatus.COMPLETED
        assert len(result.words) == 2
        assert result.language == "eng"
        assert result.processing_time == 2.5
        assert result.error_message is None
    
    def test_failed_page_result(self):
        """실패한 페이지 결과 테스트"""
        result = PageResult(
            page_number=2,
            status=ProcessingStatus.FAILED,
            error_message="OCR processing failed"
        )
        
        assert result.page_number == 2
        assert result.status == ProcessingStatus.FAILED
        assert len(result.words) == 0
        assert result.error_message == "OCR processing failed"


class TestMemoryCache:
    """메모리 캐시 테스트"""
    
    def test_cache_basic_operations(self):
        """캐시 기본 동작 테스트"""
        cache = MemoryCache()
        
        # 설정
        cache.set("key1", "value1")
        assert cache.exists("key1")
        assert cache.get("key1") == "value1"
        
        # 없는 키
        assert not cache.exists("key2")
        assert cache.get("key2") is None
        
        # 덮어쓰기
        cache.set("key1", "new_value")
        assert cache.get("key1") == "new_value"
        
        # 정리
        cache.clear()
        assert not cache.exists("key1")
    
    def test_cache_ttl(self):
        """캐시 TTL 테스트"""
        import time
        
        cache = MemoryCache()
        
        # TTL 설정
        cache.set("temp_key", "temp_value", ttl=1)
        assert cache.exists("temp_key")
        
        # TTL 만료 대기 (실제 테스트에서는 mock 사용 권장)
        time.sleep(1.1)
        assert not cache.exists("temp_key")


class TestImagePreprocessor:
    """이미지 전처리기 테스트"""
    
    def test_preprocessing_enabled(self):
        """전처리 활성화 테스트"""
        config = ProcessingConfig(preprocessing_enabled=True)
        preprocessor = ImagePreprocessor(config)
        
        # 테스트용 이미지 생성
        img = Image.new('RGB', (100, 100), color='white')
        
        # 전처리 실행
        processed = preprocessor.preprocess(img)
        
        # 이미지가 변경되었는지 확인
        assert processed is not None
        assert processed.mode in ['L', '1']  # 그레이스케일 또는 이진화
    
    def test_preprocessing_disabled(self):
        """전처리 비활성화 테스트"""
        config = ProcessingConfig(preprocessing_enabled=False)
        preprocessor = ImagePreprocessor(config)
        
        img = Image.new('RGB', (100, 100), color='white')
        processed = preprocessor.preprocess(img)
        
        # 원본 이미지와 동일해야 함
        assert processed is img


class TestLanguageDetector:
    """언어 감지기 테스트"""
    
    @patch('garage.pdf_processor.lang_detect')
    @patch('garage.pdf_processor.pytesseract.image_to_string')
    def test_language_detection(self, mock_ocr, mock_lang_detect):
        """언어 감지 테스트"""
        # Mock 설정
        mock_ocr.return_value = "Hello World"
        mock_lang_detect.return_value = "en"
        
        img = Image.new('RGB', (100, 100), color='white')
        result = LanguageDetector.detect_language(img)
        
        assert result == "eng"  # en -> eng 매핑
    
    @patch('garage.pdf_processor.lang_detect', None)
    def test_language_detection_fallback(self):
        """언어 감지 폴백 테스트"""
        img = Image.new('RGB', (100, 100), color='white')
        result = LanguageDetector.detect_language(img, fallback="kor")
        
        assert result == "kor"


class TestCheckpointManager:
    """체크포인트 관리자 테스트"""
    
    def test_checkpoint_directory_creation(self):
        """체크포인트 디렉토리 생성 테스트"""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            manager = CheckpointManager(base_dir)
            
            checkpoint_path = manager.create_checkpoint_dir("test_doc")
            
            assert checkpoint_path.exists()
            assert checkpoint_path.is_dir()
            assert "test_doc" in str(checkpoint_path)
    
    def test_manifest_save_load(self):
        """매니페스트 저장/로드 테스트"""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir)
            manager = CheckpointManager(base_dir)
            checkpoint_path = manager.create_checkpoint_dir("test_doc")
            
            # 매니페스트 데이터
            manifest = {
                "file": "test.pdf",
                "total_pages": 10,
                "completed_pages": [1, 2, 3]
            }
            
            # 저장
            manager.save_manifest(checkpoint_path, manifest)
            
            # 로드
            loaded_manifest = manager.load_manifest(checkpoint_path)
            
            assert loaded_manifest == manifest
            assert loaded_manifest["total_pages"] == 10
            assert len(loaded_manifest["completed_pages"]) == 3


class TestProcessorFactory:
    """프로세서 팩토리 테스트"""
    
    def test_processor_creation(self):
        """프로세서 생성 테스트"""
        config = ProcessingConfig()
        processor = ProcessorFactory.create_processor(config)
        
        assert isinstance(processor, PDFProcessor)
        assert processor.config == config
    
    def test_config_creation(self):
        """설정 생성 테스트"""
        config = ProcessorFactory.create_config(
            dpi=400,
            language="kor",
            workers=8
        )
        
        assert isinstance(config, ProcessingConfig)
        assert config.dpi == 400
        assert config.language == "kor"
        assert config.workers == 8


class TestOCRProcessor:
    """OCR 프로세서 테스트"""
    
    @patch('garage.pdf_processor.pytesseract.image_to_data')
    def test_extract_words(self, mock_ocr_data):
        """단어 추출 테스트"""
        # Mock OCR 데이터
        mock_ocr_data.return_value = {
            'text': ['Hello', 'World', ''],
            'conf': [85, 90, -1],
            'left': [10, 70, 0],
            'top': [20, 20, 0],
            'width': [50, 60, 0],
            'height': [15, 15, 0]
        }
        
        config = ProcessingConfig(confidence_threshold=50)
        processor = OCRProcessor(config)
        
        img = Image.new('RGB', (100, 100), color='white')
        words = processor._extract_words(img, "eng", 1)
        
        # 신뢰도 50 이상인 단어만 추출
        assert len(words) == 2
        assert words[0].text == "Hello"
        assert words[0].confidence == 85
        assert words[1].text == "World"
        assert words[1].confidence == 90


class TestAsyncProcessing:
    """비동기 처리 테스트"""
    
    @pytest.mark.asyncio
    async def test_document_processing_mock(self):
        """문서 처리 모킹 테스트"""
        config = ProcessingConfig()
        
        with patch('garage.pdf_processor.convert_from_path') as mock_convert, \
             patch.object(OCRProcessor, 'process_image') as mock_process:
            
            # Mock 설정
            mock_convert.return_value = [Image.new('RGB', (100, 100), color='white')]
            mock_process.return_value = PageResult(
                page_number=1,
                status=ProcessingStatus.COMPLETED,
                words=[],
                language="eng"
            )
            
            processor = ProcessorFactory.create_processor(config)
            
            # 임시 파일 생성
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_path = Path(temp_file.name)
            
            try:
                with tempfile.TemporaryDirectory() as output_dir:
                    # DPI 최적화를 비활성화하여 테스트 단순화
                    with patch.object(processor.dpi_optimizer, 'find_optimal_dpi', return_value=300), \
                         patch.object(processor.dpi_optimizer, '_get_pdf_page_count', return_value=1):
                        
                        result = await processor.process_document(temp_path, Path(output_dir))
                        
                        assert isinstance(result, DocumentResult)
                        assert result.file_path == temp_path
            finally:
                if temp_path.exists():
                    temp_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])