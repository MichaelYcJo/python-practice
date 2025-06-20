import os
import zipfile
import shutil
from pathlib import Path
from datetime import datetime
import getpass
try:
    import pyminizip
    PYMINIZIP_AVAILABLE = True
except ImportError:
    PYMINIZIP_AVAILABLE = False
    print("⚠️  pyminizip가 설치되지 않았습니다. 암호 보호 기능이 제한됩니다.")


class DirectoryZipper:
    """디렉토리를 압축 파일로 만드는 클래스"""
    
    def __init__(self):
        """압축 파일은 현재 디렉토리(make_zip)에 생성됩니다."""
        self.output_dir = Path.cwd()  # 현재 작업 디렉토리 (make_zip)
        print(f"압축 파일 생성 위치: {self.output_dir}")
    
    def create_zip(self, source_dir, output_path=None, exclude_patterns=None, password=None):
        """
        디렉토리를 ZIP 파일로 압축합니다.
        
        Args:
            source_dir (str): 압축할 디렉토리 경로 (상대경로 또는 절대경로)
            output_path (str, optional): 출력 ZIP 파일 경로. None이면 자동 생성
            exclude_patterns (list, optional): 제외할 파일/폴더 패턴 리스트
            password (str, optional): 압축 파일 암호. None이면 암호 없음
        
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
        
        # 암호 보호가 요청되고 pyminizip이 사용 가능한 경우
        if password and PYMINIZIP_AVAILABLE:
            return self._create_password_protected_zip(source_path, output_path, exclude_patterns, password)
        
        # 일반 압축 또는 암호 보호 불가능한 경우
        if password and not PYMINIZIP_AVAILABLE:
            print("⚠️  pyminizip가 없어서 암호 보호 없이 압축합니다.")
            password = None
        
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
                
                protection_msg = "🔒 암호 보호됨" if password else "🔓 암호 없음"
                print(f"압축 완료! 파일 크기: {self._format_size(output_path.stat().st_size)} ({protection_msg})")
                return str(output_path)
        
        except Exception as e:
            print(f"압축 중 오류 발생: {e}")
            # 실패한 경우 생성된 파일 삭제
            if output_path.exists():
                output_path.unlink()
            raise
    
    def _create_password_protected_zip(self, source_path, output_path, exclude_patterns, password):
        """pyminizip을 사용한 암호 보호 압축"""
        try:
            # 압축할 파일 목록 수집
            files_to_compress = []
            arc_names = []
            
            print(f"🔒 암호 보호 압축 시작: {source_path} -> {output_path}")
            
            for file_path in source_path.rglob('*'):
                if file_path.is_file():
                    # 제외 패턴 확인
                    if self._should_exclude(file_path, source_path, exclude_patterns):
                        continue
                    
                    files_to_compress.append(str(file_path))
                    # ZIP 파일 내에서의 상대 경로 계산
                    arc_name = str(file_path.relative_to(source_path.parent))
                    arc_names.append(arc_name)
            
            if not files_to_compress:
                raise ValueError("압축할 파일이 없습니다.")
            
            print(f"총 {len(files_to_compress)}개 파일 압축 중...")
            
            # pyminizip을 사용한 암호 보호 압축
            pyminizip.compress_multiple(
                files_to_compress,    # 압축할 파일 목록
                arc_names,           # ZIP 내에서의 파일명 목록
                str(output_path),    # 출력 ZIP 파일 경로
                password,            # 암호
                5                    # 압축 레벨 (0-9)
            )
            
            print(f"🔒 암호 보호 압축 완료! 파일 크기: {self._format_size(output_path.stat().st_size)}")
            return str(output_path)
            
        except Exception as e:
            print(f"❌ 암호 보호 압축 실패: {e}")
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
    
    def extract_zip(self, zip_path, extract_to=None, password=None):
        """
        ZIP 파일을 압축 해제합니다.
        
        Args:
            zip_path (str): 압축 해제할 ZIP 파일 경로
            extract_to (str, optional): 압축 해제할 디렉토리. None이면 ZIP 파일명으로 생성
            password (str, optional): 압축 파일 암호. None이면 암호 없음
        
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
                
                # 암호가 설정된 경우 적용
                if password:
                    print(f"🔒 암호 보호된 파일 해제 중...")
                    zipf.extractall(extract_path, pwd=password.encode('utf-8'))
                else:
                    zipf.extractall(extract_path)
                
                print(f"압축 해제 완료: {extract_path}")
                return str(extract_path)
        
        except zipfile.BadZipFile:
            print(f"❌ 잘못된 ZIP 파일입니다: {zip_path}")
            raise
        except RuntimeError as e:
            if "Bad password" in str(e):
                print(f"❌ 잘못된 암호입니다!")
                raise ValueError("잘못된 암호입니다.")
            else:
                print(f"❌ 압축 해제 중 오류 발생: {e}")
                raise
        except Exception as e:
            print(f"❌ 압축 해제 중 오류 발생: {e}")
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
                
                # 암호 입력
                password_choice = input("암호를 설정하시겠습니까? (y/N): ").strip().lower()
                password = None
                if password_choice in ['y', 'yes']:
                    password = getpass.getpass("압축 파일 암호를 입력하세요: ")
                    if password:
                        password_confirm = getpass.getpass("암호를 다시 입력하세요: ")
                        if password != password_confirm:
                            print("❌ 암호가 일치하지 않습니다.")
                            continue
                    else:
                        print("암호가 입력되지 않아 암호 없이 압축합니다.")
                
                result = zipper.create_zip(source_dir, output_path, exclude_patterns, password)
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
                
                # 암호 보호 여부 확인 후 암호 입력
                password = None
                password_choice = input("암호 보호된 파일입니까? (y/N): ").strip().lower()
                if password_choice in ['y', 'yes']:
                    password = getpass.getpass("압축 파일 암호를 입력하세요: ")
                
                result = zipper.extract_zip(zip_path, extract_to, password)
                print(f"\n✅ 압축 해제 성공: {result}")
                
            except ValueError as e:
                # 잘못된 암호인 경우 재시도 기회 제공
                if "잘못된 암호" in str(e):
                    retry_choice = input("다시 시도하시겠습니까? (y/N): ").strip().lower()
                    if retry_choice in ['y', 'yes']:
                        continue
                print(f"❌ 압축 해제 실패: {e}")
            except Exception as e:
                print(f"❌ 압축 해제 실패: {e}")
        
        elif choice == '3':
            print("프로그램을 종료합니다.")
            break
        
        else:
            print("잘못된 선택입니다. 1-3 중에서 선택해주세요.")


if __name__ == "__main__":
    main()
