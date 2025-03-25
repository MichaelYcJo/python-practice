from PyPDF2 import PdfMerger, PdfReader
import os


"""
여러 개의 PDF 파일을 순서대로 하나로 병합
사용자가 병합할 파일들을 직접 순서대로 입력
병합된 결과는 merged.pdf로 저장
외부 서버 없이 로컬에서 Python 표준 라이브러리 기반으로 실행
개선된 버전 예시: 자동 폴더 스캔 + 정렬 + 진행률 표시
"""


def is_valid_pdf(file_path):
    try:
        PdfReader(file_path)
        return True
    except:
        return False


def generate_unique_filename(base_path):
    """중복된 파일명이 있다면 숫자 붙이기"""
    if not os.path.exists(base_path):
        return base_path

    filename, ext = os.path.splitext(base_path)
    counter = 1
    while True:
        new_path = f"{filename}_{counter}{ext}"
        if not os.path.exists(new_path):
            return new_path
        counter += 1


def merge_pdfs(pdf_paths, output_path="merged.pdf"):
    merger = PdfMerger()
    error_files = []

    total = len(pdf_paths)
    for idx, pdf in enumerate(pdf_paths, 1):
        if not os.path.exists(pdf):
            print(f"❌ 파일 없음: {pdf}")
            error_files.append(pdf)
            continue

        if not is_valid_pdf(pdf):
            print(f"⚠️ 유효하지 않은 PDF: {pdf}")
            error_files.append(pdf)
            continue

        try:
            merger.append(pdf)
            page_count = len(PdfReader(pdf).pages)
            print(
                f"✅ ({idx}/{total}) 병합 추가됨: {os.path.basename(pdf)} ({page_count} pages)"
            )
        except Exception as e:
            print(f"⚠️ 병합 실패: {pdf} ({e})")
            error_files.append(pdf)

    output_path = generate_unique_filename(output_path)
    merger.write(output_path)
    merger.close()
    print(f"\n📎 병합 완료! 👉 저장 위치: {output_path}")

    if error_files:
        with open("error_log.txt", "w", encoding="utf-8") as f:
            f.writelines([line + "\n" for line in error_files])
        print(f"📄 오류 파일 로그 저장됨: error_log.txt")
