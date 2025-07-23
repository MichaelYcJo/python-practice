# python main.py sample.png --lang eng --save output.txt

import argparse
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import os


def preprocess_image(image: Image.Image) -> Image.Image:
    """OCR 정확도를 높이기 위한 전처리"""
    image = image.convert("L")
    image = image.filter(ImageFilter.MedianFilter())
    image = ImageEnhance.Contrast(image).enhance(2)
    return image


def extract_text(image_path: str, lang: str = "eng") -> str:
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"이미지 파일이 존재하지 않습니다: {image_path}")

    image = Image.open(image_path)
    image = preprocess_image(image)
    text = pytesseract.image_to_string(image, lang=lang)
    return text.strip()


def main():
    parser = argparse.ArgumentParser(description="🧠 OCR 텍스트 추출기")
    parser.add_argument("image", help="입력 이미지 경로")
    parser.add_argument("--lang", default="eng", help="언어 (기본: eng)")
    parser.add_argument("--save", help="텍스트를 저장할 파일 경로")

    args = parser.parse_args()
    try:
        result = extract_text(args.image, args.lang)
        print("\n📄 추출된 텍스트:\n")
        print(result)

        if args.save:
            with open(args.save, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"\n💾 저장 완료: {args.save}")

    except Exception as e:
        print(f"❗ 오류: {e}")


if __name__ == "__main__":
    main()