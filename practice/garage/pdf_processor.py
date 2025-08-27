"""
Enhanced PDF OCR Processing System
개선된 PDF OCR 처리 시스템 - 클래스 기반 아키텍처
"""

import asyncio
import hashlib
import json
import logging
import time
import warnings
from abc import ABC, abstractmethod
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, Any, Protocol, Callable
from io import BytesIO
from functools import wraps

import pytesseract
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
from pdf2image import convert_from_path
from pypdf import PdfReader, PdfWriter
from tqdm import tqdm

try:
    from langdetect import detect as lang_detect
    LANG_DETECT_AVAILABLE = True
except ImportError:
    lang_detect = None
    LANG_DETECT_AVAILABLE = False

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

# 경고 필터링
warnings.filterwarnings('ignore', category=UserWarning)


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
    # OCR 설정
    dpi: int = 300
    language: str = "auto"
    confidence_threshold: int = 50
    oem: int = 3  # OCR Engine Mode
    psm: int = 6  # Page Segmentation Mode
    
    # 병렬 처리 설정
    workers: int = 4
    max_memory_usage: int = 2048  # MB
    chunk_size: int = 10  # 한 번에 처리할 페이지 수
    
    # 최적화 설정
    auto_dpi: bool = False
    auto_language: bool = False
    skip_blank_pages: bool = True
    
    # 출력 설정
    save_json: bool = False
    save_images: bool = False
    output_format: str = "pdf"  # pdf, txt, json
    
    # 복구 및 캐시 설정
    resume: bool = True
    keep_checkpoints: bool = False
    cache_enabled: bool = True
    cache_ttl: int = 86400  # 24시간
    
    # 이미지 전처리 설정
    preprocessing_enabled: bool = True
    binarization_threshold: int = 140
    noise_removal: bool = False
    deskew: bool = False
    enhance_contrast: bool = True
    enhance_sharpness: bool = False
    
    # 품질 제어
    min_word_length: int = 2
    max_word_length: int = 50
    filter_numeric_only: bool = False
    
    # 로깅 설정
    log_level: str = "INFO"
    progress_bar: bool = True
    
    def validate(self) -> None:
        """설정 검증"""
        if self.dpi < 72 or self.dpi > 600:
            raise ValueError("DPI는 72-600 범위여야 합니다")
        if self.confidence_threshold < 0 or self.confidence_threshold > 100:
            raise ValueError("신뢰도 임계값은 0-100 범위여야 합니다")
        if self.workers < 1 or self.workers > 32:
            raise ValueError("워커 수는 1-32 범위여야 합니다")
        if self.output_format not in ["pdf", "txt", "json"]:
            raise ValueError("출력 형식은 pdf, txt, json 중 하나여야 합니다")


@dataclass
class WordData:
    """OCR 단어 데이터"""
    text: str
    confidence: int
    bbox: Dict[str, int]
    page_number: int
    font_size: Optional[int] = None
    is_bold: bool = False
    is_italic: bool = False
    
    @property
    def area(self) -> int:
        """바운딩 박스 면적"""
        return self.bbox["w"] * self.bbox["h"]
    
    @property
    def center(self) -> Tuple[int, int]:
        """바운딩 박스 중심점"""
        return (
            self.bbox["x"] + self.bbox["w"] // 2,
            self.bbox["y"] + self.bbox["h"] // 2
        )


