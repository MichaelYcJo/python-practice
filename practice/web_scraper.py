import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def scrape_website(url, max_links=10, keyword_filter=None):
    """웹사이트에서 제목과 모든 링크를 가져오는 웹 스크래퍼"""
    try:
        response = requests.get(url)
        response.raise_for_status()  # 요청이 실패하면 예외 발생

        # HTML 파싱
        soup = BeautifulSoup(response.text, "html.parser")

        # 페이지 제목 가져오기
        title = soup.title.string if soup.title else "제목 없음"
        print(f"\n📌 페이지 제목: {title}")

        # 모든 링크(a 태그) 추출 & 상대 경로 변환
        links = [urljoin(url, a["href"]) for a in soup.find_all("a", href=True)]

        # 키워드 필터링 적용
        if keyword_filter:
            links = [link for link in links if keyword_filter.lower() in link.lower()]

        # 링크 출력 개수 제한
        total_links = len(links)
        links = links[:max_links]  # 최대 개수 제한

        if links:
            print(f"\n🔗 페이지의 링크 목록 (최대 {max_links}개):")
            for link in links:
                print(f"- {link}")

            # 링크 저장 기능 추가
            with open("scraped_links.txt", "w", encoding="utf-8") as file:
                file.write("\n".join(links))
            print("\n💾 링크 목록이 'scraped_links.txt' 파일에 저장되었습니다!")

        else:
            print("❌ 조건에 맞는 링크가 없습니다.")

    except requests.exceptions.RequestException as e:
        print(f"⚠️ 요청 실패: {e}")


# 사용자 입력
url = input("🌐 크롤링할 웹사이트 URL을 입력하세요: ")
max_links = int(input("📌 출력할 최대 링크 개수를 입력하세요 (기본값: 10): ") or 10)
keyword_filter = (
    input(
        "🔍 특정 키워드가 포함된 링크만 찾을까요? (예: news, blog) [엔터 시 모든 링크 출력]: "
    ).strip()
    or None
)

# 실행
scrape_website(url, max_links, keyword_filter)
