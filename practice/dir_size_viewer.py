import os

# 설정값
EXCLUDE_EXTS = [".log", ".tmp", ".ds_store"]
TOP_N = 10  # 가장 큰 항목 N개 출력


def format_size(bytes_size):
    kb = bytes_size / 1024
    if kb < 1024:
        return f"{kb:.1f} KB"
    else:
        return f"{kb / 1024:.1f} MB"


def should_exclude(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in EXCLUDE_EXTS


def get_all_sizes(base_path):
    size_list = []

    for root, dirs, files in os.walk(base_path):
        # 파일 사이즈 수집
        for f in files:
            if should_exclude(f):
                continue
            full_path = os.path.join(root, f)
            try:
                size = os.path.getsize(full_path)
                rel_path = os.path.relpath(full_path, base_path)
                size_list.append((rel_path, size))
            except FileNotFoundError:
                continue

        # 폴더 사이즈 수집
        for d in dirs:
            folder_path = os.path.join(root, d)
            try:
                folder_size = get_folder_size(folder_path)
                rel_path = os.path.relpath(folder_path, base_path)
                size_list.append((rel_path + "/", folder_size))
            except:
                continue

    return size_list


def get_folder_size(path):
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            if should_exclude(f):
                continue
            try:
                total += os.path.getsize(os.path.join(root, f))
            except FileNotFoundError:
                continue
    return total


def main():
    base_path = "./"
    print(f"=== 📦 디렉토리 용량 TOP {TOP_N} 보기 ===")
    print(f"제외 확장자: {', '.join(EXCLUDE_EXTS)}\n")

    sizes = get_all_sizes(base_path)
    sizes.sort(key=lambda x: x[1], reverse=True)

    top_items = sizes[:TOP_N]

    for path, size in top_items:
        print(f"{path:<60} {format_size(size)}")


if __name__ == "__main__":
    main()
