# 🚀 Enhanced PDF OCR Processor

대용량 PDF 문서의 OCR 처리를 위한 고성능, 확장 가능한 시스템입니다.

## ✨ 주요 기능

### 🔧 핵심 기능
- **대용량 PDF 처리**: 체크포인트 기반 재개 가능한 처리
- **자동 DPI 최적화**: 문서별 최적 DPI 자동 선택
- **병렬 처리**: 멀티프로세싱을 통한 고속 처리
- **다국어 지원**: 자동 언어 감지 및 다양한 언어 OCR
- **스마트 캐싱**: 결과 캐싱으로 재처리 시간 단축

### 🌐 인터페이스
- **CLI**: 풍부한 기능의 명령행 인터페이스
- **Web API**: RESTful API 서버
- **설정 관리**: JSON 기반 유연한 설정 시스템

### 🛡️ 고급 기능
- **에러 복구**: 중단된 작업 자동 재개
- **보안**: 파일 크기/형식 검증, 인증
- **모니터링**: 실시간 진행률 및 성능 지표
- **확장성**: 플러그인 가능한 아키텍처

## 📋 요구사항

### 시스템 요구사항
- Python 3.13+
- Tesseract OCR 엔진
- Poppler (PDF 변환용)

### Python 패키지
주요 의존성은 `pyproject.toml`에 정의되어 있습니다:
- `pytesseract`: OCR 엔진
- `pdf2image`: PDF 이미지 변환
- `fastapi`: Web API 프레임워크
- `rich`: CLI 인터페이스
- `PIL`: 이미지 처리

## 🚀 설치

### 1. 저장소 클론
```bash
git clone <repository-url>
cd practice/garage
```

### 2. 의존성 설치
```bash
pip install -e .
```

### 3. 시스템 의존성 설치

#### macOS (Homebrew)
```bash
brew install tesseract poppler
```

#### Ubuntu/Debian
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-kor poppler-utils
```

#### Windows
1. [Tesseract](https://github.com/tesseract-ocr/tesseract) 설치
2. [Poppler](https://poppler.freedesktop.org/) 설치
3. 환경변수 PATH에 경로 추가

## 🎯 사용법

### CLI 사용법

#### 기본 처리
```bash
# 단일 파일 처리
python cli.py process input.pdf

# 폴더 일괄 처리
python cli.py process documents/ --recursive

# 고성능 처리
python cli.py process input.pdf --auto-dpi --workers 8 --save-json
```

#### 설정 관리
```bash
# 설정 파일 생성
python cli.py config create

# 현재 설정 확인
python cli.py config show

# 설정 검증
python cli.py config validate
```

#### 문서 분석
```bash
# PDF 분석
python cli.py analyze document.pdf

# 성능 벤치마크
python cli.py benchmark
```

#### API 서버
```bash
# 서버 시작
python cli.py server start

# 포트 지정
python cli.py server start --port 8080
```

### Web API 사용법

#### 서버 시작
```bash
python cli.py server start --host 0.0.0.0 --port 8000
```

#### API 엔드포인트

**파일 업로드 및 처리 시작**
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@document.pdf" \
  -F "dpi=300" \
  -F "language=auto" \
  -F "auto_dpi=true"
```

**처리 상태 확인**
```bash
curl "http://localhost:8000/status/{task_id}"
```

**결과 다운로드**
```bash
curl -O "http://localhost:8000/download/{task_id}/pdf"
```

### Python API 사용법

```python
import asyncio
from pathlib import Path
from garage.pdf_processor import ProcessorFactory, ProcessingConfig

async def main():
    # 설정 생성
    config = ProcessingConfig(
        dpi=300,
        language="auto",
        auto_dpi=True,
        workers=4,
        save_json=True
    )
    
    # 프로세서 생성
    processor = ProcessorFactory.create_processor(config)
    
    # 문서 처리
    result = await processor.process_document(
        Path("input.pdf"),
        Path("./output")
    )
    
    print(f"처리 완료: {result.status}")
    print(f"처리된 페이지: {result.processed_pages}/{result.total_pages}")

asyncio.run(main())
```

## ⚙️ 설정

### 설정 파일 예시 (`config.json`)

```json
{
  "ocr": {
    "default_language": "auto",
    "confidence_threshold": 50,
    "supported_languages": ["eng", "kor", "jpn", "auto"]
  },
  "image": {
    "default_dpi": 300,
    "auto_dpi_enabled": true,
    "dpi_candidates": [200, 300, 400, 500],
    "preprocessing_enabled": true,
    "binarization_threshold": 140
  },
  "processing": {
    "max_workers": 4,
    "batch_size": 10,
    "timeout_per_page": 300,
    "resume_enabled": true
  },
  "output": {
    "save_json": false,
    "keep_checkpoints": false,
    "output_directory": "./output",
    "filename_template": "{stem}_searchable.pdf"
  },
  "cache": {
    "enabled": true,
    "ttl_seconds": 86400,
    "max_size_mb": 512
  },
  "api": {
    "enabled": false,
    "host": "127.0.0.1",
    "port": 8000,
    "cors_enabled": true,
    "rate_limit_enabled": true,
    "requests_per_minute": 60
  }
}
```

