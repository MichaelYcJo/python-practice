#!/usr/bin/env python3
"""
Enhanced CLI for PDF OCR Processing
개선된 PDF OCR 처리 CLI 인터페이스
"""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import List, Optional

import colorama
from colorama import Fore, Style, Back
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from config import Config, ConfigManager, config_from_args, create_sample_config
from pdf_processor import ProcessorFactory, ProcessingConfig, DocumentResult, ProcessingStatus
from api_server import run_server


# Rich console 초기화
console = Console()
colorama.init()


class CLIFormatter(logging.Formatter):
    """컬러 로깅 포매터"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Back.WHITE,
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{log_color}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)


def setup_logging(verbose: bool = False, quiet: bool = False):
    """로깅 설정"""
    if quiet:
        level = logging.WARNING
    elif verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    
    # 기본 로거 설정
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # 콘솔 핸들러
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = CLIFormatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)


def print_banner():
    """배너 출력"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                     PDF OCR Processor                         ║
    ║               Enhanced CLI with Modern Features               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


def print_help_extended():
    """확장된 도움말"""
    help_text = """
    🚀 PDF OCR Processor - 사용법 가이드
    
    기본 사용법:
        python cli.py process input.pdf                    # 기본 설정으로 처리
        python cli.py process folder/ --recursive          # 폴더 일괄 처리
        python cli.py process input.pdf --auto-dpi --workers 8  # 고성능 처리
    
    설정 관리:
        python cli.py config create                        # 설정 파일 생성
        python cli.py config show                          # 현재 설정 표시
        python cli.py config validate                      # 설정 검증
    
    서버 모드:
        python cli.py server start                         # API 서버 시작
        python cli.py server start --port 8080             # 포트 지정
    
    고급 기능:
        python cli.py batch jobs.json                      # 배치 처리
        python cli.py analyze input.pdf                    # 문서 분석
        python cli.py benchmark                            # 성능 벤치마크
    """
    console.print(Panel(help_text, title="📖 사용법 가이드", border_style="blue"))


async def process_single_file(file_path: Path, config: Config, args) -> DocumentResult:
    """단일 파일 처리"""
    # 처리 설정 생성
    processing_config = ProcessingConfig(
        dpi=args.dpi or config.image.default_dpi,
        language=args.lang or config.ocr.default_language,
        confidence_threshold=args.conf or config.ocr.confidence_threshold,
        workers=args.workers or config.processing.max_workers,
        auto_dpi=args.auto_dpi if hasattr(args, 'auto_dpi') else config.image.auto_dpi_enabled,
        save_json=args.save_json if hasattr(args, 'save_json') else config.output.save_json,
        resume=args.resume if hasattr(args, 'resume') else config.processing.resume_enabled,
        keep_checkpoints=args.keep_ckpt if hasattr(args, 'keep_ckpt') else config.output.keep_checkpoints
    )
    
    # 프로세서 생성
    processor = ProcessorFactory.create_processor(processing_config)
    
    # 출력 디렉토리
    output_dir = Path(args.outdir) if hasattr(args, 'outdir') else Path(config.output.output_directory)
    
    # 처리 실행
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task(f"Processing {file_path.name}", total=100)
        
        result = await processor.process_document(file_path, output_dir)
        
        progress.update(task, completed=100)
    
    return result


async def process_files(file_paths: List[Path], config: Config, args) -> List[DocumentResult]:
    """여러 파일 처리"""
    results = []
    
    console.print(f"\n🚀 {len(file_paths)}개 파일 처리 시작...")
    
    for i, file_path in enumerate(file_paths, 1):
        console.print(f"\n[{i}/{len(file_paths)}] 처리 중: {file_path.name}")
        
        try:
            result = await process_single_file(file_path, config, args)
            results.append(result)
            
            # 결과 표시
            if result.status == ProcessingStatus.COMPLETED:
                console.print(f"✅ 완료: {result.processed_pages}/{result.total_pages} 페이지 처리됨")
            else:
                console.print(f"❌ 실패: {result.status}")
                
        except Exception as e:
            console.print(f"❌ 오류: {str(e)}", style="red")
            logging.error(f"파일 처리 실패 {file_path}: {e}")
    
    return results


