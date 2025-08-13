import argparse, os, json, math, logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from io import BytesIO
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
from PIL import Image, ImageOps
import pytesseract
from pdf2image import convert_from_path
from pypdf import PdfReader, PdfWriter
from tqdm import tqdm

# (Windows 사용시 필요하면 경로 명시)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

try:
    from langdetect import detect as lang_detect
except Exception:
    lang_detect = None


# ─────────────────────────────
# 로깅
# ─────────────────────────────
def setup_logger(outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    log_file = outdir / "ocr_log.txt"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler()],
    )
    logging.info("Logger initialized.")
    return log_file


# ─────────────────────────────
# 전처리: 그레이스케일/대비/이진화
# ─────────────────────────────
def preprocess(img: Image.Image) -> Image.Image:
    img = ImageOps.grayscale(img)
    img = ImageOps.autocontrast(img)
    # 간단 Otsu 유사 임계(고정 140) – 문서에 따라 조절 가능
    img = img.point(lambda x: 0 if x < 140 else 255, "1")
    return img


# ─────────────────────────────
# 자동 회전(orientation) + 스큐 교정(deskew)
# ─────────────────────────────
def autorotate_and_deskew(img: Image.Image, enable_autorotate: bool, enable_deskew: bool) -> Image.Image:
    np_img = np.array(img.convert("L"))

    # 1) 자동 회전 (Tesseract OSD)
    if enable_autorotate:
        try:
            osd = pytesseract.image_to_osd(Image.fromarray(np_img))
            # “Rotate: 90” 같은 형식
            for line in osd.splitlines():
                if "Rotate:" in line:
                    angle = int(line.split(":")[-1].strip())
                    if angle != 0:
                        img = img.rotate(-angle, expand=True)  # 반대 방향으로 보정
                        np_img = np.array(img.convert("L"))
                    break
        except Exception:
            pass

    # 2) 스큐 교정 (Hough 변환 대신 모멘트 기반 간단 추정)
    if enable_deskew:
        try:
            # 이진화
            bw = (np_img < 200).astype(np.uint8) * 255
            coords = np.column_stack(np.where(bw > 0))
            if len(coords) > 0:
                rect = cv2_min_area_rect(coords)
                angle = rect[2]
                # OpenCV 없는 환경용 간단 deskew: -45~45 내 보정
                if angle < -45:
                    angle = -(90 + angle)
                else:
                    angle = -angle
                if abs(angle) > 0.5:
                    img = img.rotate(angle, expand=True, fillcolor=255)
        except Exception:
            pass

    return img

def cv2_min_area_rect(coords: np.ndarray) -> Tuple[Tuple[float,float], Tuple[float,float], float]:
    """
    OpenCV 없이 최소 외접 사각형의 각도를 근사하기 위한 작은 헬퍼.
    PCA를 이용해 주성분 각도로 근사한다.
    """
    # 중앙화
    mean = coords.mean(axis=0)
    centered = coords - mean
    # 공분산 + 고유벡터
    cov = np.cov(centered.T)
    eigvals, eigvecs = np.linalg.eig(cov)
    major = eigvecs[:, np.argmax(eigvals)]
    angle = math.degrees(math.atan2(major[0], major[1]))  # y,x 순서 보정
    # Rect 형식 흉내(각도만 사용)
    return ((0,0),(0,0), angle)


# ─────────────────────────────
# OCR 헬퍼
# ─────────────────────────────
def image_to_pdf_bytes(img: Image.Image, lang: str) -> bytes:
    return pytesseract.image_to_pdf_or_hocr(img, lang=lang, extension="pdf")

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

def detect_language_from_image(img: Image.Image, fallback: str = "eng") -> str:
    if lang_detect is None:
        return fallback
    try:
        temp = pytesseract.image_to_string(img, lang=fallback)
        if temp.strip():
            return lang_detect(temp)
        return fallback
    except Exception:
        return fallback


