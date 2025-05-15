import os
import pandas as pd
from pathlib import Path

# 설정
TARGET_DIR = Path("files_to_rename")  # 파일들이 들어있는 폴더
RENAME_MAP_FILE = "rename_map.xlsx"  # 매핑 정보가 담긴 엑셀


def load_rename_map(filepath):
    """엑셀 파일에서 old_name → new_name 매핑 딕셔너리로 불러오기"""
    df = pd.read_excel(filepath, engine="openpyxl")
    if "old_name" not in df.columns or "new_name" not in df.columns:
        raise ValueError("엑셀 파일에 'old_name'과 'new_name' 컬럼이 필요합니다.")
    return dict(zip(df["old_name"], df["new_name"]))


def rename_files(mapping, target_dir):
    """파일명 변경 수행"""
    renamed = 0
    skipped = 0

    for file in os.listdir(target_dir):
        file_path = target_dir / file
        if not file_path.is_file():
            continue

        name, ext = os.path.splitext(file)
        if name in mapping:
            new_name = mapping[name] + ext
            new_path = target_dir / new_name

            if new_path.exists():
                print(f"⚠️ 이미 존재: {new_path.name} → 건너뜁니다.")
                skipped += 1
                continue

            os.rename(file_path, new_path)
            print(f"✅ {file} → {new_name}")
            renamed += 1
        else:
            print(f"❌ 매핑 없음: {file} → 건너뜀")
            skipped += 1

    print(f"\n📊 완료: {renamed}개 변경, {skipped}개 건너뜀")


def main():
    print("📁 파일명 자동 정리기 시작")
    try:
        mapping = load_rename_map(RENAME_MAP_FILE)
        rename_files(mapping, TARGET_DIR)
    except Exception as e:
        print(f"❗ 오류 발생: {e}")


if __name__ == "__main__":
    main()
