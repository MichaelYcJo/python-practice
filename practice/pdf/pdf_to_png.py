import fitz  # PyMuPDF
import os


def pdf_to_single_png(pdf_path, output_path="./output.png", dpi=150, target_size=None):
    """
    PDF를 단일 PNG 이미지로 변환합니다.

    Args:
        pdf_path: PDF 파일 경로
        output_path: 출력 PNG 파일 경로
        dpi: 이미지 해상도 (기본값: 150)
        target_size: (width, height) 튜플로 지정된 크기 (선택사항)
    """
    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    print(f"📄 PDF 페이지 수: {total_pages}")
    print(f"🎯 변환 설정: DPI={dpi}")
    if target_size:
        print(f"📏 목표 크기: {target_size[0]} x {target_size[1]}")

    # 첫 번째 페이지만 PNG로 변환
    page = doc[0]

    # 페이지를 이미지로 렌더링
    if target_size:
        # 지정된 크기로 변환
        mat = fitz.Matrix(
            target_size[0] / page.rect.width, target_size[1] / page.rect.height
        )
        pix = page.get_pixmap(matrix=mat)
    else:
        # DPI 기반으로 변환
        mat = fitz.Matrix(dpi / 72, dpi / 72)  # 72는 기본 DPI
        pix = page.get_pixmap(matrix=mat)

    # PNG 파일로 저장 (품질 100%)
    pix.save(output_path)

    print(f"✅ Page 1 → {output_path} ({pix.width} x {pix.height})")
    print(f"🎉 변환 완료! PNG 파일이 저장되었습니다: {output_path}")

    doc.close()
    return output_path


# 사용 예
if __name__ == "__main__":
    # PDF를 단일 PNG로 변환 (품질 100%)
    print("=" * 50)
    print("PDF → 단일 PNG 변환 시작")
    print("=" * 50)
    pdf_to_single_png("./6test.pdf", "./output.png", dpi=150)
