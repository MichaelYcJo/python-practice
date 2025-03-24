import os
from PyPDF2 import PdfMerger

"""
여러 개의 PDF 파일을 순서대로 하나로 병합
사용자가 병합할 파일들을 직접 순서대로 입력
병합된 결과는 merged.pdf로 저장
외부 서버 없이 로컬에서 Python 표준 라이브러리 기반으로 실행
개선된 버전 예시: 자동 폴더 스캔 + 정렬 + 진행률 표시
"""


def get_pdf_files_from_folder(folder_path):
    """폴더 내 모든 유효한 PDF 파일 가져오기"""
    files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.lower().endswith(".pdf")
    ]
    return sorted(files)  # 기본은 이름순 정렬


def merge_pdfs(pdf_paths, output_path="merged.pdf"):
    merger = PdfMerger()

    total = len(pdf_paths)
    for idx, pdf in enumerate(pdf_paths, 1):
        if not os.path.exists(pdf):
            print(f"❌ 파일 없음: {pdf}")
            continue

        try:
            merger.append(pdf)
            print(f"✅ ({idx}/{total}) 병합 추가됨: {os.path.basename(pdf)}")
        except Exception as e:
            print(f"⚠️ 병합 실패: {pdf} ({e})")

    merger.write(output_path)
    merger.close()
    print(f"\n📎 병합 완료! 👉 저장 위치: {output_path}")


def main():
    print("📁 병합할 PDF들이 있는 폴더 경로를 입력하세요:")
    folder_path = input("📂 폴더 경로: ").strip()

    if not os.path.isdir(folder_path):
        print("❌ 유효한 폴더가 아닙니다.")
        return

    pdf_files = get_pdf_files_from_folder(folder_path)
    if not pdf_files:
        print("❌ PDF 파일이 존재하지 않습니다.")
        return

    print("\n📑 병합할 파일 목록:")
    for f in pdf_files:
        print(" -", os.path.basename(f))

    custom_name = (
        input("\n💾 결과 파일명을 입력하세요 (기본: merged.pdf): ").strip()
        or "merged.pdf"
    )
    output_path = os.path.join(folder_path, custom_name)

    merge_pdfs(pdf_files, output_path)


if __name__ == "__main__":
    main()
