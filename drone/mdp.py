"""Step 3 · MDP, one Bellman update from V0 = 0: fly now or wait? (notebook section 3)."""

# --- Rewards (MDP) ---
DELIVERY_REWARD = 20      # parcel delivered
CRASH_PENALTY = -20       # flying in strong wind: parcel lost
WAIT_COST = -2            # waiting delays the delivery
# R(Calm, Fly) = DELIVERY_REWARD - L   (each step of the A* route costs 1)


def reward_table(L: int) -> dict[tuple[str, str], int]:
    """R(s, a) for states Calm/Windy and actions Fly/Wait, given route length L."""
    return {
        ("Calm", "Fly"): DELIVERY_REWARD - L,
        ("Windy", "Fly"): CRASH_PENALTY,
        ("Calm", "Wait"): WAIT_COST,
        ("Windy", "Wait"): WAIT_COST,
    }


def choose_action(b: float, L: int) -> tuple[str, dict[str, float], dict[tuple[str, str], int]]:
    """One Bellman update with V0 = 0, so Q(s, a) = R(s, a), weighted by the belief b.

    Returns (action, Q, R). On an exact tie max() keeps the first key, Fly.
    """
    R = reward_table(L)
    belief = {"Calm": 1 - b, "Windy": b}
    Q = {a: sum(belief[s] * R[(s, a)] for s in belief) for a in ["Fly", "Wait"]}
    return max(Q, key=Q.get), Q, R


def break_even(L: int) -> float:
    """b* where Q(Fly) = Q(Wait): (1-b)(20-L) - 20b = -2  ->  b* = (22 - L) / (40 - L).

    Same expression as the notebook's b_star line.
    """
    R = reward_table(L)
    b_star = (R[("Calm", "Fly")] - WAIT_COST) / (R[("Calm", "Fly")] - CRASH_PENALTY)
    return b_star
