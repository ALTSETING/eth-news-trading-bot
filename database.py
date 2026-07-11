import json
import sqlite3
from pathlib import Path

DB_PATH = Path("eth_news_bot.db")

NEW_COLUMNS = {
    "sentiment": "TEXT", "sentiment_score": "REAL", "relevance_score": "INTEGER",
    "source_credibility": "INTEGER", "novelty_score": "INTEGER",
    "market_scope": "TEXT", "affected_assets": "TEXT",
    "expected_direction": "TEXT", "expected_move_min": "REAL",
    "expected_move_max": "REAL", "impact_timeframe": "TEXT",
    "impact_duration": "TEXT", "already_priced_in_probability": "INTEGER",
    "fake_or_misleading_probability": "INTEGER", "urgency_score": "INTEGER",
    "risk_level": "TEXT", "key_entities": "TEXT", "ai_summary": "TEXT",
    "ai_reasoning": "TEXT", "important_facts": "TEXT",
    "missing_information": "TEXT", "tags": "TEXT", "analysis_model": "TEXT",
    "analysis_prompt_version": "TEXT", "decision": "TEXT",
}
JSON_COLUMNS = {"affected_assets", "key_entities", "important_facts", "missing_information", "tags"}


def connect() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def init_db() -> None:
    with connect() as con:
        con.execute(
            '''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                external_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                url TEXT,
                source TEXT,
                published TEXT,
                category TEXT,
                subcategory TEXT,
                score INTEGER,
                importance INTEGER,
                confidence INTEGER,
                direction TEXT,
                expected_delay_hours REAL,
                holding_hours REAL,
                fake_or_manipulative INTEGER,
                duplicate_or_old INTEGER,
                summary_ua TEXT,
                reasoning_ua TEXT,
                action TEXT,
                decision_reason TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            '''
        )
        existing = {row[1] for row in con.execute("PRAGMA table_info(news)")}
        for name, column_type in NEW_COLUMNS.items():
            if name not in existing:
                con.execute(f'ALTER TABLE news ADD COLUMN "{name}" {column_type}')


def exists(external_id: str) -> bool:
    with connect() as con:
        row = con.execute(
            "SELECT 1 FROM news WHERE external_id = ?", (external_id,)
        ).fetchone()
    return row is not None


def save_news(item: dict) -> None:
    item = dict(item)
    for name in JSON_COLUMNS:
        item[name] = json.dumps(item.get(name, []), ensure_ascii=False)
    with connect() as con:
        con.execute(
            '''
            INSERT OR IGNORE INTO news (
                external_id, title, url, source, published,
                category, subcategory, score, importance, confidence,
                direction, expected_delay_hours, holding_hours,
                fake_or_manipulative, duplicate_or_old,
                summary_ua, reasoning_ua, action, decision_reason,
                sentiment, sentiment_score, relevance_score, source_credibility,
                novelty_score, market_scope, affected_assets, expected_direction,
                expected_move_min, expected_move_max, impact_timeframe,
                impact_duration, already_priced_in_probability,
                fake_or_misleading_probability, urgency_score, risk_level,
                key_entities, ai_summary, ai_reasoning, important_facts,
                missing_information, tags, analysis_model, analysis_prompt_version,
                decision
            ) VALUES (
                :external_id, :title, :url, :source, :published,
                :category, :subcategory, :score, :importance, :confidence,
                :direction, :expected_delay_hours, :holding_hours,
                :fake_or_manipulative, :duplicate_or_old,
                :summary_ua, :reasoning_ua, :action, :decision_reason,
                :sentiment, :sentiment_score, :relevance_score, :source_credibility,
                :novelty_score, :market_scope, :affected_assets, :expected_direction,
                :expected_move_min, :expected_move_max, :impact_timeframe,
                :impact_duration, :already_priced_in_probability,
                :fake_or_misleading_probability, :urgency_score, :risk_level,
                :key_entities, :ai_summary, :ai_reasoning, :important_facts,
                :missing_information, :tags, :analysis_model, :analysis_prompt_version,
                :decision
            )
            ''',
            item,
        )


def latest_news(limit: int = 12):
    with connect() as con:
        rows = con.execute(
            "SELECT * FROM news ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        for name in JSON_COLUMNS:
            try:
                item[name] = json.loads(item.get(name) or "[]")
            except (json.JSONDecodeError, TypeError):
                item[name] = []
        result.append(item)
    return result


def total_count() -> int:
    with connect() as con:
        return con.execute("SELECT COUNT(*) FROM news").fetchone()[0]
