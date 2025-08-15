import argparse, os, json, logging, math
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from io import BytesIO
from concurrent.futures import ProcessPoolExecutor, as_completed

import pytesseract
from PIL import Image, ImageOps
from pdf2image import convert_from_path
from pypdf import PdfReader, PdfWriter
from tqdm import tqdm

# (Windows 사용자는 필요시 주석 해제 후 경로 지정)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

try:
    from langdetect import detect as lang_detect
except Exception:
    lang_detect = None


# ───────────── 로깅 ─────────────
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


# ───────────── 전처리 ─────────────
def preprocess(img: Image.Image) -> Image.Image:
    img = ImageOps.grayscale(img)
    img = ImageOps.autocontrast(img)
    # 단순 이진화(문서에 따라 130~170 사이 조정해도 좋음)
    img = img.point(lambda x: 0 if x < 140 else 255, "1")
    return img


# ───────────── 언어자동감지(옵션) ─────────────
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


# ───────────── OCR helper ─────────────
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


# ───────────── DPI 자동 선택(샘플 페이지 텍스트량 기준) ─────────────
def pick_best_dpi(pdf_path: Path, candidates: List[int], lang: str, conf: int, sample_pages: int = 2) -> int:
    best, best_score = candidates[0], -1
    # 앞쪽 몇 페이지만 샘플링
    with tqdm(total=min(sample_pages, get_pdf_num_pages(pdf_path)), desc="🔎 Auto-DPI probe", unit="page") as bar:
        page_idx = 1
        for _ in range(min(sample_pages, get_pdf_num_pages(pdf_path))):
            for dpi in candidates:
                try:
                    imgs = convert_from_path(str(pdf_path), dpi=dpi, first_page=page_idx, last_page=page_idx)
                    if not imgs:
                        continue
                    pre = preprocess(imgs[0])
                    words = image_to_words(pre, lang=lang, conf_threshold=conf)
                    score = len(words)
                    if score > best_score:
                        best_score, best = score, dpi
                except Exception:
                    pass
            page_idx += 1
            bar.update(1)
    return best

def get_pdf_num_pages(pdf_path: Path) -> int:
    r = PdfReader(str(pdf_path))
    return len(r.pages)


