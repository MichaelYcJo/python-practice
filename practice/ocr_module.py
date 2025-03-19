import pytesseract
from PIL import Image
import os

# Tesseract 경로 설정 (Windows 사용자만)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def extract_text_from_image(image_path, lang="eng"):
    """이미지에서 텍스트 추출"""
    if not os.path.exists(image_path):
        print("❌ 이미지 파일이 존재하지 않습니다.")
        return ""

    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang=lang)
        return text.strip()
    except Exception as e:
        print(f"⚠️ OCR 처리 중 오류 발생: {e}")
        return ""


def main():
    """사용자 입력을 받아 이미지 텍스트 추출"""
    img_path = input("🖼️ 텍스트를 추출할 이미지 경로를 입력하세요: ").strip()
    lang = input("🌐 언어 코드 입력 (기본: eng, 한글: kor): ").strip() or "eng"

    print("\n🔍 이미지에서 텍스트를 추출 중...\n")
    extracted_text = extract_text_from_image(img_path, lang=lang)

    if extracted_text:
        print("✅ 추출된 텍스트:\n")
        print(extracted_text)
    else:
        print("❌ 텍스트를 추출할 수 없습니다.")


# 실행
main()
