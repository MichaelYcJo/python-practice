def io_bound_func():
    print("number?")
    input_value = input()
    return int(input_value) + 100


if __name__ == "__main__":
    result = io_bound_func()
    print(result)