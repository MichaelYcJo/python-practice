# https://docs.aiohttp.org/en/stable/
# pip install aiohttp~=3.7.3


import asyncio, aiohttp, os, threading, time
import sys

# async 를통해 fetcher 자체를 코루틴화시킴
async def fetcher(session, url):
    print(f"{os.getpid()} process | {threading.get_ident()} url: {url}")
    async with session.get(url) as response:
        return await response.text()


async def main():
    urls = ["https://naver.com", "https://google.com", "https://instagram.com"] * 10

    # doc에 따른 session 사용
    async with aiohttp.ClientSession() as session:
        # * unpacking -> 각각의 원소들이 , 단위로 끊겨서 인자로 전달됨
        # 리스트 앞에 언패킹 참조 https://dojang.io/mod/page/view.php?id=2345
        result = await asyncio.gather(*[fetcher(session, url) for url in urls])
        print('흠', *[fetcher(session, url) for url in urls])
        print('그냥', [fetcher(session, url) for url in urls])
        #print(result)


if __name__ == "__main__":
    py_ver = int(f"{sys.version_info.major}{sys.version_info.minor}")
    if py_ver > 37 and sys.platform.startswith('win'):
  	    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    start = time.time()
    asyncio.run(main())
    end = time.time()
    print(end - start)  # 4.8