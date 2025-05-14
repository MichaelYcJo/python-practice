import os
import pandas as pd
from pathlib import Path

# 설정
TARGET_DIR = Path("files_to_rename")
RENAME_MAP_FILE = "rename_map.xlsx"

def load_rename_map(filepath):
    df = pd.read_excel(filepath, engine="openpyxl")
    if "old_name" not in df.columns or "new_name" not in df.columns:
        raise ValueError("엑셀 파일에 'old_name'과 'new_name' 컬럼이 필요합니다.")
    return dict(zip(df["old_name"], df["new_name"]))

def find_matching_file(old_name):
    """디렉토리 내에서 이름이 old_name인 파일을 확장자 포함하여 찾기"""
    for file in os.listdir(TARGET_DIR):
        file_path = TARGET_DIR / file
        if not file_path.is_file():
            continue
        name, _ = os.path.splitext(file)
        if name == old_name:
            return file_path
    return None

def rename_files(mapping):
    renamed = 0
    skipped = 0
    missing = 0

    print("\n📂 파일 변경 작업 시작")

    for old_name, new_name in mapping.items():
        matched_file = find_matching_file(old_name)
        if not matched_file:
            print(f"❗ 없음: {old_name} → 존재하지 않는 파일입니다.")
            missing += 1
            continue

        _, ext = os.path.splitext(matched_file.name)
        new_path = TARGET_DIR / (new_name + ext)

        if new_path.exists():
            print(f"⚠️ 이미 존재: {new_path.name} → 건너뜀")
            skipped += 1
            continue

        os.rename(matched_file, new_path)
        print(f"✅ {matched_file.name} → {new_path.name}")
        renamed += 1

    print(f"\n📊 완료 요약:")
    print(f"   ✅ 변경된 파일: {renamed}개")
    print(f"   ⚠️ 중복으로 건너뜀: {skipped}개")
    print(f"   ❌ 존재하지 않는 파일: {missing}개")

def main():
    print("📁 파일명 자동 정리기 시작")
    try:
        mapping = load_rename_map(RENAME_MAP_FILE)
        rename_files(mapping)
    except Exception as e:
        print(f"❗ 오류 발생: {e}")

if __name__ == '__main__':
    main()