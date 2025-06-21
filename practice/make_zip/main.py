import os
import zipfile
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
import getpass
import tempfile
try:
    import py7zr
    PY7ZR_AVAILABLE = True
except ImportError:
    PY7ZR_AVAILABLE = False
    print("⚠️  py7zr가 설치되지 않았습니다. 암호 보호 기능이 제한됩니다.")


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
        
        # 암호 보호가 요청된 경우
        if password:
            # 1순위: py7zr 사용 (7z 형식)
            if PY7ZR_AVAILABLE:
                return self._create_7z_password_protected(source_path, output_path, exclude_patterns, password)
            # 2순위: 시스템 zip 명령어 사용
            elif self._check_system_zip():
                return self._create_system_zip_password_protected(source_path, output_path, exclude_patterns, password)
            # 3순위: 암호 보호 불가능
            else:
                print("⚠️  암호 보호 기능을 사용할 수 없어서 일반 압축으로 진행합니다.")
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
    
    def _check_system_zip(self):
        """시스템에 zip 명령어가 있는지 확인"""
        try:
            subprocess.run(['zip', '--help'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _create_7z_password_protected(self, source_path, output_path, exclude_patterns, password):
        """py7zr을 사용한 7z 형식 암호 보호 압축"""
        try:
            # 출력 파일 확장자를 .7z로 변경
            if output_path.suffix.lower() == '.zip':
                output_path = output_path.with_suffix('.7z')
            
            print(f"🔒 7z 암호 보호 압축 시작: {source_path} -> {output_path}")
            
            with py7zr.SevenZipFile(output_path, 'w', password=password) as archive:
                total_files = 0
                processed_files = 0
                
                # 파일 개수 세기
                for file_path in source_path.rglob('*'):
                    if file_path.is_file() and not self._should_exclude(file_path, source_path, exclude_patterns):
                        total_files += 1
                
                print(f"총 {total_files}개 파일 압축 중...")
                
                for file_path in source_path.rglob('*'):
                    if file_path.is_file():
                        # 제외 패턴 확인
                        if self._should_exclude(file_path, source_path, exclude_patterns):
                            continue
                        
                        # 7z 파일 내에서의 상대 경로 계산
                        arc_name = file_path.relative_to(source_path.parent)
                        
                        try:
                            archive.write(file_path, arc_name)
                            processed_files += 1
                            
                            # 진행률 표시
                            if processed_files % 10 == 0 or processed_files == total_files:
                                progress = (processed_files / total_files) * 100
                                print(f"진행률: {progress:.1f}% ({processed_files}/{total_files})")
                        
                        except Exception as e:
                            print(f"파일 압축 실패: {file_path} - {e}")
                            continue
            
            print(f"🔒 7z 암호 보호 압축 완료! 파일 크기: {self._format_size(output_path.stat().st_size)}")
            return str(output_path)
            
        except Exception as e:
            print(f"❌ 7z 암호 보호 압축 실패: {e}")
            # 실패한 경우 생성된 파일 삭제
            if output_path.exists():
                output_path.unlink()
            raise
    
    def _create_system_zip_password_protected(self, source_path, output_path, exclude_patterns, password):
        """시스템 zip 명령어를 사용한 암호 보호 압축"""
        try:
            print(f"🔒 시스템 zip을 사용한 암호 보호 압축 시작: {source_path} -> {output_path}")
            
            # 임시 디렉토리에서 작업
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_source = Path(temp_dir) / "temp_source"
                temp_source.mkdir()
                
                # 제외 패턴을 적용하여 파일 복사
                copied_files = 0
                for file_path in source_path.rglob('*'):
                    if file_path.is_file():
                        if self._should_exclude(file_path, source_path, exclude_patterns):
                            continue
                        
                        # 상대 경로 계산
                        rel_path = file_path.relative_to(source_path)
                        dest_path = temp_source / rel_path
                        
                        # 디렉토리 생성
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # 파일 복사
                        shutil.copy2(file_path, dest_path)
                        copied_files += 1
                
                if copied_files == 0:
                    raise ValueError("압축할 파일이 없습니다.")
                
                print(f"총 {copied_files}개 파일 압축 중...")
                
                # zip 명령어로 암호 보호 압축
                cmd = [
                    'zip', '-r', '-P', password,  # -P는 암호 옵션
                    str(output_path.absolute()),
                    '.'
                ]
                
                result = subprocess.run(
                    cmd,
                    cwd=temp_source,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    raise RuntimeError(f"zip 명령어 실행 실패: {result.stderr}")
            
            print(f"🔒 시스템 zip 암호 보호 압축 완료! 파일 크기: {self._format_size(output_path.stat().st_size)}")
            return str(output_path)
            
        except Exception as e:
            print(f"❌ 시스템 zip 암호 보호 압축 실패: {e}")
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
        
        # 파일 형식에 따라 다른 해제 방법 사용
        if zip_path.suffix.lower() == '.7z':
            return self._extract_7z(zip_path, extract_path, password)
        else:
            return self._extract_zip(zip_path, extract_path, password)
    
    def _extract_zip(self, zip_path, extract_path, password):
        """ZIP 파일 해제"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                print(f"📦 ZIP 파일 해제 시작: {zip_path} -> {extract_path}")
                
                # 암호가 설정된 경우 적용
                if password:
                    print(f"🔒 암호 보호된 파일 해제 중...")
                    zipf.extractall(extract_path, pwd=password.encode('utf-8'))
                else:
                    zipf.extractall(extract_path)
                
                print(f"✅ ZIP 파일 해제 완료: {extract_path}")
                return str(extract_path)
        
        except zipfile.BadZipFile:
            print(f"❌ 잘못된 ZIP 파일입니다: {zip_path}")
            raise
        except RuntimeError as e:
            if "Bad password" in str(e):
                print(f"❌ 잘못된 암호입니다!")
                raise ValueError("잘못된 암호입니다.")
            else:
                print(f"❌ ZIP 파일 해제 중 오류 발생: {e}")
                raise
        except Exception as e:
            print(f"❌ ZIP 파일 해제 중 오류 발생: {e}")
            raise
    
    def _extract_7z(self, zip_path, extract_path, password):
        """7z 파일 해제"""
        try:
            if not PY7ZR_AVAILABLE:
                raise ImportError("py7zr이 설치되지 않았습니다.")
            
            print(f"📦 7z 파일 해제 시작: {zip_path} -> {extract_path}")
            
            with py7zr.SevenZipFile(zip_path, mode='r', password=password) as archive:
                archive.extractall(path=extract_path)
            
            print(f"✅ 7z 파일 해제 완료: {extract_path}")
            return str(extract_path)
        
        except py7zr.exceptions.Bad7zFile:
            print(f"❌ 잘못된 7z 파일입니다: {zip_path}")
            raise
        except py7zr.exceptions.PasswordRequired:
            print(f"❌ 이 파일은 암호가 필요합니다!")
            raise ValueError("암호가 필요합니다.")
        except py7zr.exceptions.BadPassword:
            print(f"❌ 잘못된 암호입니다!")
            raise ValueError("잘못된 암호입니다.")
        except Exception as e:
            print(f"❌ 7z 파일 해제 중 오류 발생: {e}")
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
