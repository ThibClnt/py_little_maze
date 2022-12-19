import random


def generate_maze(size=(20, 20)):
    maze = [[15 for _ in range(size[0])] for _ in range(size[1])]
    visited_cells = set()
    queue = []
    pos = (size[0] - 1, size[1] - 1)
    maze[0][0] = 23
    maze[-1][-1] = 45

    queue.append(pos)
    visited_cells.add(pos)

    while len(queue) > 0:

        direction_available = []
        if (pos[0] + 1, pos[1]) not in visited_cells and pos[0] + 1 < size[0]:
            direction_available.append(2)
        if (pos[0], pos[1] + 1) not in visited_cells and pos[1] + 1 < size[1]:
            direction_available.append(4)
        if (pos[0] - 1, pos[1]) not in visited_cells and pos[0] - 1 >= 0:
            direction_available.append(8)
        if (pos[0], pos[1] - 1) not in visited_cells and pos[1] - 1 >= 0:
            direction_available.append(1)

        if len(direction_available) > 0:
            direction = direction_available[random.randint(0, len(direction_available) - 1)]
            next_pos = pos
            opposite_direction = 0
            if direction == 1:
                next_pos = (pos[0], pos[1] - 1)
                opposite_direction = 4
            elif direction == 2:
                next_pos = (pos[0] + 1, pos[1])
                opposite_direction = 8
            elif direction == 4:
                next_pos = (pos[0], pos[1] + 1)
                opposite_direction = 1
            elif direction == 8:
                next_pos = (pos[0] - 1, pos[1])
                opposite_direction = 2

            maze[pos[1]][pos[0]] -= direction
            maze[next_pos[1]][next_pos[0]] -= opposite_direction
            visited_cells.add(next_pos)
            queue.append(next_pos)
            pos = next_pos
        else:
            pos = queue.pop()

    return maze


def resolve_maze(maze):
    return dfs(maze)


def dfs(maze):
    width, height = len(maze[0]), len(maze)
    stack = [(0, 0)]
    p = []
    visited_cells = set()

    while stack:
        x, y = stack.pop()
        visited_cells.add((x, y))

        if maze[y][x] & 32:
            return p + [(x, y)]

        if (x, y - 1) not in visited_cells and y - 1 >= 0 and not maze[y][x] & 1:
            stack.append((x, y - 1))
            p.append((x, y))

        elif (x + 1, y) not in visited_cells and x + 1 < width and not maze[y][x] & 2:
            stack.append((x + 1, y))
            p.append((x, y))

        elif (x, y + 1) not in visited_cells and y + 1 < height and not maze[y][x] & 4:
            stack.append((x, y + 1))
            p.append((x, y))

        elif (x - 1, y) not in visited_cells and x - 1 >= 0 and not maze[y][x] & 8:
            stack.append((x - 1, y))
            p.append((x, y))

        else:
            stack.append(p.pop())
