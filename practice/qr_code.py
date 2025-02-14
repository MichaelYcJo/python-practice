import qrcode


def generate_qr():
    """QR 코드 생성"""
    text = input("🔗 QR 코드에 넣을 텍스트(예: 웹사이트 URL, 메시지)를 입력하세요: ")

    # QR 코드 생성
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    # 이미지 생성 및 저장
    img = qr.make_image(fill="black", back_color="white")
    filename = "qrcode.png"
    img.save(filename)

    print(f"✅ QR 코드가 '{filename}' 파일로 저장되었습니다!")
    print("📷 카메라로 스캔하면 입력한 정보를 확인할 수 있습니다.")


# 실행
generate_qr()
