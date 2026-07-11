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
        analysis.relevance_score < 40,
        analysis.source_credibility < 40,
        analysis.fake_or_misleading_probability > 60,
        analysis.expected_direction == "uncertain",
        analysis.risk_level == "extreme",
    ]

    if any(blockers):
        return TradingDecision(
            action="NO_TRADE",
            confidence=analysis.confidence,
            holding_hours=0,
            reason="Недостатня сила/надійність сигналу або новина підозріла.",
        )

    buy_signal = (
        analysis.score > 0 and analysis.sentiment_score > 0
        and analysis.expected_direction in {"up", "strong_up"}
        and analysis.relevance_score >= 60 and analysis.confidence >= 60
        and analysis.source_credibility >= 50
    )
    sell_signal = (
        analysis.score < 0 and analysis.sentiment_score < 0
        and analysis.expected_direction in {"down", "strong_down"}
        and analysis.relevance_score >= 60 and analysis.confidence >= 60
        and analysis.source_credibility >= 50
    )
    if not (buy_signal or sell_signal):
        return TradingDecision(
            action="NO_TRADE", confidence=analysis.confidence, holding_hours=0,
            reason="Нові показники не підтверджують напрямок сигналу.",
        )

    action = "LONG" if buy_signal else "SHORT"

    return TradingDecision(
        action=action,
        confidence=analysis.confidence,
        holding_hours=analysis.recommended_holding_hours,
        reason=(
            f"Score {analysis.score}, importance {analysis.importance}, "
            f"confidence {analysis.confidence}."
        ),
    )