@dataclass 
class PageResult:
    """페이지 처리 결과"""
    page_number: int
    status: ProcessingStatus
    words: List[WordData] = field(default_factory=list)
    language: str = "eng"
    processing_time: float = 0.0
    error_message: Optional[str] = None
    
    # 통계 정보
    total_words: int = 0
    avg_confidence: float = 0.0
    is_blank: bool = False
    image_size: Optional[Tuple[int, int]] = None
    
    def __post_init__(self):
        """후처리 - 통계 계산"""
        self.total_words = len(self.words)
        if self.words:
            self.avg_confidence = sum(w.confidence for w in self.words) / len(self.words)
            self.is_blank = self.total_words == 0
    
    @property
    def text(self) -> str:
        """페이지의 모든 텍스트"""
        return " ".join(word.text for word in self.words)
    
    @property
    def high_confidence_words(self) -> List[WordData]:
        """높은 신뢰도 단어들"""
        return [w for w in self.words if w.confidence >= 80]


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
    
    # 통계 정보
    total_words: int = 0
    avg_confidence: float = 0.0
    detected_languages: List[str] = field(default_factory=list)
    blank_pages: List[int] = field(default_factory=list)
    error_pages: List[int] = field(default_factory=list)
    
    def __post_init__(self):
        """후처리 - 통계 계산"""
        if self.pages:
            # 전체 단어 수
            self.total_words = sum(page.total_words for page in self.pages)
            
            # 평균 신뢰도
            all_confidences = [
                word.confidence 
                for page in self.pages 
                for word in page.words
            ]
            if all_confidences:
                self.avg_confidence = sum(all_confidences) / len(all_confidences)
            
            # 언어 감지
            self.detected_languages = list(set(page.language for page in self.pages))
            
            # 빈 페이지와 오류 페이지
            self.blank_pages = [p.page_number for p in self.pages if p.is_blank]
            self.error_pages = [p.page_number for p in self.pages if p.status == ProcessingStatus.FAILED]
    
    @property
    def success_rate(self) -> float:
        """성공률"""
        if self.total_pages == 0:
            return 0.0
        return (self.processed_pages - len(self.error_pages)) / self.total_pages
    
    @property
    def full_text(self) -> str:
        """전체 문서 텍스트"""
        return "\n\n".join(page.text for page in self.pages if not page.is_blank)
    
    def get_page_by_number(self, page_num: int) -> Optional[PageResult]:
        """페이지 번호로 페이지 결과 조회"""
        for page in self.pages:
            if page.page_number == page_num:
                return page
        return None
    
    def export_summary(self) -> Dict:
        """결과 요약 내보내기"""
        return {
            "file": str(self.file_path),
            "total_pages": self.total_pages,
            "processed_pages": self.processed_pages,
            "success_rate": self.success_rate,
            "total_words": self.total_words,
            "avg_confidence": round(self.avg_confidence, 2),
            "processing_time": round(self.processing_time, 2),
            "detected_languages": self.detected_languages,
            "blank_pages": len(self.blank_pages),
            "error_pages": len(self.error_pages),
            "status": self.status.value
        }


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
    """고급 이미지 전처리 클래스"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def preprocess(self, image: Image.Image) -> Image.Image:
        """이미지 전처리 수행"""
        if not self.config.preprocessing_enabled:
            return image
        
        processed_image = image.copy()
        
        try:
            # 1. 그레이스케일 변환
            if processed_image.mode != 'L':
                processed_image = ImageOps.grayscale(processed_image)
            
            # 2. 노이즈 제거
            if self.config.noise_removal:
                processed_image = self._remove_noise(processed_image)
            
            # 3. 기울어짐 보정
            if self.config.deskew:
                processed_image = self._deskew_image(processed_image)
            
            # 4. 대비 향상
            if self.config.enhance_contrast:
                processed_image = self._enhance_contrast(processed_image)
            
            # 5. 선명도 향상
            if self.config.enhance_sharpness:
                processed_image = self._enhance_sharpness(processed_image)
            
            # 6. 이진화
            processed_image = self._binarize(processed_image)
            
            return processed_image
            
        except Exception as e:
            self.logger.warning(f"전처리 실패, 원본 이미지 사용: {e}")
            return image
    
    def _remove_noise(self, image: Image.Image) -> Image.Image:
        """노이즈 제거"""
        if not CV2_AVAILABLE:
            # PIL 기반 노이즈 제거
            return image.filter(ImageFilter.MedianFilter(size=3))
        
        # OpenCV 기반 고급 노이즈 제거
        img_array = np.array(image)
        denoised = cv2.fastNlMeansDenoising(img_array, h=10, templateWindowSize=7, searchWindowSize=21)
        return Image.fromarray(denoised)
    
    def _deskew_image(self, image: Image.Image) -> Image.Image:
        """기울어짐 보정"""
        if not CV2_AVAILABLE:
            return image
        
        try:
            img_array = np.array(image)
            
            # 가장자리 검출
            edges = cv2.Canny(img_array, 50, 150, apertureSize=3)
            
            # 허프 변환으로 직선 검출
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            if lines is not None:
                # 각도 계산
                angles = []
                for line in lines[:10]:  # 상위 10개 직선만 사용
                    rho, theta = line[0]
                    angle = theta * 180 / np.pi - 90
                    if -45 < angle < 45:
                        angles.append(angle)
                
                if angles:
                    # 중간값 사용 (이상치 제거)
                    median_angle = np.median(angles)
                    
                    # 회전
                    if abs(median_angle) > 0.5:  # 0.5도 이상 기울어진 경우만 보정
                        rotated = image.rotate(-median_angle, expand=True, fillcolor='white')
                        return rotated
            
            return image
            
        except Exception as e:
            self.logger.warning(f"기울어짐 보정 실패: {e}")
            return image
    
    def _enhance_contrast(self, image: Image.Image) -> Image.Image:
        """대비 향상"""
        # 히스토그램 균등화
        image_array = np.array(image)
        
        if CV2_AVAILABLE:
            # CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(image_array)
            return Image.fromarray(enhanced)
        else:
            # PIL 기반 대비 조정
            return ImageOps.autocontrast(image, cutoff=2)
    
    def _enhance_sharpness(self, image: Image.Image) -> Image.Image:
        """선명도 향상"""
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(1.5)  # 50% 선명도 증가
    
    def _binarize(self, image: Image.Image) -> Image.Image:
        """이진화"""
        if CV2_AVAILABLE:
            # OpenCV 기반 적응적 임계값
            img_array = np.array(image)
            binary = cv2.adaptiveThreshold(
                img_array, 
                255, 
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 
                11, 
                2
            )
            return Image.fromarray(binary)
        else:
            # PIL 기반 단순 임계값
            return image.point(
                lambda x: 0 if x < self.config.binarization_threshold else 255,
                "1"
            )
    
    def analyze_image_quality(self, image: Image.Image) -> Dict[str, float]:
        """이미지 품질 분석"""
        if not CV2_AVAILABLE:
            return {"quality_score": 0.5}
        
        try:
            img_array = np.array(image)
            
            # 라플라시안 분산 (선명도 측정)
            laplacian_var = cv2.Laplacian(img_array, cv2.CV_64F).var()
            
            # 대비 측정
            contrast = img_array.std()
            
            # 품질 점수 계산 (0-1)
            sharpness_score = min(laplacian_var / 1000, 1.0)
            contrast_score = min(contrast / 128, 1.0)
            
            quality_score = (sharpness_score + contrast_score) / 2
            
            return {
                "quality_score": quality_score,
                "sharpness": sharpness_score,
                "contrast": contrast_score,
                "laplacian_variance": laplacian_var
            }
            
        except Exception as e:
            self.logger.warning(f"품질 분석 실패: {e}")
            return {"quality_score": 0.5}


class LanguageDetector:
    """고급 언어 감지 클래스"""
    
    # 언어 코드 매핑
    LANG_MAPPING = {
        'ko': 'kor+eng',
        'kr': 'kor+eng', 
        'en': 'eng',
        'ja': 'jpn+eng',
        'zh-cn': 'chi_sim+eng',
        'zh': 'chi_sim+eng',
        'zh-tw': 'chi_tra+eng',
        'de': 'deu+eng',
        'fr': 'fra+eng',
        'es': 'spa+eng',
        'it': 'ita+eng',
        'pt': 'por+eng',
        'ru': 'rus+eng',
        'ar': 'ara+eng'
    }
    
    # 언어별 특성 패턴
    LANGUAGE_PATTERNS = {
        'kor': r'[가-힣]',
        'jpn': r'[ひらがなカタカナ一-龯]',
        'chi_sim': r'[一-龯]',
        'ara': r'[\u0600-\u06FF]',
        'rus': r'[а-яё]'
    }
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def detect_language(self, image: Image.Image, text_sample: Optional[str] = None, fallback: str = "eng") -> str:
        """고급 언어 감지"""
        
        # 1. 설정에서 자동 감지가 비활성화된 경우
        if not self.config.auto_language and self.config.language != "auto":
            return self.config.language
        
        # 2. 제공된 텍스트 샘플 분석
        if text_sample:
            detected = self._analyze_text_patterns(text_sample)
            if detected:
                return detected
        
        # 3. 이미지에서 텍스트 추출 후 분석
        if LANG_DETECT_AVAILABLE:
            detected = self._detect_from_image(image, fallback)
            if detected:
                return detected
        
        # 4. OCR 기반 언어 감지
        detected = self._ocr_based_detection(image, fallback)
        if detected:
            return detected
        
        return fallback
    
    def _analyze_text_patterns(self, text: str) -> Optional[str]:
        """텍스트 패턴 분석으로 언어 감지"""
        import re
        
        text = text.strip()
        if len(text) < 10:  # 너무 짧으면 신뢰하기 어려움
            return None
        
        # 각 언어 패턴 매칭
        scores = {}
        for lang, pattern in self.LANGUAGE_PATTERNS.items():
            matches = len(re.findall(pattern, text))
            if matches > 0:
                scores[lang] = matches / len(text)
        
        # 가장 높은 점수의 언어 선택
        if scores:
            best_lang = max(scores, key=scores.get)
            if scores[best_lang] > 0.1:  # 최소 10% 이상 매칭
                return self.LANG_MAPPING.get(best_lang, best_lang)
        
        return None
    
    def _detect_from_image(self, image: Image.Image, fallback: str) -> Optional[str]:
        """이미지에서 텍스트 추출 후 langdetect 사용"""
        try:
            # 빠른 OCR로 샘플 텍스트 추출
            temp_text = pytesseract.image_to_string(
                image, 
                lang=fallback,
                config='--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz가-힣ひらがなカタカナ一-龯'
            ).strip()
            
            if len(temp_text) < 20:
                return None
            
            # langdetect로 언어 감지
            detected = lang_detect(temp_text)
            mapped_lang = self.LANG_MAPPING.get(detected, detected)
            
            self.logger.info(f"언어 감지됨: {detected} -> {mapped_lang}")
            return mapped_lang
            
        except Exception as e:
            self.logger.warning(f"langdetect 기반 언어 감지 실패: {e}")
            return None
    
    def _ocr_based_detection(self, image: Image.Image, fallback: str) -> Optional[str]:
        """여러 언어로 OCR 수행하여 최적 언어 찾기"""
        try:
            candidate_languages = ['eng', 'kor+eng', 'jpn+eng', 'chi_sim+eng']
            best_lang = fallback
            best_score = 0
            
            for lang in candidate_languages:
                try:
                    # OCR 수행
                    data = pytesseract.image_to_data(
                        image,
                        lang=lang,
                        output_type=pytesseract.Output.DICT,
                        config='--psm 6'
                    )
                    
                    # 신뢰도 점수 계산
                    confidences = [
                        int(conf) for conf in data.get('conf', [])
                        if conf != '-1' and int(conf) > 0
                    ]
                    
                    if confidences:
                        avg_confidence = sum(confidences) / len(confidences)
                        if avg_confidence > best_score:
                            best_score = avg_confidence
                            best_lang = lang
                
                except Exception:
                    continue
            
            return best_lang if best_score > self.config.confidence_threshold else fallback
            
        except Exception as e:
            self.logger.warning(f"OCR 기반 언어 감지 실패: {e}")
            return fallback
    
    @classmethod
    def get_supported_languages(cls) -> List[str]:
        """지원되는 언어 목록 반환"""
        return list(cls.LANG_MAPPING.keys())
    
    def validate_language(self, language: str) -> str:
        """언어 코드 검증 및 정규화"""
        if language in self.LANG_MAPPING:
            return self.LANG_MAPPING[language]
        elif language in self.LANG_MAPPING.values():
            return language
        else:
            self.logger.warning(f"지원되지 않는 언어: {language}, 기본값 사용")
            return "eng"


class PerformanceMonitor:
    """성능 모니터링 클래스"""
    
    def __init__(self):
        self.metrics = {
            "start_time": 0,
            "end_time": 0,
            "pages_processed": 0,
            "total_words_extracted": 0,
            "avg_confidence": 0.0,
            "memory_peak": 0,
            "cpu_usage": [],
            "processing_times": [],
            "error_count": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        self._timers = {}
    
    def start_monitoring(self):
        """모니터링 시작"""
        self.metrics["start_time"] = time.time()
        try:
            import psutil
            self.process = psutil.Process()
            self.initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            self.process = None
    
    def stop_monitoring(self):
        """모니터링 종료"""
        self.metrics["end_time"] = time.time()
    
    @contextmanager
    def time_operation(self, operation_name: str):
        """작업 시간 측정"""
        start = time.time()
        try:
            yield
        finally:
            duration = time.time() - start
            if operation_name not in self._timers:
                self._timers[operation_name] = []
            self._timers[operation_name].append(duration)
    
    def record_page_processed(self, page_result: PageResult):
        """페이지 처리 기록"""
        self.metrics["pages_processed"] += 1
        self.metrics["total_words_extracted"] += page_result.total_words
        self.metrics["processing_times"].append(page_result.processing_time)
        
        if page_result.status == ProcessingStatus.FAILED:
            self.metrics["error_count"] += 1
        
        # 평균 신뢰도 갱신
        if page_result.words:
            all_confidences = [w.confidence for w in page_result.words]
            self.metrics["avg_confidence"] = (
                self.metrics["avg_confidence"] * (self.metrics["pages_processed"] - 1) +
                sum(all_confidences) / len(all_confidences)
            ) / self.metrics["pages_processed"]
    
    def record_cache_event(self, hit: bool):
        """캐시 이벤트 기록"""
        if hit:
            self.metrics["cache_hits"] += 1
        else:
            self.metrics["cache_misses"] += 1
    
    def update_system_metrics(self):
        """시스템 메트릭 업데이트"""
        if self.process:
            try:
                memory_mb = self.process.memory_info().rss / 1024 / 1024
                self.metrics["memory_peak"] = max(self.metrics["memory_peak"], memory_mb)
                
                cpu_percent = self.process.cpu_percent()
                self.metrics["cpu_usage"].append(cpu_percent)
            except Exception:
                pass
    
    def get_summary(self) -> Dict:
        """성능 요약 반환"""
        total_time = self.metrics["end_time"] - self.metrics["start_time"]
        
        return {
            "총_처리_시간": f"{total_time:.2f}초",
            "처리된_페이지": self.metrics["pages_processed"],
            "평균_페이지_처리_시간": f"{sum(self.metrics['processing_times']) / max(len(self.metrics['processing_times']), 1):.2f}초",
            "페이지_처리_속도": f"{self.metrics['pages_processed'] / max(total_time, 1):.2f}페이지/초",
            "추출된_단어_수": self.metrics["total_words_extracted"],
            "평균_신뢰도": f"{self.metrics['avg_confidence']:.2f}%",
            "메모리_피크": f"{self.metrics['memory_peak']:.1f}MB",
            "평균_CPU_사용률": f"{sum(self.metrics['cpu_usage']) / max(len(self.metrics['cpu_usage']), 1):.1f}%" if self.metrics['cpu_usage'] else "N/A",
            "오류_페이지": self.metrics["error_count"],
            "캐시_적중률": f"{self.metrics['cache_hits'] / max(self.metrics['cache_hits'] + self.metrics['cache_misses'], 1) * 100:.1f}%",
            "작업별_시간": {name: f"{sum(times):.2f}초" for name, times in self._timers.items()}
        }


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
    """고급 OCR 처리 클래스"""
    
    def __init__(self, config: ProcessingConfig, cache: Optional[CacheProtocol] = None):
        self.config = config
        self.cache = cache or MemoryCache()
        self.preprocessor = ImagePreprocessor(config)
        self.language_detector = LanguageDetector(config)
        self.performance_monitor = PerformanceMonitor()
        self.logger = logging.getLogger(__name__)
        
        # Tesseract 설정 검증
        self._validate_tesseract_config()
    
    def _validate_tesseract_config(self):
        """Tesseract 설정 검증"""
        try:
            # Tesseract 버전 확인
            version = pytesseract.get_tesseract_version()
            self.logger.info(f"Tesseract 버전: {version}")
            
            # 사용 가능한 언어 확인
            languages = pytesseract.get_languages()
            self.logger.info(f"지원 언어: {languages}")
            
        except Exception as e:
            self.logger.warning(f"Tesseract 설정 검증 실패: {e}")
    
    def process_image(self, image: Image.Image, page_number: int, language: str = None) -> PageResult:
        """단일 이미지 OCR 처리"""
        start_time = time.time()
        
        try:
            with self.performance_monitor.time_operation("image_preprocessing"):
                # 이미지 품질 분석
                quality_metrics = self.preprocessor.analyze_image_quality(image)
                
                # 캐시 키 생성
                cache_key = self._generate_cache_key(image, language or self.config.language)
                
                if self.config.cache_enabled and self.cache.exists(cache_key):
                    cached_result = self.cache.get(cache_key)
                    if cached_result:
                        cached_result.page_number = page_number
                        self.performance_monitor.record_cache_event(True)
                        return cached_result
                
                self.performance_monitor.record_cache_event(False)
                
                # 이미지 전처리
                processed_image = self.preprocessor.preprocess(image)
            
            with self.performance_monitor.time_operation("language_detection"):
                # 언어 감지
                detected_language = language or self.language_detector.detect_language(processed_image)
            
            with self.performance_monitor.time_operation("ocr_extraction"):
                # OCR 수행
                words = self._extract_words(processed_image, detected_language, page_number)
                
                # 빈 페이지 건너뛰기
                if self.config.skip_blank_pages and len(words) == 0:
                    result = PageResult(
                        page_number=page_number,
                        status=ProcessingStatus.COMPLETED,
                        words=[],
                        language=detected_language,
                        processing_time=time.time() - start_time,
                        is_blank=True,
                        image_size=image.size
                    )
                else:
                    # 후처리
                    words = self._post_process_words(words)
                    
                    result = PageResult(
                        page_number=page_number,
                        status=ProcessingStatus.COMPLETED,
                        words=words,
                        language=detected_language,
                        processing_time=time.time() - start_time,
                        image_size=image.size
                    )
            
            # 캐시 저장
            if self.config.cache_enabled:
                self.cache.set(cache_key, result, self.config.cache_ttl)
            
            return result
            
        except Exception as e:
            self.logger.error(f"페이지 {page_number} OCR 실패: {e}")
            return PageResult(
                page_number=page_number,
                status=ProcessingStatus.FAILED,
                error_message=str(e),
                processing_time=time.time() - start_time,
                image_size=image.size if image else None
            )
    
    def _extract_words(self, image: Image.Image, language: str, page_number: int) -> List[WordData]:
        """이미지에서 단어 추출"""
        
        # Tesseract 설정 구성
        tesseract_config = self._build_tesseract_config()
        
        try:
            data = pytesseract.image_to_data(
                image, 
                lang=language, 
                output_type=pytesseract.Output.DICT,
                config=tesseract_config
            )
        except Exception as e:
            self.logger.error(f"Tesseract OCR 실패: {e}")
            return []
        
        words = []
        text_data = data.get('text', [])
        conf_data = data.get('conf', [])
        
        for i in range(len(text_data)):
            text = (text_data[i] or "").strip()
            
            try:
                confidence = int(float(conf_data[i]))
            except (ValueError, TypeError, IndexError):
                confidence = -1
            
            # 필터링 조건
            if not self._should_include_word(text, confidence):
                continue
            
            # 바운딩 박스 정보
            bbox = {
                "x": int(data.get('left', [0] * (i + 1))[i]),
                "y": int(data.get('top', [0] * (i + 1))[i]),
                "w": int(data.get('width', [0] * (i + 1))[i]),
                "h": int(data.get('height', [0] * (i + 1))[i]),
            }
            
            words.append(WordData(
                text=text,
                confidence=confidence,
                bbox=bbox,
                page_number=page_number,
                font_size=self._estimate_font_size(bbox)
            ))
        
        return words
    
    def _build_tesseract_config(self) -> str:
        """Tesseract 설정 문자열 구성"""
        config_parts = []
        
        # OEM (OCR Engine Mode) 설정
        config_parts.append(f"--oem {self.config.oem}")
        
        # PSM (Page Segmentation Mode) 설정
        config_parts.append(f"--psm {self.config.psm}")
        
        # 신뢰도 설정
        if self.config.confidence_threshold > 0:
            config_parts.append(f"-c tessedit_min_confidence={self.config.confidence_threshold}")
        
        return " ".join(config_parts)
    
    def _should_include_word(self, text: str, confidence: int) -> bool:
        """단어 포함 여부 결정"""
        if not text:
            return False
        
        # 신뢰도 필터
        if confidence < self.config.confidence_threshold:
            return False
        
        # 길이 필터
        if len(text) < self.config.min_word_length or len(text) > self.config.max_word_length:
            return False
        
        # 숫자만 포함된 텍스트 필터 (옵션)
        if self.config.filter_numeric_only and text.isdigit():
            return False
        
        return True
    
    def _post_process_words(self, words: List[WordData]) -> List[WordData]:
        """단어 후처리"""
        if not words:
            return words
        
        # 중복 제거 (같은 위치의 유사한 단어)
        filtered_words = []
        for word in words:
            is_duplicate = False
            for existing_word in filtered_words:
                if self._are_words_duplicate(word, existing_word):
                    # 더 높은 신뢰도의 단어 유지
                    if word.confidence > existing_word.confidence:
                        filtered_words.remove(existing_word)
                        break
                    else:
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                filtered_words.append(word)
        
        return filtered_words
    
    def _are_words_duplicate(self, word1: WordData, word2: WordData) -> bool:
        """두 단어가 중복인지 확인"""
        # 위치가 비슷하고 텍스트가 유사한 경우
        bbox1, bbox2 = word1.bbox, word2.bbox
        
        # 바운딩 박스 겹침 확인
        overlap_x = max(0, min(bbox1["x"] + bbox1["w"], bbox2["x"] + bbox2["w"]) - max(bbox1["x"], bbox2["x"]))
        overlap_y = max(0, min(bbox1["y"] + bbox1["h"], bbox2["y"] + bbox2["h"]) - max(bbox1["y"], bbox2["y"]))
        
        overlap_area = overlap_x * overlap_y
        min_area = min(bbox1["w"] * bbox1["h"], bbox2["w"] * bbox2["h"])
        
        if min_area == 0:
            return False
        
        overlap_ratio = overlap_area / min_area
        
        # 50% 이상 겹치고 텍스트가 유사한 경우
        if overlap_ratio > 0.5:
            # 문자열 유사도 확인 (간단한 방법)
            shorter = min(len(word1.text), len(word2.text))
            if shorter == 0:
                return False
            
            common_chars = sum(c1 == c2 for c1, c2 in zip(word1.text, word2.text))
            similarity = common_chars / shorter
            
            return similarity > 0.8
        
        return False
    
    def _estimate_font_size(self, bbox: Dict[str, int]) -> Optional[int]:
        """바운딩 박스에서 폰트 크기 추정"""
        return bbox["h"]  # 높이를 폰트 크기로 근사
    
    def _generate_cache_key(self, image: Image.Image, language: str) -> str:
        """캐시 키 생성"""
        # 이미지 해시 + 설정 해시
        image_bytes = BytesIO()
        image.save(image_bytes, format='PNG')
        image_hash = hashlib.md5(image_bytes.getvalue()).hexdigest()
        
        config_str = f"{language}_{self.config.confidence_threshold}_{self.config.binarization_threshold}_{self.config.oem}_{self.config.psm}"
        config_hash = hashlib.md5(config_str.encode()).hexdigest()
        
        return f"{image_hash}_{config_hash}"
    
    def create_searchable_pdf(self, image: Image.Image, language: str) -> bytes:
        """검색 가능한 PDF 생성"""
        try:
            processed_image = self.preprocessor.preprocess(image)
            config = self._build_tesseract_config()
            
            return pytesseract.image_to_pdf_or_hocr(
                processed_image, 
                lang=language, 
                extension="pdf",
                config=config
            )
        except Exception as e:
            self.logger.error(f"검색 가능한 PDF 생성 실패: {e}")
            # 빈 PDF 반환
            writer = PdfWriter()
            bio = BytesIO()
            writer.write(bio)
            return bio.getvalue()
    
    def extract_text_only(self, image: Image.Image, language: str) -> str:
        """텍스트만 추출 (빠른 방법)"""
        try:
            processed_image = self.preprocessor.preprocess(image)
            config = self._build_tesseract_config()
            
            text = pytesseract.image_to_string(
                processed_image,
                lang=language,
                config=config
            )
            
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"텍스트 추출 실패: {e}")
            return ""


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
            # 설정 검증
            self.config.validate()
            
            # 출력 디렉토리 생성
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # 성능 모니터링 시작
            monitor = PerformanceMonitor()
            monitor.start_monitoring()
            
            # 문서 ID 생성
            document_id = file_path.stem
            
            # 체크포인트 설정
            checkpoint_path = self.checkpoint_manager.create_checkpoint_dir(document_id)
            
            with monitor.time_operation("dpi_optimization"):
                # 최적 DPI 결정
                optimal_dpi = self.dpi_optimizer.find_optimal_dpi(file_path)
                self.logger.info(f"📊 최적 DPI 선택: {optimal_dpi}")
            
            # PDF 처리
            result = await self._process_pdf_async(
                file_path, 
                output_dir, 
                checkpoint_path, 
                optimal_dpi,
                monitor
            )
            
            # 성능 모니터링 종료
            monitor.stop_monitoring()
            
            result.processing_time = time.time() - start_time
            result.config = self.config
            
            # 성능 요약 로깅
            performance_summary = monitor.get_summary()
            self.logger.info("📈 성능 요약:")
            for key, value in performance_summary.items():
                self.logger.info(f"  {key}: {value}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ 문서 처리 실패: {e}")
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
                                 dpi: int,
                                 monitor: PerformanceMonitor) -> DocumentResult:
        """비동기 PDF 처리"""
        
        total_pages = self.dpi_optimizer._get_pdf_page_count(pdf_path)
        self.logger.info(f"📖 총 페이지 수: {total_pages}")
        
        # 매니페스트 로드/생성
        manifest = self.checkpoint_manager.load_manifest(checkpoint_path)
        if not manifest:
            manifest = {
                "file": pdf_path.name,
                "dpi": dpi,
                "total_pages": total_pages,
                "completed_pages": [],
                "config": self.config.__dict__,
                "created_at": time.time()
            }
        
        completed_pages = set(manifest.get("completed_pages", []))
        
        # 처리할 페이지 결정
        pending_pages = [
            i for i in range(1, total_pages + 1) 
            if i not in completed_pages
        ]
        
        if not pending_pages:
            self.logger.info("✅ 모든 페이지가 이미 처리됨")
            return await self._finalize_document(pdf_path, checkpoint_path, output_dir, manifest)
        
        self.logger.info(f"🔄 처리할 페이지: {len(pending_pages)}개")
        
        # 청크 단위로 페이지 처리
        page_results = []
        chunk_size = min(self.config.chunk_size, len(pending_pages))
        
        for i in range(0, len(pending_pages), chunk_size):
            chunk = pending_pages[i:i + chunk_size]
            self.logger.info(f"📄 청크 처리 중: {i+1}-{min(i+chunk_size, len(pending_pages))} / {len(pending_pages)}")
            
            # 시스템 리소스 모니터링
            monitor.update_system_metrics()
            
            chunk_results = await self._process_pages_parallel(
                pdf_path, 
                chunk,
                dpi, 
                checkpoint_path,
                monitor
            )
            
            page_results.extend(chunk_results)
            
            # 중간 저장
            for result in chunk_results:
                if result.status == ProcessingStatus.COMPLETED:
                    completed_pages.add(result.page_number)
                    monitor.record_page_processed(result)
            
            manifest["completed_pages"] = sorted(list(completed_pages))
            manifest["last_updated"] = time.time()
            self.checkpoint_manager.save_manifest(checkpoint_path, manifest)
            
            # 메모리 정리
            if i % (chunk_size * 3) == 0:  # 3개 청크마다
                import gc
                gc.collect()
        
        # 최종 문서 생성
        return await self._finalize_document(pdf_path, checkpoint_path, output_dir, manifest)
    
    async def _process_pages_parallel(self, 
                                      pdf_path: Path, 
                                      page_numbers: List[int], 
                                      dpi: int, 
                                      checkpoint_path: Path,
                                      monitor: PerformanceMonitor) -> List[PageResult]:
        """페이지 병렬 처리 (개선됨)"""
        
        loop = asyncio.get_event_loop()
        results = []
        
        with ProcessPoolExecutor(max_workers=self.config.workers) as executor:
            # 작업 생성
            tasks = []
            for page_num in page_numbers:
                task = loop.run_in_executor(
                    executor,
                    self._process_single_page,
                    pdf_path,
                    page_num,
                    dpi
                )
                tasks.append((task, page_num))
            
            # 진행률 표시 (옵션)
            if self.config.progress_bar:
                progress_bar = tqdm(
                    total=len(tasks), 
                    desc=f"📄 {pdf_path.name}", 
                    unit="페이지",
                    ncols=100,
                    bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
                )
            else:
                progress_bar = None
            
            # 완료된 작업 수집
            for completed_task, page_num in asyncio.as_completed([(task, num) for task, num in tasks]):
                try:
                    result = await completed_task
                    results.append(result)
                    
                    # 체크포인트 저장
                    if result.status == ProcessingStatus.COMPLETED:
                        with monitor.time_operation("checkpoint_save"):
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
                    
                    # 진행률 업데이트
                    if progress_bar:
                        progress_bar.set_postfix({
                            '상태': result.status.value[:4],
                            '신뢰도': f"{result.avg_confidence:.0f}%",
                            '단어': result.total_words
                        })
                        progress_bar.update(1)
                        
                except Exception as e:
                    self.logger.error(f"페이지 {page_num} 처리 실패: {e}")
                    results.append(PageResult(
                        page_number=page_num,
                        status=ProcessingStatus.FAILED,
                        error_message=str(e)
                    ))
                    
                    if progress_bar:
                        progress_bar.update(1)
            
            if progress_bar:
                progress_bar.close()
        
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


# 배치 처리 및 유틸리티 함수
async def process_documents_batch(
    file_paths: List[Path], 
    output_dir: Path, 
    config: ProcessingConfig,
    max_concurrent: int = 3
) -> List[DocumentResult]:
    """여러 문서 배치 처리 (동시 실행 제한)"""
    
    processor = ProcessorFactory.create_processor(config)
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_single(file_path: Path) -> DocumentResult:
        async with semaphore:
            return await processor.process_document(file_path, output_dir)
    
    # 모든 작업 시작
    tasks = [process_single(file_path) for file_path in file_paths]
    
    results = []
    total_files = len(file_paths)
    
    # 진행률 표시
    if config.progress_bar:
        progress = tqdm(
            total=total_files, 
            desc="📁 배치 처리", 
            unit="파일",
            ncols=100
        )
    else:
        progress = None
    
    for completed_task in asyncio.as_completed(tasks):
        result = await completed_task
        results.append(result)
        
        if progress:
            status_emoji = "✅" if result.status == ProcessingStatus.COMPLETED else "❌"
            progress.set_postfix({
                '파일': result.file_path.name[:20],
                '상태': status_emoji,
                '페이지': f"{result.processed_pages}/{result.total_pages}"
            })
            progress.update(1)
    
    if progress:
        progress.close()
    
    return results


def create_processing_report(results: List[DocumentResult], output_path: Optional[Path] = None) -> Dict:
    """처리 결과 보고서 생성"""
    
    total_files = len(results)
    successful_files = sum(1 for r in results if r.status == ProcessingStatus.COMPLETED)
    failed_files = total_files - successful_files
    
    total_pages = sum(r.total_pages for r in results)
    processed_pages = sum(r.processed_pages for r in results)
    total_words = sum(r.total_words for r in results)
    
    avg_confidence = sum(r.avg_confidence for r in results if r.avg_confidence > 0) / max(successful_files, 1)
    total_processing_time = sum(r.processing_time for r in results)
    
    # 언어별 통계
    language_stats = {}
    for result in results:
        for lang in result.detected_languages:
            language_stats[lang] = language_stats.get(lang, 0) + 1
    
    report = {
        "처리_요약": {
            "총_파일_수": total_files,
            "성공한_파일": successful_files,
            "실패한_파일": failed_files,
            "성공률": f"{successful_files / max(total_files, 1) * 100:.1f}%"
        },
        "페이지_통계": {
            "총_페이지": total_pages,
            "처리된_페이지": processed_pages,
            "페이지_처리율": f"{processed_pages / max(total_pages, 1) * 100:.1f}%"
        },
        "OCR_성능": {
            "추출된_단어": total_words,
            "평균_신뢰도": f"{avg_confidence:.2f}%",
            "평균_페이지당_단어": f"{total_words / max(processed_pages, 1):.1f}개"
        },
        "시간_성능": {
            "총_처리_시간": f"{total_processing_time:.2f}초",
            "평균_파일_처리_시간": f"{total_processing_time / max(total_files, 1):.2f}초",
            "페이지_처리_속도": f"{processed_pages / max(total_processing_time, 1):.2f}페이지/초"
        },
        "언어_통계": language_stats,
        "실패한_파일들": [
            {
                "파일": str(r.file_path),
                "오류_페이지": len(r.error_pages),
                "처리_시간": f"{r.processing_time:.2f}초"
            }
            for r in results if r.status == ProcessingStatus.FAILED
        ]
    }
    
    # 보고서 저장 (옵션)
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    
    return report


# 사용 예시 및 테스트 함수
async def example_usage():
    """사용 예시"""
    
    # 1. 기본 설정
    config = ProcessorFactory.create_config(
        dpi=300,
        language="auto",
        auto_dpi=True,
        auto_language=True,
        workers=4,
        save_json=True,
        cache_enabled=True,
        preprocessing_enabled=True,
        noise_removal=True,
        enhance_contrast=True,
        skip_blank_pages=True,
        progress_bar=True
    )
    
    # 2. 단일 파일 처리
    print("=== 단일 파일 처리 예시 ===")
    processor = ProcessorFactory.create_processor(config)
    
    # result = await processor.process_document(
    #     Path("sample.pdf"),
    #     Path("./output")
    # )
    # print(f"처리 결과: {result.status.value}")
    # print(f"추출된 단어: {result.total_words}개")
    # print(f"평균 신뢰도: {result.avg_confidence:.2f}%")
    
    # 3. 배치 처리
    print("\n=== 배치 처리 예시 ===")
    file_paths = [
        # Path("document1.pdf"),
        # Path("document2.pdf"),
        # Path("document3.pdf")
    ]
    
    if file_paths:
        results = await process_documents_batch(
            file_paths,
            Path("./output"),
            config,
            max_concurrent=2
        )
        
        # 4. 보고서 생성
        report = create_processing_report(results, Path("./output/processing_report.json"))
        
        print("📊 처리 보고서:")
        for section, data in report.items():
            if isinstance(data, dict):
                print(f"\n{section}:")
                for key, value in data.items():
                    print(f"  {key}: {value}")
            else:
                print(f"{section}: {data}")


if __name__ == "__main__":
    # 간단한 테스트
    async def main():
        try:
            await example_usage()
        except KeyboardInterrupt:
            print("\n⏹️  처리 중단됨")
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()
    
    # 이벤트 루프 실행
    try:
        asyncio.run(main())
    except RuntimeError:
        # Jupyter 등에서 실행시
        import nest_asyncio
        nest_asyncio.apply()
        asyncio.get_event_loop().run_until_complete(main())