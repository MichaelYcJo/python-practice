import os


def format_size(bytes_size):
    """바이트 단위를 KB/MB 문자열로 변환"""
    kb = bytes_size / 1024
    if kb < 1024:
        return f"{kb:.1f} KB"
    else:
        return f"{kb / 1024:.1f} MB"


def get_folder_size(path):
    """디렉토리 전체 크기 계산 (바이트 단위)"""
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            try:
                fp = os.path.join(root, f)
                total += os.path.getsize(fp)
            except FileNotFoundError:
                continue
    return total


def print_tree(path, prefix=""):
    """재귀적으로 디렉토리 구조와 용량 출력"""
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
            else:
                try:
                    file_size = os.path.getsize(full_path)
                    print(f"{prefix}{connector}📄 {entry} ({format_size(file_size)})")
                except FileNotFoundError:
                    continue
    else:
        file_size = os.path.getsize(path)
        print(f"{prefix}📄 {basename} ({format_size(file_size)})")


def main():
    base_path = "./"  # 시작 경로 변경 가능
    print(f"=== 📁 디렉토리 용량 시각화: '{base_path}' ===\n")
    print_tree(base_path)


if __name__ == "__main__":
    main()
