import sqlite3
from pathlib import Path

DB_PATH = Path("eth_news_bot.db")


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


def exists(external_id: str) -> bool:
    with connect() as con:
        row = con.execute(
            "SELECT 1 FROM news WHERE external_id = ?", (external_id,)
        ).fetchone()
    return row is not None


def save_news(item: dict) -> None:
    with connect() as con:
        con.execute(
            '''
            INSERT OR IGNORE INTO news (
                external_id, title, url, source, published,
                category, subcategory, score, importance, confidence,
                direction, expected_delay_hours, holding_hours,
                fake_or_manipulative, duplicate_or_old,
                summary_ua, reasoning_ua, action, decision_reason
            ) VALUES (
                :external_id, :title, :url, :source, :published,
                :category, :subcategory, :score, :importance, :confidence,
                :direction, :expected_delay_hours, :holding_hours,
                :fake_or_manipulative, :duplicate_or_old,
                :summary_ua, :reasoning_ua, :action, :decision_reason
            )
            ''',
            item,
        )


def latest_news(limit: int = 12):
    with connect() as con:
        return con.execute(
            "SELECT * FROM news ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()


def total_count() -> int:
    with connect() as con:
        return con.execute("SELECT COUNT(*) FROM news").fetchone()[0]
