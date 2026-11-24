"""Property checks on top of the notebook's fixed cases."""

import random
from collections import deque

import pytest

from drone.astar import COLS, GOAL, ROWS, START, a_star, manhattan, neighbours
from drone.astar import OBSTACLES
from drone.bayes import bayes, wind_belief
from drone.mdp import break_even, choose_action
from drone.pipeline import run_mission

FREE = [(r, c) for r in range(ROWS) for c in range(COLS) if (r, c) not in (START, GOAL)]


def random_grids(n=200, seed=1303):
    rng = random.Random(seed)
    for _ in range(n):
        yield set(rng.sample(FREE, rng.randint(0, 14)))


def grid_steps(cell, obstacles):
    """Independent neighbour generator for the BFS ground truth (does not reuse drone.astar)."""
    r, c = cell
    for nr, nc in ((r + 1, c), (r, c + 1), (r - 1, c), (r, c - 1)):
        if nr in range(6) and nc in range(6) and (nr, nc) not in obstacles:
            yield nr, nc


def bfs_distances(source, obstacles):
    dist = {source: 0}
    queue = deque([source])
    while queue:
        cell = queue.popleft()
        for nb in grid_steps(cell, obstacles):
            if nb not in dist:
                dist[nb] = dist[cell] + 1
                queue.append(nb)
    return dist


def test_astar_matches_uniform_cost_on_200_random_grids():
    reachable = 0
    for obs in random_grids():
        p1, e1 = a_star(START, GOAL, obs)
        p2, e2 = a_star(START, GOAL, obs, use_heuristic=False)
        assert (p1 is None) == (p2 is None)
        if p1 is not None:
            reachable += 1
            assert len(p1) == len(p2)
            assert len(p1) - 1 == bfs_distances(START, obs)[GOAL]   # optimal
            assert len(e1) <= len(e2)                                # never more work
    assert reachable > 100                                           # the sample is meaningful


def test_route_is_valid_walk():
    for obs in random_grids(50, seed=7):
        path, _ = a_star(START, GOAL, obs)
        if path is None:
            continue
        assert path[0] == START and path[-1] == GOAL
        for a, b in zip(path, path[1:]):
            assert b in set(neighbours(a, obs))


def test_manhattan_is_admissible():
    for obs in random_grids(60, seed=42):
        dist = bfs_distances(GOAL, obs)          # true distance of every cell to the goal
        for cell, d in dist.items():
            assert manhattan(cell, GOAL) <= d


@pytest.mark.parametrize("prior", [0.0, 0.01, 0.3, 0.5, 0.99, 1.0])
@pytest.mark.parametrize("p_w,p_c", [(0.8, 0.2), (0.5, 0.5), (0.99, 0.01), (0.3, 0.7)])
@pytest.mark.parametrize("alert", [True, False])
def test_posteriors_sum_to_one(prior, p_w, p_c, alert):
    b_windy = wind_belief(prior, p_w, p_c, alert)
    if alert:
        b_calm = bayes(1 - prior, p_c, p_w)
    else:
        b_calm = bayes(1 - prior, 1 - p_c, 1 - p_w)
    assert 0.0 <= b_windy <= 1.0
    assert b_windy + b_calm == pytest.approx(1.0)


def test_break_even_formula():
    assert break_even(10) == pytest.approx(0.40)
    for L in range(0, 23):
        assert break_even(L) == pytest.approx((22 - L) / (40 - L))


@pytest.mark.parametrize("L", [8, 10, 12, 16, 20, 21])
def test_decision_flips_exactly_at_break_even(L):
    b_star = break_even(L)
    eps = 1e-9
    _, q, _ = choose_action(b_star, L)
    assert q["Fly"] == pytest.approx(q["Wait"])
    assert choose_action(b_star - eps, L)[0] == "Fly"
    assert choose_action(b_star + eps, L)[0] == "Wait"


def test_no_route_always_waits():
    for prior in (0.0, 0.3, 1.0):
        for alert in (True, False):
            m = run_mission(obstacles={(4, 5), (5, 4)}, prior=prior, alert=alert)
            assert m["path"] is None and m["L"] is None
            assert m["action"].startswith("Wait")


def test_exact_tie_fly_wins():
    """Main map, prior 0.40, both sensor rates 0.50: b = b* = 0.40 and both Q = -2.

    max() keeps the first key on a tie, so Fly wins, same as the notebook.
    """
    m = run_mission(obstacles=OBSTACLES, prior=0.40, p_alert_windy=0.50, p_alert_calm=0.50, alert=True)
    assert m["L"] == 10
    assert m["b"] == pytest.approx(break_even(10)) == pytest.approx(0.40)
    assert m["Q"]["Fly"] == pytest.approx(-2.0) and m["Q"]["Wait"] == -2
    assert m["action"] == "Fly"


def test_bayes_rejects_zero_evidence():
    with pytest.raises(ValueError, match="evidence"):
        bayes(1.0, 0.0, 0.5)
    with pytest.raises(ValueError, match="evidence"):
        wind_belief(0.0, 0.8, 1.0, False)
