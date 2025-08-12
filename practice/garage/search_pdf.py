import argparse
import os
from pathlib import Path
from typing import List

import pytesseract
from PIL import Image, ImageOps
from pdf2image import convert_from_path
from pypdf import PdfReader, PdfWriter

# (Windows라면 필요 시 주석 해제 후 경로 지정)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# ─────────────────────────────
# 전처리: 그레이스케일 + 자동 대비/이진화
# ─────────────────────────────
def preprocess_image(img: Image.Image) -> Image.Image:
    img = ImageOps.grayscale(img)
    # 적당한 대비/밝기 자동 보정 + 단순 이진화
    img = ImageOps.autocontrast(img)
    img = img.point(lambda x: 0 if x < 140 else 255, mode="1")
    return img


# ─────────────────────────────
# 단일 이미지 → OCR PDF (바이트)
# ─────────────────────────────
def image_to_ocr_pdf_bytes(img: Image.Image, lang: str) -> bytes:
    # Tesseract가 내장 텍스트 레이어 PDF 생성
    return pytesseract.image_to_pdf_or_hocr(img, lang=lang, extension="pdf")


# ─────────────────────────────
# PDF 페이지 합치기
# ─────────────────────────────
def merge_pdf_bytes_list(pdf_pages: List[bytes]) -> bytes:
    writer = PdfWriter()
    for page_bytes in pdf_pages:
        reader = PdfReader(stream=page_bytes)
        # 해당 PDF(한 페이지)에서 페이지 객체를 받아 병합
        for page in reader.pages:
            writer.add_page(page)
    out_bytes = bytearray()
    writer.write(out_bytes)
    return bytes(out_bytes)


# ─────────────────────────────
# 입력이 이미지인 경우 처리
# ─────────────────────────────
def process_image_file(path: Path, out_path: Path, lang: str):
    img = Image.open(path)
    img = preprocess_image(img)
    pdf_bytes = image_to_ocr_pdf_bytes(img, lang=lang)
    out_path.write_bytes(pdf_bytes)
    print(f"✅ 저장 완료: {out_path}")


# ─────────────────────────────
# 입력이 PDF인 경우 처리 (dpi 조정 가능)
# ─────────────────────────────
def process_pdf_file(path: Path, out_path: Path, lang: str, dpi: int):
    print(f"📕 PDF를 이미지로 변환 중… (dpi={dpi})")
    pages = convert_from_path(str(path), dpi=dpi)
    pdf_pages: List[bytes] = []

    for i, page_img in enumerate(pages, start=1):
        print(f"  ▶ 페이지 {i}/{len(pages)} OCR...")
        pre = preprocess_image(page_img)
        pdf_bytes = image_to_ocr_pdf_bytes(pre, lang=lang)
        pdf_pages.append(pdf_bytes)

    print("🧩 페이지 병합 중…")
    merged = merge_pdf_bytes_list(pdf_pages)
    out_path.write_bytes(merged)
    print(f"✅ 저장 완료: {out_path}")


# ─────────────────────────────
# 메인
# ─────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Make searchable PDF by adding OCR text layer (image/PDF → PDF)."
    )
    parser.add_argument("input", help="입력 이미지 또는 PDF 경로")
    parser.add_argument(
        "--lang",
        default="eng",
        help="Tesseract 언어 (예: eng, kor, eng+kor). 기본: eng",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="PDF → 이미지 변환 시 DPI (기본 300, 너무 높으면 느려집니다)",
    )
    parser.add_argument(
        "--output",
        help="출력 파일 경로 (.pdf). 미지정 시 입력파일명*_searchable.pdf 로 저장",
    )

    args = parser.parse_args()
    in_path = Path(args.input)
    if not in_path.exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {in_path}")

    # 출력 경로 결정
    if args.output:
        out_path = Path(args.output)
        if out_path.suffix.lower() != ".pdf":
            out_path = out_path.with_suffix(".pdf")
    else:
        out_path = in_path.with_name(in_path.stem + "_searchable.pdf")

    ext = in_path.suffix.lower()
    if ext in {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"}:
        process_image_file(in_path, out_path, lang=args.lang)
    elif ext == ".pdf":
        process_pdf_file(in_path, out_path, lang=args.lang, dpi=args.dpi)
    else:
        raise ValueError("지원하지 않는 형식입니다. 이미지(.jpg/.png/.tif…) 또는 PDF만 지원합니다.")

    print("🎉 작업 완료!")


if __name__ == "__main__":
    main()

"""
# 이미지 → 검색 가능한 PDF
python make_searchable_pdf.py ./scan.jpg --lang eng

# 한국어/영어 혼용 문서
python make_searchable_pdf.py ./receipt.png --lang eng+kor

# 스캔 PDF → 검색 가능한 PDF (DPI 조정)
python make_searchable_pdf.py ./document.pdf --dpi 300

# 출력 경로 지정
python make_searchable_pdf.py ./document.pdf --output ./out/searchable.pdf
"""