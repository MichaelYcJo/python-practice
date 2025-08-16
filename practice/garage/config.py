"""
Configuration Management System
설정 관리 시스템
"""

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging


@dataclass
class OCRSettings:
    """OCR 관련 설정"""
    default_language: str = "auto"
    confidence_threshold: int = 50
    tesseract_path: Optional[str] = None  # Windows용
    supported_languages: List[str] = None
    
    def __post_init__(self):
        if self.supported_languages is None:
            self.supported_languages = ["eng", "kor", "jpn", "chi_sim", "auto"]


@dataclass
class ImageSettings:
    """이미지 처리 설정"""
    default_dpi: int = 300
    auto_dpi_enabled: bool = False
    dpi_candidates: List[int] = None
    preprocessing_enabled: bool = True
    binarization_threshold: int = 140
    
    def __post_init__(self):
        if self.dpi_candidates is None:
            self.dpi_candidates = [200, 300, 400, 500]


@dataclass
class ProcessingSettings:
    """처리 관련 설정"""
    max_workers: int = 4
    batch_size: int = 10
    timeout_per_page: int = 300  # 초
    memory_limit_mb: int = 2048
    resume_enabled: bool = True
    
    def __post_init__(self):
        # CPU 코어 수를 기준으로 기본 워커 수 설정
        if self.max_workers <= 0:
            self.max_workers = min(os.cpu_count() or 4, 8)


@dataclass
class OutputSettings:
    """출력 관련 설정"""
    save_json: bool = False
    keep_checkpoints: bool = False
    output_directory: str = "./output"
    filename_template: str = "{stem}_searchable.pdf"
    compression_enabled: bool = True
    
    def get_output_path(self, input_path: Path) -> Path:
        """출력 파일 경로 생성"""
        output_dir = Path(self.output_directory)
        filename = self.filename_template.format(
            stem=input_path.stem,
            name=input_path.name
        )
        return output_dir / filename


@dataclass
class CacheSettings:
    """캐시 관련 설정"""
    enabled: bool = True
    ttl_seconds: int = 86400  # 24시간
    max_size_mb: int = 512
    cache_directory: str = "./.cache"
    
    def get_cache_path(self) -> Path:
        """캐시 디렉토리 경로"""
        return Path(self.cache_directory)


@dataclass
class LoggingSettings:
    """로깅 관련 설정"""
    level: str = "INFO"
    format: str = "%(asctime)s | %(levelname)s | %(message)s"
    file_enabled: bool = True
    console_enabled: bool = True
    log_directory: str = "./logs"
    max_file_size_mb: int = 10
    backup_count: int = 5
    
    def get_log_path(self) -> Path:
        """로그 디렉토리 경로"""
        return Path(self.log_directory)


