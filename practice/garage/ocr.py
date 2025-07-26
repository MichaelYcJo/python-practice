import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import os
import json
import argparse
from datetime import datetime
from langdetect import detect

# 필요시 Windows에서 경로 설정
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def detect_language(text: str) -> str:
    try:
        lang = detect(text)
        print(f"🌐 감지된 언어: {lang}")
        return lang
    except Exception:
        return "eng"

def extract_structured_data(image: Image.Image, lang: str = "eng"):
    image = image.convert("L")  # 흑백 변환
    data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)

    result = []
    for i in range(len(data['text'])):
        word = data['text'][i].strip()
        if word and int(data['conf'][i]) > 50:
            result.append({
                "text": word,
                "confidence": int(data['conf'][i]),
                "position": {
                    "x": data['left'][i],
                    "y": data['top'][i],
                    "width": data['width'][i],
                    "height": data['height'][i]
                }
            })
    return result

def handle_image(image_path: str, lang: str = None):
    image = Image.open(image_path)
    temp_text = pytesseract.image_to_string(image)
    detected_lang = detect_language(temp_text) if lang is None else lang
    print(f"🔍 처리 중: {image_path} (언어: {detected_lang})")
    data = extract_structured_data(image, lang=detected_lang)
    return data

def handle_pdf(pdf_path: str, lang: str = None):
    print(f"📕 PDF OCR 시작: {pdf_path}")
    pages = convert_from_path(pdf_path)
    all_results = []

    for i, page in enumerate(pages):
        print(f"🔎 페이지 {i + 1} OCR 중...")
        temp_text = pytesseract.image_to_string(page)
        detected_lang = detect_language(temp_text) if lang is None else lang
        page_data = extract_structured_data(page, lang=detected_lang)
        all_results.append({
            "page": i + 1,
            "results": page_data
        })
    return all_results

def save_json(data, original_path):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, _ = os.path.splitext(os.path.basename(original_path))
    filename = f"{name}_ocr_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"💾 JSON 저장 완료: {filename}")

def main():
    parser = argparse.ArgumentParser(description="🧠 OCR → 구조화된 JSON")
    parser.add_argument("path", help="이미지/PDF 경로")
    parser.add_argument("--lang", help="OCR 언어 코드 (기본값: 자동 감지)")
    parser.add_argument("--save", action="store_true", help="JSON으로 저장")

    args = parser.parse_args()
    path = args.path
    ext = os.path.splitext(path)[-1].lower()

    if not os.path.exists(path):
        print("❌ 경로를 찾을 수 없습니다.")
        return

    if ext in [".jpg", ".jpeg", ".png"]:
        result = handle_image(path, args.lang)
    elif ext == ".pdf":
        result = handle_pdf(path, args.lang)
    else:
        print("❌ 지원되지 않는 파일 형식입니다.")
        return

    if args.save:
        save_json(result, path)
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()