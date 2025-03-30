def solve_maze(maze):
    h, w = len(maze), len(maze[0])
    visited = [[False] * w for _ in range(h)]
    path = []

    def dfs(x, y):
        if not (0 <= x < w and 0 <= y < h):
            return False
        if maze[y][x] == "#" or visited[y][x]:
            return False
        if (x, y) == (w - 2, h - 2):  # 도착점
            path.append((x, y))
            return True

        visited[y][x] = True
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            if dfs(x + dx, y + dy):
                path.append((x, y))
                return True
        return False

    dfs(1, 1)  # 시작점
    for x, y in path:
        if maze[y][x] == " ":
            maze[y][x] = "."
