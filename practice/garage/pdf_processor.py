"""
Enhanced PDF OCR Processing System
개선된 PDF OCR 처리 시스템 - 클래스 기반 아키텍처
"""

import asyncio
import hashlib
import json
import logging
import time
from abc import ABC, abstractmethod
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any, Protocol
from io import BytesIO

import pytesseract
from PIL import Image, ImageOps
from pdf2image import convert_from_path
from pypdf import PdfReader, PdfWriter
from tqdm import tqdm

try:
    from langdetect import detect as lang_detect
except ImportError:
    lang_detect = None


class ProcessingStatus(Enum):
    """처리 상태 열거형"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ProcessingConfig:
    """처리 설정 클래스"""
    dpi: int = 300
    language: str = "auto"
    confidence_threshold: int = 50
    workers: int = 4
    auto_dpi: bool = False
    save_json: bool = False
    resume: bool = True
    keep_checkpoints: bool = False
    cache_enabled: bool = True
    cache_ttl: int = 86400  # 24시간
    preprocessing_enabled: bool = True
    binarization_threshold: int = 140


@dataclass
class WordData:
    """OCR 단어 데이터"""
    text: str
    confidence: int
    bbox: Dict[str, int]
    page_number: int


@dataclass
class PageResult:
    """페이지 처리 결과"""
    page_number: int
    status: ProcessingStatus
    words: List[WordData] = field(default_factory=list)
    language: str = "eng"
    processing_time: float = 0.0
    error_message: Optional[str] = None


@dataclass
class DocumentResult:
    """문서 처리 결과"""
    file_path: Path
    total_pages: int
    processed_pages: int
    status: ProcessingStatus
    pages: List[PageResult] = field(default_factory=list)
    processing_time: float = 0.0
    config: Optional[ProcessingConfig] = None


class CacheProtocol(Protocol):
    """캐시 인터페이스"""
    def get(self, key: str) -> Optional[Any]: ...
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None: ...
    def exists(self, key: str) -> bool: ...
    def clear(self) -> None: ...


class MemoryCache:
    """메모리 기반 캐시 구현"""
    
    def __init__(self):
        self._cache: Dict[str, Tuple[Any, float]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            value, expires = self._cache[key]
            if expires == 0 or time.time() < expires:
                return value
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        expires = time.time() + ttl if ttl else 0
        self._cache[key] = (value, expires)
    
    def exists(self, key: str) -> bool:
        return self.get(key) is not None
    
    def clear(self) -> None:
        self._cache.clear()


class ImagePreprocessor:
    """이미지 전처리 클래스"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
    
    def preprocess(self, image: Image.Image) -> Image.Image:
        """이미지 전처리 수행"""
        if not self.config.preprocessing_enabled:
            return image
        
        # 그레이스케일 변환
        if image.mode != 'L':
            image = ImageOps.grayscale(image)
        
        # 자동 대비 조정
        image = ImageOps.autocontrast(image)
        
        # 이진화
        image = image.point(
            lambda x: 0 if x < self.config.binarization_threshold else 255, 
            "1"
        )
        
        return image


class LanguageDetector:
    """언어 감지 클래스"""
    
    @staticmethod
    def detect_language(image: Image.Image, fallback: str = "eng") -> str:
        """이미지에서 언어 감지"""
        if lang_detect is None:
            return fallback
        
        try:
            temp_text = pytesseract.image_to_string(image, lang=fallback)
            if temp_text.strip():
                detected = lang_detect(temp_text)
                # 언어 코드 매핑 (필요시 확장)
                lang_mapping = {
                    'ko': 'kor',
                    'en': 'eng',
                    'ja': 'jpn',
                    'zh': 'chi_sim'
                }
                return lang_mapping.get(detected, detected)
            return fallback
        except Exception:
            return fallback


