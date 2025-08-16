"""
FastAPI 기반 PDF OCR 웹 API 서버
Web API Server for PDF OCR Processing
"""

import asyncio
import logging
import mimetypes
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, List, Optional, Union

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile, BackgroundTasks, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from config import Config, ConfigManager
from pdf_processor import PDFProcessor, ProcessorFactory, ProcessingConfig, DocumentResult, ProcessingStatus


# Pydantic 모델들
class ProcessingRequest(BaseModel):
    """처리 요청 모델"""
    dpi: Optional[int] = Field(default=300, ge=50, le=1000, description="이미지 변환 DPI")
    language: Optional[str] = Field(default="auto", description="OCR 언어 (auto, eng, kor 등)")
    confidence_threshold: Optional[int] = Field(default=50, ge=0, le=100, description="텍스트 신뢰도 임계값")
    auto_dpi: Optional[bool] = Field(default=False, description="자동 DPI 선택")
    save_json: Optional[bool] = Field(default=False, description="JSON 사이드카 저장")
    workers: Optional[int] = Field(default=4, ge=1, le=16, description="병렬 처리 워커 수")


class ProcessingResponse(BaseModel):
    """처리 응답 모델"""
    task_id: str
    status: str
    message: str
    estimated_time: Optional[int] = None


class TaskStatus(BaseModel):
    """작업 상태 모델"""
    task_id: str
    status: str
    progress: float
    total_pages: int
    processed_pages: int
    processing_time: float
    error_message: Optional[str] = None
    result_urls: Optional[Dict[str, str]] = None


class DocumentInfo(BaseModel):
    """문서 정보 모델"""
    filename: str
    file_size: int
    total_pages: int
    file_type: str


class HealthCheck(BaseModel):
    """헬스체크 모델"""
    status: str
    version: str
    uptime: float
    active_tasks: int
    system_info: Dict[str, Union[str, int, float]]


# 태스크 매니저
class TaskManager:
    """비동기 태스크 관리자"""
    
    def __init__(self):
        self.tasks: Dict[str, Dict] = {}
        self.results: Dict[str, DocumentResult] = {}
        self.start_time = time.time()
    
    def create_task(self, file_path: Path, config: ProcessingConfig) -> str:
        """새 태스크 생성"""
        task_id = str(uuid.uuid4())
        self.tasks[task_id] = {
            "status": ProcessingStatus.PENDING,
            "file_path": file_path,
            "config": config,
            "created_at": time.time(),
            "progress": 0.0,
            "total_pages": 0,
            "processed_pages": 0
        }
        return task_id
    
    def update_task(self, task_id: str, **kwargs):
        """태스크 상태 업데이트"""
        if task_id in self.tasks:
            self.tasks[task_id].update(kwargs)
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """태스크 정보 조회"""
        return self.tasks.get(task_id)
    
    def set_result(self, task_id: str, result: DocumentResult):
        """태스크 결과 저장"""
        self.results[task_id] = result
        self.update_task(
            task_id,
            status=result.status,
            total_pages=result.total_pages,
            processed_pages=result.processed_pages,
            processing_time=result.processing_time
        )
    
    def get_result(self, task_id: str) -> Optional[DocumentResult]:
        """태스크 결과 조회"""
        return self.results.get(task_id)
    
    def get_active_task_count(self) -> int:
        """활성 태스크 수"""
        return sum(
            1 for task in self.tasks.values()
            if task["status"] in [ProcessingStatus.PENDING, ProcessingStatus.IN_PROGRESS]
        )
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """오래된 태스크 정리"""
        current_time = time.time()
        cutoff_time = current_time - (max_age_hours * 3600)
        
        old_task_ids = [
            task_id for task_id, task in self.tasks.items()
            if task["created_at"] < cutoff_time
        ]
        
        for task_id in old_task_ids:
            self.tasks.pop(task_id, None)
            self.results.pop(task_id, None)


