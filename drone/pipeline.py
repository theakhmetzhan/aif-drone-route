"""Whole pipeline: A* -> Bayes -> MDP (notebook sections 4 and 5)."""

from .astar import COLS, GOAL, OBSTACLES, ROWS, START, Cell, a_star
from .bayes import ALERT_RECEIVED, P_ALERT_IF_CALM, P_ALERT_IF_WINDY, PRIOR_WINDY, wind_belief
from .mdp import choose_action


def run_mission(obstacles=OBSTACLES, prior=PRIOR_WINDY, p_alert_windy=P_ALERT_IF_WINDY,
                p_alert_calm=P_ALERT_IF_CALM, alert=ALERT_RECEIVED) -> dict:
    """Chain the three steps. With no route the drone waits and L, b, Q are None."""
    path, expanded = a_star(START, GOAL, obstacles)
    if path is None:
        return {"path": None, "L": None, "b": None, "action": "Wait (no route)", "Q": None}
    L = len(path) - 1
    b = wind_belief(prior, p_alert_windy, p_alert_calm, alert)
    action, Q, _ = choose_action(b, L)
    return {"path": path, "L": L, "expanded": len(expanded), "b": b, "action": action, "Q": Q}


def parse_obstacles(text: str) -> set[Cell]:
    """The notebook's lenient parser: drops off-grid cells and the start/goal.

    Raises ValueError on malformed items. The app uses drone.inputs.parse_obstacles_strict.
    """
    cells = set()
    for part in text.split():
        r, c = part.split(",")
        cell = (int(r), int(c))
        if cell not in (START, GOAL) and 0 <= cell[0] < ROWS and 0 <= cell[1] < COLS:
            cells.add(cell)
    return cells
