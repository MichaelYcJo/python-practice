def clean_text_lines(lines, keyword=None, mode="include"):
    """
    1. 빈 줄 제거
    2. 중복 줄 제거
    3. 키워드 필터링 (포함/제외)
    """
    seen = set()
    cleaned = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue  # 빈 줄 제거

        if stripped in seen:
            continue  # 중복 제거

        # 키워드 필터링
        if keyword:
            if mode == "include" and keyword not in stripped:
                continue
            if mode == "exclude" and keyword in stripped:
                continue

        seen.add(stripped)
        cleaned.append(stripped)

    return cleaned


def main():
    input_path = "input.txt"
    output_path = "cleaned_output.txt"

    # ✅ 여기에 키워드와 모드 지정
    keyword = "에러"  # 찾을 키워드
    mode = "include"  # "include" 또는 "exclude"

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"❗ 파일 '{input_path}' 을(를) 찾을 수 없습니다.")
        return

    cleaned_lines = clean_text_lines(lines, keyword, mode)

    print(f"\n=== 키워드 필터 결과 (mode: {mode}, keyword: '{keyword}') ===")
    for line in cleaned_lines:
        print(line)

    with open(output_path, "w", encoding="utf-8") as f:
        for line in cleaned_lines:
            f.write(line + "\n")

    print(f"\n✅ 정리된 결과가 '{output_path}'에 저장되었습니다.")


if __name__ == "__main__":
    main()
