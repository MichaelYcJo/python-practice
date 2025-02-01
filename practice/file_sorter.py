import os
import shutil


def organize_files(directory):
    if not os.path.exists(directory):
        print("지정한 폴더가 존재하지 않습니다.")
        return

    # 폴더 내 파일 목록 가져오기
    files = [
        f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))
    ]

    for file in files:
        ext = file.split(".")[-1].lower()  # 확장자 추출 (소문자로 변환)
        if len(file.split(".")) == 1:  # 확장자가 없는 경우 무시
            continue

        folder_name = {
            "jpg": "Images",
            "png": "Images",
            "gif": "Images",
            "mp4": "Videos",
            "mkv": "Videos",
            "avi": "Videos",
            "pdf": "Documents",
            "docx": "Documents",
            "txt": "TextFiles",
            "csv": "Data",
            "json": "Data",
        }.get(
            ext, "Others"
        )  # 지정되지 않은 확장자는 "Others" 폴더로 이동

        target_folder = os.path.join(directory, folder_name)
        os.makedirs(target_folder, exist_ok=True)  # 폴더가 없으면 생성

        shutil.move(
            os.path.join(directory, file), os.path.join(target_folder, file)
        )  # 파일 이동

    print("파일 정리가 완료되었습니다!")


# 사용 예시
target_directory = "/Users/yc/Downloads/rag-gist-3-ingestion-implementation"  # 원하는 정리할 폴더 경로 설정
organize_files(target_directory)
