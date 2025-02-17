import requests
from bs4 import BeautifulSoup


def scrape_website(url):
    """웹사이트에서 제목과 모든 링크를 가져오는 웹 스크래퍼"""
    try:
        response = requests.get(url)
        response.raise_for_status()  # 요청이 실패하면 예외 발생

        # HTML 파싱
        soup = BeautifulSoup(response.text, "html.parser")

        # 페이지 제목 가져오기
        title = soup.title.string if soup.title else "제목 없음"
        print(f"\n📌 페이지 제목: {title}")

        # 모든 링크(a 태그) 추출
        links = [a["href"] for a in soup.find_all("a", href=True)]
        if links:
            print("\n🔗 페이지의 모든 링크:")
            for link in links[:10]:  # 처음 10개만 출력
                print(f"- {link}")
        else:
            print("❌ 링크가 없습니다.")

    except requests.exceptions.RequestException as e:
        print(f"⚠️ 요청 실패: {e}")


# 사용 예시
url = input("🌐 크롤링할 웹사이트 URL을 입력하세요: ")
scrape_website(url)
