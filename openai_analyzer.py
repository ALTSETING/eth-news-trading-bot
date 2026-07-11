import json
import os
from openai import OpenAI
from models import NewsAnalysis

CATEGORIES = '''
1. institutional_money — купівля ETH компаніями, treasury strategy,
   ETF inflows, банки/фонди, фінансування Ethereum-проєктів.
2. regulation — ETF, SEC, стейкінг, заборони, судові рішення.
3. protocol_upgrade — апгрейди, throughput, fees, EVM, L1/L2, staking.
4. security_improvement — захист, post-quantum, виправлення вразливостей.
5. security_incident — hack, exploit, theft, compromised keys, bridge attack.
6. ethereum_foundation_developers — Vitalik, roadmap, leadership, ETH sales.
7. onchain_activity — transactions, exchange flows, whales, staking, unlocks.
8. defi_ecosystem — TVL, DeFi launches/failures, stablecoins, liquidations.
9. exchanges_liquidity — listing/delisting, withdrawals, reserves, futures.
10. macroeconomics — Fed, inflation, dollar, stocks, risk appetite, geopolitics.
11. competitors — Solana, BNB, Avalanche, migrations and liquidity shifts.
12. reputation_media — endorsements, criticism, hype, fake/old/manipulative news.
'''

SYSTEM_PROMPT = f'''
Ти — модуль аналізу новин для PAPER trading-бота ETH.
Класифікуй новину за категоріями:

{CATEGORIES}

Оціни можливий вплив саме на ціну ETH:
- score: від -100 (дуже негативно) до 100 (дуже позитивно);
- importance: 0..100;
- confidence: 0..100;
- expected_delay_hours: через скільки годин може проявитися реакція;
- recommended_holding_hours: орієнтовний час утримання PAPER-позиції.

Додатково оціни: sentiment і sentiment_score (-1.0..1.0), relevance_score,
source_credibility, novelty_score, market_scope, affected_assets,
expected_direction, консервативний діапазон expected_move_min/max у відсотках,
impact_timeframe, impact_duration, already_priced_in_probability,
fake_or_misleading_probability, urgency_score, risk_level, key_entities,
important_facts, missing_information і tags. Усі score/probability, крім
sentiment_score та старого score, мають діапазон 0..100.

summary_ua (2–3 речення) і reasoning_ua (4–6 речень) пиши українською.
Reasoning — лише коротке фінальне пояснення: що сталося, значення для ETH,
можливий напрямок та невизначеність; не показуй прихований ланцюжок міркувань.
important_facts має містити тільки факти з вхідних даних. Якщо даних бракує,
переліч їх у missing_information. Якщо надано лише заголовок, знижуй confidence.

decision: BUY, SELL, HOLD або NO_TRADE. Використовуй NO_TRADE, якщо relevance_score
< 40, source_credibility < 40, fake_or_misleading_probability > 60,
expected_direction = uncertain, importance дуже низька, або матеріал є оглядом,
прогнозом, думкою чи не містить нової конкретної події.

Не вигадуй фактів. Аналізуй тільки заголовок і надані поля.
Для сумнівних, старих, повторних або маніпулятивних заголовків знижуй confidence.
Поверни ТІЛЬКИ валідний JSON без markdown.
'''


def analyze_news(news: dict) -> NewsAnalysis:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    schema_hint = {
        "is_relevant_to_eth": True,
        "category": "institutional_money",
        "subcategory": "короткий тип події",
        "score": 0,
        "importance": 0,
        "confidence": 0,
        "direction": "neutral",
        "expected_delay_hours": 0,
        "recommended_holding_hours": 0,
        "is_fake_or_manipulative": False,
        "is_duplicate_or_old": False,
        "affected_assets": ["ETH"],
        "summary_ua": "Короткий опис українською",
        "reasoning_ua": "Коротке пояснення оцінки українською",
        "decision": "NO_TRADE",
        "sentiment": "neutral", "sentiment_score": 0.0,
        "relevance_score": 0, "source_credibility": 50, "novelty_score": 30,
        "market_scope": "single_asset", "expected_direction": "uncertain",
        "expected_move_min": 0.0, "expected_move_max": 0.0,
        "impact_timeframe": "unknown", "impact_duration": "unknown",
        "already_priced_in_probability": 50,
        "fake_or_misleading_probability": 50, "urgency_score": 0,
        "risk_level": "high", "key_entities": [], "important_facts": [],
        "missing_information": [], "tags": [],
    }

    response = client.responses.create(
        model=model,
        instructions=SYSTEM_PROMPT,
        input=(
            "Проаналізуй новину:\n"
            f"Title: {news['title']}\n"
            f"Source: {news['source']}\n"
            f"Published: {news['published']}\n"
            f"URL: {news['url']}\n\n"
            f"Очікувана структура JSON:\n{json.dumps(schema_hint, ensure_ascii=False)}"
        ),
    )

    raw = response.output_text.strip()
    try:
        return NewsAnalysis.model_validate_json(raw)
    except Exception:
        # Keep malformed model output visible to the worker/status log.
        raise ValueError(f"Invalid OpenAI analysis JSON: {raw[:300]!r}")
