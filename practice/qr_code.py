import qrcode
import time
from PIL import Image


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


# 실행
generate_qr()
