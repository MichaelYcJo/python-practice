import os
import uuid
import shutil
import re

# 여기서 직접 설정
ID_STR = "89"  # 사용할 ID
S3_PATH = "dormitory/centers/"
OUTPUT_DIR = "./output/"  # 저장할 경로


def generate_new_filename(id_str, index):
    """id와 uuid를 조합해 새로운 파일명 생성"""
    raw_uuid = str(uuid.uuid4()).replace("-", "_")
    return f"{id_str}_{index:02d}_{raw_uuid}"


def get_file_number(filename):
    """파일 이름에서 순서 번호를 추출합니다."""
    match = re.search(r"img_(\d+)", filename)
    if match:
        return int(match.group(1))
    return 0  # 번호가 없는 경우 기본값 0


def convert_images(id_str, output_dir, s3_base_path):
    """input 폴더 안의 파일명을 변환해서 output 폴더에 저장"""
    input_dir = "./input"
    result = []

    if not os.path.exists(input_dir):
        print(f"❗ {input_dir} 폴더가 존재하지 않습니다.")
        return result

    files = os.listdir(input_dir)

    if not files:
        print(f"📂 {input_dir} 폴더에 파일이 없습니다.")
        return result

    # 파일 이름에 있는 숫자 순서대로 정렬
    sorted_files = sorted(files, key=get_file_number)

    # output 디렉토리 없으면 생성
    os.makedirs(output_dir, exist_ok=True)

    for index, filename in enumerate(sorted_files, 1):
        original_path = os.path.join(input_dir, filename)
        if os.path.isfile(original_path):
            _, ext = os.path.splitext(filename)
            # 인덱스를 포함하여 파일 이름 생성
            new_filename = generate_new_filename(id_str, index) + ext
            new_path = os.path.join(output_dir, new_filename)

            shutil.copy2(original_path, new_path)
            file_s3_path = s3_base_path + new_filename

            result.append({"filename": new_filename, "s3_path": file_s3_path})

    return result


def main():
    print("=== 🖼️ 이미지 파일 변환기 ===")

    results = convert_images(ID_STR, OUTPUT_DIR, S3_PATH)

    if results:
        print("\n=== 복사용 S3 경로 ===")
        for item in results:
            print(item["s3_path"])
    else:
        print("⚠️ 변환할 파일이 없습니다.")


if __name__ == "__main__":
    main()
