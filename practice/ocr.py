import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import os
import sys
import argparse


def preprocess_image(image: Image.Image) -> Image.Image:
    """OCR 정확도를 높이기 위한 전처리"""
    image = image.convert("L")  # 흑백
    image = image.filter(ImageFilter.MedianFilter())  # 노이즈 제거
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)  # 대비 강화
    return image


def extract_text_from_image(image_path: str, lang: str = "eng") -> str:
    """이미지에서 텍스트 추출"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"파일이 존재하지 않음: {image_path}")

    image = Image.open(image_path)
    image = preprocess_image(image)

    text = pytesseract.image_to_string(image, lang=lang)
    return text.strip()


def main():
    parser = argparse.ArgumentParser(description="🧠 OCR 이미지 텍스트 추출기")
    parser.add_argument("image_path", type=str, help="이미지 파일 경로")
    parser.add_argument("--lang", type=str, default="eng", help="언어 설정 (eng/kor 등)")
    parser.add_argument("--save", type=str, help="결과 저장할 파일 경로 (선택)")

    args = parser.parse_args()

    try:
        result = extract_text_from_image(args.image_path, args.lang)
        print("📄 추출된 텍스트:\n")
        print(result)

        if args.save:
            with open(args.save, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"\n💾 결과 저장 완료: {args.save}")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")


if __name__ == "__main__":
    main()