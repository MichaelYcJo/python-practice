import pyshorteners
import validators
import pyperclip
import qrcode
import os

"""
QR 코드 생성 + URL 중복 체크 + 목록 조회 기능 추가
"""

STORAGE_FILE = "shortened_urls.txt"


def load_shortened_urls():
    """저장된 단축 URL 목록 불러오기"""
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "r", encoding="utf-8") as file:
            return dict(
                line.strip().split(" -> ")
                for line in file.readlines()
                if " -> " in line
            )
    return {}


def save_shortened_url(long_url, short_url):
    """단축 URL 저장"""
    with open(STORAGE_FILE, "a", encoding="utf-8") as file:
        file.write(f"{long_url} -> {short_url}\n")


def generate_qr_code(url):
    """QR 코드 생성"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")
    img.show()
    qr_filename = (
        f"qr_{url.replace('https://', '').replace('http://', '').replace('/', '_')}.png"
    )
    img.save(qr_filename)
    print(f"📸 QR 코드가 생성되었습니다: {qr_filename}")


def shorten_url(long_url):
    """긴 URL을 단축하는 함수"""

    # URL 형식 검증
    if not validators.url(long_url):
        print("❌ 오류: 올바른 URL 형식이 아닙니다.")
        return None

    # 기존 단축 URL 확인 (중복 방지)
    shortened_urls = load_shortened_urls()
    if long_url in shortened_urls:
        short_url = shortened_urls[long_url]
        print(f"🔗 이미 단축된 URL입니다: {short_url}")
    else:
        try:
            shortener = pyshorteners.Shortener()
            short_url = shortener.tinyurl.short(long_url)

            # 파일에 저장
            save_shortened_url(long_url, short_url)

            print(f"\n🔗 단축된 URL: {short_url}")

        except Exception as e:
            print(f"⚠️ URL 단축 중 오류 발생: {e}")
            return None

    # 클립보드에 자동 복사
    pyperclip.copy(short_url)
    print("📋 단축된 URL이 클립보드에 복사되었습니다!")

    # QR 코드 생성
    generate_qr_code(short_url)

    return short_url


def show_saved_urls():
    """저장된 단축 URL 목록 출력"""
    shortened_urls = load_shortened_urls()

    if not shortened_urls:
        print("📭 저장된 단축 URL이 없습니다.")
        return

    print("\n📜 저장된 단축 URL 목록:")
    for long_url, short_url in shortened_urls.items():
        print(f"🔗 {long_url} -> {short_url}")


# 실행
while True:
    print("\n🔗 URL 단축기")
    print("1. URL 단축")
    print("2. 저장된 단축 URL 목록 보기")
    print("3. 종료")

    choice = input("👉 원하는 기능을 선택하세요: ").strip()

    if choice == "1":
        long_url = input("🌍 단축할 URL을 입력하세요: ").strip()
        shorten_url(long_url)
    elif choice == "2":
        show_saved_urls()
    elif choice == "3":
        print("👋 프로그램을 종료합니다!")
        break
    else:
        print("⚠️ 올바른 선택지를 입력하세요.\n")
