import os
import zipfile
import shutil
from pathlib import Path
from datetime import datetime


class DirectoryZipper:
    """디렉토리를 압축 파일로 만드는 클래스"""
    
    def __init__(self):
        """압축 파일은 현재 디렉토리(make_zip)에 생성됩니다."""
        self.output_dir = Path.cwd()  # 현재 작업 디렉토리 (make_zip)
        print(f"압축 파일 생성 위치: {self.output_dir}")
    
    def create_zip(self, source_dir, output_path=None, exclude_patterns=None):
        """
        디렉토리를 ZIP 파일로 압축합니다.
        
        Args:
            source_dir (str): 압축할 디렉토리 경로 (상대경로 또는 절대경로)
            output_path (str, optional): 출력 ZIP 파일 경로. None이면 자동 생성
            exclude_patterns (list, optional): 제외할 파일/폴더 패턴 리스트
        
        Returns:
            str: 생성된 ZIP 파일 경로
        """
        source_path = Path(source_dir)
        # 상대 경로인 경우 절대 경로로 변환
        if not source_path.is_absolute():
            source_path = source_path.resolve()
        
        # 디렉토리가 존재하는지 확인
        if not source_path.exists():
            raise FileNotFoundError(f"디렉토리를 찾을 수 없습니다: {source_dir}")
        
        if not source_path.is_dir():
            raise ValueError(f"지정된 경로가 디렉토리가 아닙니다: {source_dir}")
        
        # 출력 경로가 지정되지 않으면 자동 생성 (make_zip 디렉토리에)
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"{source_path.name}_{timestamp}.zip"
        else:
            output_path = Path(output_path)
            # 상대 경로인 경우 make_zip 디렉토리 기준으로 설정
            if not output_path.is_absolute():
                output_path = self.output_dir / output_path
        
        # 제외 패턴 기본값 설정
        if exclude_patterns is None:
            exclude_patterns = [
                '.git', '.gitignore', '__pycache__', '.DS_Store',
                '*.pyc', '*.pyo', '.venv', 'venv', 'node_modules'
            ]
        
        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                total_files = sum(1 for _ in source_path.rglob('*') if _.is_file())
                processed_files = 0
                
                print(f"압축 시작: {source_path} -> {output_path}")
                print(f"총 {total_files}개 파일 처리 예정...")
                
                for file_path in source_path.rglob('*'):
                    if file_path.is_file():
                        # 제외 패턴 확인
                        if self._should_exclude(file_path, source_path, exclude_patterns):
                            continue
                        
                        # ZIP 파일 내에서의 상대 경로 계산
                        arc_name = file_path.relative_to(source_path.parent)
                        
                        try:
                            zipf.write(file_path, arc_name)
                            processed_files += 1
                            
                            # 진행률 표시
                            if processed_files % 10 == 0 or processed_files == total_files:
                                progress = (processed_files / total_files) * 100
                                print(f"진행률: {progress:.1f}% ({processed_files}/{total_files})")
                        
                        except Exception as e:
                            print(f"파일 압축 실패: {file_path} - {e}")
                            continue
                
                print(f"압축 완료! 파일 크기: {self._format_size(output_path.stat().st_size)}")
                return str(output_path)
        
        except Exception as e:
            print(f"압축 중 오류 발생: {e}")
            # 실패한 경우 생성된 파일 삭제
            if output_path.exists():
                output_path.unlink()
            raise
    
    def _should_exclude(self, file_path, base_path, exclude_patterns):
        """파일이 제외 패턴에 해당하는지 확인"""
        relative_path = file_path.relative_to(base_path)
        
        for pattern in exclude_patterns:
            # 디렉토리명 확인
            if pattern in str(relative_path):
                return True
            
            # 파일명 패턴 확인
            if pattern.startswith('*.'):
                extension = pattern[1:]  # *.pyc -> .pyc
                if str(file_path).endswith(extension):
                    return True
            
            # 정확한 이름 매치
            if file_path.name == pattern:
                return True
        
        return False
    
    def _format_size(self, size_bytes):
        """바이트를 읽기 쉬운 형태로 변환"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f}{size_names[i]}"
    
    def extract_zip(self, zip_path, extract_to=None):
        """
        ZIP 파일을 압축 해제합니다.
        
        Args:
            zip_path (str): 압축 해제할 ZIP 파일 경로
            extract_to (str, optional): 압축 해제할 디렉토리. None이면 ZIP 파일명으로 생성
        
        Returns:
            str: 압축 해제된 디렉토리 경로
        """
        zip_path = Path(zip_path)
        
        if not zip_path.exists():
            raise FileNotFoundError(f"ZIP 파일을 찾을 수 없습니다: {zip_path}")
        
        if extract_to is None:
            extract_to = zip_path.stem  # 확장자 제외한 파일명
        
        extract_path = Path(extract_to)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                print(f"압축 해제 시작: {zip_path} -> {extract_path}")
                zipf.extractall(extract_path)
                print(f"압축 해제 완료: {extract_path}")
                
                return str(extract_path)
        
        except Exception as e:
            print(f"압축 해제 중 오류 발생: {e}")
            raise


def main():
    """메인 함수 - 사용 예제"""
    zipper = DirectoryZipper()
    
    while True:
        print("\n=== 디렉토리 압축 도구 ===")
        print("1. 디렉토리 압축")
        print("2. ZIP 파일 압축 해제")
        print("3. 종료")
        
        choice = input("선택하세요 (1-3): ").strip()
        
        if choice == '1':
            try:
                source_dir = input("압축할 디렉토리 경로를 입력하세요: ").strip()
                if not source_dir:
                    print("디렉토리 경로를 입력해주세요.")
                    continue
                
                output_path = input("출력 ZIP 파일 경로 (엔터키: 자동 생성): ").strip()
                if not output_path:
                    output_path = None
                
                # 제외할 패턴 입력
                exclude_input = input("제외할 패턴 (쉼표로 구분, 엔터키: 기본값): ").strip()
                exclude_patterns = None
                if exclude_input:
                    exclude_patterns = [p.strip() for p in exclude_input.split(',')]
                
                result = zipper.create_zip(source_dir, output_path, exclude_patterns)
                print(f"\n✅ 압축 성공: {result}")
                
            except Exception as e:
                print(f"❌ 압축 실패: {e}")
        
        elif choice == '2':
            try:
                zip_path = input("압축 해제할 ZIP 파일 경로를 입력하세요: ").strip()
                if not zip_path:
                    print("ZIP 파일 경로를 입력해주세요.")
                    continue
                
                extract_to = input("압축 해제할 디렉토리 (엔터키: 자동 생성): ").strip()
                if not extract_to:
                    extract_to = None
                
                result = zipper.extract_zip(zip_path, extract_to)
                print(f"\n✅ 압축 해제 성공: {result}")
                
            except Exception as e:
                print(f"❌ 압축 해제 실패: {e}")
        
        elif choice == '3':
            print("프로그램을 종료합니다.")
            break
        
        else:
            print("잘못된 선택입니다. 1-3 중에서 선택해주세요.")


if __name__ == "__main__":
    main()
