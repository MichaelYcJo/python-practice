import os
from PyPDF2 import PdfMerger

"""
✅ 여러 개의 PDF 파일을 순서대로 하나로 병합
✅ 사용자가 병합할 파일들을 직접 순서대로 입력
✅ 병합된 결과는 merged.pdf로 저장
✅ 외부 서버 없이 로컬에서 Python 표준 라이브러리 기반으로 실행
"""


def merge_pdfs(pdf_paths, output_path="merged.pdf"):
    merger = PdfMerger()

    for pdf in pdf_paths:
        if not os.path.exists(pdf):
            print(f"❌ 파일 없음: {pdf}")
            continue

        try:
            merger.append(pdf)
            print(f"✅ 병합 추가됨: {pdf}")
        except Exception as e:
            print(f"⚠️ 병합 실패: {pdf} ({e})")

    merger.write(output_path)
    merger.close()
    print(f"\n📎 병합 완료! 👉 저장 위치: {output_path}")


def main():
    print("📄 병합할 PDF 파일 경로를 입력하세요 (띄어쓰기로 구분)")
    print("예: file1.pdf file2.pdf file3.pdf")
    pdf_input = input("📝 PDF 파일 목록: ").strip()

    pdf_files = pdf_input.split()
    if not pdf_files:
        print("❌ PDF 파일을 입력하지 않았습니다.")
        return

    output_name = (
        input("💾 결과 파일명을 입력하세요 (기본: merged.pdf): ").strip()
        or "merged.pdf"
    )
    merge_pdfs(pdf_files, output_path=output_name)


# 실행
if __name__ == "__main__":
    main()
