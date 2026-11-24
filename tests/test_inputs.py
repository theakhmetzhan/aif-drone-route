"""Strict obstacle validation used by the app."""

import pytest

from drone.inputs import MAX_OBSTACLES, ObstacleError, parse_obstacles_strict


def test_valid_inputs():
    assert parse_obstacles_strict("1,1 2,3 4,4") == {(1, 1), (2, 3), (4, 4)}
    assert parse_obstacles_strict("") == set()
    assert parse_obstacles_strict("  4,5   5,4 ") == {(4, 5), (5, 4)}


@pytest.mark.parametrize("text", [
    "1,1 2;3", "a,b", "1,1,1", "1, 1", "-1,0", "1.0,2", "６,1", "1,1 x",
    "<script>", "__import__('os')", "1,",
])
def test_malformed(text):
    with pytest.raises(ObstacleError, match="not row,col"):
        parse_obstacles_strict(text)


@pytest.mark.parametrize("text,msg", [
    ("6,0", "off the grid"), ("0,9", "off the grid"), ("12,3", "off the grid"),
    ("0,0", "start"), ("5,5", "goal"), ("1,1 1,1", "twice"),
])
def test_rule_violations(text, msg):
    with pytest.raises(ObstacleError, match=msg):
        parse_obstacles_strict(text)


def test_caps():
    many = " ".join(f"{r},{c}" for r in range(1, 5) for c in range(6))  # 24 cells
    assert len(parse_obstacles_strict(many)) == MAX_OBSTACLES
    with pytest.raises(ObstacleError, match="Too many"):
        parse_obstacles_strict(many + " 0,1")
    with pytest.raises(ObstacleError, match="Too long"):
        parse_obstacles_strict("1,1 " * 60)


def test_error_message_never_echoes_input():
    with pytest.raises(ObstacleError) as e:
        parse_obstacles_strict("<b>evil</b>")
    assert "evil" not in str(e.value) and "<" not in str(e.value)
