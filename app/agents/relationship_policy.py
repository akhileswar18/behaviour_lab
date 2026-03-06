from __future__ import annotations

from app.schemas.settings import get_settings


def _stance_from_scores(trust: float, affinity: float) -> str:
    combined = (trust + affinity) / 2
    if combined >= 0.35:
        return "allied"
    if combined <= -0.35:
        return "hostile"
    return "neutral"


def compute_relationship_delta(intent: str, emotional_tone: str) -> tuple[float, float]:
    settings = get_settings()
    positive = settings.relationship_positive_delta
    negative = settings.relationship_negative_delta

    positive_intents = {"propose", "cooperate"}
    negative_intents = {"warn", "avoid"}
    supportive_tones = {"supportive"}
    hard_tones = {"assertive", "guarded"}

    trust_delta = 0.0
    affinity_delta = 0.0

    if intent in positive_intents:
        trust_delta += positive
        affinity_delta += positive
    elif intent in negative_intents:
        trust_delta -= negative
        affinity_delta -= negative

    if emotional_tone in supportive_tones:
        affinity_delta += positive / 2
    elif emotional_tone in hard_tones:
        affinity_delta -= negative / 2

    return trust_delta, affinity_delta


def derive_stance(trust: float, affinity: float) -> str:
    return _stance_from_scores(trust, affinity)
