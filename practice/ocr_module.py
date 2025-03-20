import os
import pytesseract
from PIL import Image, ImageFilter, ImageOps
import argparse


def preprocess_image(image):
    """이미지 전처리: 그레이스케일 + 이진화 + 샤프닝"""
    image = image.convert("L")  # 그레이스케일
    image = image.filter(ImageFilter.SHARPEN)
    image = ImageOps.autocontrast(image)
    return image


def extract_text_from_image(image_path, lang="eng"):
    """이미지에서 텍스트 추출 (전처리 포함)"""
    if not os.path.exists(image_path):
        return f"❌ 파일 없음: {image_path}", ""

    try:
        img = Image.open(image_path)
        img = preprocess_image(img)
        text = pytesseract.image_to_string(img, lang=lang)
        return f"✅ 텍스트 추출 성공: {os.path.basename(image_path)}", text.strip()
    except Exception as e:
        return f"⚠️ 에러 발생 ({image_path}): {e}", ""


def save_text_to_file(text, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"💾 텍스트 저장 완료: {output_path}")


def process_images_in_folder(folder_path, lang="eng"):
    for file in os.listdir(folder_path):
        if file.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp")):
            image_path = os.path.join(folder_path, file)
            message, text = extract_text_from_image(image_path, lang=lang)
            print(message)
            if text:
                save_text_to_file(text, f"{image_path}.txt")


def main():
    parser = argparse.ArgumentParser(description="🖼️ 이미지에서 텍스트 추출 (OCR)")
    parser.add_argument("path", help="이미지 파일 또는 폴더 경로")
    parser.add_argument("--lang", default="eng", help="OCR 언어 코드 (기본: eng)")
    args = parser.parse_args()

    path = args.path
    lang = args.lang

    if os.path.isdir(path):
        process_images_in_folder(path, lang)
    elif os.path.isfile(path):
        msg, text = extract_text_from_image(path, lang)
        print(msg)
        if text:
            save_path = f"{path}.txt"
            save_text_to_file(text, save_path)
    else:
        print("❌ 유효하지 않은 경로입니다.")


if __name__ == "__main__":
    main()
