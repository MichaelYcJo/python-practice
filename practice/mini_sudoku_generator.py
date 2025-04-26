import random
import copy


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


def is_completed(sudoku):
    """퍼즐이 완성됐는지 체크 (0이 없어야 함)"""
    for row in sudoku:
        if 0 in row:
            return False
    return True


def get_user_input():
    """사용자 입력 받기 (행, 열, 값)"""
    try:
        row = int(input("행 번호 (1~3): ").strip()) - 1
        col = int(input("열 번호 (1~3): ").strip()) - 1
        value = int(input("입력할 숫자 (1~9): ").strip())

        if not (0 <= row < 3 and 0 <= col < 3 and 1 <= value <= 9):
            print("❗ 범위를 벗어났습니다. 다시 입력하세요.")
            return None
        return row, col, value
    except ValueError:
        print("❗ 숫자로 정확히 입력해주세요.")
        return None


def main():
    # 스도쿠 생성
    sudoku = generate_sudoku()
    # 정답 복사 (deepcopy로 완전히 별개 객체)
    answer = copy.deepcopy(sudoku)

    try:
        holes = int(input("빈칸 개수 (0~5 사이 입력, 기본 2개): ").strip() or 2)
        if holes < 0 or holes > 5:
            print("❗ 범위 초과! 기본값(2개)로 진행합니다.")
            holes = 2
    except ValueError:
        print("❗ 숫자가 아닙니다. 기본값(2개)로 진행합니다.")
        holes = 2

    # 퍼즐에 구멍 뚫기
    make_holes(sudoku, holes)

    while True:
        print_sudoku(sudoku)

        if is_completed(sudoku):
            print("🎉 퍼즐을 완성했습니다! 축하합니다!")
            break

        user_input = get_user_input()
        if user_input:
            row, col, value = user_input
            if sudoku[row][col] == 0:
                if value == answer[row][col]:
                    sudoku[row][col] = value
                    print("✅ 정답입니다! 잘했어요.")
                else:
                    print("❌ 틀렸습니다. 다시 시도해보세요.")
            else:
                print("❗ 이 칸은 이미 채워져 있습니다.")


if __name__ == "__main__":
    main()
