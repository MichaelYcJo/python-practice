import pytesseract
from PIL import Image
import os
import sys

# macOS 기본 설치 경로는 보통 /opt/homebrew/bin/tesseract
# 필요시 경로 설정
# pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

def extract_text_from_image(image_path: str):
    if not os.path.exists(image_path):
        print("❌ 이미지 파일을 찾을 수 없습니다.")
        return

    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang="eng")  # 한글: lang="kor"
        print("📄 추출된 텍스트:\n")
        print(text.strip())
    except Exception as e:
        print(f"❗ 오류 발생: {e}")


def main():
    if len(sys.argv) < 2:
        print("사용법: python ocr_reader.py 이미지파일경로")
        return

    image_path = sys.argv[1]
    extract_text_from_image(image_path)


if __name__ == "__main__":
    main()