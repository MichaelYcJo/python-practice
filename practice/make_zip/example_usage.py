#!/usr/bin/env python3
"""
디렉토리 압축 도구 사용 예제
"""

from main import DirectoryZipper


def example_basic_usage():
    """기본 사용법 예제"""
    print("=== 기본 사용법 예제 ===")
    
    zipper = DirectoryZipper()
    
    # 상위 디렉토리의 text_cleaner를 압축
    try:
        result = zipper.create_zip("../text_cleaner", "text_cleaner_backup.zip")
        print(f"✅ 압축 완료: {result}")
    except Exception as e:
        print(f"❌ 압축 실패: {e}")


def example_with_exclusions():
    """제외 패턴 사용 예제"""
    print("\n=== 제외 패턴 사용 예제 ===")
    
    zipper = DirectoryZipper()
    
    # 특정 파일들을 제외하고 압축
    exclude_patterns = [
        '*.log',        # 로그 파일 제외
        '*.tmp',        # 임시 파일 제외
        'cache',        # cache 디렉토리 제외
        '__pycache__',  # Python 캐시 제외
        '.git'          # Git 디렉토리 제외
    ]
    
    try:
        result = zipper.create_zip(
            "../img_file_changer", 
            "img_file_changer_clean.zip",
            exclude_patterns
        )
        print(f"✅ 압축 완료: {result}")
    except Exception as e:
        print(f"❌ 압축 실패: {e}")


def example_programmatic_usage():
    """프로그래밍 방식 사용 예제"""
    print("\n=== 프로그래밍 방식 사용 예제 ===")
    
    zipper = DirectoryZipper()
    
    # 여러 디렉토리를 순차적으로 압축
    directories_to_backup = [
        "../vocab_quiz",
        "../youtube_download",
        "../file_renaming"
    ]
    
    for directory in directories_to_backup:
        try:
            # 디렉토리 이름에서 상위 경로 제거
            dir_name = directory.split('/')[-1]
            output_name = f"{dir_name}_backup.zip"
            
            print(f"\n📁 {directory} 압축 중...")
            result = zipper.create_zip(directory, output_name)
            print(f"✅ {result} 생성 완료")
            
        except Exception as e:
            print(f"❌ {directory} 압축 실패: {e}")


def example_extract_zip():
    """ZIP 파일 압축 해제 예제"""
    print("\n=== ZIP 파일 압축 해제 예제 ===")
    
    zipper = DirectoryZipper()
    
    # 생성된 ZIP 파일 중 하나를 압축 해제
    zip_files = ["text_cleaner_backup.zip", "img_file_changer_clean.zip"]
    
    for zip_file in zip_files:
        try:
            print(f"\n📦 {zip_file} 압축 해제 중...")
            result = zipper.extract_zip(zip_file, f"extracted_{zip_file[:-4]}")
            print(f"✅ {result}에 압축 해제 완료")
        except FileNotFoundError:
            print(f"⚠️  {zip_file} 파일이 없습니다.")
        except Exception as e:
            print(f"❌ {zip_file} 압축 해제 실패: {e}")


if __name__ == "__main__":
    print("디렉토리 압축 도구 예제를 실행합니다...")
    
    example_basic_usage()
    example_with_exclusions()
    example_programmatic_usage()
    example_extract_zip()
    
    print("\n🎉 모든 예제가 완료되었습니다!") 