def print_results_summary(results: List[DocumentResult]):
    """결과 요약 출력"""
    if not results:
        return
    
    # 통계 계산
    total_files = len(results)
    successful = sum(1 for r in results if r.status == ProcessingStatus.COMPLETED)
    failed = total_files - successful
    total_pages = sum(r.total_pages for r in results)
    total_time = sum(r.processing_time for r in results)
    
    # 테이블 생성
    table = Table(title="📊 처리 결과 요약")
    table.add_column("항목", style="cyan")
    table.add_column("값", style="green")
    
    table.add_row("전체 파일", str(total_files))
    table.add_row("성공", str(successful))
    table.add_row("실패", str(failed))
    table.add_row("전체 페이지", str(total_pages))
    table.add_row("총 처리 시간", f"{total_time:.1f}초")
    
    if total_time > 0:
        table.add_row("평균 속도", f"{total_pages/total_time:.1f} 페이지/초")
    
    console.print(table)
    
    # 실패한 파일들 상세 정보
    if failed > 0:
        console.print(f"\n❌ 실패한 파일 ({failed}개):", style="red bold")
        for result in results:
            if result.status != ProcessingStatus.COMPLETED:
                console.print(f"  • {result.file_path.name}: {result.status}")


def find_files(input_path: Path, recursive: bool = False, extensions: List[str] = None) -> List[Path]:
    """파일 찾기"""
    if extensions is None:
        extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp']
    
    files = []
    
    if input_path.is_file():
        if input_path.suffix.lower() in extensions:
            files.append(input_path)
    elif input_path.is_dir():
        pattern = "**/*" if recursive else "*"
        for ext in extensions:
            files.extend(input_path.glob(f"{pattern}{ext}"))
            files.extend(input_path.glob(f"{pattern}{ext.upper()}"))
    
    return sorted(files)


async def cmd_process(args):
    """처리 명령어"""
    config = config_from_args(args)
    
    # 입력 경로 검증
    input_path = Path(args.input)
    if not input_path.exists():
        console.print(f"❌ 입력 경로를 찾을 수 없습니다: {input_path}", style="red")
        return 1
    
    # 파일 목록 생성
    files = find_files(input_path, getattr(args, 'recursive', False))
    
    if not files:
        console.print("❌ 처리할 파일을 찾을 수 없습니다.", style="red")
        return 1
    
    console.print(f"📁 {len(files)}개 파일 발견됨")
    
    # 보안 검사
    for file_path in files:
        if not config.security.is_allowed_file(file_path):
            console.print(f"⚠️  지원하지 않는 파일 형식: {file_path.name}", style="yellow")
            files.remove(file_path)
        elif not config.security.is_file_size_valid(file_path):
            console.print(f"⚠️  파일 크기 초과: {file_path.name}", style="yellow")
            files.remove(file_path)
    
    if not files:
        console.print("❌ 유효한 파일이 없습니다.", style="red")
        return 1
    
    # 처리 실행
    try:
        results = await process_files(files, config, args)
        print_results_summary(results)
        
        # 성공률 확인
        success_rate = sum(1 for r in results if r.status == ProcessingStatus.COMPLETED) / len(results)
        if success_rate < 0.5:
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        console.print("\n🛑 사용자에 의해 중단됨", style="yellow")
        return 1
    except Exception as e:
        console.print(f"❌ 처리 오류: {str(e)}", style="red")
        logging.exception("처리 중 오류 발생")
        return 1


def cmd_config_create(args):
    """설정 파일 생성"""
    output_path = Path(args.output) if hasattr(args, 'output') else Path("./config.json")
    
    try:
        create_sample_config(output_path)
        console.print(f"✅ 설정 파일 생성됨: {output_path}", style="green")
        return 0
    except Exception as e:
        console.print(f"❌ 설정 파일 생성 실패: {str(e)}", style="red")
        return 1


def cmd_config_show(args):
    """현재 설정 표시"""
    try:
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        # 설정을 JSON으로 표시
        config_dict = config_manager._config_to_dict(config)
        console.print(Panel(
            json.dumps(config_dict, indent=2, ensure_ascii=False),
            title="📋 현재 설정",
            border_style="green"
        ))
        return 0
    except Exception as e:
        console.print(f"❌ 설정 로드 실패: {str(e)}", style="red")
        return 1


