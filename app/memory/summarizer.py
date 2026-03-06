def score_salience(base: float, event_type: str) -> float:
    bump = 0.0
    if event_type == "message":
        bump = 0.2
    elif event_type == "decision":
        bump = 0.1
    return min(1.0, max(0.0, base + bump))