@dataclass
class SecuritySettings:
    """보안 관련 설정"""
    max_file_size_mb: int = 500
    allowed_extensions: List[str] = None
    scan_for_malware: bool = False
    temp_directory: str = "./temp"
    
    def __post_init__(self):
        if self.allowed_extensions is None:
            self.allowed_extensions = [".pdf", ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"]
    
    def is_allowed_file(self, file_path: Path) -> bool:
        """파일 확장자 검증"""
        return file_path.suffix.lower() in self.allowed_extensions
    
    def is_file_size_valid(self, file_path: Path) -> bool:
        """파일 크기 검증"""
        size_mb = file_path.stat().st_size / (1024 * 1024)
        return size_mb <= self.max_file_size_mb


@dataclass
class APISettings:
    """API 관련 설정"""
    enabled: bool = False
    host: str = "127.0.0.1"
    port: int = 8000
    workers: int = 1
    cors_enabled: bool = True
    rate_limit_enabled: bool = True
    requests_per_minute: int = 60
    auth_required: bool = False
    api_key: Optional[str] = None


@dataclass
class Config:
    """메인 설정 클래스"""
    ocr: OCRSettings = None
    image: ImageSettings = None
    processing: ProcessingSettings = None
    output: OutputSettings = None
    cache: CacheSettings = None
    logging: LoggingSettings = None
    security: SecuritySettings = None
    api: APISettings = None
    
    def __post_init__(self):
        if self.ocr is None:
            self.ocr = OCRSettings()
        if self.image is None:
            self.image = ImageSettings()
        if self.processing is None:
            self.processing = ProcessingSettings()
        if self.output is None:
            self.output = OutputSettings()
        if self.cache is None:
            self.cache = CacheSettings()
        if self.logging is None:
            self.logging = LoggingSettings()
        if self.security is None:
            self.security = SecuritySettings()
        if self.api is None:
            self.api = APISettings()


class ConfigManager:
    """설정 관리자"""
    
    DEFAULT_CONFIG_PATHS = [
        Path("./config.json"),
        Path("~/.pdf_processor/config.json").expanduser(),
        Path("/etc/pdf_processor/config.json")
    ]
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path
        self.config = Config()
        self.logger = self._setup_logger()
    
    def load_config(self, config_path: Optional[Path] = None) -> Config:
        """설정 파일 로드"""
        if config_path:
            return self._load_from_file(config_path)
        
        # 환경 변수에서 설정 파일 경로 확인
        env_config_path = os.getenv('PDF_PROCESSOR_CONFIG')
        if env_config_path:
            return self._load_from_file(Path(env_config_path))
        
        # 기본 경로들에서 설정 파일 찾기
        for path in self.DEFAULT_CONFIG_PATHS:
            if path.exists():
                self.logger.info(f"설정 파일 발견: {path}")
                return self._load_from_file(path)
        
        # 설정 파일이 없으면 기본 설정 사용
        self.logger.info("설정 파일을 찾을 수 없어 기본 설정을 사용합니다.")
        return self._load_from_env()
    
    def _load_from_file(self, config_path: Path) -> Config:
        """파일에서 설정 로드"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            config = self._dict_to_config(data)
            
            # 환경 변수로 오버라이드
            config = self._apply_env_overrides(config)
            
            self.logger.info(f"설정 파일 로드 완료: {config_path}")
            return config
            
        except Exception as e:
            self.logger.warning(f"설정 파일 로드 실패 ({config_path}): {e}")
            return self._load_from_env()
    
    def _load_from_env(self) -> Config:
        """환경 변수에서 설정 로드"""
        config = Config()
        return self._apply_env_overrides(config)
    
    def _apply_env_overrides(self, config: Config) -> Config:
        """환경 변수로 설정 오버라이드"""
        # OCR 설정
        if os.getenv('OCR_LANGUAGE'):
            config.ocr.default_language = os.getenv('OCR_LANGUAGE')
        if os.getenv('OCR_CONFIDENCE'):
            config.ocr.confidence_threshold = int(os.getenv('OCR_CONFIDENCE'))
        if os.getenv('TESSERACT_PATH'):
            config.ocr.tesseract_path = os.getenv('TESSERACT_PATH')
        
        # 이미지 설정
        if os.getenv('IMAGE_DPI'):
            config.image.default_dpi = int(os.getenv('IMAGE_DPI'))
        if os.getenv('AUTO_DPI'):
            config.image.auto_dpi_enabled = os.getenv('AUTO_DPI').lower() == 'true'
        
        # 처리 설정
        if os.getenv('MAX_WORKERS'):
            config.processing.max_workers = int(os.getenv('MAX_WORKERS'))
        if os.getenv('BATCH_SIZE'):
            config.processing.batch_size = int(os.getenv('BATCH_SIZE'))
        
        # 출력 설정
        if os.getenv('OUTPUT_DIR'):
            config.output.output_directory = os.getenv('OUTPUT_DIR')
        if os.getenv('SAVE_JSON'):
            config.output.save_json = os.getenv('SAVE_JSON').lower() == 'true'
        
        # 캐시 설정
        if os.getenv('CACHE_ENABLED'):
            config.cache.enabled = os.getenv('CACHE_ENABLED').lower() == 'true'
        if os.getenv('CACHE_TTL'):
            config.cache.ttl_seconds = int(os.getenv('CACHE_TTL'))
        
        # API 설정
        if os.getenv('API_ENABLED'):
            config.api.enabled = os.getenv('API_ENABLED').lower() == 'true'
        if os.getenv('API_HOST'):
            config.api.host = os.getenv('API_HOST')
        if os.getenv('API_PORT'):
            config.api.port = int(os.getenv('API_PORT'))
        
        return config
    
    def save_config(self, config: Config, config_path: Optional[Path] = None) -> None:
        """설정을 파일에 저장"""
        if not config_path:
            config_path = self.config_path or self.DEFAULT_CONFIG_PATHS[0]
        
        # 디렉토리 생성
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 설정을 딕셔너리로 변환
        config_dict = self._config_to_dict(config)
        
        # JSON 파일로 저장
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"설정 파일 저장 완료: {config_path}")
    
    def _dict_to_config(self, data: Dict[str, Any]) -> Config:
        """딕셔너리를 Config 객체로 변환"""
        config = Config()
        
        if 'ocr' in data:
            config.ocr = OCRSettings(**data['ocr'])
        if 'image' in data:
            config.image = ImageSettings(**data['image'])
        if 'processing' in data:
            config.processing = ProcessingSettings(**data['processing'])
        if 'output' in data:
            config.output = OutputSettings(**data['output'])
        if 'cache' in data:
            config.cache = CacheSettings(**data['cache'])
        if 'logging' in data:
            config.logging = LoggingSettings(**data['logging'])
        if 'security' in data:
            config.security = SecuritySettings(**data['security'])
        if 'api' in data:
            config.api = APISettings(**data['api'])
        
        return config
    
    def _config_to_dict(self, config: Config) -> Dict[str, Any]:
        """Config 객체를 딕셔너리로 변환"""
        return {
            'ocr': asdict(config.ocr),
            'image': asdict(config.image),
            'processing': asdict(config.processing),
            'output': asdict(config.output),
            'cache': asdict(config.cache),
            'logging': asdict(config.logging),
            'security': asdict(config.security),
            'api': asdict(config.api)
        }
    
    def validate_config(self, config: Config) -> List[str]:
        """설정 유효성 검증"""
        errors = []
        
        # OCR 설정 검증
        if config.ocr.confidence_threshold < 0 or config.ocr.confidence_threshold > 100:
            errors.append("OCR confidence threshold must be between 0 and 100")
        
        # 이미지 설정 검증
        if config.image.default_dpi < 50 or config.image.default_dpi > 1000:
            errors.append("Image DPI must be between 50 and 1000")
        
        # 처리 설정 검증
        if config.processing.max_workers < 1:
            errors.append("Max workers must be at least 1")
        
        # 보안 설정 검증
        if config.security.max_file_size_mb < 1:
            errors.append("Max file size must be at least 1 MB")
        
        # API 설정 검증
        if config.api.enabled:
            if config.api.port < 1 or config.api.port > 65535:
                errors.append("API port must be between 1 and 65535")
        
        return errors
    
    def _setup_logger(self) -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def create_sample_config(self, output_path: Path) -> None:
        """샘플 설정 파일 생성"""
        sample_config = Config()
        
        # 샘플용 설정 조정
        sample_config.ocr.default_language = "auto"
        sample_config.image.auto_dpi_enabled = True
        sample_config.processing.max_workers = 4
        sample_config.output.save_json = True
        sample_config.cache.enabled = True
        sample_config.api.enabled = False
        
        self.save_config(sample_config, output_path)
        self.logger.info(f"샘플 설정 파일 생성: {output_path}")


# 편의 함수들
def load_config(config_path: Optional[Path] = None) -> Config:
    """설정 로드 편의 함수"""
    manager = ConfigManager()
    return manager.load_config(config_path)


def create_sample_config(output_path: Path = Path("./config.json")) -> None:
    """샘플 설정 생성 편의 함수"""
    manager = ConfigManager()
    manager.create_sample_config(output_path)


# CLI용 설정 생성
def config_from_args(args) -> Config:
    """argparse 결과에서 설정 생성"""
    config = Config()
    
    # 기본 설정 로드
    if hasattr(args, 'config') and args.config:
        manager = ConfigManager()
        config = manager.load_config(Path(args.config))
    
    # 명령행 인수로 오버라이드
    if hasattr(args, 'lang') and args.lang:
        config.ocr.default_language = args.lang
    if hasattr(args, 'dpi') and args.dpi:
        config.image.default_dpi = args.dpi
    if hasattr(args, 'auto_dpi') and args.auto_dpi:
        config.image.auto_dpi_enabled = args.auto_dpi
    if hasattr(args, 'conf') and args.conf:
        config.ocr.confidence_threshold = args.conf
    if hasattr(args, 'workers') and args.workers:
        config.processing.max_workers = args.workers
    if hasattr(args, 'save_json') and args.save_json:
        config.output.save_json = args.save_json
    if hasattr(args, 'outdir') and args.outdir:
        config.output.output_directory = args.outdir
    
    return config


if __name__ == "__main__":
    # 설정 테스트
    manager = ConfigManager()
    
    # 샘플 설정 생성
    sample_path = Path("./sample_config.json")
    manager.create_sample_config(sample_path)
    
    # 설정 로드 테스트
    config = manager.load_config(sample_path)
    print("설정 로드 완료:")
    print(f"  OCR 언어: {config.ocr.default_language}")
    print(f"  기본 DPI: {config.image.default_dpi}")
    print(f"  최대 워커: {config.processing.max_workers}")
    
    # 유효성 검증
    errors = manager.validate_config(config)
    if errors:
        print("설정 오류:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("설정 유효성 검증 통과")