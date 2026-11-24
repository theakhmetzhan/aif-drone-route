"""Strict input validation for the Streamlit app (not part of the notebook)."""

import re

from .astar import COLS, GOAL, ROWS, START, Cell

MAX_OBSTACLES = 24      # the grid has 34 free cells besides start and goal
MAX_INPUT_CHARS = 200   # also enforced by the text field
_ITEM = re.compile(r"([0-9]{1,2}),([0-9]{1,2})")


class ObstacleError(ValueError):
    """Raised with a short, user-facing message. The message never echoes raw input."""


def parse_obstacles_strict(text: str) -> set[Cell]:
    """Parse "1,1 2,3 4,4" into cells. Every rule is checked; nothing is silently dropped."""
    if len(text) > MAX_INPUT_CHARS:
        raise ObstacleError(f"Too long · keep it under {MAX_INPUT_CHARS} characters.")
    items = text.split()
    if len(items) > MAX_OBSTACLES:
        raise ObstacleError(f"Too many obstacles · at most {MAX_OBSTACLES}.")
    cells: set[Cell] = set()
    for i, item in enumerate(items, start=1):
        m = _ITEM.fullmatch(item)
        if m is None:
            raise ObstacleError(f"Item {i} is not row,col · use digits like 1,1 2,3 4,4.")
        cell = (int(m.group(1)), int(m.group(2)))
        if not (0 <= cell[0] < ROWS and 0 <= cell[1] < COLS):
            raise ObstacleError(f"Item {i} ({cell[0]},{cell[1]}) is off the grid · rows and columns run 0 to 5.")
        if cell == START:
            raise ObstacleError(f"Item {i} (0,0) is the start · it cannot be an obstacle.")
        if cell == GOAL:
            raise ObstacleError(f"Item {i} (5,5) is the goal · it cannot be an obstacle.")
        if cell in cells:
            raise ObstacleError(f"Item {i} ({cell[0]},{cell[1]}) is listed twice.")
        cells.add(cell)
    return cells
