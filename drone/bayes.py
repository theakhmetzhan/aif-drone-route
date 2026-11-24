"""Step 2 · Bayesian inference: is it windy? (notebook section 2)."""

# --- Weather sensor (Bayes) ---
PRIOR_WINDY = 0.30        # P(Windy) before any alert
P_ALERT_IF_WINDY = 0.80   # P(alert | Windy): the sensor catches wind 80% of the time
P_ALERT_IF_CALM = 0.20    # P(alert | Calm): false alarm rate
ALERT_RECEIVED = True     # the drone did receive an alert


def bayes(prior: float, p_obs_if_true: float, p_obs_if_false: float) -> float:
    """Posterior P(true | observation) after one observation."""
    # Posterior P(true | observation) after one observation.
    score_true = prior * p_obs_if_true
    score_false = (1 - prior) * p_obs_if_false
    return score_true / (score_true + score_false)


def wind_belief(prior: float, p_alert_windy: float, p_alert_calm: float, alert: bool) -> float:
    """b = P(Windy | alert), or P(Windy | no alert) when alert is False."""
    if alert:
        return bayes(prior, p_alert_windy, p_alert_calm)
    return bayes(prior, 1 - p_alert_windy, 1 - p_alert_calm)   # "no alert" observation
