import argparse
import os
from pathlib import Path
from typing import List, Dict, Optional
import json
from io import BytesIO

import pytesseract
from PIL import Image, ImageOps
from pdf2image import convert_from_path
from pypdf import PdfReader, PdfWriter
from tqdm import tqdm

# 언어 감지(옵션) : 설치 안 돼 있으면 자동감지 비활성화
try:
    from langdetect import detect
except Exception:
    detect = None

# (Windows일 경우 필요 시 경로 지정)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# ─────────────────────────────
# 전처리: 그레이스케일 + 자동대비 + 단순 이진화
# ─────────────────────────────
def preprocess(img: Image.Image) -> Image.Image:
    img = ImageOps.grayscale(img)
    img = ImageOps.autocontrast(img)
    img = img.point(lambda x: 0 if x < 140 else 255, "1")
    return img


# ─────────────────────────────
# OCR: 단일 이미지 → PDF 바이트
# ─────────────────────────────
def image_to_ocr_pdf_bytes(img: Image.Image, lang: str) -> bytes:
    return pytesseract.image_to_pdf_or_hocr(img, lang=lang, extension="pdf")


# ─────────────────────────────
# OCR: 단일 이미지 → 구조화된 단어 목록(JSON 용)
# ─────────────────────────────
def image_to_words(img: Image.Image, lang: str, conf_threshold: int) -> List[Dict]:
    data = pytesseract.image_to_data(img, lang=lang, output_type=pytesseract.Output.DICT)
    out = []
    n = len(data["text"])
    for i in range(n):
        word = (data["text"][i] or "").strip()
        try:
            conf = int(float(data["conf"][i]))
        except Exception:
            conf = -1
        if word and conf >= conf_threshold:
            out.append({
                "text": word,
                "confidence": conf,
                "bbox": {
                    "x": int(data["left"][i]),
                    "y": int(data["top"][i]),
                    "w": int(data["width"][i]),
                    "h": int(data["height"][i]),
                }
            })
    return out


# ─────────────────────────────
# PDF 바이트 병합
# ─────────────────────────────
def merge_pdf_bytes_list(pdf_pages: List[bytes]) -> bytes:
    writer = PdfWriter()
    for b in pdf_pages:
        reader = PdfReader(BytesIO(b))
        for p in reader.pages:
            writer.add_page(p)
    out = BytesIO()
    writer.write(out)
    return out.getvalue()


# ─────────────────────────────
# DPI 후보 중 최적 DPI 고르기(텍스트량 기준)
# ─────────────────────────────
def pick_best_dpi_for_pdf(path: Path, dpi_candidates: List[int], lang: str, conf: int, page_limit: int = 2) -> int:
    scores = []
    for dpi in dpi_candidates:
        try:
            pages = convert_from_path(str(path), dpi=dpi)
            pages = pages[:page_limit]
            total_words = 0
            for pg in pages:
                img = preprocess(pg)
                total_words += len(image_to_words(img, lang=lang, conf_threshold=conf))
            scores.append((total_words, dpi))
        except Exception:
            scores.append((0, dpi))
    # 텍스트(단어) 개수가 가장 많은 DPI
    best = max(scores, key=lambda x: x[0])[1]
    return best


# ─────────────────────────────
# 언어 자동 감지(가능하면)
# ─────────────────────────────
def auto_detect_language(img: Image.Image, fallback: str = "eng") -> str:
    if detect is None:
        return fallback
    try:
        text = pytesseract.image_to_string(img, lang=fallback)
        lang = detect(text) if text.strip() else fallback
        return lang
    except Exception:
        return fallback


