def calculate(a, b, op):
    if op == "+":
        return a + b
    elif op == "-":
        return a - b
    elif op == "*":
        return a * b
    elif op == "/":
        return a / b if b != 0 else "0으로 나눌 수 없습니다."
    else:
        return "잘못된 연산자입니다."


if __name__ == "__main__":
    a = float(input("첫 번째 숫자를 입력하세요: "))
    op = input("연산자(+ - * /): ")
    b = float(input("두 번째 숫자를 입력하세요: "))
    result = calculate(a, b, op)
    print(f"결과: {result}")