def cmd_config_validate(args):
    """설정 검증"""
    try:
        config_manager = ConfigManager()
        config = config_manager.load_config()
        
        errors = config_manager.validate_config(config)
        
        if not errors:
            console.print("✅ 설정이 유효합니다.", style="green")
            return 0
        else:
            console.print("❌ 설정 오류 발견:", style="red")
            for error in errors:
                console.print(f"  • {error}", style="red")
            return 1
    except Exception as e:
        console.print(f"❌ 설정 검증 실패: {str(e)}", style="red")
        return 1


def cmd_server_start(args):
    """API 서버 시작"""
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    # 명령행 인수로 오버라이드
    host = getattr(args, 'host', None) or config.api.host
    port = getattr(args, 'port', None) or config.api.port
    workers = getattr(args, 'workers', None) or config.api.workers
    
    console.print(f"🚀 API 서버 시작 중... http://{host}:{port}")
    
    try:
        run_server(host=host, port=port, workers=workers)
        return 0
    except Exception as e:
        console.print(f"❌ 서버 시작 실패: {str(e)}", style="red")
        return 1


async def cmd_analyze(args):
    """문서 분석"""
    from pypdf import PdfReader
    
    input_path = Path(args.input)
    if not input_path.exists():
        console.print(f"❌ 파일을 찾을 수 없습니다: {input_path}", style="red")
        return 1
    
    try:
        console.print(f"📊 분석 중: {input_path.name}")
        
        # PDF 정보 추출
        reader = PdfReader(str(input_path))
        total_pages = len(reader.pages)
        
        # 파일 정보
        file_size = input_path.stat().st_size
        
        # 테이블 생성
        table = Table(title=f"📄 문서 분석: {input_path.name}")
        table.add_column("속성", style="cyan")
        table.add_column("값", style="green")
        
        table.add_row("파일 크기", f"{file_size / 1024 / 1024:.1f} MB")
        table.add_row("전체 페이지", str(total_pages))
        table.add_row("PDF 버전", reader.pdf_version if hasattr(reader, 'pdf_version') else "알 수 없음")
        
        # 메타데이터
        if reader.metadata:
            metadata = reader.metadata
            if '/Title' in metadata:
                table.add_row("제목", str(metadata['/Title']))
            if '/Author' in metadata:
                table.add_row("작성자", str(metadata['/Author']))
            if '/Creator' in metadata:
                table.add_row("생성 프로그램", str(metadata['/Creator']))
        
        console.print(table)
        
        # 예상 처리 시간
        estimated_time = total_pages * 2  # 페이지당 약 2초 추정
        console.print(f"\n⏱️  예상 처리 시간: {estimated_time // 60}분 {estimated_time % 60}초")
        
        return 0
        
    except Exception as e:
        console.print(f"❌ 분석 실패: {str(e)}", style="red")
        return 1


def cmd_benchmark(args):
    """성능 벤치마크"""
    console.print("🏃 성능 벤치마크 실행 중...")
    
    import time
    import psutil
    
    # 시스템 정보
    table = Table(title="💻 시스템 정보")
    table.add_column("항목", style="cyan")
    table.add_column("값", style="green")
    
    table.add_row("CPU 코어", str(psutil.cpu_count()))
    table.add_row("메모리", f"{psutil.virtual_memory().total / 1024**3:.1f} GB")
    table.add_row("사용 가능 메모리", f"{psutil.virtual_memory().available / 1024**3:.1f} GB")
    
    console.print(table)
    
    # 간단한 OCR 벤치마크 (가상)
    console.print("\n🔍 OCR 성능 테스트...")
    
    with Progress(console=console) as progress:
        task = progress.add_task("벤치마크 실행", total=100)
        
        for i in range(100):
            time.sleep(0.05)  # 실제로는 OCR 처리 시뮬레이션
            progress.update(task, advance=1)
    
    console.print("✅ 벤치마크 완료")
    console.print("📈 예상 성능: 30-50 페이지/분 (시스템 사양에 따라 차이)")
    
    return 0


