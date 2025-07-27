import argparse
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import json
from typing import List, Dict
from pathlib import Path

def pdf_to_images(pdf_path: str, dpi: int = 300) -> List[Image.Image]:
    return convert_from_path(pdf_path, dpi=dpi)

def extract_text_from_image(image: Image.Image, conf_threshold: int = 50) -> List[Dict]:
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, lang="eng")
    results = []

    for i in range(len(data['text'])):
        word = data['text'][i].strip()
        conf = int(data['conf'][i])
        if word and conf >= conf_threshold:
            results.append({
                "text": word,
                "conf": conf,
                "left": data['left'][i],
                "top": data['top'][i],
                "width": data['width'][i],
                "height": data['height'][i]
            })
    return results

def process_pdf(pdf_path: str, dpi: int, conf_threshold: int) -> Dict:
    pages = pdf_to_images(pdf_path, dpi=dpi)
    all_results = []

    for idx, image in enumerate(pages):
        text_blocks = extract_text_from_image(image, conf_threshold=conf_threshold)
        all_results.append({
            "page": idx + 1,
            "results": text_blocks
        })

    return {
        "type": "pdf",
        "file": str(Path(pdf_path).name),
        "pages": all_results
    }

def main():
    parser = argparse.ArgumentParser(description="PDF OCR with DPI adjustment")
    parser.add_argument("pdf", type=str, help="PDF 파일 경로")
    parser.add_argument("--dpi", type=int, default=300, help="이미지 변환 시 DPI 값 (기본값: 300)")
    parser.add_argument("--conf", type=int, default=50, help="텍스트 신뢰도 필터 기준 (기본값: 50)")
    args = parser.parse_args()

    result = process_pdf(args.pdf, dpi=args.dpi, conf_threshold=args.conf)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()