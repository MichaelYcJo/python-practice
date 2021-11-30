import time, os, threading


nums = [50, 63, 32]

def cpu_bound_func(num):
    print(f"{os.getpid()} process | {threading.get_ident()} thread")
    total = 1
    numbers = range(1, num)
    for i in numbers:
        for j in numbers:
            for k in numbers:
                total *= i * j * k
                
    return total


def main():
    for num in nums:
        results = [cpu_bound_func(num), for num in nums]
        print(results)


if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    print(end - start)
    
    
    
    