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


def find_matching_files(old_name):
    """재귀적으로 old_name과 일치하는 파일 경로 리스트 반환"""
    matches = []
    for path in TARGET_DIR.rglob("*"):
        if path.is_file() and path.stem == old_name:
            matches.append(path)
    return matches


def rename_files(mapping):
    renamed = 0
    skipped = 0
    missing = 0

    print("\n📂 재귀적으로 파일 변경 작업 시작")

    for old_name, new_name in mapping.items():
        matches = find_matching_files(old_name)

        if not matches:
            print(f"❗ 없음: {old_name} → 존재하지 않음")
            missing += 1
            continue

        for matched_file in matches:
            new_filename = new_name + matched_file.suffix
            new_path = matched_file.with_name(new_filename)

            if new_path.exists():
                print(f"⚠️ 중복: {new_path} → 건너뜀")
                skipped += 1
                continue

            os.rename(matched_file, new_path)
            print(
                f"✅ {matched_file.relative_to(TARGET_DIR)} → {new_path.relative_to(TARGET_DIR)}"
            )
            renamed += 1

    print(f"\n📊 완료 요약:")
    print(f"   ✅ 변경된 파일: {renamed}개")
    print(f"   ⚠️ 중복으로 건너뜀: {skipped}개")
    print(f"   ❌ 존재하지 않는 파일: {missing}개")


def main():
    print("📁 파일명 자동 정리기 (하위 폴더 포함) 시작")
    try:
        mapping = load_rename_map(RENAME_MAP_FILE)
        rename_files(mapping)
    except Exception as e:
        print(f"❗ 오류 발생: {e}")


if __name__ == "__main__":
    main()
