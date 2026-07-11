import os
from models import NewsAnalysis, TradingDecision


def make_decision(analysis: NewsAnalysis) -> TradingDecision:
    min_confidence = int(os.getenv("MIN_CONFIDENCE_TO_TRADE", "70"))
    min_score = int(os.getenv("MIN_ABS_SCORE_TO_TRADE", "35"))

    blockers = [
        not analysis.is_relevant_to_eth,
        analysis.is_fake_or_manipulative,
        analysis.is_duplicate_or_old,
        analysis.confidence < min_confidence,
        analysis.importance < 40,
        abs(analysis.score) < min_score,
    ]

    if any(blockers):
        return TradingDecision(
            action="NO_TRADE",
            confidence=analysis.confidence,
            holding_hours=0,
            reason="Недостатня сила/надійність сигналу або новина підозріла.",
        )

    action = "LONG" if analysis.score > 0 else "SHORT"

    return TradingDecision(
        action=action,
        confidence=analysis.confidence,
        holding_hours=analysis.recommended_holding_hours,
        reason=(
            f"Score {analysis.score}, importance {analysis.importance}, "
            f"confidence {analysis.confidence}."
        ),
    )
