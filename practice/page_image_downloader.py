import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

SAVE_PATH = "website_images"

# 저장 폴더 생성
if not os.path.exists(SAVE_PATH):
    os.makedirs(SAVE_PATH)


def get_all_images(url):
    """웹사이트에서 모든 이미지 URL 가져오기"""
    response = requests.get(url)

    if response.status_code != 200:
        print("❌ 웹사이트를 불러올 수 없습니다.")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    image_urls = []

    for img_tag in soup.find_all("img"):
        img_url = img_tag.get("src")
        if img_url:
            full_url = urljoin(url, img_url)  # 상대경로 처리
            image_urls.append(full_url)

    return list(set(image_urls))  # 중복 제거


def download_image(image_url):
    """이미지 다운로드 및 저장"""
    filename = os.path.basename(urlparse(image_url).path)

    if not filename:  # 파일명이 없으면 건너뜀
        return

    save_path = os.path.join(SAVE_PATH, filename)

    if os.path.exists(save_path):
        print(f"⚠️ 이미 다운로드된 이미지: {filename}")
        return

    response = requests.get(image_url, stream=True)

    if response.status_code == 200:
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)

        print(f"✅ 이미지 다운로드 완료: {filename}")
    else:
        print(f"❌ 다운로드 실패: {filename}")


def main():
    """사용자 입력을 받아 이미지 다운로드"""
    website_url = input("🌐 이미지가 포함된 웹사이트 URL을 입력하세요: ").strip()
    image_urls = get_all_images(website_url)

    if not image_urls:
        print("⚠️ 다운로드할 이미지가 없습니다.")
        return

    print(
        f"\n🎨 총 {len(image_urls)}개의 이미지를 찾았습니다. 다운로드를 시작합니다...\n"
    )

    for img_url in image_urls:
        download_image(img_url)


# 실행
main()
