import random


def generate_sudoku():
    numbers = list(range(1, 10))  # 1~9 숫자 리스트
    random.shuffle(numbers)  # 랜덤으로 섞기

    sudoku = []
    for i in range(0, 9, 3):
        row = numbers[i : i + 3]
        sudoku.append(row)

    return sudoku


def print_sudoku(sudoku):
    print("\n=== 🧩 3x3 미니 스도쿠 ===")
    for row in sudoku:
        print(" | ".join(str(num) for num in row))
        print("-" * 11)


def main():
    sudoku = generate_sudoku()
    print_sudoku(sudoku)


if __name__ == "__main__":
    main()
