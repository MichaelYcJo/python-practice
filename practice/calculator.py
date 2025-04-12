def calculate(a: float, b: float, op: str):
    if op == "+":
        return a + b
    elif op == "-":
        return a - b
    elif op == "*":
        return a * b
    elif op == "/":
        if b == 0:
            raise ZeroDivisionError("0으로 나눌 수 없습니다.")
        return a / b
    else:
        raise ValueError("지원하지 않는 연산자입니다.")


def get_number(prompt: str) -> float:
    while True:
        try:
            value = input(prompt).strip()
            if value.lower() == "q":
                exit("👋 계산기를 종료합니다.")
            return float(value)
        except ValueError:
            print("❗ 숫자를 정확히 입력해주세요.")


def get_operator() -> str:
    while True:
        op = input("연산자 (+, -, *, /) 중 하나를 입력하세요: ").strip()
        if op in ["+", "-", "*", "/"]:
            return op
        else:
            print("❗ 잘못된 연산자입니다. 다시 입력해주세요.")


def main():
    print("=== 🧮 간단한 CLI 계산기 ===")
    print("※ 종료하려면 숫자 입력 시 'q' 입력")

    while True:
        a = get_number("첫 번째 숫자를 입력하세요: ")
        op = get_operator()
        b = get_number("두 번째 숫자를 입력하세요: ")

        try:
            result = calculate(a, b, op)
            print(f"👉 결과: {a} {op} {b} = {result}")
        except ZeroDivisionError as zde:
            print(f"❗ 오류: {zde}")
        except ValueError as ve:
            print(f"❗ 오류: {ve}")

        again = input("계속하시겠습니까? (y/n): ").strip().lower()
        if again != "y":
            print("👋 계산기를 종료합니다.")
            break


if __name__ == "__main__":
    main()
