def clean_text_lines(lines):
    """빈 줄과 공백만 있는 줄 제거"""
    cleaned = []
    for line in lines:
        if line.strip():  # 줄에 내용이 있으면 추가
            cleaned.append(line.rstrip())  # 우측 공백 제거
    return cleaned


def main():
    input_path = "input.txt"  # 처리할 파일 경로

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"❗ 파일 '{input_path}' 을(를) 찾을 수 없습니다.")
        return

    cleaned_lines = clean_text_lines(lines)

    print("\n=== 결과 미리보기 ===")
    for line in cleaned_lines:
        print(line)

    # 원한다면 저장 기능도 여기에 추가할 수 있음


if __name__ == "__main__":
    main()
