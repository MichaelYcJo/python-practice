def clean_text_lines(lines):
    """빈 줄, 공백만 있는 줄 제거 + 중복 제거"""
    seen = set()
    cleaned = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue  # 공백/빈 줄 제거

        if stripped not in seen:
            seen.add(stripped)
            cleaned.append(stripped)

    return cleaned


def main():
    input_path = "input.txt"  # 입력 파일
    output_path = "cleaned_output.txt"  # 출력 파일

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"❗ 파일 '{input_path}' 을(를) 찾을 수 없습니다.")
        return

    cleaned_lines = clean_text_lines(lines)

    # 결과 출력
    print("\n=== 결과 미리보기 ===")
    for line in cleaned_lines:
        print(line)

    # 저장
    with open(output_path, "w", encoding="utf-8") as f:
        for line in cleaned_lines:
            f.write(line + "\n")

    print(f"\n✅ 정리된 텍스트가 '{output_path}'에 저장되었습니다.")


if __name__ == "__main__":
    main()