# ─────────────────────────────
# PDF 바이트 병합 (순서 보장)
# ─────────────────────────────
def merge_pdf_bytes_list(pages: List[Tuple[int, bytes]]) -> bytes:
    writer = PdfWriter()
    for _, b in sorted(pages, key=lambda x: x[0]):
        reader = PdfReader(BytesIO(b))
        for p in reader.pages:
            writer.add_page(p)
    out = BytesIO()
    writer.write(out)
    return out.getvalue()


# ─────────────────────────────
# 자동 DPI 선택 (단어 수 기준)
# ─────────────────────────────
def pick_best_dpi(pdf_path: Path, candidates: List[int], lang: str, conf: int, page_limit: int = 2) -> int:
    best = candidates[0]
    best_score = -1
    for dpi in candidates:
        try:
            pages = convert_from_path(str(pdf_path), dpi=dpi)[:page_limit]
            score = 0
            for pg in pages:
                pre = preprocess(pg)
                words = image_to_words(pre, lang=lang, conf_threshold=conf)
                score += len(words)
            if score > best_score:
                best_score, best = score, dpi
        except Exception:
            continue
    return best


# ─────────────────────────────
# 페이지 단위 작업자 (병렬)
# ─────────────────────────────
def ocr_page_worker(idx: int,
                    pil_bytes: bytes,
                    lang_opt: str,
                    conf: int,
                    autorotate: bool,
                    deskew: bool,
                    save_json: bool) -> Tuple[int, Optional[bytes], Optional[Dict]]:
    try:
        img = Image.open(BytesIO(pil_bytes))
        img = autorotate_and_deskew(img, enable_autorotate=autorotate, enable_deskew=deskew)
        img = preprocess(img)

        lang = lang_opt
        if lang_opt == "auto":
            lang = detect_language_from_image(img, fallback="eng")

        pdf_b = image_to_pdf_bytes(img, lang=lang)
        sidecar = None
        if save_json:
            sidecar = {"page": idx + 1, "lang": lang, "words": image_to_words(img, lang=lang, conf_threshold=conf)}
        return idx, pdf_b, sidecar
    except Exception as e:
        logging.error(f"Page {idx+1} OCR failed: {e}")
        return idx, None, None


# ─────────────────────────────
# 파일 처리 (PDF/이미지)
# ─────────────────────────────
def process_pdf(path: Path, outdir: Path, args):
    out_pdf = outdir / f"{path.stem}_searchable.pdf"
    out_json = outdir / f"{path.stem}_ocr.json"

    if args.resume and out_pdf.exists():
        logging.info(f"[SKIP] Already exists (resume): {out_pdf.name}")
        return

    probe_lang = "eng" if args.lang == "auto" else args.lang
    dpi = args.dpi
    if args.auto_dpi:
        dpi = pick_best_dpi(path, [200, 300, 400], probe_lang, args.conf)
        logging.info(f"Auto DPI -> {dpi}")

    try:
        pages = convert_from_path(str(path), dpi=dpi)
    except Exception as e:
        logging.error(f"PDF to images failed: {path.name} ({e})")
        return

    # 병렬 처리 준비
    jobs = []
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for i, pg in enumerate(pages):
            buf = BytesIO()
            pg.save(buf, format="PNG")
            jobs.append(ex.submit(
                ocr_page_worker, i, buf.getvalue(), args.lang, args.conf,
                args.autorotate, args.deskew, args.save_json
            ))

        pdf_pages: List[Tuple[int, bytes]] = []
        sidecar_pages: List[Dict] = []

        for f in tqdm(as_completed(jobs), total=len(jobs), desc=f"📕 {path.name}", unit="page"):
            idx, pdf_b, side = f.result()
            if pdf_b:
                pdf_pages.append((idx, pdf_b))
            if side:
                sidecar_pages.append(side)

    if not pdf_pages:
        logging.warning(f"No OCR pages produced: {path.name}")
        return

    merged = merge_pdf_bytes_list(pdf_pages)
    out_pdf.write_bytes(merged)
    logging.info(f"PDF saved: {out_pdf.name}")

    if args.save_json:
        data = {"type": "pdf", "file": path.name, "dpi": dpi, "pages": sorted(sidecar_pages, key=lambda x: x['page'])}
        out_json.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        logging.info(f"JSON saved: {out_json.name}")


