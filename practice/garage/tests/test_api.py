"""
API Server tests
API 서버 테스트
"""

import asyncio
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import pytest
from fastapi.testclient import TestClient

from garage.api_server import app, TaskManager, ProcessingRequest
from garage.config import Config
from garage.pdf_processor import ProcessingStatus, DocumentResult


@pytest.fixture
def client():
    """테스트 클라이언트 생성"""
    return TestClient(app)


@pytest.fixture
def task_manager():
    """태스크 매니저 픽스처"""
    return TaskManager()


class TestTaskManager:
    """태스크 매니저 테스트"""
    
    def test_create_task(self, task_manager):
        """태스크 생성 테스트"""
        from garage.pdf_processor import ProcessingConfig
        
        file_path = Path("test.pdf")
        config = ProcessingConfig()
        
        task_id = task_manager.create_task(file_path, config)
        
        assert task_id is not None
        assert len(task_id) > 0
        
        task = task_manager.get_task(task_id)
        assert task is not None
        assert task["file_path"] == file_path
        assert task["status"] == ProcessingStatus.PENDING
    
    def test_update_task(self, task_manager):
        """태스크 업데이트 테스트"""
        from garage.pdf_processor import ProcessingConfig
        
        file_path = Path("test.pdf")
        config = ProcessingConfig()
        
        task_id = task_manager.create_task(file_path, config)
        
        # 상태 업데이트
        task_manager.update_task(task_id, status=ProcessingStatus.IN_PROGRESS)
        
        task = task_manager.get_task(task_id)
        assert task["status"] == ProcessingStatus.IN_PROGRESS
    
    def test_set_result(self, task_manager):
        """결과 설정 테스트"""
        from garage.pdf_processor import ProcessingConfig
        
        file_path = Path("test.pdf")
        config = ProcessingConfig()
        
        task_id = task_manager.create_task(file_path, config)
        
        # 결과 생성
        result = DocumentResult(
            file_path=file_path,
            total_pages=10,
            processed_pages=10,
            status=ProcessingStatus.COMPLETED,
            processing_time=30.5
        )
        
        task_manager.set_result(task_id, result)
        
        # 검증
        stored_result = task_manager.get_result(task_id)
        assert stored_result == result
        
        task = task_manager.get_task(task_id)
        assert task["status"] == ProcessingStatus.COMPLETED
        assert task["total_pages"] == 10
        assert task["processed_pages"] == 10
    
    def test_cleanup_old_tasks(self, task_manager):
        """오래된 태스크 정리 테스트"""
        import time
        from garage.pdf_processor import ProcessingConfig
        
        file_path = Path("test.pdf")
        config = ProcessingConfig()
        
        # 태스크 생성
        task_id = task_manager.create_task(file_path, config)
        
        # 생성 시간을 과거로 설정
        task_manager.tasks[task_id]["created_at"] = time.time() - 25 * 3600  # 25시간 전
        
        # 정리 실행
        task_manager.cleanup_old_tasks(max_age_hours=24)
        
        # 태스크가 제거되었는지 확인
        assert task_manager.get_task(task_id) is None


class TestProcessingRequest:
    """처리 요청 모델 테스트"""
    
    def test_valid_request(self):
        """유효한 요청 테스트"""
        request = ProcessingRequest(
            dpi=300,
            language="kor",
            confidence_threshold=70,
            auto_dpi=True,
            save_json=True,
            workers=4
        )
        
        assert request.dpi == 300
        assert request.language == "kor"
        assert request.confidence_threshold == 70
        assert request.auto_dpi is True
        assert request.save_json is True
        assert request.workers == 4
    
    def test_default_values(self):
        """기본값 테스트"""
        request = ProcessingRequest()
        
        assert request.dpi == 300
        assert request.language == "auto"
        assert request.confidence_threshold == 50
        assert request.auto_dpi is False
        assert request.save_json is False
        assert request.workers == 4
    
    def test_validation_errors(self):
        """검증 오류 테스트"""
        with pytest.raises(ValueError):
            ProcessingRequest(dpi=10)  # 최소값 미만
        
        with pytest.raises(ValueError):
            ProcessingRequest(dpi=2000)  # 최대값 초과
        
        with pytest.raises(ValueError):
            ProcessingRequest(confidence_threshold=-1)  # 음수
        
        with pytest.raises(ValueError):
            ProcessingRequest(workers=0)  # 0 이하


