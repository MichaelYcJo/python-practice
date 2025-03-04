import pyshorteners


def shorten_url(long_url):
    """긴 URL을 단축하는 함수"""
    try:
        shortener = pyshorteners.Shortener()
        short_url = shortener.tinyurl.short(long_url)
        print(f"🔗 단축된 URL: {short_url}")
        return short_url
    except Exception as e:
        print(f"⚠️ URL 단축 중 오류 발생: {e}")


# 사용 예시
long_url = input("🌍 단축할 URL을 입력하세요: ")
shorten_url(long_url)