# ───────────── 체크포인트 매니페스트 ─────────────
def load_or_init_manifest(ckpt_dir: Path, pdf_path: Path, dpi: int, lang_opt: str, conf: int) -> Dict:
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = ckpt_dir / "manifest.json"
    if manifest_path.exists():
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    total_pages = get_pdf_num_pages(pdf_path)
    manifest = {
        "file": pdf_path.name,
        "dpi": dpi,
        "lang_opt": lang_opt,
        "conf": conf,
        "total_pages": total_pages,
        "completed_pages": []  # 1-based indices
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest

def save_manifest(ckpt_dir: Path, manifest: Dict):
    (ckpt_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


# ───────────── 단일 페이지 처리(작업자) ─────────────
def ocr_pdf_page_worker(pdf_path: str,
                        page_index_1based: int,
                        dpi: int,
                        lang_opt: str,
                        conf: int,
                        save_json: bool,
                        ckpt_dir: str) -> Tuple[int, bool, Optional[str]]:
    """
    반환: (페이지번호, 성공여부, 오류메시지)
    """
    try:
        imgs = convert_from_path(pdf_path, dpi=dpi, first_page=page_index_1based, last_page=page_index_1based)
        if not imgs:
            return page_index_1based, False, "pdf2image returned no image"
        pre = preprocess(imgs[0])

        lang = lang_opt
        if lang_opt == "auto":
            lang = detect_language_from_image(pre, fallback="eng")

        # OCR PDF 저장(체크포인트)
        page_pdf = image_to_pdf_bytes(pre, lang=lang)
        page_pdf_path = Path(ckpt_dir) / f"page_{page_index_1based:05d}.pdf"
        page_pdf_path.write_bytes(page_pdf)

        # 사이드카 JSON (옵션)
        if save_json:
            words = image_to_words(pre, lang=lang, conf_threshold=conf)
            page_json = {
                "page": page_index_1based,
                "lang": lang,
                "words": words
            }
            page_json_path = Path(ckpt_dir) / f"page_{page_index_1based:05d}.json"
            page_json_path.write_text(json.dumps(page_json, ensure_ascii=False, indent=2), encoding="utf-8")

        return page_index_1based, True, None
    except Exception as e:
        return page_index_1based, False, str(e)


# ───────────── 최종 병합 ─────────────
def finalize_merge(pdf_path: Path, ckpt_dir: Path, out_pdf: Path, save_json: bool):
    writer = PdfWriter()
    pages = sorted(ckpt_dir.glob("page_*.pdf"))
    if not pages:
        raise RuntimeError("No checkpointed pages to merge.")
    for p in pages:
        reader = PdfReader(str(p))
        for pg in reader.pages:
            writer.add_page(pg)
    out_pdf.write_bytes(write_pdf_to_bytes(writer))

    # JSON 병합
    if save_json:
        merged = {"type": "pdf", "file": pdf_path.name, "pages": []}
        for j in sorted(ckpt_dir.glob("page_*.json")):
            merged["pages"].append(json.loads(j.read_text(encoding="utf-8")))
        out_json = out_pdf.with_suffix(".json")
        out_json.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")

def write_pdf_to_bytes(writer: PdfWriter) -> bytes:
    bio = BytesIO()
    writer.write(bio)
    return bio.getvalue()


# ───────────── 메인 처리 ─────────────
def process_pdf_with_checkpoint(pdf_path: Path,
                                outdir: Path,
                                dpi: int,
                                auto_dpi: bool,
                                lang_opt: str,
                                conf: int,
                                save_json: bool,
                                workers: int,
                                resume: bool,
                                keep_ckpt: bool):
    outdir.mkdir(parents=True, exist_ok=True)
    out_pdf = outdir / f"{pdf_path.stem}_searchable.pdf"

    # 체크포인트 디렉토리
    ckpt_root = outdir / ".checkpoints"
    ckpt_dir = ckpt_root / pdf_path.stem
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    # 매니페스트 로드/초기화
    manifest = load_or_init_manifest(ckpt_dir, pdf_path, dpi, lang_opt, conf)

    # DPI 자동 선택 (매니페스트 초기화 직후에만)
    if auto_dpi and not manifest.get("dpi_finalized"):
        probe_lang = "eng" if lang_opt == "auto" else lang_opt
        chosen = pick_best_dpi(pdf_path, [200, 300, 400], probe_lang, conf)
        manifest["dpi"] = chosen
        manifest["dpi_finalized"] = True
        save_manifest(ckpt_dir, manifest)
        logging.info(f"Auto-DPI selected: {chosen}")

    dpi = manifest["dpi"]
    total_pages = manifest["total_pages"]
    completed = set(manifest.get("completed_pages", []))

    # 이미 최종 산출물이 있으면 바로 리턴(Resume)
    if resume and out_pdf.exists() and len(completed) == total_pages:
        logging.info(f"[RESUME] Already completed: {pdf_path.name}")
        return

    # 이미 존재하는 페이지 조각 스캔 (파일 기준으로도 복구)
    for p in ckpt_dir.glob("page_*.pdf"):
        try:
            idx = int(p.stem.split("_")[1])
            completed.add(idx)
        except Exception:
            pass
    manifest["completed_pages"] = sorted(list(completed))
    save_manifest(ckpt_dir, manifest)

    # 처리할 페이지 인덱스
    todo = [i for i in range(1, total_pages + 1) if i not in completed]
    if not todo:
        logging.info("No remaining pages. Merging…")
        finalize_merge(pdf_path, ckpt_dir, out_pdf, save_json)
        if not keep_ckpt:
            for f in ckpt_dir.glob("*"):
                try:
                    f.unlink()
                except Exception:
                    pass
            try:
                ckpt_dir.rmdir()
            except Exception:
                pass
        logging.info(f"✅ Done: {out_pdf}")
        return

    logging.info(f"Start OCR: {pdf_path.name} | pages: {total_pages}, todo: {len(todo)}, dpi={dpi}, lang={lang_opt}")

    # 병렬 처리
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futures = [
            ex.submit(
                ocr_pdf_page_worker,
                str(pdf_path),
                idx,
                dpi,
                lang_opt,
                conf,
                save_json,
                str(ckpt_dir)
            ) for idx in todo
        ]
        for fut in tqdm(as_completed(futures), total=len(futures), desc=f"📕 {pdf_path.name}", unit="page"):
            page_idx, ok, err = fut.result()
            if ok:
                completed.add(page_idx)
                manifest["completed_pages"] = sorted(list(completed))
                save_manifest(ckpt_dir, manifest)
            else:
                logging.error(f"Page {page_idx} failed: {err}")

    # 완료 여부 확인 후 병합
    if len(completed) == total_pages:
        logging.info("Merging all pages…")
        finalize_merge(pdf_path, ckpt_dir, out_pdf, save_json)
        if not keep_ckpt:
            for f in ckpt_dir.glob("*"):
                try:
                    f.unlink()
                except Exception:
                    pass
            try:
                ckpt_dir.rmdir()
            except Exception:
                pass
        logging.info(f"✅ Done: {out_pdf}")
    else:
        logging.info(f"Partial complete. Resume later with --resume (done {len(completed)}/{total_pages}).")


# ───────────── 이미지 파일도 지원(간단) ─────────────
def process_image_simple(img_path: Path, outdir: Path, lang_opt: str, conf: int, save_json: bool):
    out_pdf = outdir / f"{img_path.stem}_searchable.pdf"
    img = Image.open(img_path)
    pre = preprocess(img)

    lang = lang_opt
    if lang_opt == "auto":
        lang = detect_language_from_image(pre, fallback="eng")

    pdf_b = image_to_pdf_bytes(pre, lang=lang)
    out_pdf.write_bytes(pdf_b)

    if save_json:
        words = image_to_words(pre, lang=lang, conf_threshold=conf)
        out_json = out_pdf.with_suffix(".json")
        data = {"type": "image", "file": img_path.name, "pages": [{"page": 1, "lang": lang, "words": words}]}
        out_json.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    logging.info(f"✅ Image done: {out_pdf}")


# ───────────── 엔트리 ─────────────
def main():
    ap = argparse.ArgumentParser(description="Searchable PDF maker with robust checkpointing/resume for large PDFs.")
    ap.add_argument("--input", required=True, help="입력 경로(파일 또는 폴더)")
    ap.add_argument("--outdir", default="./output", help="출력 폴더 (기본 ./output)")
    ap.add_argument("--lang", default="auto", help="Tesseract 언어 (예: eng, kor, eng+kor, auto=자동)")
    ap.add_argument("--dpi", type=int, default=300, help="PDF→이미지 변환 DPI(기본 300)")
    ap.add_argument("--auto-dpi", action="store_true", help="200/300/400 중 자동 선택")
    ap.add_argument("--conf", type=int, default=50, help="단어 confidence 임계값(기본 50)")
    ap.add_argument("--save-json", action="store_true", help="페이지 단어/좌표 JSON 사이드카 저장")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 4, help="병렬 프로세스 수")
    ap.add_argument("--resume", action="store_true", help="체크포인트 기반 재개")
    ap.add_argument("--keep-ckpt", action="store_true", help="최종 병합 후 체크포인트 보존")

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
                process_pdf_with_checkpoint(
                    p, outdir,
                    dpi=args.dpi, auto_dpi=args.auto_dpi,
                    lang_opt=args.lang, conf=args.conf,
                    save_json=args.save_json, workers=args.workers,
                    resume=args.resume, keep_ckpt=args.keep_ckpt
                )
            else:
                process_image_simple(p, outdir, args.lang, args.conf, args.save_json)
        except Exception as e:
            logging.exception(f"Failed: {p.name} ({e})")

    logging.info("All done! Log: %s", log_file)


if __name__ == "__main__":
    main()

    """
    # 대용량 PDF에 체크포인트 활성 + 자동 DPI + 병렬 6개
python make_searchable_pdf_checkpoint.py --input ./bigdoc.pdf --resume --auto-dpi --workers 6

# 폴더 일괄 처리 + JSON 사이드카 저장, 완료 후에도 체크포인트 보존
python make_searchable_pdf_checkpoint.py --input ./scans --save-json --keep-ckpt

# 중도 중단 → 다시 이어서
python make_searchable_pdf_checkpoint.py --input ./bigdoc.pdf --resume
    """