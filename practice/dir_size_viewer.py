import os
import json

# 설정값
EXCLUDE_EXTS = [".log", ".tmp", ".ds_store"]
INCLUDE_EXTS = [".jpg", ".png", ".py"]
TOP_N = 10
OUTPUT_FILE = "top_files.json"


def format_size(bytes_size):
    kb = bytes_size / 1024
    if kb < 1024:
        return f"{kb:.1f} KB"
    else:
        return f"{kb / 1024:.1f} MB"


def should_include(filename):
    ext = os.path.splitext(filename)[1].lower()
    return (ext in INCLUDE_EXTS) if INCLUDE_EXTS else True


def should_exclude(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in EXCLUDE_EXTS


def get_all_sizes(base_path):
    size_list = []

    for root, dirs, files in os.walk(base_path):
        for f in files:
            if should_exclude(f) or not should_include(f):
                continue

            full_path = os.path.join(root, f)
            try:
                size = os.path.getsize(full_path)
                rel_path = os.path.relpath(full_path, base_path)
                size_list.append((rel_path, size))
            except FileNotFoundError:
                continue

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
            if should_exclude(f) or not should_include(f):
                continue
            try:
                total += os.path.getsize(os.path.join(root, f))
            except FileNotFoundError:
                continue
    return total


def save_to_json(items, output_file):
    json_list = [{"path": path, "size": format_size(size)} for path, size in items]
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(json_list, f, indent=2, ensure_ascii=False)
    print(f"\n📝 결과가 '{output_file}' 파일로 저장되었습니다.")


def main():
    base_path = "./"
    print(f"=== 📦 디렉토리 용량 TOP {TOP_N} (JSON 저장 포함) ===")
    print(f"제외 확장자: {', '.join(EXCLUDE_EXTS)}")
    print(f"포함 확장자: {', '.join(INCLUDE_EXTS) if INCLUDE_EXTS else '전체 포함'}\n")

    sizes = get_all_sizes(base_path)
    sizes.sort(key=lambda x: x[1], reverse=True)

    top_items = sizes[:TOP_N]

    for path, size in top_items:
        print(f"{path:<60} {format_size(size)}")

    save_to_json(top_items, OUTPUT_FILE)


if __name__ == "__main__":
    main()
