import random


def generate_sudoku():
    """1~9까지 중복 없이 섞어서 3x3 스도쿠 생성"""
    numbers = list(range(1, 9 + 1))
    random.shuffle(numbers)

    sudoku = []
    for i in range(0, 9, 3):
        row = numbers[i : i + 3]
        sudoku.append(row)

    return sudoku


def make_holes(sudoku, holes=2):
    """랜덤으로 holes 개수만큼 빈칸(0) 만들기"""
    positions = [(i, j) for i in range(3) for j in range(3)]
    random.shuffle(positions)

    for _ in range(holes):
        if positions:
            i, j = positions.pop()
            sudoku[i][j] = 0


def print_sudoku(sudoku):
    """스도쿠 예쁘게 출력하기"""
    print("\n=== 🧩 3x3 미니 스도쿠 ===")
    for row in sudoku:
        print(" | ".join(str(num) if num != 0 else " " for num in row))
        print("-" * 11)


def main():
    sudoku = generate_sudoku()

    try:
        holes = int(input("빈칸 개수 (0~5 사이 입력, 기본 2개): ").strip() or 2)
        if holes < 0 or holes > 5:
            print("❗ 범위 초과! 기본값(2개)로 진행합니다.")
            holes = 2
    except ValueError:
        print("❗ 숫자가 아닙니다. 기본값(2개)로 진행합니다.")
        holes = 2

    make_holes(sudoku, holes)
    print_sudoku(sudoku)


if __name__ == "__main__":
    main()
