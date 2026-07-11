from typing import Literal
from pydantic import BaseModel, Field


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


class TradingDecision(BaseModel):
    action: Literal["LONG", "SHORT", "NO_TRADE"]
    confidence: int
    holding_hours: float
    reason: str
