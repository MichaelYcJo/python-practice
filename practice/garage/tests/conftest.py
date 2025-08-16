"""
Pytest configuration and shared fixtures
Pytest 설정 및 공유 픽스처
"""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import pytest
from PIL import Image

from garage.config import Config, ProcessingConfig
from garage.pdf_processor import ProcessorFactory


@pytest.fixture(scope="session")
def event_loop():
    """세션 스코프 이벤트 루프"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir():
    """임시 디렉토리 픽스처"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def test_config():
    """테스트용 설정"""
    return Config()


@pytest.fixture
def processing_config():
    """테스트용 처리 설정"""
    return ProcessingConfig(
        dpi=300,
        language="eng",
        confidence_threshold=50,
        workers=2,  # 테스트에서는 적은 워커 사용
        cache_enabled=False  # 테스트에서는 캐시 비활성화
    )


@pytest.fixture
def mock_processor():
    """모킹된 프로세서"""
    processor = Mock()
    processor.config = ProcessingConfig()
    return processor


@pytest.fixture
def test_image():
    """테스트용 이미지"""
    # 100x100 흰색 이미지 생성
    img = Image.new('RGB', (100, 100), color='white')
    return img


@pytest.fixture
def test_pdf_path(temp_dir):
    """테스트용 PDF 파일 경로"""
    pdf_path = temp_dir / "test.pdf"
    # 빈 파일 생성 (실제 테스트에서는 유효한 PDF 생성 필요)
    pdf_path.touch()
    return pdf_path


@pytest.fixture
def mock_tesseract():
    """Tesseract 모킹"""
    with patch('garage.pdf_processor.pytesseract') as mock:
        # 기본 OCR 결과 설정
        mock.image_to_string.return_value = "Sample text"
        mock.image_to_data.return_value = {
            'text': ['Sample', 'text'],
            'conf': [85, 90],
            'left': [10, 60],
            'top': [20, 20],
            'width': [45, 35],
            'height': [15, 15]
        }
        mock.image_to_pdf_or_hocr.return_value = b"fake pdf bytes"
        yield mock


@pytest.fixture
def mock_pdf2image():
    """pdf2image 모킹"""
    with patch('garage.pdf_processor.convert_from_path') as mock:
        # 테스트 이미지 반환
        test_img = Image.new('RGB', (100, 100), color='white')
        mock.return_value = [test_img]
        yield mock


@pytest.fixture
def mock_pypdf():
    """pypdf 모킹"""
    with patch('garage.pdf_processor.PdfReader') as mock_reader, \
         patch('garage.pdf_processor.PdfWriter') as mock_writer:
        
        # Reader 모킹
        mock_reader_instance = Mock()
        mock_reader_instance.pages = [Mock() for _ in range(5)]  # 5페이지 PDF
        mock_reader.return_value = mock_reader_instance
        
        # Writer 모킹
        mock_writer_instance = Mock()
        mock_writer.return_value = mock_writer_instance
        
        yield mock_reader, mock_writer


@pytest.fixture
def mock_langdetect():
    """langdetect 모킹"""
    with patch('garage.pdf_processor.lang_detect') as mock:
        mock.return_value = 'en'
        yield mock


@pytest.fixture(autouse=True)
def setup_logging():
    """테스트용 로깅 설정"""
    import logging
    logging.getLogger().setLevel(logging.WARNING)  # 테스트 중 로그 최소화


@pytest.fixture
def mock_file_operations(temp_dir):
    """파일 연산 모킹"""
    class MockFileOps:
        def __init__(self, temp_dir):
            self.temp_dir = temp_dir
            self.created_files = []
        
        def create_pdf(self, name="test.pdf", pages=1):
            """테스트용 PDF 파일 생성"""
            pdf_path = self.temp_dir / name
            pdf_path.write_bytes(b"fake pdf content")
            self.created_files.append(pdf_path)
            return pdf_path
        
        def create_image(self, name="test.jpg", size=(100, 100)):
            """테스트용 이미지 파일 생성"""
            img_path = self.temp_dir / name
            img = Image.new('RGB', size, color='white')
            img.save(img_path)
            self.created_files.append(img_path)
            return img_path
        
        def cleanup(self):
            """생성된 파일들 정리"""
            for file_path in self.created_files:
                if file_path.exists():
                    file_path.unlink()
            self.created_files.clear()
    
    ops = MockFileOps(temp_dir)
    yield ops
    ops.cleanup()


# 테스트 마커 정의
pytest.mark.unit = pytest.mark.unit  # 단위 테스트
pytest.mark.integration = pytest.mark.integration  # 통합 테스트
pytest.mark.slow = pytest.mark.slow  # 시간이 오래 걸리는 테스트
pytest.mark.api = pytest.mark.api  # API 테스트


def pytest_configure(config):
    """Pytest 설정"""
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "slow: marks tests as slow running")
    config.addinivalue_line("markers", "api: marks tests as API tests")


def pytest_collection_modifyitems(config, items):
    """테스트 항목 수정"""
    for item in items:
        # 테스트 파일 이름에 따라 마커 자동 추가
        if "test_api" in item.nodeid:
            item.add_marker(pytest.mark.api)
        elif "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        else:
            item.add_marker(pytest.mark.unit)


# 커스텀 어설션
def assert_processing_result_valid(result):
    """처리 결과 유효성 검증"""
    from garage.pdf_processor import DocumentResult, ProcessingStatus
    
    assert isinstance(result, DocumentResult)
    assert result.file_path is not None
    assert result.total_pages >= 0
    assert result.processed_pages >= 0
    assert result.processed_pages <= result.total_pages
    assert isinstance(result.status, ProcessingStatus)
    assert result.processing_time >= 0


def assert_config_valid(config):
    """설정 유효성 검증"""
    from garage.config import Config
    
    assert isinstance(config, Config)
    assert config.ocr is not None
    assert config.image is not None
    assert config.processing is not None
    assert config.output is not None