def process_image(path: Path, outdir: Path, args):
    out_pdf = outdir / f"{path.stem}_searchable.pdf"
    out_json = outdir / f"{path.stem}_ocr.json"

    if args.resume and out_pdf.exists():
        logging.info(f"[SKIP] Already exists (resume): {out_pdf.name}")
        return

    try:
        img = Image.open(path)
    except Exception as e:
        logging.error(f"Open image failed: {path.name} ({e})")
        return

    img = autorotate_and_deskew(img, enable_autorotate=args.autorotate, enable_deskew=args.deskew)
    img = preprocess(img)

    lang = args.lang
    if args.lang == "auto":
        lang = detect_language_from_image(img, fallback="eng")

    try:
        pdf_b = image_to_pdf_bytes(img, lang=lang)
    except Exception as e:
        logging.error(f"OCR failed: {path.name} ({e})")
        return

    out_pdf.write_bytes(pdf_b)
    logging.info(f"PDF saved: {out_pdf.name}")

    if args.save_json:
        words = image_to_words(img, lang=lang, conf_threshold=args.conf)
        data = {"type": "image", "file": path.name, "pages": [{"page": 1, "lang": lang, "words": words}]}
        out_json.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        logging.info(f"JSON saved: {out_json.name}")


# ─────────────────────────────
# 메인
# ─────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="Ultra OCR: searchable PDF (batch, auto-DPI/lang, rotate/deskew, parallel).")
    ap.add_argument("--input", required=True, help="입력 경로(파일 또는 폴더)")
    ap.add_argument("--outdir", default="./output", help="출력 폴더")
    ap.add_argument("--lang", default="auto", help="Tesseract 언어 (예: eng, kor, eng+kor, auto)")
    ap.add_argument("--dpi", type=int, default=300, help="PDF→이미지 DPI(기본 300)")
    ap.add_argument("--auto-dpi", action="store_true", help="200/300/400 중 자동 선택")
    ap.add_argument("--conf", type=int, default=50, help="단어 confidence 임계값(기본 50)")
    ap.add_argument("--save-json", action="store_true", help="좌표/신뢰도 JSON 저장")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 4, help="병렬 작업 프로세스 수")
    ap.add_argument("--autorotate", action="store_true", help="자동 회전 보정")
    ap.add_argument("--deskew", action="store_true", help="스큐(기울기) 보정")
    ap.add_argument("--resume", action="store_true", help="기존 산출물 있으면 건너뛰기")

    args = ap.parse_args()

    outdir = Path(args.outdir)
    log_file = setup_logger(outdir)
    logging.info(f"Args: {vars(args)}")

    in_path = Path(args.input)
    if not in_path.exists():
        logging.error(f"Input path not found: {in_path}")
        return

    targets: List[Path] = []
    if in_path.is_dir():
        for p in sorted(in_path.iterdir()):
            if p.suffix.lower() in {".pdf", ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"}:
                targets.append(p)
    else:
        targets = [in_path]

    for p in targets:
        try:
            if p.suffix.lower() == ".pdf":
                process_pdf(p, outdir, args)
            else:
                process_image(p, outdir, args)
        except Exception as e:
            logging.exception(f"Failed: {p.name} ({e})")

    logging.info("All done! Log: %s", log_file)


if __name__ == "__main__":
    main()

    """
    # PDF 폴더 배치 처리, 자동 DPI/언어, 자동 회전+스큐, 병렬 6개, JSON 저장
python make_searchable_pdf_ultra.py --input ./scans --auto-dpi --autorotate --deskew --workers 6 --save-json

# 단일 이미지, 한글+영문 수동 지정, 리줌
python make_searchable_pdf_ultra.py --input ./page.png --lang eng+kor --resume
    """