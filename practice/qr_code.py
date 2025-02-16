import qrcode
import time
import os
from PIL import Image
from pyzbar.pyzbar import decode

"""
QR 코드 생성 기능 (색상 & 배경색 사용자 지정)
QR 코드 저장 시 자동 파일명 설정 (qrcode_YYYYMMDD_HHMMSS.png)
QR 코드 즉시 표시 기능 추가
QR 코드 읽기(스캔) 기능 추가 (파일 자동 탐색 후 QR 코드 데이터 출력)
CLI에서 기능 선택 가능 (QR 코드 생성 / 스캔 / 종료)
"""


def generate_qr():
    """QR 코드 생성"""
    text = input("🔗 QR 코드에 넣을 텍스트(예: 웹사이트 URL, 메시지)를 입력하세요: ")

    # 사용자 지정 색상 입력
    fill_color = (
        input("🎨 QR 코드 색상을 입력하세요 (예: black, blue, red): ").strip()
        or "black"
    )
    back_color = (
        input("🎨 배경 색상을 입력하세요 (예: white, yellow, green): ").strip()
        or "white"
    )

    # QR 코드 설정
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    # 사용자 지정 색상 적용
    img = qr.make_image(fill_color=fill_color, back_color=back_color)

    # 파일명 자동 생성 (시간 기반)
    filename = f"qrcode_{time.strftime('%Y%m%d_%H%M%S')}.png"
    img.save(filename)

    # QR 코드 즉시 표시
    img.show()

    print(f"✅ QR 코드가 '{filename}' 파일로 저장되었습니다!")
    print("📷 카메라로 스캔하면 입력한 정보를 확인할 수 있습니다.")


def scan_qr():
    """QR 코드 이미지 스캔 (디코딩)"""
    # 현재 디렉토리에서 가장 최근 QR 코드 파일 찾기
    qr_files = sorted(
        [f for f in os.listdir() if f.startswith("qrcode_") and f.endswith(".png")],
        reverse=True,
    )

    if not qr_files:
        print("❌ QR 코드 이미지 파일을 찾을 수 없습니다!")
        return

    latest_qr_file = qr_files[0]
    print(f"🔍 '{latest_qr_file}' 파일에서 QR 코드 정보를 읽는 중...")

    # QR 코드 이미지 디코딩
    img = Image.open(latest_qr_file)
    decoded_data = decode(img)

    if decoded_data:
        for obj in decoded_data:
            print(f"📄 QR 코드 데이터: {obj.data.decode('utf-8')}")
    else:
        print("⚠️ QR 코드가 인식되지 않았습니다.")


def main():
    """QR 코드 생성 or 스캔 선택"""
    while True:
        print("\n📱 QR 코드 프로그램")
        print("1. QR 코드 생성")
        print("2. QR 코드 읽기 (스캔)")
        print("3. 종료")

        choice = input("👉 원하는 기능을 선택하세요: ")

        if choice == "1":
            generate_qr()
        elif choice == "2":
            scan_qr()
        elif choice == "3":
            print("👋 프로그램을 종료합니다!")
            break
        else:
            print("⚠️ 올바른 선택지를 입력하세요.\n")


# 실행
main()