### 환경 변수

주요 설정은 환경 변수로 오버라이드 가능합니다:

```bash
export OCR_LANGUAGE=kor
export IMAGE_DPI=400
export MAX_WORKERS=8
export OUTPUT_DIR=./results
export API_ENABLED=true
export API_PORT=8080
```

## 🧪 테스트

### 테스트 실행
```bash
# 전체 테스트
pytest

# 단위 테스트만
pytest -m unit

# 커버리지 포함
pytest --cov=garage --cov-report=html

# 특정 테스트 파일
pytest tests/test_processor.py -v
```

### 테스트 카테고리
- `unit`: 단위 테스트
- `integration`: 통합 테스트
- `api`: API 테스트
- `slow`: 시간이 오래 걸리는 테스트

## 📁 프로젝트 구조

```
garage/
├── cli.py                  # CLI 인터페이스
├── api_server.py          # Web API 서버
├── pdf_processor.py       # 핵심 처리 로직
├── config.py              # 설정 관리
├── search_pdf.py          # 기존 스크립트 (호환성)
├── tests/                 # 테스트 파일들
│   ├── __init__.py
│   ├── conftest.py        # 테스트 설정
│   ├── test_config.py     # 설정 테스트
│   ├── test_processor.py  # 프로세서 테스트
│   └── test_api.py        # API 테스트
├── pytest.ini            # Pytest 설정
└── README.md              # 문서
```

## 🔄 기존 코드와의 호환성

기존 `search_pdf.py` 스크립트는 그대로 사용할 수 있습니다:

```bash
python search_pdf.py --input document.pdf --auto-dpi --workers 4
```

새로운 CLI는 더 많은 기능을 제공합니다:

```bash
python cli.py process document.pdf --auto-dpi --workers 4
```

## 🚀 성능 최적화 팁

### 1. DPI 설정
- `--auto-dpi`: 자동 최적화 (권장)
- 수동 설정: 일반 문서 300 DPI, 고해상도 필요시 400-500 DPI

### 2. 병렬 처리
- `--workers`: CPU 코어 수의 75% 정도 권장
- 메모리 사용량 고려하여 조정

### 3. 캐시 활용
- 설정에서 캐시 활성화
- 반복 처리 시 성능 향상

### 4. 체크포인트
- 대용량 파일은 `--resume` 옵션 활용
- 중단된 작업 자동 재개

## 🐛 문제 해결

### 일반적인 문제

**Tesseract를 찾을 수 없음**
```bash
# Windows
set TESSERACT_PATH="C:\Program Files\Tesseract-OCR\tesseract.exe"

# 또는 config.json에서
"tesseract_path": "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
```

**메모리 부족**
- `workers` 수 줄이기
- `batch_size` 줄이기
- 대용량 파일은 체크포인트 모드 사용

**처리 속도 느림**
- `--auto-dpi` 사용
- `workers` 수 늘리기
- SSD 사용 권장

### 디버그 모드
```bash
python cli.py process document.pdf --verbose
```

## 📊 모니터링

### 성능 지표
- 페이지 처리 속도
- 메모리 사용량
- CPU 사용률
- 캐시 적중률

### 로그 분석
로그 파일은 출력 디렉토리의 `logs/` 폴더에 저장됩니다.

## 🔒 보안

### 파일 검증
- 허용된 파일 형식만 처리
- 파일 크기 제한
- 악성 파일 스캔 (선택사항)

### API 보안
- API 키 인증
- 요청 제한
- CORS 설정

## 📈 확장성

### 플러그인 시스템
새로운 전처리기나 후처리기를 쉽게 추가할 수 있습니다.

### 스케일링
- 분산 처리를 위한 Redis/Celery 통합 가능
- 클라우드 배포 지원
- Docker 컨테이너화

## 🤝 기여

1. Fork 생성
2. 기능 브랜치 생성 (`git checkout -b feature/AmazingFeature`)
3. 변경사항 커밋 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치 푸시 (`git push origin feature/AmazingFeature`)
5. Pull Request 생성

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🙏 감사의 말

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [pdf2image](https://github.com/Belval/pdf2image)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Rich](https://github.com/willmcgugan/rich)

---

더 자세한 정보나 지원이 필요하시면 Issues를 생성해 주세요.