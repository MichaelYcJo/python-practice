# https://docs.aiohttp.org/en/stable/
# pip install aiohttp~=3.7.3


import aiohttp
import time
import asyncio


# async 를통해 fetcher 자체를 코루틴화시킴
async def fetcher(session, url):
    async with session.get(url) as response:
        return await response.text()


async def main():
    urls = ["https://naver.com", "https://google.com", "https://instagram.com"] * 10

    # doc에 따른 session 사용
    async with aiohttp.ClientSession() as session:
        # * unpacking -> 각각의 원소들이 , 단위로 끊겨서 인자로 전달됨
        result = await asyncio.gather(*[fetcher(session, url) for url in urls])
        print(result)


if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    end = time.time()
    print(end - start)  # 4.8