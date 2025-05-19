import os
import re
import emoji
from cleantext import clean
from pathlib import Path

# 기본 stopwords
KOR_STOPWORDS = {
    "그리고",
    "하지만",
    "그러나",
    "그래서",
    "또한",
    "때문에",
    "즉",
    "등",
    "이런",
    "저런",
    "있는",
    "하는",
}
ENG_STOPWORDS = {
    "and",
    "but",
    "so",
    "or",
    "the",
    "a",
    "an",
    "in",
    "on",
    "at",
    "is",
    "are",
    "was",
    "were",
    "be",
}

INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")


def clean_text(text: str) -> str:
    cleaned = clean(
        text,
        fix_unicode=True,
        lower=True,
        no_line_breaks=True,
        no_urls=True,
        no_emails=True,
        no_phone_numbers=True,
        no_currency_symbols=True,
        no_punct=True,
    )
    cleaned = emoji.replace_emoji(cleaned, replace="")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = re.sub(r"[^가-힣a-zA-Z0-9\s]", "", cleaned)
    return cleaned


def remove_stopwords(text: str) -> str:
    words = text.split()
    filtered = [w for w in words if w not in KOR_STOPWORDS and w not in ENG_STOPWORDS]
    return " ".join(filtered)


def process_file(filepath: Path):
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()

    cleaned = clean_text(raw)
    cleaned = remove_stopwords(cleaned)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / filepath.name

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cleaned)

    print(f"✅ {filepath.name} 정제 완료 → {output_path}")


def main():
    print("📁 텍스트 파일 전체 정제 시작")
    if not INPUT_DIR.exists():
        print("❗ input 폴더가 존재하지 않습니다.")
        return

    txt_files = list(INPUT_DIR.glob("*.txt"))
    if not txt_files:
        print("📭 처리할 텍스트 파일이 없습니다.")
        return

    for file in txt_files:
        process_file(file)

    print("\n🎉 전체 정제 완료!")


if __name__ == "__main__":
    main()
