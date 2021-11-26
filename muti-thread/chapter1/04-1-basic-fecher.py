# https://2.python-requests.org/en/master/user/advanced/#id1
# pip install requests

import requests
import time


def fetcher(session, url):
    with session.get(url) as response:
        return response.text


def main():
    urls = ["https://naver.com", "https://google.com", "https://instagram.com"] * 10
    
    
    '''
    with을 사용하지않으면
    session = requests.Session()
    session.get(url)
    session.close()
    이렇게 열고닫음을 명시해주어서 핸들링 해야한다.
    
    with을 사용하면
    
    with requests.Sesstion() as session:
    session.get(url)
    로 축약가능하다. 즉 with을 사용하므로 세션을 열고 닫을 수 있게되는 것이다. 
    
    '''

    with requests.Session() as session:
        result = [fetcher(session, url) for url in urls]
        print(result)


if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print(end - start)  # 12