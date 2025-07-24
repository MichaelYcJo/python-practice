import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from langdetect import detect
import argparse
import os

# tesseract 설치 경로 (윈도우에서 필요시 설정)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def detect_language(text: str) -> str:
    try:
        lang = detect(text)
        print(f"🌍 자동 감지된 언어: {lang}")
        return lang
    except Exception:
        print("⚠️ 언어 감지 실패. 기본값 'eng' 사용")
        return "eng"

def preprocess_image(image: Image.Image) -> Image.Image:
    image = image.convert("L")  # 그레이스케일
    return image.point(lambda x: 0 if x < 140 else 255, '1')  # 이진화

def extract_text_from_image(image_path: str, lang="eng") -> str:
    image = Image.open(image_path)
    image = preprocess_image(image)
    text = pytesseract.image_to_string(image, lang=lang)
    return text.strip()

def extract_text_from_pdf(pdf_path: str, lang="eng") -> str:
    pages = convert_from_path(pdf_path)
    texts = []
    for i, page in enumerate(pages):
        print(f"📄 페이지 {i+1} OCR 중...")
        image = preprocess_image(page)
        text = pytesseract.image_to_string(image, lang=lang)
        texts.append(text)
    return "\n\n".join(texts).strip()

def extract_with_boxes(image_path: str, lang="eng"):
    image = Image.open(image_path)
    image = preprocess_image(image)
    data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)

    print("📦 바운딩 박스 추출 결과:")
    for i in range(len(data["text"])):
        if int(data["conf"][i]) > 60 and data["text"][i].strip():
            print(f"{data['text'][i]} → x: {data['left'][i]}, y: {data['top'][i]}")

def main():
    parser = argparse.ArgumentParser(description="🧠 OCR 도구 (이미지 / PDF 지원)")
    parser.add_argument("path", help="이미지 또는 PDF 파일 경로")
    parser.add_argument("--lang", help="언어 코드 (기본: 자동 감지)", default=None)
    parser.add_argument("--box", action="store_true", help="텍스트의 위치(좌표) 정보도 추출")

    args = parser.parse_args()
    path = args.path

    if not os.path.exists(path):
        print("❌ 파일 경로가 잘못되었습니다.")
        return

    ext = os.path.splitext(path)[-1].lower()

    if ext in [".jpg", ".jpeg", ".png"]:
        text = extract_text_from_image(path, lang="eng")
        lang = args.lang or detect_language(text)
        if args.box:
            extract_with_boxes(path, lang=lang)
        else:
            print("\n📝 OCR 결과:\n")
            print(text)

    elif ext == ".pdf":
        text = extract_text_from_pdf(path, lang=args.lang or "eng")
        lang = args.lang or detect_language(text)
        print("\n📝 OCR 결과 (PDF):\n")
        print(text)

    else:
        print("⚠️ 지원하지 않는 파일 형식입니다. (이미지 또는 PDF만 가능)")


if __name__ == "__main__":
    main()


"""
python ocr_tool.py ./sample_image.jpg
python ocr_tool.py ./doc.pdf --lang kor
python ocr_tool.py ./sample.jpg --box
"""