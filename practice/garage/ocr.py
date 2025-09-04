import argparse
import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance, ImageFilter
import json
from typing import List, Dict
from pathlib import Path
import multiprocessing as mp
from functools import partial
import logging
from tqdm import tqdm
import gc

def pdf_to_images(pdf_path: str, dpi: int = 300, first_page: int = None, last_page: int = None) -> List[Image.Image]:
    return convert_from_path(pdf_path, dpi=dpi, first_page=first_page, last_page=last_page)

def preprocess_image(image: Image.Image) -> Image.Image:
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    gray = image.convert('L')
    
    enhancer = ImageEnhance.Contrast(gray)
    enhanced = enhancer.enhance(1.5)
    
    filtered = enhanced.filter(ImageFilter.MedianFilter(size=3))
    
    return filtered

def extract_text_from_image(image: Image.Image, conf_threshold: int = 50, preprocess: bool = True) -> List[Dict]:
    if preprocess:
        image = preprocess_image(image)
    
    config = '--oem 3 --psm 6'
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, lang="eng", config=config)
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

def process_single_page(args_tuple) -> Dict:
    page_idx, image, conf_threshold, preprocess = args_tuple
    try:
        text_blocks = extract_text_from_image(image, conf_threshold=conf_threshold, preprocess=preprocess)
        return {
            "page": page_idx + 1,
            "results": text_blocks
        }
    except Exception as e:
        logging.error(f"Error processing page {page_idx + 1}: {e}")
        return {
            "page": page_idx + 1,
            "results": [],
            "error": str(e)
        }
    finally:
        del image
        gc.collect()

def process_pdf(pdf_path: str, dpi: int, conf_threshold: int, workers: int = None, preprocess: bool = True, batch_size: int = None) -> Dict:
    if workers is None:
        workers = min(mp.cpu_count(), 4)
    
    logging.info(f"Processing PDF: {pdf_path}")
    logging.info(f"Using {workers} workers, DPI: {dpi}, Confidence threshold: {conf_threshold}")
    
    if batch_size:
        return process_pdf_in_batches(pdf_path, dpi, conf_threshold, workers, preprocess, batch_size)
    
    pages = pdf_to_images(pdf_path, dpi=dpi)
    total_pages = len(pages)
    logging.info(f"Total pages to process: {total_pages}")
    
    if total_pages == 1 or workers == 1:
        all_results = []
        for idx, image in enumerate(tqdm(pages, desc="Processing pages")):
            result = process_single_page((idx, image, conf_threshold, preprocess))
            all_results.append(result)
    else:
        args_list = [(idx, image, conf_threshold, preprocess) for idx, image in enumerate(pages)]
        
        with mp.Pool(processes=workers) as pool:
            all_results = list(tqdm(
                pool.imap(process_single_page, args_list),
                total=total_pages,
                desc="Processing pages"
            ))
    
    del pages
    gc.collect()
    
    return {
        "type": "pdf",
        "file": str(Path(pdf_path).name),
        "total_pages": total_pages,
        "pages": all_results
    }

def process_pdf_in_batches(pdf_path: str, dpi: int, conf_threshold: int, workers: int, preprocess: bool, batch_size: int) -> Dict:
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        total_pages = doc.page_count
        doc.close()
    except ImportError:
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
        except ImportError:
            pages = pdf_to_images(pdf_path, dpi=dpi, first_page=1, last_page=1)
            total_pages = len(convert_from_path(pdf_path, dpi=100))
            del pages
            gc.collect()
    
    logging.info(f"Processing {total_pages} pages in batches of {batch_size}")
    
    all_results = []
    
    for start_page in tqdm(range(1, total_pages + 1, batch_size), desc="Processing batches"):
        end_page = min(start_page + batch_size - 1, total_pages)
        
        batch_pages = pdf_to_images(pdf_path, dpi=dpi, first_page=start_page, last_page=end_page)
        
        if len(batch_pages) == 1 or workers == 1:
            for idx, image in enumerate(batch_pages):
                result = process_single_page((start_page + idx - 1, image, conf_threshold, preprocess))
                all_results.append(result)
        else:
            args_list = [(start_page + idx - 1, image, conf_threshold, preprocess) 
                        for idx, image in enumerate(batch_pages)]
            
            with mp.Pool(processes=min(workers, len(batch_pages))) as pool:
                batch_results = pool.map(process_single_page, args_list)
                all_results.extend(batch_results)
        
        del batch_pages
        gc.collect()
    
    return {
        "type": "pdf",
        "file": str(Path(pdf_path).name),
        "total_pages": total_pages,
        "pages": all_results
    }

def main():
    parser = argparse.ArgumentParser(description="PDF OCR with performance optimizations")
    parser.add_argument("pdf", type=str, help="PDF 파일 경로")
    parser.add_argument("--dpi", type=int, default=300, help="이미지 변환 시 DPI 값 (기본값: 300)")
    parser.add_argument("--conf", type=int, default=50, help="텍스트 신뢰도 필터 기준 (기본값: 50)")
    parser.add_argument("--workers", type=int, default=None, help="병렬 처리 워커 수 (기본값: CPU 코어 수, 최대 4)")
    parser.add_argument("--no-preprocess", action="store_true", help="이미지 전처리 비활성화")
    parser.add_argument("--batch-size", type=int, default=None, help="대용량 PDF를 위한 배치 크기")
    parser.add_argument("--verbose", "-v", action="store_true", help="상세 로그 출력")
    args = parser.parse_args()

    log_level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )

    preprocess = not args.no_preprocess
    
    result = process_pdf(
        args.pdf, 
        dpi=args.dpi, 
        conf_threshold=args.conf,
        workers=args.workers,
        preprocess=preprocess,
        batch_size=args.batch_size
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()