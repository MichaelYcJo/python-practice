import random


def generate_maze(n):
    maze = [["#"] * (n * 2 + 1) for _ in range(n * 2 + 1)]

    def carve(x, y):
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < n and 0 <= ny < n and maze[ny * 2 + 1][nx * 2 + 1] == "#":
                maze[y * 2 + 1 + dy][x * 2 + 1 + dx] = " "
                maze[ny * 2 + 1][nx * 2 + 1] = " "
                carve(nx, ny)

    # 시작점
    maze[1][1] = " "
    carve(0, 0)

    # 입구/출구 열기
    maze[1][0] = " "  # Start
    maze[-2][-1] = " "  # End

    return maze


def print_maze(maze):
    for row in maze:
        print("".join(row))


def main():
    print("🎲 랜덤 미로 생성기")
    size = input("🧱 미로 크기를 입력하세요 (예: 10): ").strip()
    if not size.isdigit():
        print("❌ 숫자를 입력해주세요.")
        return

    n = int(size)
    maze = generate_maze(n)
    print("\n🌀 생성된 미로:")
    print_maze(maze)


# 실행
if __name__ == "__main__":
    main()
