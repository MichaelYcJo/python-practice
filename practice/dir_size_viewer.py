import os

# 제외할 확장자 목록 (소문자로 입력)
EXCLUDE_EXTS = [".log", ".tmp", ".ds_store"]


def format_size(bytes_size):
    kb = bytes_size / 1024
    if kb < 1024:
        return f"{kb:.1f} KB"
    else:
        return f"{kb / 1024:.1f} MB"


def should_exclude(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in EXCLUDE_EXTS


def get_folder_size(path):
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            if should_exclude(f):
                continue
            try:
                fp = os.path.join(root, f)
                total += os.path.getsize(fp)
            except FileNotFoundError:
                continue
    return total


def print_tree(path, prefix=""):
    if not os.path.exists(path):
        print(f"❗ 경로 '{path}'가 존재하지 않습니다.")
        return

    basename = os.path.basename(path) or path
    if os.path.isdir(path):
        folder_size = get_folder_size(path)
        print(f"{prefix}📁 {basename} ({format_size(folder_size)})")
        try:
            entries = sorted(os.listdir(path))
        except PermissionError:
            print(f"{prefix}  └─ 접근 권한 없음")
            return

        for i, entry in enumerate(entries):
            full_path = os.path.join(path, entry)
            connector = "└── " if i == len(entries) - 1 else "├── "
            new_prefix = prefix + ("    " if i == len(entries) - 1 else "│   ")

            if os.path.isdir(full_path):
                print_tree(full_path, prefix + connector)
            elif not should_exclude(entry):
                try:
                    file_size = os.path.getsize(full_path)
                    print(f"{prefix}{connector}📄 {entry} ({format_size(file_size)})")
                except FileNotFoundError:
                    continue
    else:
        if not should_exclude(path):
            file_size = os.path.getsize(path)
            print(f"{prefix}📄 {basename} ({format_size(file_size)})")


def main():
    base_path = "./"  # 분석 시작 경로
    print(f"=== 📁 디렉토리 용량 시각화 (확장자 필터 적용) ===")
    print(f"제외 확장자: {', '.join(EXCLUDE_EXTS)}\n")
    print_tree(base_path)


if __name__ == "__main__":
    main()