# ─────────────────────────────
# 이미지 파일 처리
# ─────────────────────────────
def process_image(path: Path, out_pdf_dir: Path, save_json: bool, lang_opt: str,
                  conf: int) -> None:
    try:
        img = Image.open(path)
    except Exception as e:
        print(f"❌ 이미지 열기 실패: {path.name} ({e})")
        return

    pre = preprocess(img)
    lang = lang_opt
    if lang_opt == "auto":
        # 기본 eng로 1차 → 언어감지 → 다국어 조합도 가능하면 사용자가 직접 지정 권장
        lang = auto_detect_language(pre, fallback="eng")

    # OCR PDF
    try:
        pdf_bytes = image_to_ocr_pdf_bytes(pre, lang=lang)
    except Exception as e:
        print(f"❌ OCR 실패: {path.name} ({e})")
        return

    out_pdf_path = out_pdf_dir / f"{path.stem}_searchable.pdf"
    out_pdf_path.write_bytes(pdf_bytes)

    # 사이드카 JSON
    if save_json:
        words = image_to_words(pre, lang=lang, conf_threshold=conf)
        sidecar = {
            "type": "image",
            "file": path.name,
            "lang": lang,
            "pages": [{"page": 1, "words": words}]
        }
        (out_pdf_dir / f"{path.stem}_ocr.json").write_text(
            json.dumps(sidecar, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    print(f"✅ {path.name} → {out_pdf_path.name}  (lang={lang}, words≥{conf})")


# ─────────────────────────────
# PDF 파일 처리
# ─────────────────────────────
def process_pdf(path: Path, out_pdf_dir: Path, save_json: bool, lang_opt: str,
                dpi: int, auto_dpi: bool, conf: int) -> None:
    # DPI 결정
    use_dpi = dpi
    if auto_dpi:
        probe_lang = "eng" if lang_opt == "auto" else lang_opt
        use_dpi = pick_best_dpi_for_pdf(path, [200, 300, 400], probe_lang, conf)
        print(f"🔎 자동 DPI 선택: {use_dpi}")

    try:
        pages = convert_from_path(str(path), dpi=use_dpi)
    except Exception as e:
        print(f"❌ PDF 변환 실패: {path.name} ({e})")
        return

    pdf_pages = []
    sidecar_pages = []

    for idx, pg in enumerate(tqdm(pages, desc=f"📕 {path.name} OCR", unit="page")):
        pre = preprocess(pg)

        # 언어 결정
        lang = lang_opt
        if lang_opt == "auto":
            lang = auto_detect_language(pre, fallback="eng")

        # 페이지 OCR (PDF/JSON)
        try:
            pdf_bytes = image_to_ocr_pdf_bytes(pre, lang=lang)
            pdf_pages.append(pdf_bytes)
            if save_json:
                words = image_to_words(pre, lang=lang, conf_threshold=conf)
                sidecar_pages.append({"page": idx + 1, "lang": lang, "words": words})
        except Exception as e:
            print(f"❌ 페이지 {idx+1} OCR 실패: {e}")

    if not pdf_pages:
        print(f"⚠️ OCR된 페이지가 없습니다: {path.name}")
        return

    merged = merge_pdf_bytes_list(pdf_pages)
    out_pdf_path = out_pdf_dir / f"{path.stem}_searchable.pdf"
    out_pdf_path.write_bytes(merged)

    if save_json:
        sidecar = {"type": "pdf", "file": path.name, "dpi": use_dpi, "pages": sidecar_pages}
        (out_pdf_dir / f"{path.stem}_ocr.json").write_text(
            json.dumps(sidecar, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    print(f"✅ {path.name} → {out_pdf_path.name}  (dpi={use_dpi}, words≥{conf})")


# ─────────────────────────────
# 엔트리포인트
# ─────────────────────────────
def main():
    ap = argparse.ArgumentParser(
        description="Make searchable PDFs with OCR (image/PDF, batch folder, auto-DPI/lang, JSON sidecar)."
    )
    ap.add_argument("--input", required=True, help="입력 경로(파일 또는 폴더)")
    ap.add_argument("--outdir", default="./output", help="출력 폴더 (기본 ./output)")
    ap.add_argument("--lang", default="auto",
                    help="Tesseract 언어. 예) eng, kor, eng+kor, auto(기본)")
    ap.add_argument("--dpi", type=int, default=300, help="PDF→이미지 변환 DPI (기본 300)")
    ap.add_argument("--auto-dpi", action="store_true", help="200/300/400 중 자동 선택")
    ap.add_argument("--conf", type=int, default=50, help="JSON 단어 신뢰도 임계값 (기본 50)")
    ap.add_argument("--save-json", action="store_true", help="OCR 좌표/신뢰도 JSON 사이드카 저장")

    args = ap.parse_args()
    in_path = Path(args.input)
    out_dir = Path(args.outdir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not in_path.exists():
        raise FileNotFoundError(f"입력 경로가 존재하지 않습니다: {in_path}")

    targets: List[Path] = []
    if in_path.is_dir():
        for p in sorted(in_path.iterdir()):
            if p.suffix.lower() in {".pdf", ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"}:
                targets.append(p)
    else:
        targets = [in_path]

    for p in targets:
        if p.suffix.lower() == ".pdf":
            process_pdf(p, out_dir, args.save_json, args.lang, args.dpi, args.auto_dpi, args.conf)
        else:
            process_image(p, out_dir, args.save_json, args.lang, args.conf)

    print("🎉 모든 작업 완료!")


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