class DPIOptimizer:
    """DPI 최적화 클래스"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.candidate_dpis = [200, 300, 400, 500]
    
    def find_optimal_dpi(self, pdf_path: Path, sample_pages: int = 2) -> int:
        """최적 DPI 찾기"""
        if not self.config.auto_dpi:
            return self.config.dpi
        
        best_dpi = self.candidate_dpis[0]
        best_score = -1
        total_pages = self._get_pdf_page_count(pdf_path)
        
        with tqdm(
            total=min(sample_pages, total_pages) * len(self.candidate_dpis),
            desc="🔍 DPI 최적화",
            unit="test"
        ) as pbar:
            for page_num in range(1, min(sample_pages + 1, total_pages + 1)):
                for dpi in self.candidate_dpis:
                    try:
                        score = self._evaluate_dpi(pdf_path, page_num, dpi)
                        if score > best_score:
                            best_score = score
                            best_dpi = dpi
                    except Exception:
                        pass
                    finally:
                        pbar.update(1)
        
        return best_dpi
    
    def _evaluate_dpi(self, pdf_path: Path, page_num: int, dpi: int) -> int:
        """특정 DPI로 페이지 평가"""
        images = convert_from_path(
            str(pdf_path), 
            dpi=dpi, 
            first_page=page_num, 
            last_page=page_num
        )
        
        if not images:
            return 0
        
        preprocessor = ImagePreprocessor(self.config)
        processed_image = preprocessor.preprocess(images[0])
        
        data = pytesseract.image_to_data(
            processed_image, 
            output_type=pytesseract.Output.DICT
        )
        
        # 신뢰도 높은 단어 수 반환
        return sum(
            1 for i, conf in enumerate(data.get('conf', []))
            if data.get('text', [None] * len(data.get('conf', [])))[i] and 
            int(conf) >= self.config.confidence_threshold
        )
    
    @staticmethod
    def _get_pdf_page_count(pdf_path: Path) -> int:
        """PDF 페이지 수 반환"""
        return len(PdfReader(str(pdf_path)).pages)


class CheckpointManager:
    """체크포인트 관리 클래스"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.checkpoint_dir = base_dir / ".checkpoints"
    
    def create_checkpoint_dir(self, document_id: str) -> Path:
        """체크포인트 디렉토리 생성"""
        checkpoint_path = self.checkpoint_dir / document_id
        checkpoint_path.mkdir(parents=True, exist_ok=True)
        return checkpoint_path
    
    def save_manifest(self, checkpoint_path: Path, manifest: Dict) -> None:
        """매니페스트 저장"""
        manifest_file = checkpoint_path / "manifest.json"
        manifest_file.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    
    def load_manifest(self, checkpoint_path: Path) -> Optional[Dict]:
        """매니페스트 로드"""
        manifest_file = checkpoint_path / "manifest.json"
        if manifest_file.exists():
            return json.loads(manifest_file.read_text(encoding="utf-8"))
        return None
    
    def save_page_result(self, checkpoint_path: Path, page_result: PageResult, pdf_bytes: bytes) -> None:
        """페이지 결과 저장"""
        # PDF 저장
        pdf_file = checkpoint_path / f"page_{page_result.page_number:05d}.pdf"
        pdf_file.write_bytes(pdf_bytes)
        
        # JSON 저장 (설정에 따라)
        json_file = checkpoint_path / f"page_{page_result.page_number:05d}.json"
        page_data = {
            "page": page_result.page_number,
            "status": page_result.status.value,
            "language": page_result.language,
            "processing_time": page_result.processing_time,
            "words": [
                {
                    "text": word.text,
                    "confidence": word.confidence,
                    "bbox": word.bbox
                }
                for word in page_result.words
            ]
        }
        json_file.write_text(
            json.dumps(page_data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    
    def cleanup_checkpoints(self, checkpoint_path: Path) -> None:
        """체크포인트 정리"""
        for file in checkpoint_path.glob("*"):
            try:
                file.unlink()
            except Exception:
                pass
        try:
            checkpoint_path.rmdir()
        except Exception:
            pass


class OCRProcessor:
    """OCR 처리 클래스"""
    
    def __init__(self, config: ProcessingConfig, cache: Optional[CacheProtocol] = None):
        self.config = config
        self.cache = cache or MemoryCache()
        self.preprocessor = ImagePreprocessor(config)
        self.language_detector = LanguageDetector()
    
    def process_image(self, image: Image.Image, page_number: int, language: str) -> PageResult:
        """단일 이미지 OCR 처리"""
        start_time = time.time()
        
        try:
            # 캐시 키 생성
            cache_key = self._generate_cache_key(image, language)
            
            if self.config.cache_enabled and self.cache.exists(cache_key):
                cached_result = self.cache.get(cache_key)
                if cached_result:
                    cached_result.page_number = page_number
                    return cached_result
            
            # 이미지 전처리
            processed_image = self.preprocessor.preprocess(image)
            
            # 언어 감지
            if language == "auto":
                language = self.language_detector.detect_language(processed_image)
            
            # OCR 수행
            words = self._extract_words(processed_image, language, page_number)
            
            result = PageResult(
                page_number=page_number,
                status=ProcessingStatus.COMPLETED,
                words=words,
                language=language,
                processing_time=time.time() - start_time
            )
            
            # 캐시 저장
            if self.config.cache_enabled:
                self.cache.set(cache_key, result, self.config.cache_ttl)
            
            return result
            
        except Exception as e:
            return PageResult(
                page_number=page_number,
                status=ProcessingStatus.FAILED,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
    
    def _extract_words(self, image: Image.Image, language: str, page_number: int) -> List[WordData]:
        """이미지에서 단어 추출"""
        data = pytesseract.image_to_data(
            image, 
            lang=language, 
            output_type=pytesseract.Output.DICT
        )
        
        words = []
        for i in range(len(data.get('text', []))):
            text = (data['text'][i] or "").strip()
            try:
                confidence = int(float(data['conf'][i]))
            except (ValueError, TypeError):
                confidence = -1
            
            if text and confidence >= self.config.confidence_threshold:
                words.append(WordData(
                    text=text,
                    confidence=confidence,
                    bbox={
                        "x": int(data['left'][i]),
                        "y": int(data['top'][i]),
                        "w": int(data['width'][i]),
                        "h": int(data['height'][i]),
                    },
                    page_number=page_number
                ))
        
        return words
    
    def _generate_cache_key(self, image: Image.Image, language: str) -> str:
        """캐시 키 생성"""
        # 이미지 해시 + 설정 해시
        image_bytes = BytesIO()
        image.save(image_bytes, format='PNG')
        image_hash = hashlib.md5(image_bytes.getvalue()).hexdigest()
        
        config_str = f"{language}_{self.config.confidence_threshold}_{self.config.binarization_threshold}"
        config_hash = hashlib.md5(config_str.encode()).hexdigest()
        
        return f"{image_hash}_{config_hash}"
    
    def create_searchable_pdf(self, image: Image.Image, language: str) -> bytes:
        """검색 가능한 PDF 생성"""
        processed_image = self.preprocessor.preprocess(image)
        return pytesseract.image_to_pdf_or_hocr(
            processed_image, 
            lang=language, 
            extension="pdf"
        )


class PDFProcessor:
    """PDF 처리 메인 클래스"""
    
    def __init__(self, config: ProcessingConfig, cache: Optional[CacheProtocol] = None):
        self.config = config
        self.cache = cache or MemoryCache()
        self.ocr_processor = OCRProcessor(config, cache)
        self.dpi_optimizer = DPIOptimizer(config)
        self.checkpoint_manager = CheckpointManager(Path("./output"))
        self.logger = self._setup_logger()
    
    async def process_document(self, file_path: Path, output_dir: Path) -> DocumentResult:
        """문서 처리 (비동기)"""
        start_time = time.time()
        
        try:
            # 출력 디렉토리 생성
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 문서 ID 생성
            document_id = file_path.stem
            
            # 체크포인트 설정
            checkpoint_path = self.checkpoint_manager.create_checkpoint_dir(document_id)
            
            # 최적 DPI 결정
            optimal_dpi = self.dpi_optimizer.find_optimal_dpi(file_path)
            self.logger.info(f"최적 DPI 선택됨: {optimal_dpi}")
            
            # PDF 처리
            result = await self._process_pdf_async(
                file_path, 
                output_dir, 
                checkpoint_path, 
                optimal_dpi
            )
            
            result.processing_time = time.time() - start_time
            result.config = self.config
            
            return result
            
        except Exception as e:
            self.logger.error(f"문서 처리 실패: {e}")
            return DocumentResult(
                file_path=file_path,
                total_pages=0,
                processed_pages=0,
                status=ProcessingStatus.FAILED,
                processing_time=time.time() - start_time
            )
    
    async def _process_pdf_async(self, 
                                 pdf_path: Path, 
                                 output_dir: Path, 
                                 checkpoint_path: Path, 
                                 dpi: int) -> DocumentResult:
        """비동기 PDF 처리"""
        
        total_pages = self.dpi_optimizer._get_pdf_page_count(pdf_path)
        
        # 매니페스트 로드/생성
        manifest = self.checkpoint_manager.load_manifest(checkpoint_path)
        if not manifest:
            manifest = {
                "file": pdf_path.name,
                "dpi": dpi,
                "total_pages": total_pages,
                "completed_pages": [],
                "config": self.config.__dict__
            }
        
        completed_pages = set(manifest.get("completed_pages", []))
        
        # 처리할 페이지 결정
        pending_pages = [
            i for i in range(1, total_pages + 1) 
            if i not in completed_pages
        ]
        
        if not pending_pages:
            self.logger.info("모든 페이지가 이미 처리됨")
            return await self._finalize_document(pdf_path, checkpoint_path, output_dir, manifest)
        
        # 병렬 처리
        page_results = await self._process_pages_parallel(
            pdf_path, 
            pending_pages, 
            dpi, 
            checkpoint_path
        )
        
        # 매니페스트 업데이트
        for result in page_results:
            if result.status == ProcessingStatus.COMPLETED:
                completed_pages.add(result.page_number)
        
        manifest["completed_pages"] = sorted(list(completed_pages))
        self.checkpoint_manager.save_manifest(checkpoint_path, manifest)
        
        # 최종 문서 생성
        return await self._finalize_document(pdf_path, checkpoint_path, output_dir, manifest)
    
    async def _process_pages_parallel(self, 
                                      pdf_path: Path, 
                                      page_numbers: List[int], 
                                      dpi: int, 
                                      checkpoint_path: Path) -> List[PageResult]:
        """페이지 병렬 처리"""
        
        loop = asyncio.get_event_loop()
        results = []
        
        with ProcessPoolExecutor(max_workers=self.config.workers) as executor:
            tasks = []
            for page_num in page_numbers:
                task = loop.run_in_executor(
                    executor,
                    self._process_single_page,
                    pdf_path,
                    page_num,
                    dpi
                )
                tasks.append(task)
            
            # 진행률 표시
            with tqdm(total=len(tasks), desc=f"📄 {pdf_path.name}", unit="page") as pbar:
                for completed_task in asyncio.as_completed(tasks):
                    result = await completed_task
                    results.append(result)
                    
                    # 체크포인트 저장
                    if result.status == ProcessingStatus.COMPLETED:
                        # PDF 바이트 생성
                        images = convert_from_path(
                            str(pdf_path), 
                            dpi=dpi, 
                            first_page=result.page_number, 
                            last_page=result.page_number
                        )
                        if images:
                            pdf_bytes = self.ocr_processor.create_searchable_pdf(
                                images[0], 
                                result.language
                            )
                            self.checkpoint_manager.save_page_result(
                                checkpoint_path, 
                                result, 
                                pdf_bytes
                            )
                    
                    pbar.update(1)
        
        return results
    
    def _process_single_page(self, pdf_path: Path, page_number: int, dpi: int) -> PageResult:
        """단일 페이지 처리 (워커 프로세스용)"""
        try:
            # PDF를 이미지로 변환
            images = convert_from_path(
                str(pdf_path), 
                dpi=dpi, 
                first_page=page_number, 
                last_page=page_number
            )
            
            if not images:
                return PageResult(
                    page_number=page_number,
                    status=ProcessingStatus.FAILED,
                    error_message="이미지 변환 실패"
                )
            
            # OCR 처리
            return self.ocr_processor.process_image(
                images[0], 
                page_number, 
                self.config.language
            )
            
        except Exception as e:
            return PageResult(
                page_number=page_number,
                status=ProcessingStatus.FAILED,
                error_message=str(e)
            )
    
    async def _finalize_document(self, 
                                 pdf_path: Path, 
                                 checkpoint_path: Path, 
                                 output_dir: Path, 
                                 manifest: Dict) -> DocumentResult:
        """문서 최종화"""
        
        # PDF 병합
        output_pdf = output_dir / f"{pdf_path.stem}_searchable.pdf"
        await self._merge_pdfs(checkpoint_path, output_pdf)
        
        # JSON 병합 (옵션)
        if self.config.save_json:
            await self._merge_json_files(checkpoint_path, output_pdf.with_suffix(".json"))
        
        # 체크포인트 정리
        if not self.config.keep_checkpoints:
            self.checkpoint_manager.cleanup_checkpoints(checkpoint_path)
        
        # 결과 생성
        total_pages = manifest["total_pages"]
        completed_pages = len(manifest.get("completed_pages", []))
        
        return DocumentResult(
            file_path=pdf_path,
            total_pages=total_pages,
            processed_pages=completed_pages,
            status=ProcessingStatus.COMPLETED if completed_pages == total_pages else ProcessingStatus.FAILED
        )
    
    async def _merge_pdfs(self, checkpoint_path: Path, output_path: Path) -> None:
        """PDF 파일들 병합"""
        writer = PdfWriter()
        pdf_files = sorted(checkpoint_path.glob("page_*.pdf"))
        
        for pdf_file in pdf_files:
            reader = PdfReader(str(pdf_file))
            for page in reader.pages:
                writer.add_page(page)
        
        # 비동기로 쓰기
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None, 
            lambda: output_path.write_bytes(self._write_pdf_to_bytes(writer))
        )
    
    async def _merge_json_files(self, checkpoint_path: Path, output_path: Path) -> None:
        """JSON 파일들 병합"""
        merged_data = {
            "type": "pdf",
            "pages": []
        }
        
        json_files = sorted(checkpoint_path.glob("page_*.json"))
        for json_file in json_files:
            page_data = json.loads(json_file.read_text(encoding="utf-8"))
            merged_data["pages"].append(page_data)
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: output_path.write_text(
                json.dumps(merged_data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        )
    
    def _write_pdf_to_bytes(self, writer: PdfWriter) -> bytes:
        """PDF Writer를 바이트로 변환"""
        bio = BytesIO()
        writer.write(bio)
        return bio.getvalue()
    
    def _setup_logger(self) -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)s | %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger


# 팩토리 패턴
class ProcessorFactory:
    """프로세서 팩토리"""
    
    @staticmethod
    def create_processor(config: ProcessingConfig, cache: Optional[CacheProtocol] = None) -> PDFProcessor:
        """프로세서 생성"""
        return PDFProcessor(config, cache)
    
    @staticmethod
    def create_config(**kwargs) -> ProcessingConfig:
        """설정 생성"""
        return ProcessingConfig(**kwargs)


# 사용 예시 함수
async def process_documents(file_paths: List[Path], output_dir: Path, config: ProcessingConfig) -> List[DocumentResult]:
    """여러 문서 처리"""
    processor = ProcessorFactory.create_processor(config)
    
    tasks = [
        processor.process_document(file_path, output_dir)
        for file_path in file_paths
    ]
    
    results = []
    for completed_task in asyncio.as_completed(tasks):
        result = await completed_task
        results.append(result)
    
    return results


if __name__ == "__main__":
    # 간단한 테스트
    async def main():
        config = ProcessorFactory.create_config(
            dpi=300,
            auto_dpi=True,
            workers=4,
            save_json=True
        )
        
        # 단일 파일 처리 예시
        # processor = ProcessorFactory.create_processor(config)
        # result = await processor.process_document(
        #     Path("input.pdf"),
        #     Path("./output")
        # )
        # print(f"처리 완료: {result.status}")
    
    # asyncio.run(main())