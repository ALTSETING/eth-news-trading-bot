import os
import queue
import threading
import time
from dotenv import load_dotenv

from database import init_db, exists, save_news
from news_source import fetch_news
from openai_analyzer import analyze_news
from strategy import make_decision
from terminal_ui import render_loop

load_dotenv()

NEWS_POLL_SECONDS = int(os.getenv("NEWS_POLL_SECONDS", "60"))
TERMINAL_REFRESH_SECONDS = float(os.getenv("TERMINAL_REFRESH_SECONDS", "1"))

news_queue: queue.Queue[dict] = queue.Queue()
stop_event = threading.Event()
status = {"state": "starting", "queue": 0, "error": "-"}


def collector():
    while not stop_event.is_set():
        try:
            status["state"] = "searching_news"
            items = fetch_news()

            for item in reversed(items):
                if not exists(item["external_id"]):
                    news_queue.put(item)

            status["queue"] = news_queue.qsize()
            status["state"] = "waiting"
            status["error"] = "-"
        except Exception as exc:
            status["error"] = f"collector: {exc}"
            status["state"] = "error"

        stop_event.wait(NEWS_POLL_SECONDS)


def analyzer_worker():
    while not stop_event.is_set():
        try:
            item = news_queue.get(timeout=1)
        except queue.Empty:
            continue

        try:
            status["state"] = "openai_analysis"
            status["queue"] = news_queue.qsize()

            analysis = analyze_news(item)
            decision = make_decision(analysis)

            save_news(
                {
                    **item,
                    "category": analysis.category,
                    "subcategory": analysis.subcategory,
                    "score": analysis.score,
                    "importance": analysis.importance,
                    "confidence": analysis.confidence,
                    "direction": analysis.direction,
                    "expected_delay_hours": analysis.expected_delay_hours,
                    "holding_hours": decision.holding_hours,
                    "fake_or_manipulative": int(analysis.is_fake_or_manipulative),
                    "duplicate_or_old": int(analysis.is_duplicate_or_old),
                    "summary_ua": analysis.summary_ua,
                    "reasoning_ua": analysis.reasoning_ua,
                    "action": decision.action,
                    "decision_reason": decision.reason,
                    "decision": analysis.decision,
                    "sentiment": analysis.sentiment,
                    "sentiment_score": analysis.sentiment_score,
                    "relevance_score": analysis.relevance_score,
                    "source_credibility": analysis.source_credibility,
                    "novelty_score": analysis.novelty_score,
                    "market_scope": analysis.market_scope,
                    "affected_assets": analysis.affected_assets,
                    "expected_direction": analysis.expected_direction,
                    "expected_move_min": analysis.expected_move_min,
                    "expected_move_max": analysis.expected_move_max,
                    "impact_timeframe": analysis.impact_timeframe,
                    "impact_duration": analysis.impact_duration,
                    "already_priced_in_probability": analysis.already_priced_in_probability,
                    "fake_or_misleading_probability": analysis.fake_or_misleading_probability,
                    "urgency_score": analysis.urgency_score,
                    "risk_level": analysis.risk_level,
                    "key_entities": analysis.key_entities,
                    "ai_summary": analysis.summary_ua,
                    "ai_reasoning": analysis.reasoning_ua,
                    "important_facts": analysis.important_facts,
                    "missing_information": analysis.missing_information,
                    "tags": analysis.tags,
                    "analysis_model": os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
                    "analysis_prompt_version": "2",
                }
            )
            status["error"] = "-"
        except Exception as exc:
            status["error"] = f"analysis: {exc}"
        finally:
            news_queue.task_done()
            status["queue"] = news_queue.qsize()
            status["state"] = "waiting"


def main():
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Додай OPENAI_API_KEY у файл .env")

    init_db()

    threads = [
        threading.Thread(target=collector, daemon=True),
        threading.Thread(target=analyzer_worker, daemon=True),
        threading.Thread(
            target=render_loop,
            args=(status, stop_event, TERMINAL_REFRESH_SECONDS),
            daemon=True,
        ),
    ]

    for thread in threads:
        thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        status["state"] = "stopping"
        stop_event.set()
        for thread in threads:
            thread.join(timeout=3)


if __name__ == "__main__":
    main()
