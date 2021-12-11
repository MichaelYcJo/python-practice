# https://docs.python.org/3.7/library/concurrent.futures.html#concurrent.futures.ThreadPoolExecutor
import time, threading, os, math
from concurrent.futures import ProcessPoolExecutor

PRIMES = [
    112272535095293,
    112582705942171,
    112272535095293,
    115280095190773,
    115797848077099,
    1099726899285419
    ]

def is_prime(num):
    print(f"{os.getpid()} process | {threading.get_ident()} thread, {num}")
    if num % 2 == 0:
        return False
    
    sqrt_n = int(math.floor(math.sqrt(num)))
    for i in range(3, sqrt_n + 1, 2):
        if num % i == 0:
            return False
    return True

def main():

    executor = ProcessPoolExecutor(max_workers=10)
    results = list(executor.map(is_prime, PRIMES))
    print(results)


if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print(end - start)  # 6.8