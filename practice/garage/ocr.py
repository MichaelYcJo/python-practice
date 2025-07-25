import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from langdetect import detect
import argparse
import os
import datetime

# Windows 사용자는 필요시 경로 설정
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def detect_language(text: str) -> str:
    try:
        lang = detect(text)
        print(f"🌐 감지된 언어: {lang}")
        return lang
    except Exception:
        print("⚠️ 언어 감지 실패. 기본값 'eng' 사용")
        return "eng"

def preprocess_image(image: Image.Image) -> Image.Image:
    image = image.convert("L")
    return image.point(lambda x: 0 if x < 140 else 255, '1')

def extract_text_from_image(image_path: str, lang="eng", save_box=False) -> str:
    image = Image.open(image_path)
    image = preprocess_image(image)

    if save_box:
        data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)
        for i in range(len(data["text"])):
            if int(data["conf"][i]) > 60 and data["text"][i].strip():
                print(f"{data['text'][i]} → x: {data['left'][i]}, y: {data['top'][i]}")
    return pytesseract.image_to_string(image, lang=lang).strip()

def extract_text_from_pdf(pdf_path: str, lang="eng", save_images=False) -> str:
    pages = convert_from_path(pdf_path)
    texts = []
    for i, page in enumerate(pages):
        print(f"📄 PDF 페이지 {i+1} OCR 중...")
        image = preprocess_image(page)
        if save_images:
            page_path = f"{os.path.splitext(pdf_path)[0]}_page{i+1}.png"
            image.save(page_path)
        text = pytesseract.image_to_string(image, lang=lang)
        texts.append(text)
    return "\n\n".join(texts).strip()

def save_to_file(text: str, original_path: str):
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base = os.path.basename(original_path)
    name, _ = os.path.splitext(base)
    output_file = f"{name}_ocr_{now}.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"💾 결과 저장 완료: {output_file}")

def handle_file(path, args):
    ext = os.path.splitext(path)[-1].lower()

    if ext in [".jpg", ".jpeg", ".png"]:
        print(f"🖼 이미지 OCR: {path}")
        text = extract_text_from_image(path, lang=args.lang or "eng", save_box=args.box)
        if args.lang is None:
            detected_lang = detect_language(text)
            if detected_lang != "eng":
                print(f"🔁 감지된 언어 '{detected_lang}'로 재시도...")
                text = extract_text_from_image(path, lang=detected_lang, save_box=args.box)
        print("\n📝 OCR 결과:\n")
        print(text)
        if args.save:
            save_to_file(text, path)

    elif ext == ".pdf":
        print(f"📕 PDF OCR: {path}")
        text = extract_text_from_pdf(path, lang=args.lang or "eng", save_images=args.save_pdf_images)
        if args.lang is None:
            detected_lang = detect_language(text)
            if detected_lang != "eng":
                print(f"🔁 감지된 언어 '{detected_lang}'로 재시도...")
                text = extract_text_from_pdf(path, lang=detected_lang, save_images=args.save_pdf_images)
        print("\n📝 OCR 결과:\n")
        print(text)
        if args.save:
            save_to_file(text, path)
    else:
        print(f"❌ 지원되지 않는 파일 형식: {path}")

def main():
    parser = argparse.ArgumentParser(description="🧠 OCR 도구 (이미지/PDF/폴더)")
    parser.add_argument("path", help="파일 또는 폴더 경로")
    parser.add_argument("--lang", help="언어 코드 (기본: 자동 감지)")
    parser.add_argument("--box", action="store_true", help="텍스트 위치 박스 출력")
    parser.add_argument("--save", action="store_true", help="OCR 결과를 .txt로 저장")
    parser.add_argument("--save-pdf-images", action="store_true", help="PDF 페이지 이미지를 저장")

    args = parser.parse_args()

    if os.path.isdir(args.path):
        for fname in os.listdir(args.path):
            fpath = os.path.join(args.path, fname)
            if os.path.isfile(fpath) and fname.lower().endswith((".jpg", ".png", ".jpeg", ".pdf")):
                handle_file(fpath, args)
    else:
        handle_file(args.path, args)

if __name__ == "__main__":
    main()