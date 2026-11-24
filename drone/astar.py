"""Step 1 · A* search: shortest route on the 6x6 grid (notebook section 1)."""

import heapq
from collections.abc import Iterator

Cell = tuple[int, int]

# --- Map (row, col); row 0 is the top row ---
ROWS, COLS = 6, 6
START = (0, 0)                        # depot
GOAL = (5, 5)                         # customer
OBSTACLES = {(1, 1), (2, 3), (4, 4)}  # 3 buildings the drone cannot enter
# Moves: up, down, left, right. Each move costs 1 (one unit of battery).


def manhattan(a: Cell, b: Cell) -> int:
    """Manhattan distance |r1 - r2| + |c1 - c2| (admissible on a 4-direction grid)."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def neighbours(cell: Cell, obstacles: set[Cell]) -> Iterator[Cell]:
    """Yield the free cells one step up, down, left or right of `cell`."""
    r, c = cell
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:   # up, down, left, right
        nr, nc = r + dr, c + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS and (nr, nc) not in obstacles:
            yield (nr, nc)


def a_star(start: Cell, goal: Cell, obstacles: set[Cell],
           use_heuristic: bool = True) -> tuple[list[Cell] | None, list[Cell]]:
    """Return (path, expanded). path is None when no route exists.

    Expands the open node with the smallest f = g + h; ties go to the smaller h,
    then to the node pushed first. use_heuristic=False gives h = 0
    (uniform-cost search) for the node-count comparison.
    """
    h = (lambda n: manhattan(n, goal)) if use_heuristic else (lambda n: 0)
    counter = 0                                   # last tie-breaker: first pushed, first out
    frontier = [(h(start), h(start), counter, start)]   # (f, h, counter, node): equal f -> closer to goal first
    g = {start: 0}
    parent = {start: None}
    expanded = []
    while frontier:
        f, _, _, node = heapq.heappop(frontier)
        if node in expanded:
            continue                              # an older, worse copy of this node
        expanded.append(node)
        if node == goal:                          # goal test when expanded -> optimal
            path = []
            while node is not None:
                path.append(node)
                node = parent[node]
            return path[::-1], expanded
        for nb in neighbours(node, obstacles):
            new_g = g[node] + 1
            if nb not in g or new_g < g[nb]:
                g[nb] = new_g
                parent[nb] = node
                counter += 1
                heapq.heappush(frontier, (new_g + h(nb), h(nb), counter, nb))
    return None, expanded                         # no route exists


def draw_ascii(path: list[Cell] | None, obstacles: set[Cell]) -> None:
    """Print the grid: S start, G goal, # obstacle, * route, . free."""
    for r in range(ROWS):
        row = []
        for c in range(COLS):
            cell = (r, c)
            row.append("S" if cell == START else "G" if cell == GOAL else
                       "#" if cell in obstacles else "*" if path and cell in path else ".")
        print(" ".join(row))
