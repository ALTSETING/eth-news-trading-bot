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
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.removeprefix("json").strip()

    return NewsAnalysis.model_validate_json(raw)
