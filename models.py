from typing import Literal
from pydantic import BaseModel, Field, model_validator


Category = Literal[
    "institutional_money",
    "regulation",
    "protocol_upgrade",
    "security_improvement",
    "security_incident",
    "ethereum_foundation_developers",
    "onchain_activity",
    "defi_ecosystem",
    "exchanges_liquidity",
    "macroeconomics",
    "competitors",
    "reputation_media",
    "other",
]


class NewsAnalysis(BaseModel):
    is_relevant_to_eth: bool
    category: Category
    subcategory: str
    score: int = Field(ge=-100, le=100)
    importance: int = Field(ge=0, le=100)
    confidence: int = Field(ge=0, le=100)
    direction: Literal["bullish", "bearish", "neutral"]
    expected_delay_hours: float = Field(ge=0, le=720)
    recommended_holding_hours: float = Field(ge=0, le=720)
    is_fake_or_manipulative: bool
    is_duplicate_or_old: bool
    affected_assets: list[str]
    summary_ua: str
    reasoning_ua: str
    decision: Literal["BUY", "SELL", "HOLD", "NO_TRADE"] = "NO_TRADE"
    sentiment: Literal[
        "very_negative", "negative", "neutral", "positive", "very_positive"
    ] = "neutral"
    sentiment_score: float = Field(default=0.0, ge=-1.0, le=1.0)
    relevance_score: int = Field(default=0, ge=0, le=100)
    source_credibility: int = Field(default=50, ge=0, le=100)
    novelty_score: int = Field(default=30, ge=0, le=100)
    market_scope: Literal[
        "single_asset", "sector", "crypto_market", "global_market"
    ] = "single_asset"
    expected_direction: Literal[
        "strong_down", "down", "neutral", "up", "strong_up", "uncertain"
    ] = "uncertain"
    expected_move_min: float = 0.0
    expected_move_max: float = 0.0
    impact_timeframe: Literal[
        "minutes", "hours", "one_day", "several_days", "weeks", "months",
        "long_term", "unknown",
    ] = "unknown"
    impact_duration: Literal[
        "very_short", "short", "medium", "long", "permanent", "unknown"
    ] = "unknown"
    already_priced_in_probability: int = Field(default=50, ge=0, le=100)
    fake_or_misleading_probability: int = Field(default=50, ge=0, le=100)
    urgency_score: int = Field(default=0, ge=0, le=100)
    risk_level: Literal["low", "medium", "high", "extreme"] = "high"
    key_entities: list[str] = Field(default_factory=list)
    important_facts: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_move_range(self):
        if self.expected_move_min > self.expected_move_max:
            raise ValueError("expected_move_min must be <= expected_move_max")
        return self


class TradingDecision(BaseModel):
    action: Literal["LONG", "SHORT", "NO_TRADE"]
    confidence: int
    holding_hours: float
    reason: str