class TestAPIEndpoints:
    """API 엔드포인트 테스트"""
    
    @patch('garage.api_server.app_config')
    def test_root_endpoint(self, mock_config, client):
        """루트 엔드포인트 테스트"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["message"] == "PDF OCR API"
    
    @patch('garage.api_server.app_config')
    @patch('psutil.cpu_count')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_health_endpoint(self, mock_disk, mock_memory, mock_cpu, mock_config, client):
        """헬스체크 엔드포인트 테스트"""
        # Mock 설정
        mock_cpu.return_value = 8
        mock_memory.return_value = Mock(total=16*1024**3, available=8*1024**3)
        mock_disk.return_value = Mock(free=100*1024**3)
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "uptime" in data
        assert "system_info" in data
        assert data["system_info"]["cpu_count"] == 8
    
    @patch('garage.api_server.app_config')
    @patch('garage.api_server.auth')
    def test_upload_endpoint_validation(self, mock_auth, mock_config, client):
        """업로드 엔드포인트 검증 테스트"""
        # 인증 모킹
        mock_auth.return_value = True
        
        # 설정 모킹
        mock_security = Mock()
        mock_security.is_allowed_file.return_value = False
        mock_config.security = mock_security
        
        # 허용되지 않은 파일 업로드
        with tempfile.NamedTemporaryFile(suffix='.txt') as temp_file:
            response = client.post(
                "/upload",
                files={"file": ("test.txt", temp_file, "text/plain")}
            )
        
        assert response.status_code == 400
        assert "지원하지 않는 파일 형식" in response.json()["detail"]
    
    @patch('garage.api_server.app_config')
    @patch('garage.api_server.auth')
    @patch('garage.api_server.task_manager')
    def test_status_endpoint(self, mock_task_manager, mock_auth, mock_config, client):
        """상태 조회 엔드포인트 테스트"""
        # 인증 모킹
        mock_auth.return_value = True
        
        # 태스크 모킹
        mock_task = {
            "status": ProcessingStatus.COMPLETED,
            "progress": 100.0,
            "total_pages": 10,
            "processed_pages": 10,
            "processing_time": 30.5,
            "error_message": None
        }
        mock_task_manager.get_task.return_value = mock_task
        
        # 결과 모킹
        mock_result = DocumentResult(
            file_path=Path("test.pdf"),
            total_pages=10,
            processed_pages=10,
            status=ProcessingStatus.COMPLETED,
            processing_time=30.5
        )
        mock_task_manager.get_result.return_value = mock_result
        
        response = client.get("/status/test-task-id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "test-task-id"
        assert data["status"] == "completed"
        assert data["total_pages"] == 10
        assert data["processed_pages"] == 10
    
    @patch('garage.api_server.app_config')
    @patch('garage.api_server.auth')
    @patch('garage.api_server.task_manager')
    def test_status_endpoint_not_found(self, mock_task_manager, mock_auth, mock_config, client):
        """존재하지 않는 태스크 상태 조회 테스트"""
        # 인증 모킹
        mock_auth.return_value = True
        
        # 태스크 없음
        mock_task_manager.get_task.return_value = None
        
        response = client.get("/status/nonexistent-task-id")
        
        assert response.status_code == 404
        assert "태스크를 찾을 수 없습니다" in response.json()["detail"]
    
    @patch('garage.api_server.app_config')
    @patch('garage.api_server.auth')
    @patch('garage.api_server.task_manager')
    def test_tasks_list_endpoint(self, mock_task_manager, mock_auth, mock_config, client):
        """태스크 목록 조회 엔드포인트 테스트"""
        # 인증 모킹
        mock_auth.return_value = True
        
        # 태스크 목록 모킹
        mock_tasks = {
            "task1": {
                "status": ProcessingStatus.COMPLETED,
                "progress": 100.0,
                "total_pages": 5,
                "processed_pages": 5,
                "processing_time": 15.0
            },
            "task2": {
                "status": ProcessingStatus.IN_PROGRESS,
                "progress": 50.0,
                "total_pages": 10,
                "processed_pages": 5,
                "processing_time": 0.0
            }
        }
        mock_task_manager.tasks = mock_tasks
        mock_task_manager.get_result.return_value = None
        
        response = client.get("/tasks")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["task_id"] == "task1"
        assert data[1]["task_id"] == "task2"


class TestRateLimitMiddleware:
    """요청 제한 미들웨어 테스트"""
    
    @patch('garage.api_server.app_config')
    def test_rate_limit_within_bounds(self, mock_config, client):
        """정상적인 요청률 테스트"""
        # 설정 모킹
        mock_config.api.rate_limit_enabled = True
        mock_config.api.requests_per_minute = 60
        
        # 여러 요청을 빠르게 전송 (제한 내)
        for _ in range(5):
            response = client.get("/")
            assert response.status_code == 200
    
    @patch('garage.api_server.app_config')
    def test_rate_limit_exceeded(self, mock_config):
        """요청 제한 초과 테스트"""
        from garage.api_server import RateLimitMiddleware
        from starlette.applications import Starlette
        from starlette.responses import JSONResponse
        from starlette.testclient import TestClient as StarletteTestClient
        
        # 간단한 앱 생성
        app = Starlette()
        app.add_middleware(RateLimitMiddleware, requests_per_minute=2)
        
        @app.route("/")
        async def homepage(request):
            return JSONResponse({"message": "Hello"})
        
        client = StarletteTestClient(app)
        
        # 제한을 초과하는 요청 전송
        client.get("/")  # 1번째 요청
        client.get("/")  # 2번째 요청
        response = client.get("/")  # 3번째 요청 (제한 초과)
        
        assert response.status_code == 429
        assert "Rate limit exceeded" in response.json()["detail"]


class TestAuthenticationFlow:
    """인증 플로우 테스트"""
    
    @patch('garage.api_server.app_config')
    def test_no_auth_required(self, mock_config, client):
        """인증 불필요 시나리오 테스트"""
        # API 키 없는 설정
        mock_config.api.api_key = None
        
        response = client.get("/")
        assert response.status_code == 200
    
    @patch('garage.api_server.app_config')
    @patch('garage.api_server.auth')
    def test_valid_api_key(self, mock_auth, mock_config, client):
        """유효한 API 키 테스트"""
        # 인증 성공 모킹
        mock_auth.return_value = True
        
        headers = {"Authorization": "Bearer valid-api-key"}
        response = client.get("/health", headers=headers)
        
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])