# 미들웨어
class RateLimitMiddleware(BaseHTTPMiddleware):
    """요청 제한 미들웨어"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, List[float]] = {}
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # 클라이언트별 요청 기록 관리
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # 1분 이내 요청들만 유지
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < 60
        ]
        
        # 요청 제한 확인
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Try again later."}
            )
        
        # 현재 요청 기록
        self.requests[client_ip].append(current_time)
        
        response = await call_next(request)
        return response


# 인증
class APIKeyAuth:
    """API 키 기반 인증"""
    
    def __init__(self, api_key: Optional[str]):
        self.api_key = api_key
        self.security = HTTPBearer() if api_key else None
    
    async def __call__(self, credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())):
        if not self.api_key:
            return True  # 인증 비활성화
        
        if not credentials or credentials.credentials != self.api_key:
            raise HTTPException(
                status_code=401,
                detail="Invalid API key"
            )
        return True


# 전역 변수들
task_manager = TaskManager()
config_manager = ConfigManager()
app_config: Config = None
processor: PDFProcessor = None
auth: APIKeyAuth = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 생명주기 관리"""
    global app_config, processor, auth
    
    # 시작 시 초기화
    app_config = config_manager.load_config()
    
    # 프로세서 초기화
    processing_config = ProcessingConfig(
        dpi=app_config.image.default_dpi,
        language=app_config.ocr.default_language,
        confidence_threshold=app_config.ocr.confidence_threshold,
        workers=app_config.processing.max_workers,
        auto_dpi=app_config.image.auto_dpi_enabled,
        save_json=app_config.output.save_json,
        cache_enabled=app_config.cache.enabled,
        cache_ttl=app_config.cache.ttl_seconds
    )
    processor = ProcessorFactory.create_processor(processing_config)
    
    # 인증 초기화
    auth = APIKeyAuth(app_config.api.api_key)
    
    # 출력 디렉토리 생성
    Path(app_config.output.output_directory).mkdir(parents=True, exist_ok=True)
    
    logging.info("PDF OCR API 서버 시작됨")
    
    yield
    
    # 종료 시 정리
    logging.info("PDF OCR API 서버 종료됨")


# FastAPI 앱 생성
app = FastAPI(
    title="PDF OCR API",
    description="PDF 문서 OCR 처리를 위한 REST API",
    version="1.0.0",
    lifespan=lifespan
)


# CORS 설정
async def setup_cors():
    if app_config and app_config.api.cors_enabled:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


# Rate limiting 설정
async def setup_rate_limiting():
    if app_config and app_config.api.rate_limit_enabled:
        app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=app_config.api.requests_per_minute
        )


# 백그라운드 태스크
async def process_document_task(task_id: str, file_path: Path, config: ProcessingConfig):
    """문서 처리 백그라운드 태스크"""
    try:
        # 태스크 상태 업데이트
        task_manager.update_task(task_id, status=ProcessingStatus.IN_PROGRESS)
        
        # 문서 처리
        result = await processor.process_document(
            file_path, 
            Path(app_config.output.output_directory)
        )
        
        # 결과 저장
        task_manager.set_result(task_id, result)
        
    except Exception as e:
        logging.error(f"태스크 {task_id} 처리 실패: {e}")
        task_manager.update_task(
            task_id, 
            status=ProcessingStatus.FAILED,
            error_message=str(e)
        )


# API 엔드포인트들
@app.get("/", response_model=dict)
async def root():
    """루트 엔드포인트"""
    return {
        "message": "PDF OCR API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "/health"
    }


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """헬스체크"""
    import psutil
    import platform
    
    return HealthCheck(
        status="healthy",
        version="1.0.0",
        uptime=time.time() - task_manager.start_time,
        active_tasks=task_manager.get_active_task_count(),
        system_info={
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "disk_free": psutil.disk_usage("/").free
        }
    )


@app.post("/upload", response_model=ProcessingResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    request: ProcessingRequest = ProcessingRequest(),
    authenticated: bool = Depends(auth)
):
    """파일 업로드 및 처리 시작"""
    
    # 파일 검증
    if not file.filename:
        raise HTTPException(status_code=400, detail="파일명이 없습니다")
    
    file_path = Path(file.filename)
    if not app_config.security.is_allowed_file(file_path):
        raise HTTPException(
            status_code=400, 
            detail=f"지원하지 않는 파일 형식입니다: {file_path.suffix}"
        )
    
    # 임시 파일 저장
    temp_dir = Path(app_config.security.temp_directory)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    temp_file_path = temp_dir / f"{uuid.uuid4()}_{file.filename}"
    
    try:
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 파일 크기 검증
        if not app_config.security.is_file_size_valid(temp_file_path):
            temp_file_path.unlink()
            raise HTTPException(
                status_code=400,
                detail=f"파일 크기가 너무 큽니다 (최대: {app_config.security.max_file_size_mb}MB)"
            )
        
        # 처리 설정 생성
        processing_config = ProcessingConfig(
            dpi=request.dpi or app_config.image.default_dpi,
            language=request.language or app_config.ocr.default_language,
            confidence_threshold=request.confidence_threshold or app_config.ocr.confidence_threshold,
            workers=request.workers or app_config.processing.max_workers,
            auto_dpi=request.auto_dpi if request.auto_dpi is not None else app_config.image.auto_dpi_enabled,
            save_json=request.save_json if request.save_json is not None else app_config.output.save_json
        )
        
        # 태스크 생성
        task_id = task_manager.create_task(temp_file_path, processing_config)
        
        # 백그라운드에서 처리 시작
        background_tasks.add_task(
            process_document_task,
            task_id,
            temp_file_path,
            processing_config
        )
        
        return ProcessingResponse(
            task_id=task_id,
            status="accepted",
            message="파일 업로드 완료. 처리가 시작되었습니다.",
            estimated_time=None
        )
        
    except HTTPException:
        # HTTP 예외는 그대로 전달
        if temp_file_path.exists():
            temp_file_path.unlink()
        raise
    except Exception as e:
        # 기타 예외 처리
        if temp_file_path.exists():
            temp_file_path.unlink()
        raise HTTPException(status_code=500, detail=f"파일 처리 오류: {str(e)}")


