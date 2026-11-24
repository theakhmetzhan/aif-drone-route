"""The notebook's own test cases (section 4), unchanged in substance."""

from drone.astar import GOAL, OBSTACLES, START, a_star
from drone.pipeline import parse_obstacles, run_mission

WALL = {(1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5)}


def test_main_scenario_alert_waits():
    m = run_mission()
    assert m["L"] == 10                       # Manhattan distance 5 + 5, no detour
    assert round(m["b"], 4) == 0.6316         # 0.24 / 0.38
    assert round(m["Q"]["Fly"], 2) == -8.95 and m["Q"]["Wait"] == -2
    assert m["action"] == "Wait"


def test_no_alert_flies():
    m2 = run_mission(alert=False)
    assert m2["L"] == 10
    assert round(m2["b"], 4) == 0.0968        # 0.06 / 0.62
    assert round(m2["Q"]["Fly"], 2) == 7.10
    assert m2["action"] == "Fly"


def test_two_long_walls_no_alert():
    m2 = run_mission(alert=False)
    m3 = run_mission(obstacles=WALL, alert=False)
    assert m3["L"] == 20                      # right, down, all the way left, down, right
    assert round(m3["Q"]["Fly"], 2) == -1.94
    assert m3["action"] == "Fly"              # only just: -1.94 > -2
    assert m3["Q"]["Fly"] < m2["Q"]["Fly"]    # same weather, longer route -> flying is worth less


def test_goal_walled_in_waits():
    m4 = run_mission(obstacles={(4, 5), (5, 4)})
    assert m4["path"] is None and m4["action"].startswith("Wait")


def test_astar_same_length_as_uninformed_on_notebook_maps():
    for obs in [OBSTACLES, WALL]:
        p1, _ = a_star(START, GOAL, obs)
        p2, _ = a_star(START, GOAL, obs, use_heuristic=False)
        assert len(p1) == len(p2)


def test_node_counts_11_vs_33():
    _, expanded = a_star(START, GOAL, OBSTACLES)
    _, expanded_ucs = a_star(START, GOAL, OBSTACLES, use_heuristic=False)
    assert len(expanded) == 11
    assert len(expanded_ucs) == 33


def test_notebook_parser_is_lenient():
    assert parse_obstacles("1,1 2,3 4,4") == OBSTACLES
    assert parse_obstacles("0,0 5,5 9,9 1,1") == {(1, 1)}
