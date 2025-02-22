import os
import shutil
import logging
import argparse
from pdf2image import convert_from_path

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def convert_pdf_to_png(pdf_path, output_folder, dpi=200):
    """
    PDF 파일을 PNG 이미지로 변환.
    한 PDF 파일에 여러 페이지가 있을 경우 각 페이지마다
    <원본파일명>_page<페이지번호>.png 형식으로 저장합니다.
    변환 성공 시 생성된 이미지 경로 리스트를 반환합니다.
    """
    try:
        images = convert_from_path(pdf_path, dpi=dpi)
    except Exception as e:
        logging.error(f"PDF 변환 실패: {pdf_path}, 에러: {e}")
        return None

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    created_images = []
    for i, image in enumerate(images, start=1):
        output_filename = f"{base_name}_page{i}.png"
        output_path = os.path.join(output_folder, output_filename)
        try:
            image.save(output_path, "PNG")
            created_images.append(output_path)
        except Exception as e:
            logging.error(f"이미지 저장 실패: {output_path}, 에러: {e}")
            # 페이지 단위 실패 시 계속 진행할지 결정
            continue
    return created_images if created_images else None


def log_failed_files(base_dir, failed_files):
    if failed_files:
        failed_list_path = os.path.join(base_dir, "failed_files.txt")
        with open(failed_list_path, "w", encoding="utf-8") as f:
            for failed_file in failed_files:
                f.write(failed_file + "\n")
        logging.info(f"실패한 파일 목록이 저장되었습니다: {failed_list_path}")


def copy_failed_files(base_dir, failed_files):
    failed_copy_dir = os.path.join(base_dir, "FAILED_FILES")
    for failed_file in failed_files:
        relative_path = os.path.relpath(failed_file, base_dir)
        dest_path = os.path.join(failed_copy_dir, relative_path)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        try:
            shutil.copy2(failed_file, dest_path)
            logging.info(f"실패한 파일 복사 완료: {dest_path}")
        except Exception as e:
            logging.error(f"실패한 파일 복사 실패: {failed_file}, 에러: {e}")


def convert_pdfs_in_folder(base_dir, dpi=200):
    failed_files = []  # 변환에 실패한 PDF 파일 경로 리스트

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            # PDF 파일만 선택
            if not file.lower().endswith(".pdf"):
                continue

            original_path = os.path.join(root, file)
            # 원본 폴더 기준 상대 경로 계산
            relative_dir = os.path.relpath(root, base_dir)
            # 변환된 이미지들을 저장할 폴더 (CONVERTED 폴더 내 동일한 폴더 구조)
            output_folder = os.path.join(base_dir, "CONVERTED", relative_dir)
            os.makedirs(output_folder, exist_ok=True)

            created_images = convert_pdf_to_png(original_path, output_folder, dpi=dpi)
            if created_images is None:
                logging.error(f"변환 실패: {original_path}")
                failed_files.append(original_path)
            else:
                logging.info(
                    f"변환 완료: {original_path} -> {len(created_images)} 개 이미지 생성"
                )

    log_failed_files(base_dir, failed_files)
    copy_failed_files(base_dir, failed_files)


def main():
    parser = argparse.ArgumentParser(description="PDF를 PNG로 변환하는 스크립트")
    parser.add_argument("base_directory", help="PDF 파일들이 위치한 최상위 폴더 경로")
    parser.add_argument("--dpi", type=int, default=200, help="출력 DPI (기본값: 200)")
    args = parser.parse_args()

    convert_pdfs_in_folder(args.base_directory, dpi=args.dpi)


if __name__ == "__main__":
    main()