@app.get("/status/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str, authenticated: bool = Depends(auth)):
    """태스크 상태 조회"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="태스크를 찾을 수 없습니다")
    
    result_urls = None
    if task["status"] == ProcessingStatus.COMPLETED:
        result = task_manager.get_result(task_id)
        if result:
            base_name = result.file_path.stem
            result_urls = {
                "pdf": f"/download/{task_id}/pdf",
                "json": f"/download/{task_id}/json" if app_config.output.save_json else None
            }
    
    return TaskStatus(
        task_id=task_id,
        status=task["status"].value if hasattr(task["status"], "value") else str(task["status"]),
        progress=task.get("progress", 0.0),
        total_pages=task.get("total_pages", 0),
        processed_pages=task.get("processed_pages", 0),
        processing_time=task.get("processing_time", 0.0),
        error_message=task.get("error_message"),
        result_urls=result_urls
    )


@app.get("/download/{task_id}/{file_type}")
async def download_result(
    task_id: str, 
    file_type: str,
    authenticated: bool = Depends(auth)
):
    """처리 결과 다운로드"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="태스크를 찾을 수 없습니다")
    
    if task["status"] != ProcessingStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="처리가 완료되지 않았습니다")
    
    result = task_manager.get_result(task_id)
    if not result:
        raise HTTPException(status_code=404, detail="처리 결과를 찾을 수 없습니다")
    
    output_dir = Path(app_config.output.output_directory)
    base_name = f"{result.file_path.stem}_searchable"
    
    if file_type == "pdf":
        file_path = output_dir / f"{base_name}.pdf"
        media_type = "application/pdf"
    elif file_type == "json":
        if not app_config.output.save_json:
            raise HTTPException(status_code=404, detail="JSON 파일이 생성되지 않았습니다")
        file_path = output_dir / f"{base_name}.json"
        media_type = "application/json"
    else:
        raise HTTPException(status_code=400, detail="지원하지 않는 파일 형식입니다")
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
    
    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=file_path.name
    )


@app.get("/tasks", response_model=List[TaskStatus])
async def list_tasks(
    limit: int = 10,
    status_filter: Optional[str] = None,
    authenticated: bool = Depends(auth)
):
    """태스크 목록 조회"""
    tasks = []
    
    for task_id, task_data in list(task_manager.tasks.items())[-limit:]:
        if status_filter and str(task_data["status"]) != status_filter:
            continue
        
        result_urls = None
        if task_data["status"] == ProcessingStatus.COMPLETED:
            result = task_manager.get_result(task_id)
            if result:
                result_urls = {
                    "pdf": f"/download/{task_id}/pdf",
                    "json": f"/download/{task_id}/json" if app_config.output.save_json else None
                }
        
        tasks.append(TaskStatus(
            task_id=task_id,
            status=task_data["status"].value if hasattr(task_data["status"], "value") else str(task_data["status"]),
            progress=task_data.get("progress", 0.0),
            total_pages=task_data.get("total_pages", 0),
            processed_pages=task_data.get("processed_pages", 0),
            processing_time=task_data.get("processing_time", 0.0),
            error_message=task_data.get("error_message"),
            result_urls=result_urls
        ))
    
    return tasks


@app.delete("/tasks/{task_id}")
async def cancel_task(task_id: str, authenticated: bool = Depends(auth)):
    """태스크 취소"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="태스크를 찾을 수 없습니다")
    
    if task["status"] in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED]:
        raise HTTPException(status_code=400, detail="이미 완료된 태스크입니다")
    
    # 태스크 취소 (실제 구현에서는 더 정교한 취소 로직 필요)
    task_manager.update_task(task_id, status=ProcessingStatus.CANCELLED)
    
    return {"message": "태스크가 취소되었습니다"}


@app.post("/cleanup")
async def cleanup_old_tasks(authenticated: bool = Depends(auth)):
    """오래된 태스크 정리"""
    task_manager.cleanup_old_tasks()
    return {"message": "오래된 태스크가 정리되었습니다"}


# 서버 실행 함수
def create_app() -> FastAPI:
    """FastAPI 앱 생성"""
    return app


def run_server(
    host: str = "127.0.0.1",
    port: int = 8000,
    workers: int = 1,
    reload: bool = False
):
    """서버 실행"""
    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        workers=workers,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    # 설정 로드
    config = config_manager.load_config()
    
    # 서버 실행
    run_server(
        host=config.api.host,
        port=config.api.port,
        workers=config.api.workers,
        reload=False
    )