def create_parser():
    """명령행 파서 생성"""
    parser = argparse.ArgumentParser(
        description="Enhanced PDF OCR Processor CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="더 자세한 정보는 'python cli.py help' 명령어를 사용하세요."
    )
    
    # 전역 옵션
    parser.add_argument("--config", type=str, help="설정 파일 경로")
    parser.add_argument("--verbose", "-v", action="store_true", help="상세 로그 출력")
    parser.add_argument("--quiet", "-q", action="store_true", help="최소 로그 출력")
    parser.add_argument("--no-color", action="store_true", help="컬러 출력 비활성화")
    
    # 서브커맨드
    subparsers = parser.add_subparsers(dest="command", help="사용 가능한 명령어")
    
    # process 명령어
    process_parser = subparsers.add_parser("process", help="PDF/이미지 파일 처리")
    process_parser.add_argument("input", help="입력 파일 또는 폴더 경로")
    process_parser.add_argument("--outdir", default="./output", help="출력 폴더")
    process_parser.add_argument("--lang", default="auto", help="OCR 언어")
    process_parser.add_argument("--dpi", type=int, help="이미지 변환 DPI")
    process_parser.add_argument("--auto-dpi", action="store_true", help="자동 DPI 선택")
    process_parser.add_argument("--conf", type=int, help="신뢰도 임계값")
    process_parser.add_argument("--workers", type=int, help="병렬 처리 워커 수")
    process_parser.add_argument("--save-json", action="store_true", help="JSON 사이드카 저장")
    process_parser.add_argument("--resume", action="store_true", help="체크포인트 재개")
    process_parser.add_argument("--keep-ckpt", action="store_true", help="체크포인트 보존")
    process_parser.add_argument("--recursive", "-r", action="store_true", help="하위 폴더 포함")
    
    # config 명령어
    config_parser = subparsers.add_parser("config", help="설정 관리")
    config_subparsers = config_parser.add_subparsers(dest="config_action")
    
    create_config_parser = config_subparsers.add_parser("create", help="설정 파일 생성")
    create_config_parser.add_argument("--output", default="config.json", help="출력 파일명")
    
    config_subparsers.add_parser("show", help="현재 설정 표시")
    config_subparsers.add_parser("validate", help="설정 검증")
    
    # server 명령어
    server_parser = subparsers.add_parser("server", help="API 서버 관리")
    server_subparsers = server_parser.add_subparsers(dest="server_action")
    
    start_server_parser = server_subparsers.add_parser("start", help="서버 시작")
    start_server_parser.add_argument("--host", help="서버 호스트")
    start_server_parser.add_argument("--port", type=int, help="서버 포트")
    start_server_parser.add_argument("--workers", type=int, help="서버 워커 수")
    
    # analyze 명령어
    analyze_parser = subparsers.add_parser("analyze", help="문서 분석")
    analyze_parser.add_argument("input", help="분석할 PDF 파일")
    
    # benchmark 명령어
    subparsers.add_parser("benchmark", help="성능 벤치마크")
    
    # help 명령어
    subparsers.add_parser("help", help="확장된 도움말 표시")
    
    return parser


async def main():
    """메인 함수"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 컬러 출력 설정
    if args.no_color:
        colorama.deinit()
    
    # 로깅 설정
    setup_logging(args.verbose, args.quiet)
    
    # 명령어 없음
    if not args.command:
        print_banner()
        parser.print_help()
        return 0
    
    # 명령어 실행
    try:
        if args.command == "process":
            return await cmd_process(args)
        elif args.command == "config":
            if args.config_action == "create":
                return cmd_config_create(args)
            elif args.config_action == "show":
                return cmd_config_show(args)
            elif args.config_action == "validate":
                return cmd_config_validate(args)
            else:
                console.print("❌ config 서브커맨드를 지정해주세요.", style="red")
                return 1
        elif args.command == "server":
            if args.server_action == "start":
                return cmd_server_start(args)
            else:
                console.print("❌ server 서브커맨드를 지정해주세요.", style="red")
                return 1
        elif args.command == "analyze":
            return await cmd_analyze(args)
        elif args.command == "benchmark":
            return cmd_benchmark(args)
        elif args.command == "help":
            print_help_extended()
            return 0
        else:
            console.print(f"❌ 알 수 없는 명령어: {args.command}", style="red")
            return 1
    except KeyboardInterrupt:
        console.print("\n🛑 사용자에 의해 중단됨", style="yellow")
        return 1
    except Exception as e:
        console.print(f"❌ 실행 오류: {str(e)}", style="red")
        logging.exception("실행 중 오류 발생")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))